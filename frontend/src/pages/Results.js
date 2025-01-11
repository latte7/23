import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const workoutPlans = {
  beginner: {
    strength: [
      { day: 'Monday', focus: 'Full Body Strength', exercises: ['Squats', 'Push-ups', 'Dumbbell Rows'] },
      { day: 'Wednesday', focus: 'Core & Cardio', exercises: ['Planks', 'Mountain Climbers', 'Walking'] },
      { day: 'Friday', focus: 'Full Body Strength', exercises: ['Lunges', 'Bench Press', 'Lat Pulldowns'] }
    ],
    muscle: [
      { day: 'Monday', focus: 'Upper Body', exercises: ['Push-ups', 'Dumbbell Curls', 'Tricep Extensions'] },
      { day: 'Wednesday', focus: 'Lower Body', exercises: ['Squats', 'Lunges', 'Calf Raises'] },
      { day: 'Friday', focus: 'Full Body', exercises: ['Bench Press', 'Rows', 'Leg Press'] }
    ],
    endurance: [
      { day: 'Monday', focus: 'Cardio', exercises: ['Jogging', 'Jump Rope', 'Burpees'] },
      { day: 'Wednesday', focus: 'Circuit Training', exercises: ['Mountain Climbers', 'High Knees', 'Jumping Jacks'] },
      { day: 'Friday', focus: 'Endurance Strength', exercises: ['Body Weight Squats', 'Push-ups', 'Pull-ups'] }
    ],
    'weight-loss': [
      { day: 'Monday', focus: 'HIIT', exercises: ['Burpees', 'Mountain Climbers', 'Jump Rope'] },
      { day: 'Wednesday', focus: 'Strength & Cardio', exercises: ['Circuit Training', 'Rowing', 'Cycling'] },
      { day: 'Friday', focus: 'Full Body', exercises: ['Squats', 'Push-ups', 'Planks'] }
    ]
  }
  // Add more plans for intermediate and advanced levels
};

const Results = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState(null);
  const [workoutPlan, setWorkoutPlan] = useState(null);

  useEffect(() => {
    const savedData = localStorage.getItem('workoutFormData');
    if (!savedData) {
      navigate('/form');
      return;
    }

    const parsedData = JSON.parse(savedData);
    setFormData(parsedData);

    // Get the workout plan based on fitness level and goals
    const plan = workoutPlans[parsedData.fitnessLevel]?.[parsedData.goals];
    setWorkoutPlan(plan);
  }, [navigate]);

  if (!formData || !workoutPlan) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        Loading your workout plan...
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-center" role="heading">
          Your Personalized Workout Plan
        </h1>
        
        <div className="bg-blue-50 p-4 rounded-lg mb-6">
          <h2 className="text-xl font-semibold mb-2">Plan Details</h2>
          <p><strong>Fitness Level:</strong> {formData.fitnessLevel}</p>
          <p><strong>Goal:</strong> {formData.goals}</p>
          {formData.requirements && (
            <p><strong>Special Requirements:</strong> {formData.requirements}</p>
          )}
        </div>

        <div className="space-y-6">
          {workoutPlan.map((day, index) => (
            <div 
              key={index} 
              className="bg-white p-6 rounded-lg shadow-lg"
              role="region"
              aria-label={`Workout for ${day.day}`}
            >
              <h3 className="text-xl font-semibold mb-2">{day.day}</h3>
              <p className="text-blue-600 mb-3">Focus: {day.focus}</p>
              <ul className="list-disc list-inside space-y-2">
                {day.exercises.map((exercise, i) => (
                  <li key={i} className="text-gray-700">{exercise}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-8 text-center">
          <button
            onClick={() => navigate('/form')}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            aria-label="Create a new workout plan"
          >
            Create New Plan
          </button>
        </div>
      </div>
    </div>
  );
};

export default Results;
