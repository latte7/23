# OptiHealth

Project for Deltahacks-xi

# OptiHealth

OptiHealth is an AI-powered workout split generator that personalizes fitness routines for individuals. It utilizes React.js with Tailwind CSS for the frontend and Flask for the backend, integrating the Cohere API as the AI-powered workout planner.

## Features
- AI-generated workout plans tailored to user goals
- Responsive and modern UI with Tailwind CSS
- Fast and scalable backend with Flask
- AI processing powered by the Cohere API

## Tech Stack
- **Frontend**: React.js, Tailwind CSS
- **Backend**: Flask (Python)
- **AI Integration**: Cohere API
- **Database**: SQLite/PostgreSQL (if applicable)

## Installation

### Prerequisites
Ensure you have the following installed:
- Node.js & npm
- Python & pip

### Backend Setup
```sh
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
flask run
```

### Frontend Setup
```sh
cd frontend
npm install
npm start
```

## Environment Variables
Create a `.env` file in the backend directory and add your Cohere API key:
```env
COHERE_API_KEY=your_cohere_api_key_here
```

## Usage
1. Open `http://localhost:3000` in your browser.
2. Enter your fitness goals and preferences.
3. Receive an AI-generated workout plan.


## License
This project is licensed under the MIT License.

