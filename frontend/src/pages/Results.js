import { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';

const Results = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState(null);
  const [workoutPlan, setWorkoutPlan] = useState(null);
  const [hoveredDay, setHoveredDay] = useState(null);
  const [lastHoveredDay, setLastHoveredDay] = useState(null);
  
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const dayMapping = {
    'Sunday': 'Sun',
    'Monday': 'Mon',
    'Tuesday': 'Tue',
    'Wednesday': 'Wed',
    'Thursday': 'Thu',
    'Friday': 'Fri',
    'Saturday': 'Sat'
  };
  
  const parsedWorkoutPlan = useMemo(() => {
    if (!workoutPlan?.plan) return null;
    
    // Initialize empty plan for all days
    const dailyPlans = days.reduce((acc, day) => {
      acc[day] = [];
      return acc;
    }, {});
    
    // Parse the plan string and organize by day
    const planLines = workoutPlan.plan.split('\n').map(line => line.trim()).filter(line => line);
    let currentDay = null;
    let currentExercise = null;
    
    planLines.forEach(line => {
      // Remove any leading dashes
      const cleanLine = line.replace(/^-\s*/, '');
      
      // Check for day headers
      const dayMatch = cleanLine.match(/^(Sun|Mon|Tue|Wed|Thu|Fri|Sat|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)(?:\s*\([^)]+\))?:/i);
      
      if (dayMatch) {
        // Convert full day names to three-letter codes
        const matchedDay = dayMatch[1];
        currentDay = dayMapping[matchedDay] || matchedDay.substring(0, 3);
      } else if (currentDay) {
        if (line.startsWith('-')) {
          // New exercise entry
          const exerciseMatch = cleanLine.match(/(.*?):\s*(\d+)\s*x\s*(\d+(?:\/leg)?)\s*(?:\(Rest\s*(\d+)s?\))?/);
          if (exerciseMatch) {
            const [_, name, sets, reps, rest] = exerciseMatch;
            currentExercise = {
              name: name.trim(),
              sets: parseInt(sets),
              reps: parseInt(reps),
              rest: rest ? parseInt(rest) : null,
              explanation: ''
            };
            dailyPlans[currentDay].push(currentExercise);
          }
        } else if (line.trim().startsWith('[EXPLANATION]')) {
          // Add explanation to current exercise
          if (currentExercise) {
            currentExercise.explanation = line.replace('[EXPLANATION]:', '').trim();
          }
        }
      }
    });
    
    return dailyPlans;
  }, [workoutPlan, days, dayMapping]);

  useEffect(() => {
    const savedPlan = localStorage.getItem('workoutPlan');
    const savedData = localStorage.getItem('workoutFormData');
    
    if (!savedPlan || !savedData) {
      navigate('/form');
      return;
    }

    try {
      const parsedData = JSON.parse(savedData);
      const parsedPlan = JSON.parse(savedPlan);
      
      setFormData(parsedData);
      setWorkoutPlan(parsedPlan);
    } catch (error) {
      console.error('Error parsing saved data:', error);
      navigate('/form');
    }
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

  const goalDisplay = {
    'strength': 'Building Strength',
    'muscle': 'Building Muscle',
    'endurance': 'Improving Endurance',
    'weight-loss': 'Weight Loss'
  };

  const levelDisplay = {
    'beginner': 'Beginner',
    'intermediate': 'Intermediate',
    'advanced': 'Advanced'
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8 text-center" role="heading">
          Your Personalized Workout Plan
        </h1>
        
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Left section - Profile Overview */}
          <div className="lg:w-1/4 bg-white p-6 rounded-lg shadow-lg">
            <h2 className="text-xl font-semibold mb-4">Workout Profile</h2>
            <div className="space-y-4">
              <div>
                <p className="font-medium text-gray-600">Fitness Level</p>
                <p className="text-lg">{levelDisplay[formData.fitnessLevel] || formData.fitnessLevel}</p>
              </div>
              <div>
                <p className="font-medium text-gray-600">Primary Goal</p>
                <p className="text-lg">{goalDisplay[formData.goals] || formData.goals}</p>
              </div>
              {formData.disabilities && (
                <div>
                  <p className="font-medium text-gray-600">Accommodations</p>
                  <p className="text-lg">{formData.disabilities}</p>
                </div>
              )}
              <div className="mt-6">
                <h3 className="font-semibold mb-2">Program Focus</h3>
                <div className="text-gray-600 space-y-2">
                  {workoutPlan.focus ? (
                    workoutPlan.focus.split('\n').map((line, index) => (
                      <p key={index} className="text-sm">{line}</p>
                    ))
                  ) : (
                    <p className="text-sm">
                      This program is tailored for your {formData.fitnessLevel} level, focusing on {goalDisplay[formData.goals]?.toLowerCase() || formData.goals}
                      {formData.disabilities ? ' with appropriate modifications.' : '.'}
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
                  
          {/* Right section - Workout Schedule */}
          <div className="lg:w-3/4 flex flex-wrap lg:flex-nowrap gap-1">
            {days.map((day) => (
              <div
                key={day}
                className={`bg-white rounded-lg shadow-lg overflow-hidden transition-all duration-300 ease-in-out
                  ${hoveredDay === day ? 'flex-grow' : 'flex-shrink'}
                  ${hoveredDay && hoveredDay !== day ? 'flex-shrink-2' : ''}
                  ${formData.workoutDays.includes(day) ? 'border-t-4 border-blue-500' : ''}
                `}
                onMouseEnter={() => {
                  setHoveredDay(day);
                  setLastHoveredDay(day);
                }}
                onMouseLeave={() => setHoveredDay(null)}
                style={{
                  flexBasis: hoveredDay === day ? '50%' : 
                           hoveredDay ? '8%' : 
                           lastHoveredDay === day ? '50%' :
                           lastHoveredDay ? '8%' :
                           `${100/7}%`
                }}
              >
                <div className="h-full p-4">
                  <h3 className={`text-lg font-semibold mb-4 ${(hoveredDay === day || (!hoveredDay && lastHoveredDay === day)) ? '' : 'writing-vertical-lr'}`}>
                    {day}
                  </h3>
                  {(hoveredDay === day || (!hoveredDay && lastHoveredDay === day)) && (
                    <div className="space-y-3">
                      {formData.workoutDays.includes(day) ? (
                        parsedWorkoutPlan && Array.isArray(parsedWorkoutPlan[day]) && parsedWorkoutPlan[day].length > 0 ? (
                          parsedWorkoutPlan[day].map((exercise, index) => (
                            <div key={index} className="bg-gray-50 p-3 rounded">
                              <div>
                                <p className="text-sm font-medium">{exercise.name}</p>
                                {exercise.sets && (exercise.reps || exercise.duration) && (
                                  <p className="text-xs text-gray-600 mt-1">
                                    {exercise.sets} sets × {exercise.duration ? 
                                      `${exercise.duration} seconds` : 
                                      `${exercise.reps} reps`}
                                    {exercise.rest && ` (Rest ${exercise.rest}s)`}
                                  </p>
                                )}
                                {exercise.explanation && (
                                  <p className="text-xs text-gray-600 mt-2 italic">
                                    {exercise.explanation}
                                  </p>
                                )}
                              </div>
                            </div>
                          ))
                        ) : (
                          <p className="text-sm text-gray-500">Generating exercises for this day...</p>
                        )
                      ) : (
                        <p className="text-sm text-gray-500 italic">Rest Day</p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
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
