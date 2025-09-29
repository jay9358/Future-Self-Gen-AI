# resume_analyzer.py - Complete Enhanced Version with Gemini Integration
import re
import PyPDF2
import docx
import json
import logging
import os
from collections import Counter
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import skills database
try:
    from models.career_database import SKILLS_DATABASE
except ImportError:
    # Fallback skills database if import fails
    SKILLS_DATABASE = {
        "technical": [
            "Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", "Swift", 
            "Kotlin", "TypeScript", "PHP", "Ruby", "Scala", "R", "MATLAB",
            "Machine Learning", "Deep Learning", "Data Analysis", "Data Visualization",
            "Web Development", "Mobile Development", "Cloud Computing", "DevOps",
            "Cybersecurity", "Blockchain", "IoT", "AI", "NLP", "Computer Vision"
        ],
        "soft": [
            "Leadership", "Communication", "Problem Solving", "Teamwork",
            "Project Management", "Time Management", "Analytical Thinking",
            "Creativity", "Adaptability", "Attention to Detail", "Critical Thinking",
            "Decision Making", "Conflict Resolution", "Presentation Skills",
            "Mentoring", "Strategic Planning", "Customer Service", "Negotiation"
        ],
        "business": [
            "Business Analysis", "Strategic Planning", "Market Research",
            "Product Management", "Business Development", "Sales", "Marketing",
            "Financial Analysis", "Risk Management", "Operations Management"
        ],
        "creative": [
            "UI Design", "UX Design", "Graphic Design", "Video Editing",
            "Animation", "3D Modeling", "Photography", "Content Creation"
        ]
    }

class ResumeAnalyzer:
    """Enhanced Resume Analyzer with Gemini AI Integration"""
    
    def __init__(self):
        self.gemini_model = None
        self.initialize_gemini()
    
    def initialize_gemini(self):
        """Initialize Gemini AI model"""
        try:
            import google.generativeai as genai
            
            # Try both possible environment variable names
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                
                # List available models first
                try:
                    models = genai.list_models()
                    available_models = [model.name for model in models if 'generateContent' in model.supported_generation_methods]
                    logger.info(f"Available models: {available_models}")
                    
                    # Try to find a working model
                    model_names_to_try = ['gemini-2.0-flash', 'gemini-1.5-pro', 'gemini-pro']
                    
                    for model_name in model_names_to_try:
                        try:
                            self.gemini_model = genai.GenerativeModel(model_name)
                            logger.info(f"✅ {model_name} initialized successfully")
                            break
                        except Exception as e:
                            logger.warning(f"Failed to initialize {model_name}: {e}")
                            continue
                    
                    if not self.gemini_model:
                        logger.error("No working Gemini model found")
                        
                except Exception as e:
                    logger.error(f"Error listing models: {e}")
                    # Fallback to gemini-pro
                    try:
                        self.gemini_model = genai.GenerativeModel('gemini-pro')
                        logger.info("✅ Gemini Pro initialized successfully (fallback)")
                    except Exception as fallback_error:
                        logger.error(f"Fallback also failed: {fallback_error}")
                        self.gemini_model = None
            else:
                self.gemini_model = None
                logger.warning("Gemini API key not found (GOOGLE_API_KEY or GEMINI_API_KEY) - using pattern matching only")
        except ImportError:
            self.gemini_model = None
            logger.warning("google-generativeai not installed - using pattern matching only")
        except Exception as e:
            self.gemini_model = None
            logger.error(f"Gemini initialization error: {e}")

    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from various file formats"""
        try:
            if file_path.lower().endswith('.pdf'):
                return self.extract_text_from_pdf(file_path)
            elif file_path.lower().endswith(('.docx', '.doc')):
                return self.extract_text_from_docx(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"File extraction error: {e}")
            return ""

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return ""

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"DOCX extraction error: {e}")
            return ""

    def analyze_resume(self, resume_text: str, career_goal: str = None) -> Dict[str, Any]:
        """Main analysis function - comprehensive resume analysis using Gemini AI only"""
        if not resume_text:
            return self._empty_analysis()
        
        # Use Gemini for all data extraction
        if self.gemini_model:
            try:
                logger.info("Starting Gemini-only resume analysis...")
                analysis = self._extract_all_information_with_gemini(resume_text, career_goal)
                analysis['analysis_method'] = 'Gemini AI Only'
                logger.info("✅ Resume analysis completed using Gemini AI only")
                return analysis
            except Exception as e:
                logger.error(f"Gemini analysis failed: {e}")
                return self._empty_analysis()
        else:
            logger.error("Gemini model not available - cannot perform analysis")
            return self._empty_analysis()

    def _extract_all_information_with_gemini(self, resume_text: str, career_goal: str = None) -> Dict[str, Any]:
        """Extract all information from resume using Gemini AI only"""
        try:
            # Create comprehensive prompt for Gemini to extract all resume data
            prompt = f"""You are an expert resume parser and career analyst. Extract ALL information from this resume and provide a comprehensive JSON response.

RESUME TEXT:
{resume_text}

CAREER GOAL (if provided): {career_goal or "Not specified"}

Please extract and analyze the following information and return a JSON response with this EXACT structure:

{{
  "personal_info": {{
    "name": "Full name",
    "email": "email@example.com",
    "phone": "phone number",
    "linkedin": "LinkedIn profile",
    "github": "GitHub profile",
    "location": "City, State/Country"
  }},
  "skills": {{
    "technical": ["technical skills"],
    "soft": ["soft skills"],
    "languages": ["programming languages"],
    "frameworks": ["frameworks and libraries"],
    "databases": ["database technologies"],
    "cloud": ["cloud platforms and services"],
    "tools": ["development tools and software"],
    "methodologies": ["development methodologies like Agile, Scrum"]
  }},
  "experience": [
    {{
      "title": "Job Title",
      "company": "Company Name",
      "duration": "Start Date - End Date",
      "years": "number of years"
    }}
  ],
  "education": [
    {{
      "degree": "Degree Type",
      "field": "Field of Study",
      "institution": "University/Institution Name",
      "year": "Graduation Year"
    }}
  ],
  "years_experience": "total years of professional experience as number",
  "education_level": "education level as number (0-5: 0=high school, 1=certificate, 2=associate, 3=bachelor, 4=master, 5=phd)",
  "certifications": ["list of certifications"],
  "projects": [
    {{
      "name": "Project Name",
      "description": "Project Description"
    }}
  ],
  "detected_career": "most suitable career path (software_engineer, frontend_developer, backend_developer, fullstack_developer, data_scientist, data_analyst, data_engineer, machine_learning_engineer, devops_engineer, cloud_architect, mobile_developer, ui_ux_designer, product_manager, project_manager, qa_engineer, security_engineer)",
  "career_match": {{
    "match_percentage": "percentage as number",
    "career_readiness": "Learning Phase/Entry-Level/Mid-Level/Senior-Ready",
    "matched_skills": ["skills that match the career"],
    "missing_skills": ["skills needed for the career"],
    "recommendations": ["recommendations for career development"],
    "next_steps": ["next steps to take"],
    "timeline_to_goal": "estimated timeline",
    "confidence_score": "confidence score as number"
  }},
  "career_insights": {{
    "strengths": ["key strengths"],
    "areas_for_improvement": ["areas to improve"],
    "skill_level": "Beginner/Developing/Intermediate/Advanced/Expert",
    "market_demand": "Emerging/Moderate/High/Very High",
    "recommended_next_role": "recommended next job title",
    "total_skills_count": "total number of skills as number",
    "career_readiness": "Foundation Building/Entry-Level Ready/Mid-Level Ready/Senior-Ready"
  }},
  "extracted_info": {{
    "skills": ["flattened list of all skills"],
    "years_experience": "total years as number",
    "education_level": "education level as number",
    "personal_info": {{
      "name": "Full name"
    }}
  }}
}}

IMPORTANT INSTRUCTIONS:
1. Extract ALL information accurately from the resume text
2. For years_experience, calculate the total professional experience
3. For education_level, use the scale 0-5 as specified
4. For detected_career, choose the most appropriate career from the list provided
5. For career_match, calculate how well the person matches their career goal (or detected career if no goal provided)
6. For career_insights, provide comprehensive analysis of strengths, weaknesses, and recommendations
7. Ensure all arrays contain actual extracted data, not empty arrays
8. Be thorough and accurate in your extraction
9. If information is not found, use appropriate defaults (empty strings for text, 0 for numbers, empty arrays for lists)
10. Make sure the JSON is valid and complete

Return ONLY the JSON response, no additional text."""

            response = self.gemini_model.generate_content(prompt)
            
            if response and response.text:
                try:
                    # Parse the JSON response
                    text = response.text.strip()
                    
                    # Clean up the response to extract JSON
                    json_start = text.find('{')
                    json_end = text.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = text[json_start:json_end]
                        analysis = json.loads(json_str)
                        
                        # Validate and clean the analysis
                        analysis = self._validate_and_clean_gemini_analysis(analysis)
                        
                        logger.info("✅ Gemini AI extraction completed successfully")
                        return analysis
                    else:
                        logger.error("No valid JSON found in Gemini response")
                        return self._empty_analysis()
                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing failed: {e}")
                    logger.error(f"Raw response: {response.text}")
                    return self._empty_analysis()
            else:
                logger.error("No response from Gemini")
                return self._empty_analysis()
                
        except Exception as e:
            logger.error(f"Gemini extraction error: {e}")
            return self._empty_analysis()

    def _validate_and_clean_gemini_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the Gemini analysis to ensure proper structure"""
        # Ensure all required fields exist with proper defaults
        cleaned_analysis = {
            'personal_info': analysis.get('personal_info', {}),
            'skills': analysis.get('skills', {}),
            'experience': analysis.get('experience', []),
            'education': analysis.get('education', []),
            'years_experience': analysis.get('years_experience', 0),
            'education_level': analysis.get('education_level', 0),
            'certifications': analysis.get('certifications', []),
            'projects': analysis.get('projects', []),
            'detected_career': analysis.get('detected_career', 'software_engineer'),
            'career_match': analysis.get('career_match', {}),
            'career_insights': analysis.get('career_insights', {}),
            'extracted_info': analysis.get('extracted_info', {})
        }
        
        # Ensure skills structure is complete
        if not isinstance(cleaned_analysis['skills'], dict):
            cleaned_analysis['skills'] = {}
        
        required_skill_categories = ['technical', 'soft', 'languages', 'frameworks', 'databases', 'cloud', 'tools', 'methodologies']
        for category in required_skill_categories:
            if category not in cleaned_analysis['skills']:
                cleaned_analysis['skills'][category] = []
        
        # Ensure personal_info structure
        if not isinstance(cleaned_analysis['personal_info'], dict):
            cleaned_analysis['personal_info'] = {}
        
        # Ensure career_match structure
        if not isinstance(cleaned_analysis['career_match'], dict):
            cleaned_analysis['career_match'] = {}
        
        # Ensure career_insights structure
        if not isinstance(cleaned_analysis['career_insights'], dict):
            cleaned_analysis['career_insights'] = {}
        
        # Ensure extracted_info structure
        if not isinstance(cleaned_analysis['extracted_info'], dict):
            cleaned_analysis['extracted_info'] = {}
        
        # Create extracted_info for backward compatibility
        cleaned_analysis['extracted_info'] = {
            'skills': self._flatten_skills(cleaned_analysis['skills']),
            'years_experience': cleaned_analysis['years_experience'],
            'education_level': cleaned_analysis['education_level'],
            'personal_info': cleaned_analysis['personal_info']
        }
        
        return cleaned_analysis

    def _extract_all_information(self, resume_text: str) -> Dict[str, Any]:
        """Extract all information from resume"""
        return {
            'personal_info': self._extract_personal_info(resume_text),
            'skills': self._extract_categorized_skills(resume_text),
            'experience': self._extract_experience(resume_text),
            'education': self._extract_education(resume_text),
            'years_experience': self._calculate_years_experience(resume_text),
            'education_level': self._determine_education_level(resume_text),
            'certifications': self._extract_certifications(resume_text),
            'projects': self._extract_projects(resume_text)
        }

    def _extract_personal_info(self, resume_text: str) -> Dict[str, str]:
        """Extract personal information from resume"""
        personal_info = {}
        
        # Extract name (improved logic)
        lines = resume_text.strip().split('\n')
        for i, line in enumerate(lines[:5]):
            line = line.strip()
            # Skip empty lines and headers
            if not line or len(line) < 3:
                continue
            # Check if line looks like a name
            if (len(line.split()) >= 2 and len(line.split()) <= 4 and
                not re.search(r'[@\d\(\)\|]', line) and
                not any(word in line.lower() for word in ['resume', 'cv', 'curriculum', 'vitae', 'portfolio', 'profile'])):
                # Additional check: first letter of each word should be capital
                words = line.split()
                if all(word[0].isupper() for word in words if word):
                    personal_info['name'] = line
                    break
        
        # Fallback name extraction
        if 'name' not in personal_info:
            name_pattern = r'^([A-Z][a-z]+ (?:[A-Z]\. )?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
            name_match = re.search(name_pattern, resume_text, re.MULTILINE)
            if name_match:
                personal_info['name'] = name_match.group(1)
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, resume_text)
        if email_match:
            personal_info['email'] = email_match.group()
        
        # Extract phone
        phone_patterns = [
            r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{4}',
            r'[\+]?[0-9]{1,3}[-\s]?[0-9]{3,4}[-\s]?[0-9]{3,4}[-\s]?[0-9]{3,4}',
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, resume_text)
            if phone_match:
                personal_info['phone'] = phone_match.group()
                break
        
        # Extract LinkedIn
        linkedin_patterns = [
            r'linkedin\.com/in/[\w-]+',
            r'linkedin\.com/[\w-]+',
            r'linkedin:\s*([\w-]+)'
        ]
        for pattern in linkedin_patterns:
            linkedin_match = re.search(pattern, resume_text, re.IGNORECASE)
            if linkedin_match:
                personal_info['linkedin'] = linkedin_match.group()
                break
        
        # Extract GitHub
        github_patterns = [
            r'github\.com/[\w-]+',
            r'github:\s*([\w-]+)'
        ]
        for pattern in github_patterns:
            github_match = re.search(pattern, resume_text, re.IGNORECASE)
            if github_match:
                personal_info['github'] = github_match.group()
                break
        
        # Extract location
        location_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})\s*(?:\d{5})?',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z][a-z]+)',
            r'Location:\s*([^\n]+)'
        ]
        for pattern in location_patterns:
            location_match = re.search(pattern, resume_text)
            if location_match:
                personal_info['location'] = location_match.group(0)
                break
        
        # Default name if not found
        if 'name' not in personal_info or not personal_info['name']:
            personal_info['name'] = 'Professional'
        
        return personal_info

    def _extract_categorized_skills(self, resume_text: str) -> Dict[str, List[str]]:
        """Extract and categorize all skills from resume"""
        resume_lower = resume_text.lower()
        
        skills = {
            'technical': [],
            'soft': [],
            'languages': [],
            'frameworks': [],
            'databases': [],
            'cloud': [],
            'tools': [],
            'methodologies': []
        }
        
        # Programming Languages
        languages = {
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'C',
            'Go', 'Rust', 'Swift', 'Kotlin', 'PHP', 'Ruby', 'Scala', 'R',
            'MATLAB', 'Perl', 'Objective-C', 'Dart', 'Julia', 'Elixir',
            'Clojure', 'Haskell', 'Lua', 'Fortran', 'COBOL', 'Pascal',
            'VB.NET', 'F#', 'Scheme', 'Erlang', 'Groovy', 'Crystal',
            'HTML', 'HTML5', 'CSS', 'CSS3', 'SASS', 'SCSS', 'LESS',
            'SQL', 'NoSQL', 'GraphQL', 'Bash', 'PowerShell', 'Shell'
        }
        
        for lang in languages:
            if re.search(r'\b' + re.escape(lang.lower()) + r'\b', resume_lower):
                skills['languages'].append(lang)
        
        # Frameworks & Libraries
        frameworks = {
            # JavaScript
            'React', 'React.js', 'Angular', 'Vue', 'Vue.js', 'Svelte',
            'Next.js', 'Nuxt.js', 'Gatsby', 'Ember.js', 'Backbone.js',
            'jQuery', 'Redux', 'MobX', 'RxJS', 'Express', 'Express.js',
            'Koa', 'Fastify', 'NestJS', 'Node.js',
            # Python
            'Django', 'Flask', 'FastAPI', 'Pyramid', 'Tornado',
            'Pandas', 'NumPy', 'SciPy', 'Matplotlib', 'Seaborn',
            'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn',
            # Java
            'Spring', 'Spring Boot', 'Struts', 'Hibernate', 'Maven', 'Gradle',
            # .NET
            '.NET', 'ASP.NET', 'Entity Framework', '.NET Core',
            # PHP
            'Laravel', 'Symfony', 'CodeIgniter', 'Yii', 'Slim',
            # Ruby
            'Rails', 'Ruby on Rails', 'Sinatra',
            # Mobile
            'React Native', 'Flutter', 'Ionic', 'Xamarin'
        }
        
        for framework in frameworks:
            if re.search(r'\b' + re.escape(framework.lower()) + r'\b', resume_lower):
                skills['frameworks'].append(framework)
        
        # Databases
        databases = {
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Cassandra',
            'Elasticsearch', 'Neo4j', 'DynamoDB', 'CosmosDB', 'Firestore',
            'Firebase', 'Oracle', 'SQL Server', 'SQLite', 'MariaDB',
            'CouchDB', 'Memcached', 'InfluxDB', 'TimescaleDB',
            'CockroachDB', 'ArangoDB', 'RethinkDB', 'FaunaDB', 'Supabase'
        }
        
        for db in databases:
            if re.search(r'\b' + re.escape(db.lower()) + r'\b', resume_lower):
                skills['databases'].append(db)
        
        # Cloud Platforms & Services
        cloud_services = {
            'AWS', 'Amazon Web Services', 'EC2', 'S3', 'Lambda', 'RDS',
            'CloudFront', 'Route53', 'Elastic Beanstalk', 'ECS', 'EKS',
            'Azure', 'Microsoft Azure', 'Azure Functions', 'Azure DevOps',
            'GCP', 'Google Cloud', 'Google Cloud Platform', 'Firebase',
            'Heroku', 'DigitalOcean', 'Linode', 'Vultr', 'Netlify',
            'Vercel', 'Cloudflare', 'Fastly', 'Akamai', 'Alibaba Cloud',
            'IBM Cloud', 'Oracle Cloud'
        }
        
        for service in cloud_services:
            if re.search(r'\b' + re.escape(service.lower()) + r'\b', resume_lower):
                skills['cloud'].append(service)
        
        # Tools & Technologies
        tools = {
            # Version Control
            'Git', 'GitHub', 'GitLab', 'Bitbucket', 'SVN', 'Mercurial',
            # CI/CD
            'Jenkins', 'Travis CI', 'CircleCI', 'GitHub Actions',
            'GitLab CI', 'Bamboo', 'TeamCity', 'Azure DevOps',
            # Containerization
            'Docker', 'Kubernetes', 'OpenShift', 'Rancher', 'Podman',
            # Configuration Management
            'Ansible', 'Puppet', 'Chef', 'Terraform', 'Vagrant',
            # Monitoring
            'Prometheus', 'Grafana', 'ELK Stack', 'Splunk', 'Datadog',
            'New Relic', 'Sentry', 'PagerDuty',
            # Project Management
            'Jira', 'Confluence', 'Slack', 'Teams', 'Asana', 'Trello',
            'Notion', 'Monday.com', 'ClickUp',
            # Design Tools
            'Figma', 'Sketch', 'Adobe XD', 'Photoshop', 'Illustrator',
            'InVision', 'Zeplin', 'Principle', 'Framer',
            # Testing
            'Selenium', 'Cypress', 'Jest', 'Mocha', 'Jasmine', 'Pytest',
            'JUnit', 'TestNG', 'Postman', 'SoapUI'
        }
        
        for tool in tools:
            if re.search(r'\b' + re.escape(tool.lower()) + r'\b', resume_lower):
                skills['tools'].append(tool)
        
        # Methodologies & Practices
        methodologies = {
            'Agile', 'Scrum', 'Kanban', 'Lean', 'DevOps', 'CI/CD',
            'Test-Driven Development', 'TDD', 'Behavior-Driven Development',
            'BDD', 'Pair Programming', 'Code Review', 'Microservices',
            'RESTful API', 'GraphQL', 'SOAP', 'Design Patterns',
            'SOLID Principles', 'Clean Code', 'Domain-Driven Design',
            'Event-Driven Architecture', 'Serverless', 'Cloud Native'
        }
        
        for method in methodologies:
            if re.search(r'\b' + re.escape(method.lower()) + r'\b', resume_lower):
                skills['methodologies'].append(method)
        
        # Technical Skills from database
        for skill in SKILLS_DATABASE.get('technical', []):
            if skill.lower() in resume_lower and skill not in skills['technical']:
                skills['technical'].append(skill)
        
        # Soft Skills from database
        for skill in SKILLS_DATABASE.get('soft', []):
            if skill.lower() in resume_lower and skill not in skills['soft']:
                skills['soft'].append(skill)
        
        # Remove duplicates and sort
        for category in skills:
            skills[category] = sorted(list(set(skills[category])))
        
        return skills

    def _extract_experience(self, resume_text: str) -> List[Dict[str, Any]]:
        """Extract work experience from resume"""
        experience = []
        
        # Multiple patterns for different resume formats
        patterns = [
            # Pattern: Title at Company (Date - Date)
            r'([A-Za-z\s,&.]+?(?:Engineer|Developer|Manager|Analyst|Designer|Architect|Lead|Senior|Junior|Intern|Consultant|Specialist|Director|Head|Chief))\s+(?:at|@|,)\s+([A-Za-z0-9\s,&.()-]+?)\s*[\(\[]?\s*(\d{4}|\w{3}\s+\d{4})\s*[-–—]\s*(\d{4}|\w{3}\s+\d{4}|[Pp]resent|[Cc]urrent)',
            
            # Pattern: Company | Title | Dates
            r'([A-Za-z0-9\s,&.()-]+?)\s*[\|•]\s*([A-Za-z\s,&.]+?(?:Engineer|Developer|Manager|Analyst|Designer))\s*[\|•]\s*(\d{4}|\w{3}\s+\d{4})\s*[-–—]\s*(\d{4}|\w{3}\s+\d{4}|[Pp]resent|[Cc]urrent)',
            
            # Pattern: Title \n Company \n Dates
            r'([A-Za-z\s,&.]+?(?:Engineer|Developer|Manager|Analyst|Designer|Architect|Lead|Senior|Junior|Intern))\n([A-Za-z0-9\s,&.()-]+?)\n.*?(\d{4}|\w{3}\s+\d{4})\s*[-–—]\s*(\d{4}|\w{3}\s+\d{4}|[Pp]resent|[Cc]urrent)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, resume_text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                if len(match) == 4:
                    # Determine which is title and which is company based on pattern
                    if 'at' in pattern or match[0].lower().endswith(('engineer', 'developer', 'manager', 'analyst', 'designer')):
                        title = match[0].strip()
                        company = match[1].strip()
                    else:
                        title = match[1].strip()
                        company = match[0].strip()
                    
                    start = match[2]
                    end = match[3]
                    
                    # Calculate years
                    years = self._calculate_duration(start, end)
                    
                    experience.append({
                        'title': title,
                        'company': company,
                        'duration': f"{start} - {end}",
                        'years': years
                    })
        
        # Remove duplicates
        seen = set()
        unique_experience = []
        for exp in experience:
            key = (exp['title'], exp['company'])
            if key not in seen:
                seen.add(key)
                unique_experience.append(exp)
        
        return unique_experience

    def _calculate_duration(self, start: str, end: str) -> int:
        """Calculate duration in years"""
        try:
            # Extract years
            start_year_match = re.search(r'\d{4}', start)
            
            if end.lower() in ['present', 'current']:
                end_year = datetime.now().year
            else:
                end_year_match = re.search(r'\d{4}', end)
                end_year = int(end_year_match.group()) if end_year_match else datetime.now().year
            
            start_year = int(start_year_match.group()) if start_year_match else end_year - 1
            
            return max(1, end_year - start_year)
        except:
            return 1

    def _extract_education(self, resume_text: str) -> List[Dict[str, Any]]:
        """Extract education information from resume"""
        education = []
        
        # Degree patterns
        degree_types = [
            'Bachelor', 'B.S.', 'B.A.', 'B.Sc.', 'B.Tech', 'B.E.',
            'Master', 'M.S.', 'M.A.', 'M.Sc.', 'M.Tech', 'M.E.', 'MBA',
            'Ph.D', 'PhD', 'Doctorate', 'Associate', 'A.S.', 'A.A.',
            'Diploma', 'Certificate'
        ]
        
        # Create pattern for degrees
        degree_pattern = '(?:' + '|'.join(re.escape(d) for d in degree_types) + ')'
        
        # Patterns for education extraction
        patterns = [
            # Degree in Field from University, Year
            rf'({degree_pattern})[^\n]*?(?:in|of)?\s*([A-Za-z\s,]+?)(?:\n|from|at)\s*([A-Za-z\s,&.]+?)[,\s]*(?:\()?(\d{{4}})(?:\))?',
            # University - Degree - Year
            rf'([A-Za-z\s,&.]+?)\s*[-–|]\s*({degree_pattern})[^\n]*?\s*[-–|]\s*(\d{{4}})'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            for match in matches:
                if len(match) >= 3:
                    if len(match) == 4:
                        education.append({
                            'degree': match[0],
                            'field': match[1].strip(),
                            'institution': match[2].strip(),
                            'year': match[3]
                        })
                    else:
                        education.append({
                            'degree': match[1] if degree_pattern in pattern else match[0],
                            'institution': match[0] if degree_pattern in pattern else match[1],
                            'year': match[2]
                        })
        
        return education

    def _extract_certifications(self, resume_text: str) -> List[str]:
        """Extract certifications from resume"""
        certifications = []
        
        # Common certification patterns
        cert_keywords = [
            'AWS Certified', 'Azure Certified', 'Google Cloud Certified',
            'Cisco Certified', 'CompTIA', 'PMP', 'ITIL', 'Scrum Master',
            'Six Sigma', 'CISSP', 'CISA', 'CEH', 'CCNA', 'CCNP', 'MCSE'
        ]
        
        resume_lower = resume_text.lower()
        
        for cert in cert_keywords:
            if cert.lower() in resume_lower:
                certifications.append(cert)
        
        # Look for certification section
        cert_section = re.search(
            r'(certifications?|certificates?)[\s:]*([^\n]+(?:\n[^\n]+)*)',
            resume_text, re.IGNORECASE
        )
        
        if cert_section:
            cert_text = cert_section.group(2)
            # Extract individual certifications
            cert_lines = cert_text.split('\n')
            for line in cert_lines[:5]:  # Limit to avoid false positives
                if len(line.strip()) > 5 and len(line.strip()) < 100:
                    certifications.append(line.strip())
        
        return list(set(certifications))

    def _extract_projects(self, resume_text: str) -> List[Dict[str, str]]:
        """Extract projects from resume"""
        projects = []
        
        # Look for projects section
        project_section = re.search(
            r'(projects?)[\s:]*\n([^\n]+(?:\n[^\n]+)*?)(?=\n[A-Z][a-z]+:|$)',
            resume_text, re.IGNORECASE | re.MULTILINE
        )
        
        if project_section:
            project_text = project_section.group(2)
            # Extract individual projects
            project_patterns = [
                r'([A-Za-z0-9\s]+):\s*([^\n]+)',  # Name: Description
                r'[•·]\s*([A-Za-z0-9\s]+)\s*[-–]\s*([^\n]+)',  # • Name - Description
                r'([A-Za-z0-9\s]+)\s*\|([^\n]+)'  # Name | Description
            ]
            
            for pattern in project_patterns:
                matches = re.findall(pattern, project_text)
                for match in matches:
                    if len(match) == 2:
                        projects.append({
                            'name': match[0].strip(),
                            'description': match[1].strip()
                        })
        
        return projects[:5]  # Limit to top 5 projects

    def _calculate_years_experience(self, resume_text: str) -> int:
        """Calculate total years of experience"""
        resume_lower = resume_text.lower()
        
        # Look for explicit mentions
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:professional\s*)?experience',
            r'experience:\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*(?:of\s*)?work(?:ing)?\s*experience'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, resume_lower)
            if matches:
                try:
                    return max(map(int, matches))
                except:
                    pass
        
        # Calculate from experience entries
        experience = self._extract_experience(resume_text)
        if experience:
            total_years = sum(exp.get('years', 0) for exp in experience)
            return max(1, total_years)
        
        # Estimate from graduation year
        grad_year_match = re.search(r'(?:graduated?|graduation)\s*:?\s*(\d{4})', resume_lower)
        if grad_year_match:
            grad_year = int(grad_year_match.group(1))
            current_year = datetime.now().year
            estimated_years = current_year - grad_year
            if 0 < estimated_years < 50:
                return estimated_years
        
        return 0

    def _determine_education_level(self, resume_text: str) -> int:
        """Determine education level (0-5 scale)"""
        resume_lower = resume_text.lower()
        
        education_levels = [
            (5, ['phd', 'ph.d', 'doctorate', 'doctoral']),
            (4, ['master', 'mba', 'm.s.', 'm.a.', 'msc', 'm.tech', 'm.e.']),
            (3, ['bachelor', 'b.s.', 'b.a.', 'bsc', 'b.tech', 'b.e.']),
            (2, ['associate', 'a.s.', 'a.a.']),
            (1, ['diploma', 'certificate', 'certification']),
            (0, ['high school', 'secondary'])
        ]
        
        for level, keywords in education_levels:
            for keyword in keywords:
                if keyword in resume_lower:
                    return level
        
        return 0

    def _detect_career_path(self, skills: Dict[str, List[str]], resume_text: str) -> str:
        """Detect most likely career path based on skills and content"""
        
        resume_lower = resume_text.lower()
        
        # Career scoring system
        career_scores = {
            'software_engineer': 0,
            'frontend_developer': 0,
            'backend_developer': 0,
            'fullstack_developer': 0,
            'data_scientist': 0,
            'data_analyst': 0,
            'data_engineer': 0,
            'machine_learning_engineer': 0,
            'devops_engineer': 0,
            'cloud_architect': 0,
            'mobile_developer': 0,
            'ui_ux_designer': 0,
            'product_manager': 0,
            'project_manager': 0,
            'qa_engineer': 0,
            'security_engineer': 0,
            'blockchain_developer': 0,
            'game_developer': 0
        }
        
        # Score based on programming languages
        for lang in skills.get('languages', []):
            lang_lower = lang.lower()
            
            # Frontend languages
            if lang_lower in ['javascript', 'typescript', 'html', 'css', 'sass', 'scss']:
                career_scores['frontend_developer'] += 3
                career_scores['fullstack_developer'] += 2
                
            # Backend languages
            if lang_lower in ['python', 'java', 'go', 'rust', 'c#', 'php', 'ruby']:
                career_scores['backend_developer'] += 3
                career_scores['software_engineer'] += 2
                career_scores['fullstack_developer'] += 2
                
            # Data science languages
            if lang_lower in ['python', 'r', 'julia', 'matlab', 'sas']:
                career_scores['data_scientist'] += 3
                career_scores['data_analyst'] += 2
                career_scores['machine_learning_engineer'] += 2
                
            # Mobile languages
            if lang_lower in ['swift', 'kotlin', 'dart', 'objective-c', 'java']:
                career_scores['mobile_developer'] += 4
                
            # Systems languages
            if lang_lower in ['c', 'c++', 'rust', 'go']:
                career_scores['software_engineer'] += 3
                
        # Score based on frameworks
        for framework in skills.get('frameworks', []):
            framework_lower = framework.lower()
            
            # Frontend frameworks
            if framework_lower in ['react', 'angular', 'vue', 'svelte', 'next.js', 'nuxt.js']:
                career_scores['frontend_developer'] += 4
                career_scores['fullstack_developer'] += 3
                
            # Backend frameworks
            if framework_lower in ['django', 'flask', 'fastapi', 'spring', 'express', 'rails']:
                career_scores['backend_developer'] += 4
                career_scores['fullstack_developer'] += 3
                career_scores['software_engineer'] += 2
                
            # ML frameworks
            if framework_lower in ['tensorflow', 'pytorch', 'keras', 'scikit-learn']:
                career_scores['data_scientist'] += 4
                career_scores['machine_learning_engineer'] += 5
                
            # Mobile frameworks
            if framework_lower in ['react native', 'flutter', 'ionic', 'xamarin']:
                career_scores['mobile_developer'] += 4
        
        # Score based on tools (reduced weights to prevent over-scoring)
        for tool in skills.get('tools', []):
            tool_lower = tool.lower()
            
            # DevOps tools (reduced weight - these are often used by developers too)
            if tool_lower in ['docker', 'kubernetes', 'jenkins', 'terraform', 'ansible']:
                career_scores['devops_engineer'] += 2  # Reduced from 4
                career_scores['cloud_architect'] += 1  # Reduced from 2
                career_scores['software_engineer'] += 1  # Developers use these too
                career_scores['backend_developer'] += 1
                
            # Design tools
            if tool_lower in ['figma', 'sketch', 'adobe xd', 'photoshop', 'illustrator']:
                career_scores['ui_ux_designer'] += 5
                
            # QA tools
            if tool_lower in ['selenium', 'cypress', 'jest', 'postman']:
                career_scores['qa_engineer'] += 3
                
            # Development tools (give points to software engineers)
            if tool_lower in ['git', 'github', 'gitlab', 'jira', 'confluence', 'vscode', 'intellij']:
                career_scores['software_engineer'] += 2
                career_scores['frontend_developer'] += 1
                career_scores['backend_developer'] += 1
                
        # Score based on cloud services (reduced weight)
        for cloud in skills.get('cloud', []):
            career_scores['cloud_architect'] += 2  # Reduced from 3
            career_scores['devops_engineer'] += 1  # Reduced from 3
            career_scores['software_engineer'] += 1  # Developers use cloud too
            career_scores['backend_developer'] += 1
        
        # Score based on databases
        database_count = len(skills.get('databases', []))
        if database_count > 3:
            career_scores['data_engineer'] += 3
            career_scores['backend_developer'] += 2
        
        # Score based on job titles in experience (increased weight)
        experience = self._extract_experience(resume_text)
        for exp in experience:
            title_lower = exp.get('title', '').lower()
            
            for career, keywords in {
                'software_engineer': ['software engineer', 'software developer', 'developer', 'programmer', 'engineer'],
                'frontend_developer': ['frontend', 'front-end', 'ui developer', 'frontend developer', 'react developer', 'angular developer'],
                'backend_developer': ['backend', 'back-end', 'server', 'backend developer', 'api developer', 'server developer'],
                'fullstack_developer': ['fullstack', 'full-stack', 'full stack', 'fullstack developer', 'full stack developer'],
                'data_scientist': ['data scientist', 'ml engineer', 'machine learning engineer', 'ai engineer'],
                'data_analyst': ['data analyst', 'business analyst', 'analyst'],
                'data_engineer': ['data engineer', 'etl developer', 'data pipeline'],
                'devops_engineer': ['devops', 'site reliability', 'sre', 'devops engineer', 'platform engineer'],
                'cloud_architect': ['cloud architect', 'solutions architect', 'cloud engineer'],
                'mobile_developer': ['mobile', 'ios', 'android', 'mobile developer', 'ios developer', 'android developer'],
                'ui_ux_designer': ['ui', 'ux', 'designer', 'ui designer', 'ux designer', 'product designer'],
                'product_manager': ['product manager', 'product owner', 'product lead'],
                'project_manager': ['project manager', 'program manager', 'scrum master'],
                'qa_engineer': ['qa', 'quality', 'test', 'qa engineer', 'test engineer', 'quality assurance'],
                'security_engineer': ['security', 'cybersecurity', 'infosec', 'security engineer', 'cyber security']
            }.items():
                if any(keyword in title_lower for keyword in keywords):
                    career_scores[career] += 15  # Increased weight for actual job titles
                    
        # Additional context analysis from resume text
        resume_lower = resume_text.lower()
        
        # Look for specific career indicators in the text
        career_indicators = {
            'software_engineer': ['software development', 'application development', 'system development', 'coding', 'programming'],
            'frontend_developer': ['user interface', 'user experience', 'web design', 'responsive design', 'frontend development'],
            'backend_developer': ['api development', 'server-side', 'database design', 'backend development', 'microservices'],
            'data_scientist': ['machine learning', 'artificial intelligence', 'predictive modeling', 'statistical analysis', 'data science'],
            'data_analyst': ['business intelligence', 'reporting', 'data visualization', 'analytics', 'kpi'],
            'devops_engineer': ['ci/cd', 'continuous integration', 'continuous deployment', 'infrastructure', 'automation'],
            'mobile_developer': ['mobile app', 'ios app', 'android app', 'mobile development', 'app store'],
            'ui_ux_designer': ['wireframing', 'prototyping', 'user research', 'design system', 'interaction design']
        }
        
        for career, indicators in career_indicators.items():
            for indicator in indicators:
                if indicator in resume_lower:
                    career_scores[career] += 3  # Moderate weight for context indicators
        
        # Get the highest scoring career with better logic
        if career_scores:
            # Sort careers by score
            sorted_careers = sorted(career_scores.items(), key=lambda x: x[1], reverse=True)
            best_career, best_score = sorted_careers[0]
            
            # Only return the best career if it has a reasonable score
            if best_score >= 5:  # Minimum threshold
                # Check if there's a close second place
                if len(sorted_careers) > 1:
                    second_career, second_score = sorted_careers[1]
                    # If scores are very close, prefer more general roles
                    if best_score - second_score <= 3:
                        # Prefer software_engineer over very specific roles if scores are close
                        if best_career in ['devops_engineer', 'cloud_architect', 'qa_engineer'] and second_career == 'software_engineer':
                            return 'software_engineer'
                        elif best_career in ['frontend_developer', 'backend_developer'] and second_career == 'fullstack_developer':
                            return 'fullstack_developer'
                
                # Log top 3 career scores for debugging
                top_3 = sorted_careers[:3]
                logger.info(f"Career detection scores: {top_3}")
                logger.info(f"Selected career: {best_career} (score: {best_score})")
                return best_career
        
        # Default fallback
        logger.info("Career detection: Using default software_engineer")
        return 'software_engineer'

    def _calculate_career_match(self, skills: Dict[str, List[str]], career_goal: str, years_exp: int) -> Dict[str, Any]:
        """Calculate how well the resume matches the career goal"""
        
        # Define ideal requirements for each career
        career_requirements = {
            'software_engineer': {
                'required': ['Programming', 'Data Structures', 'Algorithms', 'Git', 'Testing'],
                'languages': ['Python', 'Java', 'JavaScript', 'C++', 'Go'],
                'tools': ['Git', 'Docker', 'CI/CD', 'Cloud'],
                'soft': ['Problem Solving', 'Communication', 'Teamwork']
            },
            'frontend_developer': {
                'required': ['JavaScript', 'HTML', 'CSS', 'React/Vue/Angular', 'Responsive Design'],
                'languages': ['JavaScript', 'TypeScript', 'HTML', 'CSS'],
                'tools': ['Git', 'Webpack', 'npm/yarn', 'Chrome DevTools'],
                'soft': ['Design Sense', 'User Experience', 'Communication']
            },
            'backend_developer': {
                'required': ['Server-side Programming', 'Database', 'API', 'Security', 'Performance'],
                'languages': ['Python', 'Java', 'Go', 'Node.js', 'C#'],
                'tools': ['Docker', 'Redis', 'Message Queue', 'Cloud'],
                'soft': ['Problem Solving', 'System Design', 'Communication']
            },
            'data_scientist': {
                'required': ['Statistics', 'Machine Learning', 'Python/R', 'Data Analysis', 'Visualization'],
                'languages': ['Python', 'R', 'SQL'],
                'tools': ['TensorFlow/PyTorch', 'Jupyter', 'Pandas', 'Cloud'],
                'soft': ['Analytical Thinking', 'Communication', 'Business Understanding']
            },
            'devops_engineer': {
                'required': ['CI/CD', 'Containerization', 'Cloud', 'Monitoring', 'Scripting'],
                'languages': ['Python', 'Bash', 'Go', 'JavaScript'],
                'tools': ['Docker', 'Kubernetes', 'Terraform', 'Jenkins'],
                'soft': ['Problem Solving', 'Communication', 'Collaboration']
            }
        }
        
        # Get requirements for the career goal
        requirements = career_requirements.get(
            career_goal,
            career_requirements['software_engineer']  # Default
        )
        
        # Flatten user skills
        user_skills_flat = self._flatten_skills(skills)
        user_skills_lower = [s.lower() for s in user_skills_flat]
        
        # Calculate matches
        matched_skills = []
        missing_skills = []
        
        # Check required skills
        for req_skill in requirements['required']:
            matched = False
            for user_skill in user_skills_flat:
                if req_skill.lower() in user_skill.lower() or user_skill.lower() in req_skill.lower():
                    matched_skills.append(req_skill)
                    matched = True
                    break
            if not matched:
                missing_skills.append(req_skill)
        
        # Check language requirements
        lang_match = 0
        for req_lang in requirements.get('languages', []):
            if req_lang in skills.get('languages', []):
                lang_match += 1
        
        # Check tool requirements
        tool_match = 0
        for req_tool in requirements.get('tools', []):
            for user_tool in skills.get('tools', []):
                if req_tool.lower() in user_tool.lower():
                    tool_match += 1
                    break
        
        # Calculate match percentage
        total_requirements = len(requirements['required']) + len(requirements.get('languages', [])) + len(requirements.get('tools', []))
        total_matched = len(matched_skills) + lang_match + tool_match
        
        if total_requirements > 0:
            match_percentage = (total_matched / total_requirements) * 100
        else:
            match_percentage = 0
        
        # Adjust for experience
        if years_exp >= 5:
            match_percentage = min(100, match_percentage + 15)
        elif years_exp >= 3:
            match_percentage = min(100, match_percentage + 10)
        elif years_exp >= 1:
            match_percentage = min(100, match_percentage + 5)
        
        # Determine readiness level
        if match_percentage >= 80:
            readiness = "Senior-Ready"
        elif match_percentage >= 65:
            readiness = "Mid-Level"
        elif match_percentage >= 45:
            readiness = "Entry-Level"
        else:
            readiness = "Learning Phase"
        
        # Generate recommendations
        recommendations = []
        if missing_skills:
            recommendations.append(f"Focus on learning: {', '.join(missing_skills[:3])}")
        if lang_match < 2:
            recommendations.append("Strengthen programming language skills")
        if tool_match < 2:
            recommendations.append("Gain hands-on experience with industry tools")
        recommendations.append("Build portfolio projects showcasing your skills")
        recommendations.append("Network with professionals in your target field")
        
        # Generate next steps
        next_steps = []
        if match_percentage >= 70:
            next_steps.append("Apply for positions matching your skill level")
            next_steps.append("Negotiate for better roles with confidence")
        elif match_percentage >= 50:
            next_steps.append("Apply for entry to mid-level positions")
            next_steps.append("Continue building expertise in core areas")
        else:
            next_steps.append("Focus on fundamental skill development")
            next_steps.append("Consider internships or junior positions")
            next_steps.append("Complete online courses or bootcamps")
        
        return {
            'match_percentage': round(match_percentage, 1),
            'career_readiness': readiness,
            'matched_skills': matched_skills[:10],
            'missing_skills': missing_skills[:5],
            'recommendations': recommendations[:5],
            'next_steps': next_steps[:3],
            'timeline_to_goal': self._estimate_timeline(match_percentage),
            'confidence_score': round(match_percentage / 10, 1)
        }

    def _estimate_timeline(self, match_percentage: float) -> str:
        """Estimate timeline to achieve career goal"""
        if match_percentage >= 80:
            return "Ready now - 3 months for fine-tuning"
        elif match_percentage >= 65:
            return "3-6 months of focused development"
        elif match_percentage >= 45:
            return "6-12 months with consistent effort"
        elif match_percentage >= 25:
            return "12-18 months of dedicated learning"
        else:
            return "18-24 months to build foundation"

    def _generate_career_insights(self, skills: Dict[str, List[str]], years_exp: int, 
                                 edu_level: int, detected_career: str) -> Dict[str, Any]:
        """Generate comprehensive career insights"""
        
        total_skills = sum(len(skill_list) for skill_list in skills.values())
        
        # Analyze strengths
        strengths = []
        if total_skills > 20:
            strengths.append("Exceptional technical skill diversity")
        elif total_skills > 15:
            strengths.append("Strong technical foundation")
        elif total_skills > 10:
            strengths.append("Solid skill set")
        
        if years_exp > 5:
            strengths.append(f"{years_exp} years of valuable experience")
        elif years_exp > 2:
            strengths.append("Growing professional experience")
        
        if edu_level >= 4:
            strengths.append("Advanced academic credentials")
        elif edu_level >= 3:
            strengths.append("Strong educational background")
        
        if len(skills.get('cloud', [])) > 2:
            strengths.append("Cloud platform expertise")
        
        if len(skills.get('frameworks', [])) > 5:
            strengths.append("Proficiency in multiple frameworks")
        
        # Areas for improvement
        improvements = []
        if years_exp < 2:
            improvements.append("Build more professional experience")
        
        if not skills.get('cloud'):
            improvements.append("Learn cloud platforms (AWS/GCP/Azure)")
        
        if len(skills.get('languages', [])) < 3:
            improvements.append("Expand programming language repertoire")
        
        if not skills.get('methodologies'):
            improvements.append("Learn modern development methodologies")
        
        # Skill level assessment
        if total_skills > 25 and years_exp > 5:
            skill_level = "Expert"
        elif total_skills > 20 and years_exp > 3:
            skill_level = "Advanced"
        elif total_skills > 15 and years_exp > 1:
            skill_level = "Intermediate"
        elif total_skills > 10:
            skill_level = "Developing"
        else:
            skill_level = "Beginner"
        
        # Market demand assessment
        high_demand_skills = ['python', 'javascript', 'react', 'aws', 'docker', 'kubernetes', 
                              'machine learning', 'data science', 'cloud', 'devops']
        
        user_skills_lower = [skill.lower() for skill_list in skills.values() for skill in skill_list]
        demand_matches = sum(1 for skill in high_demand_skills if any(skill in s for s in user_skills_lower))
        
        if demand_matches >= 6:
            market_demand = "Very High"
        elif demand_matches >= 4:
            market_demand = "High"
        elif demand_matches >= 2:
            market_demand = "Moderate"
        else:
            market_demand = "Emerging"
        
        # Recommended next role
        role_progression = {
            'software_engineer': {
                0: "Junior Software Engineer",
                2: "Software Engineer",
                5: "Senior Software Engineer",
                8: "Staff/Lead Software Engineer",
                10: "Principal Engineer/Engineering Manager"
            },
            'data_scientist': {
                0: "Junior Data Analyst",
                2: "Data Scientist",
                5: "Senior Data Scientist",
                8: "Lead Data Scientist",
                10: "Chief Data Scientist"
            },
            'frontend_developer': {
                0: "Junior Frontend Developer",
                2: "Frontend Developer",
                5: "Senior Frontend Developer",
                8: "Frontend Lead/Architect",
                10: "Frontend Principal/Engineering Manager"
            }
        }
        
        career_path = role_progression.get(detected_career, role_progression['software_engineer'])
        
        for min_years, role in sorted(career_path.items(), reverse=True):
            if years_exp >= min_years:
                recommended_role = role
                break
        else:
            recommended_role = career_path[0]
        
        return {
            'strengths': strengths[:5],
            'areas_for_improvement': improvements[:3],
            'skill_level': skill_level,
            'market_demand': market_demand,
            'recommended_next_role': recommended_role,
            'total_skills_count': total_skills,
            'career_readiness': self._determine_readiness(total_skills, years_exp, edu_level)
        }

    def _determine_readiness(self, total_skills: int, years_exp: int, edu_level: int) -> str:
        """Determine overall career readiness"""
        score = (total_skills * 2) + (years_exp * 10) + (edu_level * 5)
        
        if score >= 100:
            return "Senior-Ready"
        elif score >= 70:
            return "Mid-Level Ready"
        elif score >= 40:
            return "Entry-Level Ready"
        else:
            return "Foundation Building"

    def _get_gemini_enhanced_data(self, resume_text: str, initial_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get enhanced skills and career detection from Gemini"""
        if not self.gemini_model:
            return None
        
        try:
            prompt = f"""You are an expert resume parser. Extract and enhance the following information from this resume:

RESUME TEXT:
{resume_text[:2500]}

CURRENT EXTRACTED DATA:
- Skills: {initial_analysis['skills']}
- Detected Career: {initial_analysis['detected_career']}
- Years Experience: {initial_analysis['years_experience']}

Please provide a JSON response with enhanced data:
{{
  "enhanced_skills": {{
    "languages": ["programming languages found"],
    "frameworks": ["frameworks and libraries"],
    "tools": ["development tools and software"],
    "databases": ["database technologies"],
    "cloud": ["cloud platforms and services"],
    "soft_skills": ["soft skills and competencies"],
    "certifications": ["professional certifications"],
    "methodologies": ["development methodologies like Agile, Scrum"]
  }},
  "enhanced_career": {{
    "primary_career": "most accurate career path",
    "career_level": "entry/mid/senior/lead/executive",
    "specialization": "specific specialization within the field",
    "industry": "target industry"
  }},
  "enhanced_experience": {{
    "years_experience": "more accurate years of experience",
    "experience_quality": "assessment of experience depth",
    "leadership_experience": "any leadership or management experience",
    "key_achievements": ["notable achievements and accomplishments"]
  }},
  "education_enhancement": {{
    "education_level": "more accurate education level",
    "relevant_degrees": ["relevant degrees and qualifications"],
    "institutions": ["educational institutions"]
  }}
}}

Focus on accuracy and completeness. Extract skills that might have been missed by pattern matching."""

            response = self.gemini_model.generate_content(prompt)
            
            if response and response.text:
                try:
                    text = response.text.strip()
                    json_start = text.find('{')
                    json_end = text.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = text[json_start:json_end]
                        enhanced_data = json.loads(json_str)
                        
                        # Merge enhanced skills with existing skills
                        if 'enhanced_skills' in enhanced_data:
                            for category, skills in enhanced_data['enhanced_skills'].items():
                                if skills and isinstance(skills, list):
                                    # Add new skills to existing categories
                                    if category in initial_analysis['skills']:
                                        initial_analysis['skills'][category].extend(skills)
                                        initial_analysis['skills'][category] = list(set(initial_analysis['skills'][category]))
                                    else:
                                        initial_analysis['skills'][category] = skills
                        
                        # Override career detection if Gemini provides a more specific one
                        if 'enhanced_career' in enhanced_data and enhanced_data['enhanced_career'].get('primary_career'):
                            gemini_career = enhanced_data['enhanced_career']['primary_career'].lower().replace(' ', '_')
                            if gemini_career in ['software_engineer', 'frontend_developer', 'backend_developer', 'fullstack_developer', 
                                               'data_scientist', 'data_analyst', 'devops_engineer', 'mobile_developer', 
                                               'ui_ux_designer', 'product_manager', 'qa_engineer']:
                                initial_analysis['detected_career'] = gemini_career
                                logger.info(f"✅ Gemini overrode career detection: {gemini_career}")
                        
                        logger.info("✅ Gemini enhanced data extraction completed")
                        return enhanced_data
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"Gemini enhanced data JSON parsing failed: {e}")
                    
        except Exception as e:
            logger.error(f"Gemini enhanced data extraction error: {e}")
            
        return None

    def _enhance_with_gemini(self, resume_text: str, initial_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Enhance analysis with comprehensive Gemini AI insights"""
        if not self.gemini_model:
            return None
        
        try:
            # Prepare comprehensive data for Gemini
            skills_summary = {
                'languages': initial_analysis['skills'].get('languages', [])[:10],
                'frameworks': initial_analysis['skills'].get('frameworks', [])[:10],
                'tools': initial_analysis['skills'].get('tools', [])[:10],
                'databases': initial_analysis['skills'].get('databases', [])[:5],
                'cloud': initial_analysis['skills'].get('cloud', [])[:5],
                'soft_skills': initial_analysis['skills'].get('soft_skills', [])[:10]
            }
            
            # Create a more comprehensive prompt for better analysis
            prompt = f"""You are an expert career advisor and resume analyst. Analyze this resume comprehensively and provide detailed insights.

RESUME TEXT:
{resume_text[:3000]}

CURRENT ANALYSIS:
- Detected Career: {initial_analysis['detected_career']}
- Years Experience: {initial_analysis['years_experience']}
- Education Level: {initial_analysis['education_level']}
- Skills Found: {skills_summary}
- Personal Info: {initial_analysis.get('personal_info', {})}

Please provide a comprehensive JSON analysis with the following structure:
{{
  "career_assessment": {{
    "primary_career": "most suitable career path",
    "alternative_careers": ["alternative career options"],
    "career_level": "entry/mid/senior/executive",
    "confidence_score": 85
  }},
  "skills_analysis": {{
    "technical_strengths": ["strong technical skills"],
    "missing_skills": ["skills to develop"],
    "skill_gaps": ["areas for improvement"],
    "unique_skills": ["rare or valuable skills"]
  }},
  "experience_evaluation": {{
    "experience_quality": "assessment of experience depth",
    "career_progression": "how career has progressed",
    "leadership_indicators": ["leadership experience found"],
    "achievement_highlights": ["notable achievements"]
  }},
  "market_positioning": {{
    "target_roles": ["specific job titles to target"],
    "salary_expectation": "estimated salary range",
    "market_demand": "how in-demand these skills are",
    "competitive_advantages": ["what makes them competitive"]
  }},
  "development_recommendations": {{
    "immediate_actions": ["what to do in next 3 months"],
    "skill_development": ["skills to learn/improve"],
    "certification_suggestions": ["relevant certifications"],
    "career_advancement": ["how to advance career"]
  }},
  "resume_improvements": {{
    "strengths": ["what's working well"],
    "weaknesses": ["areas to improve"],
    "suggestions": ["specific improvement suggestions"],
    "keyword_optimization": ["keywords to add"]
  }}
}}

Provide detailed, actionable insights based on the resume content. Be specific and practical in your recommendations."""

            response = self.gemini_model.generate_content(prompt)
            
            if response and response.text:
                try:
                    # Try to parse JSON from response
                    text = response.text.strip()
                    
                    # Look for JSON content more robustly
                    json_start = text.find('{')
                    json_end = text.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = text[json_start:json_end]
                        insights = json.loads(json_str)
                        
                        # Validate the insights structure
                        if self._validate_gemini_insights(insights):
                            logger.info("✅ Comprehensive Gemini insights generated successfully")
                            return insights
                        else:
                            logger.warning("Gemini insights structure validation failed")
                            return self._create_fallback_insights(response.text)
                    else:
                        return self._create_fallback_insights(response.text)
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parsing failed: {e}")
                    return self._create_fallback_insights(response.text)
                    
        except Exception as e:
            logger.error(f"Gemini enhancement error: {e}")
            return None

    def _validate_gemini_insights(self, insights: Dict[str, Any]) -> bool:
        """Validate that Gemini insights have the expected structure"""
        required_sections = [
            'career_assessment', 'skills_analysis', 'experience_evaluation',
            'market_positioning', 'development_recommendations', 'resume_improvements'
        ]
        
        for section in required_sections:
            if section not in insights:
                return False
        return True

    def _create_fallback_insights(self, raw_text: str) -> Dict[str, Any]:
        """Create structured insights from raw Gemini response"""
        return {
            'raw_analysis': raw_text,
            'career_assessment': {
                'primary_career': 'Analysis in progress',
                'confidence_score': 70
            },
            'skills_analysis': {
                'technical_strengths': ['See raw analysis for details'],
                'missing_skills': ['See raw analysis for details']
            },
            'development_recommendations': {
                'immediate_actions': ['Review raw analysis for specific recommendations']
            },
            'analysis_note': 'Gemini provided detailed analysis in text format'
        }

    def _flatten_skills(self, skills: Dict[str, List[str]]) -> List[str]:
        """Flatten skills dictionary into a single list"""
        flat_skills = []
        for category, skill_list in skills.items():
            flat_skills.extend(skill_list)
        return list(set(flat_skills))

    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'personal_info': {'name': 'Professional'},
            'skills': {
                'technical': [],
                'soft': [],
                'languages': [],
                'frameworks': [],
                'databases': [],
                'cloud': [],
                'tools': [],
                'methodologies': []
            },
            'experience': [],
            'education': [],
            'years_experience': 0,
            'education_level': 0,
            'detected_career': 'software_engineer',
            'career_match': {
                'match_percentage': 0,
                'career_readiness': 'Unknown',
                'matched_skills': [],
                'missing_skills': []
            },
            'career_insights': {
                'strengths': [],
                'areas_for_improvement': [],
                'skill_level': 'Beginner',
                'market_demand': 'Unknown'
            },
            'extracted_info': {
                'skills': [],
                'years_experience': 0,
                'education_level': 0,
                'personal_info': {'name': 'Professional'}
            },
            'analysis_method': 'No data'
        }

# Create global analyzer instance
resume_analyzer = ResumeAnalyzer()

# Wrapper functions for backward compatibility
def extract_text_from_pdf(file_path):
    return resume_analyzer.extract_text_from_pdf(file_path)

def extract_text_from_docx(file_path):
    return resume_analyzer.extract_text_from_docx(file_path)

def extract_skills_from_resume(resume_text):
    return resume_analyzer.analyze_resume(resume_text)

def analyze_resume_with_career_goal(resume_text, career_goal):
    return resume_analyzer.analyze_resume(resume_text, career_goal)

def calculate_career_match(resume_analysis, career_goal):
    if isinstance(resume_analysis, dict) and 'career_match' in resume_analysis:
        return resume_analysis['career_match']
    
    # Fallback calculation
    skills = resume_analysis.get('skills', {})
    years_exp = resume_analysis.get('years_experience', 0)
    return resume_analyzer._calculate_career_match(skills, career_goal, years_exp)

# Export all functions
__all__ = [
    'ResumeAnalyzer',
    'resume_analyzer',
    'extract_text_from_pdf',
    'extract_text_from_docx', 
    'extract_skills_from_resume',
    'analyze_resume_with_career_goal',
    'calculate_career_match'
]