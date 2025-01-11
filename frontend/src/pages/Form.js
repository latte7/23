import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Form = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    fitnessLevel: '',
    goals: '',
    requirements: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // In a real app, we would send this data to a backend
    // For now, we'll store it in localStorage and redirect
    localStorage.setItem('workoutFormData', JSON.stringify(formData));
    navigate('/results');
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-lg mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-center" role="heading">
          Create Your Workout Plan
        </h1>
        <form onSubmit={handleSubmit} className="space-y-6" role="form">
          <div>
            <label 
              htmlFor="fitnessLevel" 
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Fitness Level
            </label>
            <select
              id="fitnessLevel"
              name="fitnessLevel"
              value={formData.fitnessLevel}
              onChange={handleChange}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              required
              aria-required="true"
            >
              <option value="">Select your fitness level</option>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>

          <div>
            <label 
              htmlFor="goals" 
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Fitness Goals
            </label>
            <select
              id="goals"
              name="goals"
              value={formData.goals}
              onChange={handleChange}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              required
              aria-required="true"
            >
              <option value="">Select your primary goal</option>
              <option value="strength">Build Strength</option>
              <option value="muscle">Build Muscle</option>
              <option value="endurance">Improve Endurance</option>
              <option value="weight-loss">Weight Loss</option>
            </select>
          </div>

          <div>
            <label 
              htmlFor="requirements" 
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Special Requirements
            </label>
            <textarea
              id="requirements"
              name="requirements"
              value={formData.requirements}
              onChange={handleChange}
              rows="4"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              placeholder="Any injuries, time constraints, or preferences?"
              aria-label="Special requirements or constraints"
            ></textarea>
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors"
            aria-label="Generate workout plan"
          >
            Generate Workout Plan
          </button>
        </form>
      </div>
    </div>
  );
};

export default Form;
