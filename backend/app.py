from flask import Flask, request, jsonify
from flask_cors import CORS
import cohere
import os
from dotenv import load_dotenv

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

        # Create prompt for Cohere
        selected_days = ', '.join(data['workoutDays'])
        prompt = f"""As a certified personal trainer and rehabilitation specialist, create a workout plan that prioritizes safety and effectiveness based on the following client profile:

USER PROFILE:
- Fitness Level: {data['fitnessLevel']}
- Primary Goal: {data['goals']}
- Workout Days: {selected_days}
- Physical Limitations or Disabilities: {data['disabilities'] if data.get('disabilities') else 'None'}
- Additional Requirements: {data['requirements'] if data.get('requirements') else 'None'}

EXERCISE SELECTION CRITERIA:
1. SAFETY FIRST: Begin by analyzing the client's disabilities and injuries to:
   - Identify movements that must be avoided
   - List safe movement patterns that won't aggravate existing conditions
   - Determine appropriate exercise modifications needed

2. EXERCISE ADAPTATION:
   - Choose exercises that can be safely performed with their specific limitations
   - Include alternative versions of exercises when needed
   - Specify any equipment modifications required
   - Adjust ranges of motion based on physical limitations

3. PROGRESSION PLANNING:
   - Start with the most conservative version of each exercise
   - Include specific form cues that address their limitations
   - Plan gradual progression that respects their conditions

First, provide a detailed program focus explanation:
[FOCUS]
Explain how this program specifically addresses the client's limitations and goals:
1. How exercises were selected to work around their specific disabilities/injuries
2. Why these exercises are safe and effective for their condition
3. How the program allows for progress while maintaining safety
[/FOCUS]

Then list the daily exercises with explanations for each:

[Day]:
- [Exercise Name]: [Sets] x [Reps] (Optional: Rest [Time])
  [EXPLANATION]: Explain why this exercise is safe for their condition and how it's been modified for their specific needs

Example Format:
Mon:
- Modified Push-ups: 3 x 8 (Rest 90 seconds)
  [EXPLANATION]: Wall push-ups chosen to accommodate shoulder limitation, reducing stress on joints while building strength safely.
- Seated Rows: 3 x 12 (Rest 60 seconds)
  [EXPLANATION]: Seated position provides stability for lower back condition, focusing on proper scapular retraction.

Note: Each exercise must include:
1. Specific modifications for their disabilities/injuries
2. Why it's safe for their condition
3. How it helps achieve their goals while respecting limitations"""

        print("Sending prompt to Cohere:", prompt)

        try:
            # Generate response using Cohere with optimized parameters
            response = co.generate(
                model='command',
                prompt=prompt,
                max_tokens=2000,  # Increased for more detailed responses
                temperature=0.4,  # Reduced for more consistent outputs
                k=0,
                stop_sequences=["\n\n\n"],  # Stop at triple newline to maintain formatting
                return_likelihoods='NONE'
            )
            
            plan = response.generations[0].text.strip()
            print("Received response from Cohere:", plan[:100] + "...")  # Print first 100 chars
            
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
                if any(line.lower().startswith(day.lower() + ':') for day in data['workoutDays']):
                    if current_day:  # Add spacing between days
                        formatted_lines.append('')
                    current_day = line
                    formatted_lines.append(line)
                elif line.startswith('-'):
                    formatted_lines.append(line)
                elif line.startswith('[EXPLANATION]'):
                    # Ensure explanation is properly indented
                    formatted_lines.append('  ' + line)
                else:
                    # If it's an exercise without a dash, add one
                    formatted_lines.append(f"- {line}")
            
            formatted_plan = '\n'.join(formatted_lines)
            
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
