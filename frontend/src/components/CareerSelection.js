import React, { useState } from 'react';

const CAREERS = [
  {
    key: 'doctor',
    emoji: '👨‍⚕️',
    title: 'Doctor',
    salary: '$250K/year',
    description: 'Save lives, long training'
  },
  {
    key: 'software_engineer',
    emoji: '👨‍💻',
    title: 'Software Engineer',
    salary: '$180K/year',
    description: 'Build the future, flexible'
  },
  {
    key: 'data_scientist',
    emoji: '📊',
    title: 'Data Scientist',
    salary: '$130K/year',
    description: 'Insights from data, high demand'
  },
  {
    key: 'entrepreneur',
    emoji: '🚀',
    title: 'Entrepreneur',
    salary: 'Variable',
    description: 'Your own boss, high risk/reward'
  },
  {
    key: 'teacher',
    emoji: '👨‍🏫',
    title: 'Teacher',
    salary: '$65K/year',
    description: 'Shape minds, summers off'
  }
];

const CareerSelection = ({ careerMatches, onCareerSelect, onBack, onNext }) => {
  const [selectedCareer, setSelectedCareer] = useState(null);

  const handleCareerClick = (careerKey) => {
    setSelectedCareer(careerKey);
    onCareerSelect(careerKey);
  };

  const getMatchPercentage = (careerKey) => {
    return careerMatches[careerKey]?.match_percentage || 0;
  };

  return (
    <div className="step active">
      <h2>Step 3: Choose Your Future Career Path</h2>
      <p>Select the career you want to explore</p>

      <div className="career-grid">
        {CAREERS.map((career) => {
          const matchPercentage = getMatchPercentage(career.key);
          return (
            <div
              key={career.key}
              className={`career-card ${selectedCareer === career.key ? 'selected' : ''}`}
              onClick={() => handleCareerClick(career.key)}
            >
              <div className="emoji">{career.emoji}</div>
              <h3>{career.title}</h3>
              <p>{career.salary}</p>
              <small>{career.description}</small>
              {matchPercentage > 0 && (
                <div className="match-badge">
                  {Math.round(matchPercentage)}%
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="button-group">
        <button className="btn btn-secondary" onClick={onBack}>Back</button>
        <button 
          className="btn" 
          onClick={onNext}
          disabled={!selectedCareer}
        >
          Generate Future Self
        </button>
      </div>
    </div>
  );
};

export default CareerSelection;
