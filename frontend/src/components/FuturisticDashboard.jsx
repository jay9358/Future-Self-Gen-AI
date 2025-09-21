// FuturisticDashboard.jsx - Enhanced version with comprehensive data display
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Card, 
  CardHeader, 
  CardBody, 
  CardTitle, 
  CardDescription, 
  Button, 
  Badge, 
  SkillBadge, 
  ProgressBar, 
  CircularProgress,
  Modal 
} from './ui';

// Helper function to get career-specific recommendations
const getCareerRecommendations = (detectedCareer) => {
  const recommendations = {
    'software_engineer': [
      'Master modern frameworks like React, Vue, or Angular',
      'Learn cloud platforms (AWS, Azure, GCP)',
      'Develop system design and architecture skills',
      'Contribute to open-source projects',
      'Build a strong GitHub portfolio'
    ],
    'frontend_developer': [
      'Master React, Angular, or Vue.js ecosystem',
      'Learn advanced CSS and animation techniques',
      'Understand web performance optimization',
      'Build responsive and accessible interfaces',
      'Create an impressive portfolio website'
    ],
    'backend_developer': [
      'Master server-side languages (Python, Java, Go)',
      'Learn database optimization and design',
      'Understand microservices architecture',
      'Develop API design skills',
      'Learn message queuing and caching strategies'
    ],
    'fullstack_developer': [
      'Balance frontend and backend expertise',
      'Master both client and server architectures',
      'Learn DevOps and deployment strategies',
      'Understand database design and optimization',
      'Build end-to-end applications'
    ],
    'data_scientist': [
      'Master machine learning algorithms and frameworks',
      'Learn advanced statistics and mathematics',
      'Develop expertise in Python/R and data visualization',
      'Work on real-world data science projects',
      'Stay updated with AI/ML research papers'
    ],
    'data_analyst': [
      'Master SQL and data querying techniques',
      'Learn business intelligence tools (Tableau, Power BI)',
      'Develop statistical analysis skills',
      'Understand business metrics and KPIs',
      'Learn data storytelling and visualization'
    ],
    'devops_engineer': [
      'Master containerization (Docker, Kubernetes)',
      'Learn CI/CD pipeline automation',
      'Develop cloud infrastructure skills',
      'Learn monitoring and logging tools',
      'Understand security best practices'
    ],
    'cloud_architect': [
      'Get certified in major cloud platforms',
      'Master infrastructure as code (Terraform, CloudFormation)',
      'Learn cloud security and compliance',
      'Understand cost optimization strategies',
      'Design scalable and resilient architectures'
    ],
    'mobile_developer': [
      'Master native development (Swift/Kotlin) or React Native/Flutter',
      'Understand mobile UI/UX principles',
      'Learn app store optimization',
      'Develop offline-first architectures',
      'Build cross-platform applications'
    ],
    'machine_learning_engineer': [
      'Master deep learning frameworks (TensorFlow, PyTorch)',
      'Learn MLOps and model deployment',
      'Understand model optimization techniques',
      'Develop expertise in specific ML domains',
      'Contribute to ML research or open source'
    ],
    'product_manager': [
      'Develop user research and analytics skills',
      'Learn agile and scrum methodologies',
      'Master product strategy and roadmap planning',
      'Build technical communication skills',
      'Understand market analysis and competitive intelligence'
    ],
    'ui_ux_designer': [
      'Master design tools (Figma, Sketch, Adobe XD)',
      'Learn user research and usability testing',
      'Develop prototyping and interaction design skills',
      'Understand design systems and accessibility',
      'Build a strong design portfolio'
    ]
  };
  
  return recommendations[detectedCareer] || [
    'Focus on developing leadership skills',
    'Learn cloud technologies and AI/ML',
    'Build a strong professional network',
    'Consider advanced certifications',
    'Start a side project to showcase skills'
  ];
};

// Helper to format career name
const formatCareerName = (career) => {
  if (!career) return 'Software Engineer';
  return career.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ');
};

const FuturisticDashboard = ({ resumeAnalysis, persona, onStartChat, onBack }) => {
  const [selectedTab, setSelectedTab] = useState('overview');
  const [showModal, setShowModal] = useState(false);
  const [expandedSkillCategory, setExpandedSkillCategory] = useState(null);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'skills', label: 'Skills Analysis', icon: '🎯' },
    { id: 'career', label: 'Career Path', icon: '🚀' },
    { id: 'insights', label: 'AI Insights', icon: '💡' }
  ];

  // Get skills data - handle both old and new format
  const getSkillsData = () => {
    if (resumeAnalysis?.skills && typeof resumeAnalysis.skills === 'object') {
      return resumeAnalysis.skills;
    }
    // Fallback to extracted_info
    return {
      technical: resumeAnalysis?.extracted_info?.skills || [],
      languages: [],
      frameworks: [],
      databases: [],
      cloud: [],
      tools: [],
      soft: []
    };
  };

  const skillsData = getSkillsData();
  const totalSkillsCount = Object.values(skillsData).flat().length;

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card variant="glass" glow>
          <CardBody className="text-center">
            <CircularProgress 
              value={resumeAnalysis?.career_match?.match_percentage || 0} 
              size={80}
              variant="primary"
            />
            <h3 className="text-lg font-semibold text-white mt-4">Career Match</h3>
            <p className="text-white/60">
              {resumeAnalysis?.career_match?.career_readiness || 'Analyzing...'}
            </p>
          </CardBody>
        </Card>

        <Card variant="glass" glow>
          <CardBody className="text-center">
            <div className="text-4xl font-bold text-cyan-400 mb-2">
              {resumeAnalysis?.years_experience || resumeAnalysis?.extracted_info?.years_experience || 0}
            </div>
            <h3 className="text-lg font-semibold text-white">Years Experience</h3>
            <p className="text-white/60">Professional Background</p>
          </CardBody>
        </Card>

        <Card variant="glass" glow>
          <CardBody className="text-center">
            <div className="text-4xl font-bold text-purple-400 mb-2">
              {totalSkillsCount}
            </div>
            <h3 className="text-lg font-semibold text-white">Total Skills</h3>
            <p className="text-white/60">All Categories</p>
          </CardBody>
        </Card>

        <Card variant="glass" glow>
          <CardBody className="text-center">
            <div className="text-4xl font-bold text-green-400 mb-2">
              {resumeAnalysis?.career_insights?.market_demand || 'High'}
            </div>
            <h3 className="text-lg font-semibold text-white">Market Demand</h3>
            <p className="text-white/60">For Your Skills</p>
          </CardBody>
        </Card>
      </div>

      {/* Future Self Preview */}
      <Card variant="accent" glow>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span>🔮</span>
            <span>Your Future Self</span>
          </CardTitle>
        </CardHeader>
        <CardBody>
          <div className="flex items-center space-x-6">
            <motion.div
              whileHover={{ scale: 1.1 }}
              className="w-20 h-20 bg-gradient-to-br from-cyan-400 to-purple-500 rounded-full flex items-center justify-center"
            >
              <span className="text-2xl">👤</span>
            </motion.div>
            <div className="flex-1">
              <h3 className="text-xl font-semibold text-white">
                {persona?.name || resumeAnalysis?.personal_info?.name || 'Future You'}
              </h3>
              <p className="text-cyan-400 font-medium">
                {persona?.current_role || formatCareerName(resumeAnalysis?.detected_career)}
              </p>
              <p className="text-white/70 mt-2">
                10 years from now, with {(resumeAnalysis?.years_experience || 0) + 10}+ years of experience, 
                ready to guide your journey to success.
              </p>
            </div>
            <Button onClick={onStartChat} variant="primary" size="lg">
              Start Chat →
            </Button>
          </div>
        </CardBody>
      </Card>

      {/* Quick Insights */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card variant="dark">
          <CardHeader>
            <CardTitle>Strengths</CardTitle>
          </CardHeader>
          <CardBody>
            <div className="space-y-2">
              {(resumeAnalysis?.career_insights?.strengths || []).map((strength, i) => (
                <div key={i} className="flex items-center space-x-2">
                  <span className="text-green-400">✓</span>
                  <span className="text-white/80">{strength}</span>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        <Card variant="dark">
          <CardHeader>
            <CardTitle>Next Steps</CardTitle>
          </CardHeader>
          <CardBody>
            <div className="space-y-2">
              {(resumeAnalysis?.career_match?.next_steps || []).map((step, i) => (
                <div key={i} className="flex items-center space-x-2">
                  <span className="text-blue-400">{i + 1}.</span>
                  <span className="text-white/80">{step}</span>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );

  const renderSkills = () => (
    <div className="space-y-6">
      {/* Skill Categories */}
      {skillsData.languages && skillsData.languages.length > 0 && (
        <Card variant="dark">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span>💻</span>
                <span>Programming Languages</span>
                <Badge variant="primary" size="sm">{skillsData.languages.length}</Badge>
              </div>
            </CardTitle>
          </CardHeader>
          <CardBody>
            <div className="flex flex-wrap gap-2">
              {skillsData.languages.map((lang, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <Badge variant="primary" size="lg">{lang}</Badge>
                </motion.div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {skillsData.frameworks && skillsData.frameworks.length > 0 && (
        <Card variant="dark">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <span>🔧</span>
              <span>Frameworks & Libraries</span>
              <Badge variant="secondary" size="sm">{skillsData.frameworks.length}</Badge>
            </CardTitle>
          </CardHeader>
          <CardBody>
            <div className="flex flex-wrap gap-2">
              {skillsData.frameworks.map((framework, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <Badge variant="secondary" size="lg">{framework}</Badge>
                </motion.div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {/* Cloud & DevOps Skills */}
      {(skillsData.cloud?.length > 0 || skillsData.tools?.length > 0) && (
        <Card variant="dark">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <span>☁️</span>
              <span>Cloud & Tools</span>
              <Badge variant="accent" size="sm">
                {(skillsData.cloud?.length || 0) + (skillsData.tools?.length || 0)}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardBody>
            <div className="space-y-4">
              {skillsData.cloud?.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-white/60 mb-2">Cloud Platforms</h4>
                  <div className="flex flex-wrap gap-2">
                    {skillsData.cloud.map((cloud, i) => (
                      <Badge key={i} variant="accent">{cloud}</Badge>
                    ))}
                  </div>
                </div>
              )}
              {skillsData.tools?.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-white/60 mb-2">Tools & Technologies</h4>
                  <div className="flex flex-wrap gap-2">
                    {skillsData.tools.map((tool, i) => (
                      <Badge key={i} variant="warning">{tool}</Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardBody>
        </Card>
      )}

      {/* Databases */}
      {skillsData.databases && skillsData.databases.length > 0 && (
        <Card variant="dark">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <span>🗄️</span>
              <span>Databases</span>
              <Badge variant="success" size="sm">{skillsData.databases.length}</Badge>
            </CardTitle>
          </CardHeader>
          <CardBody>
            <div className="flex flex-wrap gap-2">
              {skillsData.databases.map((db, i) => (
                <Badge key={i} variant="success" size="lg">{db}</Badge>
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {/* Technical & Soft Skills */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {skillsData.technical && skillsData.technical.length > 0 && (
          <Card variant="dark">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <span>⚡</span>
                <span>Technical Skills</span>
              </CardTitle>
            </CardHeader>
            <CardBody>
              <div className="flex flex-wrap gap-2">
                {skillsData.technical.slice(0, 15).map((skill, i) => (
                  <SkillBadge key={i} skill={skill} level="advanced" />
                ))}
              </div>
            </CardBody>
          </Card>
        )}

        {skillsData.soft && skillsData.soft.length > 0 && (
          <Card variant="dark">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <span>🤝</span>
                <span>Soft Skills</span>
              </CardTitle>
            </CardHeader>
            <CardBody>
              <div className="flex flex-wrap gap-2">
                {skillsData.soft.map((skill, i) => (
                  <Badge key={i} variant="default">{skill}</Badge>
                ))}
              </div>
            </CardBody>
          </Card>
        )}
      </div>

      {/* Skills Gap Analysis */}
      {resumeAnalysis?.career_match?.missing_skills && resumeAnalysis.career_match.missing_skills.length > 0 && (
        <Card variant="warning">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <span>📈</span>
              <span>Skills to Develop</span>
            </CardTitle>
          </CardHeader>
          <CardBody>
            <div className="space-y-3">
              <div className="flex flex-wrap gap-2">
                {resumeAnalysis.career_match.missing_skills.map((skill, index) => (
                  <Badge key={index} variant="warning" size="lg">
                    {skill}
                  </Badge>
                ))}
              </div>
              <p className="text-sm text-white/60 mt-3">
                Timeline: {resumeAnalysis.career_match.timeline_to_goal || '3-6 months with focused learning'}
              </p>
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  );

  const renderCareer = () => (
    <div className="space-y-6">
      {/* Detected Career Path */}
      <Card variant="accent" glow>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span>🎯</span>
            <span>Your Career Path</span>
          </CardTitle>
        </CardHeader>
        <CardBody>
          <div className="text-center space-y-4">
            <div className="text-4xl font-bold text-cyan-400 mb-2">
              {formatCareerName(resumeAnalysis?.detected_career)}
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              <div className="p-3 bg-white/5 rounded-lg">
                <div className="text-2xl font-bold text-white">
                  {resumeAnalysis?.career_match?.match_percentage || 0}%
                </div>
                <div className="text-xs text-white/60">Career Match</div>
              </div>
              <div className="p-3 bg-white/5 rounded-lg">
                <div className="text-lg font-bold text-purple-400">
                  {resumeAnalysis?.career_match?.career_readiness || 'Entry-Level'}
                </div>
                <div className="text-xs text-white/60">Readiness</div>
              </div>
              <div className="p-3 bg-white/5 rounded-lg">
                <div className="text-lg font-bold text-green-400">
                  {resumeAnalysis?.career_insights?.skill_level || 'Developing'}
                </div>
                <div className="text-xs text-white/60">Skill Level</div>
              </div>
              <div className="p-3 bg-white/5 rounded-lg">
                <div className="text-lg font-bold text-yellow-400">
                  {resumeAnalysis?.career_insights?.market_demand || 'Moderate'}
                </div>
                <div className="text-xs text-white/60">Demand</div>
              </div>
            </div>

            {/* Matched Skills */}
            {resumeAnalysis?.career_match?.matched_skills && resumeAnalysis.career_match.matched_skills.length > 0 && (
              <div className="mt-6 p-4 bg-white/5 rounded-lg">
                <h4 className="font-semibold text-white mb-3">Matched Skills</h4>
                <div className="flex flex-wrap gap-2 justify-center">
                  {resumeAnalysis.career_match.matched_skills.slice(0, 10).map((skill, i) => (
                    <Badge key={i} variant="success">{skill}</Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        </CardBody>
      </Card>

      {/* Career Timeline */}
      <Card variant="glass" glow>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span>🗺️</span>
            <span>Your Career Journey</span>
          </CardTitle>
        </CardHeader>
        <CardBody>
          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center space-x-4"
            >
              <div className="w-4 h-4 rounded-full bg-cyan-400" />
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <h4 className="font-semibold text-white">Current Position</h4>
                  <Badge variant="primary" size="sm">Now</Badge>
                </div>
                <p className="text-white/60">
                  {resumeAnalysis?.years_experience || 0} years experience • 
                  {resumeAnalysis?.career_insights?.skill_level || 'Building Foundation'}
                </p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="flex items-center space-x-4"
            >
              <div className="w-4 h-4 rounded-full bg-yellow-400" />
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <h4 className="font-semibold text-white">Next Role</h4>
                  <Badge variant="warning" size="sm">1-2 Years</Badge>
                </div>
                <p className="text-white/60">
                  {resumeAnalysis?.career_insights?.recommended_next_role || 'Mid-Level Position'}
                </p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="flex items-center space-x-4"
            >
              <div className="w-4 h-4 rounded-full bg-purple-400" />
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <h4 className="font-semibold text-white">5 Year Goal</h4>
                  <Badge variant="secondary" size="sm">5 Years</Badge>
                </div>
                <p className="text-white/60">
                  Senior {formatCareerName(resumeAnalysis?.detected_career)}
                </p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="flex items-center space-x-4"
            >
              <div className="w-4 h-4 rounded-full bg-gradient-to-r from-cyan-400 to-purple-400" />
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <h4 className="font-semibold text-white">Future Self</h4>
                  <Badge variant="accent" size="sm">10 Years</Badge>
                </div>
                <p className="text-white/60">
                  {persona?.current_role || `Lead ${formatCareerName(resumeAnalysis?.detected_career)}`}
                </p>
              </div>
            </motion.div>
          </div>
        </CardBody>
      </Card>

      {/* Personalized Recommendations */}
      <Card variant="dark">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span>💡</span>
            <span>Personalized Recommendations</span>
          </CardTitle>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            {(resumeAnalysis?.career_match?.recommendations || 
              getCareerRecommendations(resumeAnalysis?.detected_career)).map((rec, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className="flex items-start space-x-3"
              >
                <span className="text-cyan-400 mt-1">→</span>
                <span className="text-white/80">{rec}</span>
              </motion.div>
            ))}
          </div>
        </CardBody>
      </Card>
    </div>
  );

  const renderInsights = () => (
    <div className="space-y-6">
      {/* AI Analysis Summary */}
      <Card variant="glass" glow>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span>🤖</span>
            <span>AI Analysis Summary</span>
          </CardTitle>
        </CardHeader>
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-white/5 rounded-lg">
              <h4 className="font-semibold text-white mb-2">Method</h4>
              <p className="text-white/70">
                {resumeAnalysis?.analysis_method || 'Pattern Matching'}
              </p>
            </div>
            <div className="p-4 bg-white/5 rounded-lg">
              <h4 className="font-semibold text-white mb-2">Confidence</h4>
              <p className="text-white/70">
                {resumeAnalysis?.career_match?.confidence_score 
                  ? `${resumeAnalysis.career_match.confidence_score}/10`
                  : 'High'}
              </p>
            </div>
            <div className="p-4 bg-white/5 rounded-lg">
              <h4 className="font-semibold text-white mb-2">Skills Found</h4>
              <p className="text-white/70">{totalSkillsCount} Total</p>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Gemini AI Insights if available */}
      {resumeAnalysis?.gemini_insights && (
        <Card variant="accent" glow>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <span>✨</span>
              <span>Gemini AI Insights</span>
            </CardTitle>
          </CardHeader>
          <CardBody>
            <div className="space-y-4">
              {resumeAnalysis.gemini_insights.career_confirmation && (
                <div className="p-4 bg-white/5 rounded-lg">
                  <h4 className="font-semibold text-white mb-2">Career Path Confirmation</h4>
                  <p className="text-white/80">{resumeAnalysis.gemini_insights.career_confirmation}</p>
                </div>
              )}
              
              {resumeAnalysis.gemini_insights.unique_value_proposition && (
                <div className="p-4 bg-white/5 rounded-lg">
                  <h4 className="font-semibold text-white mb-2">Your Unique Value</h4>
                  <p className="text-white/80">{resumeAnalysis.gemini_insights.unique_value_proposition}</p>
                </div>
              )}

              {resumeAnalysis.gemini_insights.career_trajectory && (
                <div className="p-4 bg-white/5 rounded-lg">
                  <h4 className="font-semibold text-white mb-2">5-Year Trajectory</h4>
                  <p className="text-white/80">{resumeAnalysis.gemini_insights.career_trajectory}</p>
                </div>
              )}

              {resumeAnalysis.gemini_insights.strategic_recommendations && (
                <div className="p-4 bg-white/5 rounded-lg">
                  <h4 className="font-semibold text-white mb-2">Strategic Advice</h4>
                  <ul className="space-y-2">
                    {resumeAnalysis.gemini_insights.strategic_recommendations.map((rec, i) => (
                      <li key={i} className="flex items-start space-x-2">
                        <span className="text-cyan-400">•</span>
                        <span className="text-white/80">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </CardBody>
        </Card>
      )}

      {/* Career Insights */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card variant="dark">
          <CardHeader>
            <CardTitle>Strengths</CardTitle>
          </CardHeader>
          <CardBody>
            <div className="space-y-3">
              {(resumeAnalysis?.career_insights?.strengths || []).map((strength, i) => (
                <div key={i} className="flex items-start space-x-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <span className="text-white/80">{strength}</span>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        <Card variant="dark">
          <CardHeader>
            <CardTitle>Areas for Growth</CardTitle>
          </CardHeader>
          <CardBody>
            <div className="space-y-3">
              {(resumeAnalysis?.career_insights?.areas_for_improvement || []).map((area, i) => (
                <div key={i} className="flex items-start space-x-2">
                  <span className="text-yellow-400 mt-1">!</span>
                  <span className="text-white/80">{area}</span>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Experience & Education Summary */}
      <Card variant="glass">
        <CardHeader>
          <CardTitle>Background Summary</CardTitle>
        </CardHeader>
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Experience */}
            {resumeAnalysis?.experience && resumeAnalysis.experience.length > 0 && (
              <div>
                <h4 className="font-semibold text-white mb-3">Work Experience</h4>
                <div className="space-y-2">
                  {resumeAnalysis.experience.slice(0, 3).map((exp, i) => (
                    <div key={i} className="p-3 bg-white/5 rounded-lg">
                      <p className="text-sm font-medium text-white">{exp.title}</p>
                      <p className="text-xs text-white/60">{exp.company} • {exp.duration}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Education */}
            {resumeAnalysis?.education && resumeAnalysis.education.length > 0 && (
              <div>
                <h4 className="font-semibold text-white mb-3">Education</h4>
                <div className="space-y-2">
                  {resumeAnalysis.education.slice(0, 2).map((edu, i) => (
                    <div key={i} className="p-3 bg-white/5 rounded-lg">
                      <p className="text-sm font-medium text-white">{edu.degree}</p>
                      <p className="text-xs text-white/60">
                        {edu.institution} • {edu.year || 'Completed'}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </CardBody>
      </Card>
    </div>
  );

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="max-w-7xl mx-auto p-6"
    >
      {/* Header */}
      <Card variant="glass" className="mb-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl">
                Welcome, {resumeAnalysis?.personal_info?.name || 'Future Professional'}!
              </CardTitle>
              <CardDescription className="text-lg">
                Your AI-powered career dashboard and future self guidance system
              </CardDescription>
            </div>
            <div className="flex items-center space-x-3">
              <Button variant="secondary" onClick={onBack}>
                ← Back
              </Button>
              <Button onClick={() => setShowModal(true)}>
                View Raw Data
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Tabs */}
      <Card variant="dark" className="mb-6">
        <CardBody className="p-0">
          <div className="flex space-x-1 p-1">
            {tabs.map((tab) => (
              <motion.button
                key={tab.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setSelectedTab(tab.id)}
                className={`flex-1 flex items-center justify-center space-x-2 px-4 py-3 rounded-lg transition-all duration-300 ${
                  selectedTab === tab.id
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                    : 'text-white/60 hover:text-white hover:bg-white/10'
                }`}
              >
                <span>{tab.icon}</span>
                <span className="font-medium">{tab.label}</span>
              </motion.button>
            ))}
          </div>
        </CardBody>
      </Card>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={selectedTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          {selectedTab === 'overview' && renderOverview()}
          {selectedTab === 'skills' && renderSkills()}
          {selectedTab === 'career' && renderCareer()}
          {selectedTab === 'insights' && renderInsights()}
        </motion.div>
      </AnimatePresence>

      {/* Raw Data Modal */}
      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Raw Analysis Data"
        size="xl"
      >
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-6">
            <div>
              <h3 className="font-semibold text-white mb-3">Complete Resume Analysis</h3>
              <pre className="text-xs text-white/70 bg-black/20 p-4 rounded-lg overflow-auto max-h-96">
                {JSON.stringify(resumeAnalysis, null, 2)}
              </pre>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-3">Persona Configuration</h3>
              <pre className="text-xs text-white/70 bg-black/20 p-4 rounded-lg overflow-auto max-h-64">
                {JSON.stringify(persona, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      </Modal>
    </motion.div>
  );
};

export default FuturisticDashboard;