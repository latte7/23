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
        prompt = f"""Create a concise workout plan for a {data['fitnessLevel']} level person focusing on {data['goals']}, training on these days: {selected_days}.
{f'Accommodate for: {data["disabilities"]}.' if data.get('disabilities') else ''}
{f'Additional requirements: {data["requirements"]}.' if data.get('requirements') else ''}

[FOCUS]
Brief program focus explaining safety and effectiveness for the user's level and goals.
[/FOCUS]

For each day, provide 2-3 exercises in this format:
[Day]:
- [Exercise]: [Sets] x [Reps] (Rest [Time])
  [EXPLANATION]: Brief explanation of form and safety

Example:
Mon:
- Push-ups: 3 x 8 (Rest 60s)
  [EXPLANATION]: Keep core tight, modify on knees if needed
- Squats: 3 x 10 (Rest 60s)
  [EXPLANATION]: Focus on form, go only as deep as comfortable

IMPORTANT: Provide exercises for ALL of these days: {selected_days}"""

        print("Sending prompt to Cohere:", prompt)

        try:
            # Generate response using Cohere with optimized parameters
            response = co.generate(
                model='command',
                prompt=prompt,
                max_tokens=1500,  # Reduced for faster response
                temperature=0.4,  # Reduced for more consistent outputs
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
                    # Ensure consistent day format (add colon if missing)
                    if not line.endswith(':'):
                        line = line + ':'
                    current_day = line
                    formatted_lines.append(line)
                elif line.startswith('-'):
                    # Ensure exercise format is correct
                    if ':' in line and 'x' in line.lower():
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
                    formatted_plan += f"\n\n{day}:\n- Basic Exercise: 3 x 10 (Rest 60s)\n  [EXPLANATION]: Starting with a basic exercise suitable for your level."
            
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
