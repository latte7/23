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
        prompt = f"""Create a personalized workout plan based on the following information:
        Fitness Level: {data['fitnessLevel']}
        Fitness Goals: {data['goals']}
        Workout Days Per Week: {data['workoutDays']}
        Physical Limitations: {data['disabilities'] if data.get('disabilities') else 'None'}
        Additional Requirements: {data['requirements'] if data.get('requirements') else 'None'}

        Please provide a detailed workout plan that:
        1. Respects any physical limitations
        2. Matches the specified number of workout days ({data['workoutDays']})
        3. Focuses on the stated fitness goals ({data['goals']})
        4. Is appropriate for the given fitness level ({data['fitnessLevel']})
        5. Includes specific exercises, sets, and reps
        6. Provides rest day recommendations
        """

        print("Sending prompt to Cohere:", prompt)

        try:
            # Generate response using Cohere
            response = co.generate(
                model='command',
                prompt=prompt,
                max_tokens=1000,
                temperature=0.7,
                k=0,
                stop_sequences=[],
                return_likelihoods='NONE'
            )
            
            plan = response.generations[0].text.strip()
            print("Received response from Cohere:", plan[:100] + "...")  # Print first 100 chars
            
            return jsonify({
                'plan': plan
            })

        except Exception as cohere_error:
            print("Cohere API error:", str(cohere_error))
            return jsonify({'error': f'Cohere API error: {str(cohere_error)}'}), 500

    except Exception as e:
        print("Server error:", str(e))
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
