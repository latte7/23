from flask import Flask, request, jsonify
from flask_cors import CORS
import cohere
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize Cohere client
api_key = os.getenv('COHERE_API_KEY')
if not api_key:
    raise ValueError("COHERE_API_KEY not found in environment variables. Please check your .env file.")

try:
    co = cohere.Client(api_key)
    # Test the client with a simple completion to verify it works
    test_response = co.generate(
        model='command',
        prompt='Say "test"',
        max_tokens=5
    )
    print("Cohere client initialized successfully")
except Exception as e:
    print(f"Error initializing Cohere client: {str(e)}")
    raise

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "Backend server is running"}), 200

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    try:
        start_time = time.time()
        
        # Check if API key is available
        if not os.getenv('COHERE_API_KEY'):
            return jsonify({'error': 'Cohere API key not found'}), 500

        # Log incoming request
        data = request.json
        print("Received form data:", data)
        
        # Validate required fields
        required_fields = ['fitnessLevel', 'goals', 'workoutDays']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Create prompt for Cohere - optimized for faster response
        selected_days = ', '.join(data['workoutDays'])
        prompt = f"""Create a comprehensive split-based workout plan for a {data['fitnessLevel']} level person focusing on {data['goals']}, training on these days: {selected_days}.
{f'Accommodate for: {data["disabilities"]}.' if data.get('disabilities') else ''}
{f'Additional requirements: {data["requirements"]}.' if data.get('requirements') else ''}

[FOCUS]
Brief program focus explaining the split routine structure and its effectiveness for the user's goals.
[/FOCUS]

Organize the workouts in a Push/Pull/Legs split or Upper/Lower split based on the number of workout days.
For each day, provide 3-5 exercises that target the day's muscle groups, using this format:
[Day]:
- [Exercise]: [Sets] x [Reps] (Rest [Time])
  [EXPLANATION]: Brief explanation of form, safety, and muscle engagement

Example:
(Mon (Push):
 - Incline Push-ups: 3 x 12 (Rest 90s)
  [EXPLANATION]: Keep core tight, hands shoulder-width, focus on chest engagement
 - Shoulder Press: 3 x 10 (Rest 90s)
  [EXPLANATION]: Stand or sit with back straight, press directly overhead
 - Diamond Push-ups: 3 x 8 (Rest 90s)
  [EXPLANATION]: Hands close together, elbows tucked for tricep focus
 - Lateral Raises: 3 x 12 (Rest 60s)
  [EXPLANATION]: Slight bend in elbows, controlled movement

Wed (Pull):
 - Inverted Rows: 3 x 10 (Rest 90s)
  [EXPLANATION]: Use table or bar, keep body straight, squeeze shoulder blades
 - Face Pulls: 3 x 15 (Rest 60s)
  [EXPLANATION]: Pull toward face level, focus on rear deltoids
 - Chin-ups or Band Pull-downs: 3 x 8 (Rest 90s)
  [EXPLANATION]: Focus on lat engagement, controlled negative
 - Reverse Flyes: 3 x 12 (Rest 60s)
  [EXPLANATION]: Bend forward, keep back straight, squeeze shoulder blades)

IMPORTANT: 
- Provide exercises for ALL of these days: {selected_days}
- Each day should focus on specific muscle groups following the split pattern
- Include 3-5 exercises per day with proper progression
- Adjust exercise difficulty based on the {data['fitnessLevel']} fitness level"""

        print("Sending prompt to Cohere:", prompt)

        try:
            # Generate response using Cohere with optimized parameters
            response = co.generate(
                model='command',
                prompt=prompt,
                max_tokens=2500,  # Increased for more complete responses
                temperature=0.7,  # Increased for more creative responses
                k=0,
                stop_sequences=["\n\n\n"],
                return_likelihoods='NONE'
            )
            
            plan = response.generations[0].text.strip()
            print("Received response from Cohere:", plan[:100] + "...")
            
            # Process the response to ensure consistent formatting
            lines = plan.split('\n')
            formatted_lines = []
            current_day = None
            
            # First, find and extract the [FOCUS] section
            focus_section = ""
            in_focus = False
            remaining_lines = []
            
            for line in lines:
                if "[FOCUS]" in line:
                    in_focus = True
                    continue
                elif "[/FOCUS]" in line:
                    in_focus = False
                    continue
                elif in_focus:
                    focus_section += line + "\n"
                else:
                    remaining_lines.append(line)
            
            # Determine split type based on number of workout days
            total_days = len(data['workoutDays'])
            if total_days <= 3:
                split_type = "Upper/Lower"
                split_mapping = {0: "Upper", 1: "Lower", 2: "Upper"}
            else:
                split_type = "Push/Pull/Legs"
                split_mapping = {0: "Push", 1: "Pull", 2: "Legs"}
            
            # Then process the exercise days
            for line in remaining_lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line starts with a day
                day_prefixes = data['workoutDays'] + [d + ':' for d in data['workoutDays']]
                is_day_header = any(line.lower().startswith(day.lower()) for day in day_prefixes)
                
                if is_day_header:
                    if current_day:  # Add spacing between days
                        formatted_lines.append('')
                    # Extract day and add split type
                    day = next(d for d in day_prefixes if line.lower().startswith(d.lower()))
                    day_index = data['workoutDays'].index(day.rstrip(':'))
                    split = split_mapping[day_index % len(split_mapping)]
                    current_day = f"{day.rstrip(':')} ({split}):"
                    formatted_lines.append(current_day)
                elif line.startswith('-'):
                    # Ensure exercise format is correct
                    if ':' in line and 'x' in line.lower():
                        # Standardize rest time format
                        if '(Rest' in line:
                            line = line.replace('seconds', 's').replace('second', 's')
                            if not line.endswith(')'):
                                line += ')'
                        formatted_lines.append(line)
                    else:
                        # Try to fix common formatting issues
                        parts = line.split('-', 1)[1].strip().split(':', 1)
                        if len(parts) == 2:
                            exercise_name = parts[0].strip()
                            details = parts[1].strip()
                            formatted_lines.append(f"- {exercise_name}: {details}")
                        else:
                            formatted_lines.append(line)
                elif line.startswith('[EXPLANATION]'):
                    # Ensure explanation is properly indented and formatted
                    formatted_lines.append('  ' + line)
                else:
                    # If it's an exercise without a dash, add one
                    formatted_lines.append(f"- {line}")
            
            formatted_plan = '\n'.join(formatted_lines)
            
            # Ensure each selected day has at least one exercise
            for day in data['workoutDays']:
                day_found = False
                for line in formatted_lines:
                    if line.lower().startswith(day.lower() + ':'):
                        day_found = True
                        break
                if not day_found:
                    # Determine workout split based on number of workout days
                    total_days = len(data['workoutDays'])
                    day_index = data['workoutDays'].index(day)
                    
                    # Default split-based exercises
                    splits = {
                        'push': {
                            'beginner': [
                                ('Push-ups', '3 x 10', 'Keep core tight, modify on knees if needed'),
                                ('Wall Pike Push-ups', '3 x 8', 'Walk feet closer to wall for more difficulty'),
                                ('Tricep Dips on Chair', '3 x 8', 'Keep elbows close to body, lower slowly'),
                                ('Incline Push-ups', '3 x 10', 'Higher surface for less difficulty, focus on chest')
                            ],
                            'intermediate': [
                                ('Diamond Push-ups', '3 x 12', 'Keep elbows close, focus on triceps'),
                                ('Pike Push-ups', '3 x 10', 'Progress toward handstand push-up'),
                                ('Dips', '3 x 10', 'Full range of motion, chest forward for chest focus'),
                                ('Decline Push-ups', '3 x 12', 'Elevate feet, focus on upper chest')
                            ],
                            'advanced': [
                                ('Handstand Push-ups', '3 x 8', 'Use wall for balance, focus on shoulder strength'),
                                ('Ring Push-ups', '3 x 12', 'Control the rings, keep body tight'),
                                ('Weighted Dips', '3 x 10', 'Add weight as you progress'),
                                ('Planche Push-up Progression', '3 x 6', 'Start with tuck planche, progress slowly')
                            ]
                        },
                        'pull': {
                            'beginner': [
                                ('Inverted Rows', '3 x 10', 'Use table or low bar, keep body straight'),
                                ('Band Pull-aparts', '3 x 12', 'Focus on squeezing shoulder blades'),
                                ('Negative Pull-ups', '3 x 5', 'Lower slowly, focus on control'),
                                ('Face Pulls with Band', '3 x 15', 'Pull to face level, focus on rear delts')
                            ],
                            'intermediate': [
                                ('Pull-ups', '3 x 8', 'Full range of motion, engage lats'),
                                ('Australian Pull-ups', '3 x 12', 'Feet elevated for more difficulty'),
                                ('Scapular Pulls', '3 x 12', 'Focus on shoulder blade movement'),
                                ('Band Rows', '3 x 15', 'Squeeze shoulder blades, keep elbows close')
                            ],
                            'advanced': [
                                ('Weighted Pull-ups', '3 x 8', 'Add weight progressively'),
                                ('L-Sit Pull-ups', '3 x 8', 'Maintain L position throughout'),
                                ('Front Lever Rows', '3 x 6', 'Start with tuck position'),
                                ('One Arm Pull-up Progression', '3 x 5', 'Start with assisted variations')
                            ]
                        },
                        'legs': {
                            'beginner': [
                                ('Bodyweight Squats', '3 x 12', 'Keep chest up, push through heels'),
                                ('Lunges', '3 x 10/leg', 'Step forward, knee behind toes'),
                                ('Glute Bridges', '3 x 15', 'Squeeze glutes at top'),
                                ('Calf Raises', '3 x 20', 'Full range of motion, pause at top')
                            ],
                            'intermediate': [
                                ('Jump Squats', '3 x 10', 'Land softly, immediately sink into next rep'),
                                ('Walking Lunges', '3 x 12/leg', 'Keep torso upright, alternate legs'),
                                ('Single Leg Glute Bridges', '3 x 12/leg', 'Keep hips level'),
                                ('Split Squats', '3 x 10/leg', 'Control the movement, keep front knee stable')
                            ],
                            'advanced': [
                                ('Pistol Squats', '3 x 8/leg', 'Control descent, maintain balance'),
                                ('Plyometric Lunges', '3 x 10/leg', 'Explosive movement, land softly'),
                                ('Nordic Hamstring Curls', '3 x 6', 'Control lowering phase'),
                                ('Box Jumps', '3 x 8', 'Land softly, step down between reps')
                            ]
                        }
                    }
                    
                    # Determine split type based on workout frequency
                    if total_days <= 3:
                        # Full body or Upper/Lower split
                        split_type = 'push' if day_index % 2 == 0 else 'pull'
                    else:
                        # Push/Pull/Legs split
                        split_type = ['push', 'pull', 'legs'][day_index % 3]
                    
                    level = data.get('fitnessLevel', 'beginner')
                    exercises = splits[split_type][level]
                    
                    # Add the exercises to the plan
                    formatted_plan += f"\n\n{day} ({split_type.capitalize()}):"
                    for exercise, sets_reps, explanation in exercises:
                        formatted_plan += f"\n- {exercise}: {sets_reps} (Rest 90s)\n  [EXPLANATION]: {explanation}"
            
            end_time = time.time()
            print(f"Total processing time: {end_time - start_time:.2f} seconds")
            
            return jsonify({
                'plan': formatted_plan,
                'focus': focus_section.strip()
            })

        except Exception as cohere_error:
            print("Cohere API error:", str(cohere_error))
            return jsonify({'error': f'Cohere API error: {str(cohere_error)}'}), 500

    except Exception as e:
        print("Server error:", str(e))
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
