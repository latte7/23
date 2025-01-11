import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Form = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    fitnessLevel: '',
    goals: '',
    requirements: '',
    workoutDays: '',
    disabilities: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateForm = () => {
    if (!formData.fitnessLevel) {
      alert('Please select your fitness level');
      return false;
    }
    if (!formData.goals) {
      alert('Please select your fitness goals');
      return false;
    }
    if (!formData.workoutDays) {
      alert('Please select number of workout days');
      return false;
    }
    return true;
  };

  const testBackendConnection = async () => {
    try {
      const response = await axios.get('http://localhost:5000/test');
      console.log('Backend connection test:', response.data);
      return true;
    } catch (error) {
      console.error('Backend connection test failed:', error);
      return false;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsLoading(true);

    // Test backend connection first
    const isConnected = await testBackendConnection();
    if (!isConnected) {
      alert('Unable to connect to the server. Please ensure the backend server is running.');
      setIsLoading(false);
      return;
    }
    try {
      // Store form data first
      localStorage.setItem('workoutFormData', JSON.stringify(formData));
      
      console.log('Sending data to backend:', formData);
      const response = await axios.post('http://localhost:5000/generate-plan', formData, {
        timeout: 30000 // 30 second timeout
      });
      console.log('Received response:', response.data);
      
      localStorage.setItem('workoutPlan', JSON.stringify(response.data));
      navigate('/results');
    } catch (error) {
      console.error('Detailed error:', error.response?.data || error.message);
      alert(`Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsLoading(false);
    }
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
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Number of Workout Days per Week
            </label>
            <div className="flex justify-center gap-4 flex-wrap">
              {[1, 2, 3, 4, 5, 6, 7].map((day) => (
                <button
                  key={day}
                  type="button"
                  onClick={() => setFormData(prev => ({ ...prev, workoutDays: day.toString() }))}
                  className={`w-12 h-12 rounded-full flex items-center justify-center text-lg font-semibold transition-colors
                    ${formData.workoutDays === day.toString()
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
                  aria-label={`${day} days per week`}
                  aria-pressed={formData.workoutDays === day.toString()}
                >
                  {day}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label 
              htmlFor="disabilities" 
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Physical Disabilities or Limitations
            </label>
            <textarea
              id="disabilities"
              name="disabilities"
              value={formData.disabilities}
              onChange={handleChange}
              rows="4"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              placeholder="Please describe any physical disabilities or limitations"
              aria-label="Physical disabilities or limitations"
            ></textarea>
          </div>

          <div>
            <label 
              htmlFor="requirements" 
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Additional Requirements
            </label>
            <textarea
              id="requirements"
              name="requirements"
              value={formData.requirements}
              onChange={handleChange}
              rows="4"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              placeholder="Any other requirements or preferences?"
              aria-label="Additional requirements or constraints"
            ></textarea>
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-blue-300"
            aria-label="Generate workout plan"
            disabled={isLoading}
          >
            {isLoading ? 'Generating Plan...' : 'Generate Workout Plan'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Form;
