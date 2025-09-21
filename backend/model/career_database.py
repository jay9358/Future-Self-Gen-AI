# models/career_database.py - Complete career database with proper exports
from typing import Dict, List, Any, Optional, Tuple

# Skills database for matching
SKILLS_DATABASE = {
    "technical": [
        "Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", "Swift", 
        "Kotlin", "TypeScript", "PHP", "Ruby", "Scala", "R", "MATLAB",
        "Machine Learning", "Deep Learning", "Data Analysis", "Data Visualization",
        "Web Development", "Mobile Development", "Cloud Computing", "DevOps",
        "Cybersecurity", "Blockchain", "IoT", "AI", "NLP", "Computer Vision",
        "System Design", "Database Design", "API Development", "Microservices",
        "Testing", "Debugging", "Performance Optimization", "Security"
    ],
    "soft": [
        "Leadership", "Communication", "Problem Solving", "Teamwork",
        "Project Management", "Time Management", "Analytical Thinking",
        "Creativity", "Adaptability", "Attention to Detail", "Critical Thinking",
        "Decision Making", "Conflict Resolution", "Presentation Skills",
        "Mentoring", "Strategic Planning", "Customer Service", "Negotiation",
        "Emotional Intelligence", "Initiative", "Flexibility", "Reliability"
    ],
    "business": [
        "Business Analysis", "Strategic Planning", "Market Research",
        "Product Management", "Business Development", "Sales", "Marketing",
        "Financial Analysis", "Risk Management", "Operations Management",
        "Supply Chain", "Customer Success", "Account Management",
        "Stakeholder Management", "Budgeting", "Forecasting"
    ],
    "creative": [
        "UI Design", "UX Design", "Graphic Design", "Video Editing",
        "Animation", "3D Modeling", "Photography", "Content Creation",
        "Copywriting", "Brand Design", "Motion Graphics", "Illustration"
    ]
}

class CareerDatabase:
    """Career database with requirements and information"""
    
    def __init__(self):
        self.careers = self._initialize_careers()
        self.categories = self._initialize_categories()
    
    def _initialize_careers(self) -> Dict[str, Dict[str, Any]]:
        """Initialize all career paths with requirements"""
        return {
            "software_engineer": {
                "title": "Software Engineer",
                "category": "Engineering",
                "description": "Design and develop software applications and systems",
                "required_skills": [
                    "Programming", "Data Structures", "Algorithms", "Git", 
                    "Testing", "Problem Solving", "System Design"
                ],
                "preferred_skills": [
                    "Cloud Platforms", "Docker", "CI/CD", "Agile", 
                    "Database Design", "API Development"
                ],
                "languages": ["Python", "Java", "JavaScript", "C++", "Go"],
                "tools": ["Git", "Docker", "Jenkins", "AWS", "Linux"],
                "experience_levels": {
                    "entry": "0-2 years",
                    "mid": "2-5 years",
                    "senior": "5+ years"
                },
                "salary_range": {
                    "entry": "$60k-$90k",
                    "mid": "$90k-$130k",
                    "senior": "$130k-$200k+"
                },
                "growth_path": [
                    "Junior Developer",
                    "Software Engineer",
                    "Senior Software Engineer",
                    "Staff/Principal Engineer",
                    "Engineering Manager/Architect"
                ]
            },
            "frontend_developer": {
                "title": "Frontend Developer",
                "category": "Engineering",
                "description": "Build user interfaces and client-side applications",
                "required_skills": [
                    "JavaScript", "HTML", "CSS", "React/Vue/Angular",
                    "Responsive Design", "Browser DevTools"
                ],
                "preferred_skills": [
                    "TypeScript", "Testing", "Performance Optimization",
                    "Accessibility", "State Management", "Build Tools"
                ],
                "languages": ["JavaScript", "TypeScript", "HTML", "CSS"],
                "tools": ["React", "Vue", "Angular", "Webpack", "Git", "Figma"],
                "experience_levels": {
                    "entry": "0-2 years",
                    "mid": "2-5 years",
                    "senior": "5+ years"
                },
                "salary_range": {
                    "entry": "$55k-$85k",
                    "mid": "$85k-$120k",
                    "senior": "$120k-$180k+"
                },
                "growth_path": [
                    "Junior Frontend Developer",
                    "Frontend Developer",
                    "Senior Frontend Developer",
                    "Frontend Lead",
                    "Frontend Architect"
                ]
            },
            "backend_developer": {
                "title": "Backend Developer",
                "category": "Engineering",
                "description": "Develop server-side logic and database systems",
                "required_skills": [
                    "Server Programming", "Database", "API Development",
                    "Security", "Performance", "System Architecture"
                ],
                "preferred_skills": [
                    "Microservices", "Message Queues", "Caching",
                    "Cloud Services", "DevOps", "Monitoring"
                ],
                "languages": ["Python", "Java", "Go", "Node.js", "C#"],
                "tools": ["PostgreSQL", "Redis", "Docker", "AWS", "Kubernetes"],
                "experience_levels": {
                    "entry": "0-2 years",
                    "mid": "2-5 years",
                    "senior": "5+ years"
                },
                "salary_range": {
                    "entry": "$60k-$90k",
                    "mid": "$90k-$130k",
                    "senior": "$130k-$200k+"
                },
                "growth_path": [
                    "Junior Backend Developer",
                    "Backend Developer",
                    "Senior Backend Developer",
                    "Backend Lead",
                    "System Architect"
                ]
            },
            "data_scientist": {
                "title": "Data Scientist",
                "category": "Data & AI",
                "description": "Analyze complex data to help companies make decisions",
                "required_skills": [
                    "Statistics", "Machine Learning", "Python/R",
                    "Data Analysis", "Data Visualization", "SQL"
                ],
                "preferred_skills": [
                    "Deep Learning", "Big Data", "Cloud ML",
                    "A/B Testing", "Feature Engineering", "MLOps"
                ],
                "languages": ["Python", "R", "SQL", "Julia"],
                "tools": ["TensorFlow", "PyTorch", "Pandas", "Jupyter", "Spark"],
                "experience_levels": {
                    "entry": "0-2 years",
                    "mid": "2-5 years",
                    "senior": "5+ years"
                },
                "salary_range": {
                    "entry": "$70k-$100k",
                    "mid": "$100k-$150k",
                    "senior": "$150k-$250k+"
                },
                "growth_path": [
                    "Junior Data Analyst",
                    "Data Scientist",
                    "Senior Data Scientist",
                    "Lead Data Scientist",
                    "Chief Data Scientist"
                ]
            },
            "devops_engineer": {
                "title": "DevOps Engineer",
                "category": "Engineering",
                "description": "Bridge development and operations with automation",
                "required_skills": [
                    "CI/CD", "Containerization", "Cloud Platforms",
                    "Monitoring", "Scripting", "Infrastructure as Code"
                ],
                "preferred_skills": [
                    "Kubernetes", "Security", "Networking",
                    "Configuration Management", "Performance Tuning"
                ],
                "languages": ["Python", "Bash", "Go", "JavaScript"],
                "tools": ["Docker", "Kubernetes", "Jenkins", "Terraform", "AWS"],
                "experience_levels": {
                    "entry": "0-2 years",
                    "mid": "2-5 years",
                    "senior": "5+ years"
                },
                "salary_range": {
                    "entry": "$65k-$95k",
                    "mid": "$95k-$140k",
                    "senior": "$140k-$200k+"
                },
                "growth_path": [
                    "Junior DevOps Engineer",
                    "DevOps Engineer",
                    "Senior DevOps Engineer",
                    "DevOps Lead",
                    "DevOps Architect"
                ]
            },
            "product_manager": {
                "title": "Product Manager",
                "category": "Product & Business",
                "description": "Guide product strategy and coordinate development",
                "required_skills": [
                    "Product Strategy", "User Research", "Analytics",
                    "Communication", "Leadership", "Business Acumen"
                ],
                "preferred_skills": [
                    "Technical Knowledge", "Data Analysis", "UX Design",
                    "Market Research", "Agile/Scrum", "SQL"
                ],
                "languages": [],
                "tools": ["Jira", "Analytics Tools", "Figma", "SQL", "Excel"],
                "experience_levels": {
                    "entry": "0-3 years",
                    "mid": "3-6 years",
                    "senior": "6+ years"
                },
                "salary_range": {
                    "entry": "$70k-$100k",
                    "mid": "$100k-$150k",
                    "senior": "$150k-$250k+"
                },
                "growth_path": [
                    "Associate Product Manager",
                    "Product Manager",
                    "Senior Product Manager",
                    "Group Product Manager",
                    "VP of Product"
                ]
            },
            "ui_ux_designer": {
                "title": "UI/UX Designer",
                "category": "Design",
                "description": "Design user interfaces and experiences",
                "required_skills": [
                    "Design Principles", "User Research", "Prototyping",
                    "Visual Design", "Interaction Design", "Design Tools"
                ],
                "preferred_skills": [
                    "HTML/CSS", "Design Systems", "Accessibility",
                    "Motion Design", "User Testing", "Information Architecture"
                ],
                "languages": ["HTML", "CSS", "JavaScript"],
                "tools": ["Figma", "Sketch", "Adobe XD", "Photoshop", "Illustrator"],
                "experience_levels": {
                    "entry": "0-2 years",
                    "mid": "2-5 years",
                    "senior": "5+ years"
                },
                "salary_range": {
                    "entry": "$50k-$80k",
                    "mid": "$80k-$120k",
                    "senior": "$120k-$180k+"
                },
                "growth_path": [
                    "Junior Designer",
                    "UI/UX Designer",
                    "Senior Designer",
                    "Lead Designer",
                    "Design Director"
                ]
            },
            "fullstack_developer": {
                "title": "Full Stack Developer",
                "category": "Engineering",
                "description": "Develop both frontend and backend applications",
                "required_skills": [
                    "Frontend Development", "Backend Development",
                    "Database", "API Design", "Version Control"
                ],
                "preferred_skills": [
                    "Cloud Services", "DevOps", "Mobile Development",
                    "Testing", "Security", "Performance"
                ],
                "languages": ["JavaScript", "Python", "TypeScript", "SQL"],
                "tools": ["React", "Node.js", "PostgreSQL", "Docker", "AWS"],
                "experience_levels": {
                    "entry": "0-2 years",
                    "mid": "2-5 years",
                    "senior": "5+ years"
                },
                "salary_range": {
                    "entry": "$60k-$90k",
                    "mid": "$90k-$130k",
                    "senior": "$130k-$200k+"
                },
                "growth_path": [
                    "Junior Full Stack Developer",
                    "Full Stack Developer",
                    "Senior Full Stack Developer",
                    "Technical Lead",
                    "Solutions Architect"
                ]
            },
            "machine_learning_engineer": {
                "title": "Machine Learning Engineer",
                "category": "Data & AI",
                "description": "Build and deploy machine learning models",
                "required_skills": [
                    "Machine Learning", "Deep Learning", "Python",
                    "Mathematics", "Model Deployment", "MLOps"
                ],
                "preferred_skills": [
                    "Cloud ML", "Big Data", "Computer Vision",
                    "NLP", "Reinforcement Learning", "Edge Computing"
                ],
                "languages": ["Python", "C++", "Julia", "Scala"],
                "tools": ["TensorFlow", "PyTorch", "Kubernetes", "MLflow", "Kubeflow"],
                "experience_levels": {
                    "entry": "0-2 years",
                    "mid": "2-5 years",
                    "senior": "5+ years"
                },
                "salary_range": {
                    "entry": "$80k-$120k",
                    "mid": "$120k-$180k",
                    "senior": "$180k-$300k+"
                },
                "growth_path": [
                    "Junior ML Engineer",
                    "ML Engineer",
                    "Senior ML Engineer",
                    "Staff ML Engineer",
                    "ML Architect"
                ]
            },
            "cloud_architect": {
                "title": "Cloud Architect",
                "category": "Engineering",
                "description": "Design and oversee cloud infrastructure",
                "required_skills": [
                    "Cloud Platforms", "Architecture Design", "Security",
                    "Networking", "Cost Optimization", "Migration"
                ],
                "preferred_skills": [
                    "Multi-cloud", "Serverless", "Containers",
                    "Compliance", "Disaster Recovery", "Automation"
                ],
                "languages": ["Python", "Go", "JavaScript", "Bash"],
                "tools": ["AWS", "Azure", "GCP", "Terraform", "Kubernetes"],
                "experience_levels": {
                    "entry": "3-5 years",
                    "mid": "5-8 years",
                    "senior": "8+ years"
                },
                "salary_range": {
                    "entry": "$100k-$140k",
                    "mid": "$140k-$180k",
                    "senior": "$180k-$250k+"
                },
                "growth_path": [
                    "Cloud Engineer",
                    "Senior Cloud Engineer",
                    "Cloud Architect",
                    "Senior Cloud Architect",
                    "Principal Architect"
                ]
            }
        }
    
    def _initialize_categories(self) -> Dict[str, List[str]]:
        """Initialize career categories"""
        return {
            "Engineering": [
                "software_engineer", "frontend_developer", "backend_developer",
                "fullstack_developer", "devops_engineer", "cloud_architect"
            ],
            "Data & AI": [
                "data_scientist", "machine_learning_engineer", "data_analyst"
            ],
            "Design": [
                "ui_ux_designer", "product_designer", "graphic_designer"
            ],
            "Product & Business": [
                "product_manager", "project_manager", "business_analyst"
            ]
        }
    
    def get_career(self, career_id: str) -> Optional[Dict[str, Any]]:
        """Get career information by ID"""
        return self.careers.get(career_id)
    
    def get_all_careers(self) -> Dict[str, Dict[str, Any]]:
        """Get all careers"""
        return self.careers
    
    def get_career_categories(self) -> Dict[str, List[str]]:
        """Get career categories"""
        return self.categories
    
    def get_careers_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get careers by category"""
        career_ids = self.categories.get(category, [])
        return [self.careers[cid] for cid in career_ids if cid in self.careers]
    
    def search_careers(self, query: str) -> List[Dict[str, Any]]:
        """Search careers by keyword"""
        query_lower = query.lower()
        results = []
        
        for career_id, career in self.careers.items():
            if (query_lower in career['title'].lower() or
                query_lower in career['description'].lower() or
                any(query_lower in skill.lower() for skill in career['required_skills'])):
                results.append(career)
        
        return results
    
    def get_career_requirements(self, career_id: str) -> Dict[str, List[str]]:
        """Get requirements for a specific career"""
        career = self.careers.get(career_id)
        if not career:
            return {"required": [], "preferred": []}
        
        return {
            "required": career.get('required_skills', []),
            "preferred": career.get('preferred_skills', []),
            "languages": career.get('languages', []),
            "tools": career.get('tools', [])
        }
    
    def match_skills_to_careers(self, user_skills: List[str]) -> List[Tuple[str, float]]:
        """Match user skills to careers and return sorted matches"""
        matches = []
        user_skills_lower = [skill.lower() for skill in user_skills]
        
        for career_id, career in self.careers.items():
            required = career.get('required_skills', [])
            preferred = career.get('preferred_skills', [])
            
            required_matches = sum(1 for skill in required 
                                 if any(skill.lower() in s for s in user_skills_lower))
            preferred_matches = sum(1 for skill in preferred 
                                  if any(skill.lower() in s for s in user_skills_lower))
            
            if required:
                match_score = (required_matches / len(required)) * 0.7
            else:
                match_score = 0
                
            if preferred:
                match_score += (preferred_matches / len(preferred)) * 0.3
            
            matches.append((career_id, match_score * 100))
        
        return sorted(matches, key=lambda x: x[1], reverse=True)

# Create global instance
career_database = CareerDatabase()

# Export everything
__all__ = ['SKILLS_DATABASE', 'CareerDatabase', 'career_database']