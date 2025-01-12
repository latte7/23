import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Results = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState(null);
  const [workoutPlan, setWorkoutPlan] = useState(null);

  useEffect(() => {
    const savedPlan = localStorage.getItem('workoutPlan');
    const savedData = localStorage.getItem('workoutFormData');
    
    if (!savedPlan || !savedData) {
      navigate('/form');
      return;
    }

    const parsedData = JSON.parse(savedData);
    const parsedPlan = JSON.parse(savedPlan);
    
    setFormData(parsedData);
    setWorkoutPlan(parsedPlan);
  }, [navigate]);

  if (!formData || !workoutPlan) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <div className="max-w-lg mx-auto">
          <h2 className="text-xl font-semibold mb-4">No workout plan found</h2>
          <p className="mb-4">Please create a new workout plan to get started.</p>
          <button
            onClick={() => navigate('/form')}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Create Workout Plan
          </button>
        </div>
      </div>
    );
  }

  const styledPlan = `
  <h2 style="font-size: 1.25rem; font-weight: bold; margin-bottom: 1rem; color: #1f2937;">
    Personalized Workout Plan
  </h2>
  <div style="white-space: pre-wrap; font-size: 1rem; line-height: 1.6; color: #374151;">
    ${workoutPlan.plan}
  </div>
`;


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
          <p><strong>Workout Days per Week:</strong> {formData.workoutDays}</p>
          {formData.disabilities && (
            <p><strong>Physical Limitations:</strong> {formData.disabilities}</p>
          )}
          {formData.requirements && (
            <p><strong>Additional Requirements:</strong> {formData.requirements}</p>
          )}
        </div>

        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold mb-4">Your Personalized Workout Plan</h3>
            <div
              className="bg-white p-6 rounded-lg shadow-lg"
              dangerouslySetInnerHTML={{ __html: styledPlan }}
        ></div>
          </div>
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
