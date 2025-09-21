# Career Database with Skills Requirements
CAREER_DATABASE = {
    "doctor": {
        "title": "Medical Doctor",
        "age_modifier": 10,
        "personality": "Professional, caring, analytical, detail-oriented",
        "salary_range": {"entry": 60000, "mid": 180000, "senior": 350000},
        "required_skills": [
            "Biology", "Chemistry", "Anatomy", "Physiology", "Pharmacology",
            "Clinical Skills", "Patient Care", "Medical Ethics", "Research"
        ],
        "education_path": [
            "Pre-med undergraduate (4 years)",
            "Medical school (4 years)",
            "Residency (3-7 years)",
            "Optional: Fellowship (1-3 years)"
        ],
        "certifications": ["MCAT", "USMLE Step 1-3", "Board Certification"],
        "career_progression": {
            "0-2": "Medical Student",
            "3-7": "Resident Physician",
            "8-12": "Attending Physician",
            "13-20": "Senior Physician",
            "20+": "Department Head/Chief"
        }
    },
    "software_engineer": {
        "title": "Software Engineer",
        "age_modifier": 10,
        "personality": "Logical, creative, problem-solver, continuous learner",
        "salary_range": {"entry": 75000, "mid": 130000, "senior": 200000},
        "required_skills": [
            "Programming", "Data Structures", "Algorithms", "System Design",
            "Git", "Testing", "Debugging", "Agile", "Cloud Computing"
        ],
        "education_path": [
            "Computer Science degree (4 years) OR Bootcamp (3-6 months)",
            "Internships during study",
            "Entry-level position",
            "Continuous learning and certifications"
        ],
        "certifications": ["AWS Certified", "Google Cloud", "Azure", "Scrum Master"],
        "career_progression": {
            "0-2": "Junior Developer",
            "3-5": "Mid-level Developer",
            "6-10": "Senior Developer",
            "10-15": "Staff/Principal Engineer",
            "15+": "Engineering Manager/Architect"
        }
    },
    "data_scientist": {
        "title": "Data Scientist",
        "age_modifier": 10,
        "personality": "Analytical, curious, detail-oriented, communicative",
        "salary_range": {"entry": 85000, "mid": 130000, "senior": 180000},
        "required_skills": [
            "Python", "R", "SQL", "Statistics", "Machine Learning",
            "Data Visualization", "Big Data", "Deep Learning", "Business Acumen"
        ],
        "education_path": [
            "Mathematics/Statistics/CS degree",
            "Master's in Data Science (optional)",
            "Online courses and projects",
            "Kaggle competitions"
        ],
        "certifications": ["TensorFlow Certificate", "AWS ML", "Tableau", "SAS"],
        "career_progression": {
            "0-2": "Junior Data Analyst",
            "3-5": "Data Scientist",
            "6-10": "Senior Data Scientist",
            "10-15": "Lead Data Scientist",
            "15+": "Chief Data Officer"
        }
    },
    "entrepreneur": {
        "title": "Entrepreneur",
        "age_modifier": 10,
        "personality": "Risk-taker, visionary, resilient, adaptable",
        "salary_range": {"entry": -50000, "mid": 100000, "senior": 1000000},
        "required_skills": [
            "Business Strategy", "Marketing", "Sales", "Finance", "Leadership",
            "Networking", "Product Development", "Risk Management", "Negotiation"
        ],
        "education_path": [
            "Any degree (business preferred)",
            "MBA (optional but helpful)",
            "Accelerator programs",
            "Mentorship and networking"
        ],
        "certifications": ["Lean Startup", "Digital Marketing", "PMP"],
        "career_progression": {
            "0-2": "Startup Founder",
            "3-5": "Growing Business Owner",
            "6-10": "Established Entrepreneur",
            "10-15": "Serial Entrepreneur",
            "15+": "Investor/Mentor"
        }
    },
    "teacher": {
        "title": "Teacher",
        "age_modifier": 10,
        "personality": "Patient, nurturing, communicative, organized",
        "salary_range": {"entry": 40000, "mid": 55000, "senior": 75000},
        "required_skills": [
            "Subject Expertise", "Curriculum Development", "Classroom Management",
            "Communication", "Assessment", "Technology Integration", "Psychology"
        ],
        "education_path": [
            "Bachelor's in Education or Subject",
            "Teaching Credential Program",
            "Student Teaching",
            "Master's in Education (for advancement)"
        ],
        "certifications": ["Teaching License", "Subject Specialization", "ESL"],
        "career_progression": {
            "0-2": "New Teacher",
            "3-7": "Experienced Teacher",
            "8-15": "Department Head",
            "15-20": "Assistant Principal",
            "20+": "Principal/Administrator"
        }
    }
}

# Skills Database for Matching
SKILLS_DATABASE = {
    "technical": [
        "Python", "Java", "JavaScript", "C++", "SQL", "R", "HTML/CSS",
        "React", "Node.js", "Machine Learning", "Data Analysis", "Cloud Computing"
    ],
    "soft": [
        "Leadership", "Communication", "Problem Solving", "Teamwork",
        "Time Management", "Critical Thinking", "Creativity", "Adaptability"
    ],
    "business": [
        "Project Management", "Marketing", "Sales", "Finance", "Strategy",
        "Business Development", "Customer Service", "Negotiation"
    ],
    "creative": [
        "Design", "Writing", "Video Editing", "Photography", "UI/UX",
        "Content Creation", "Branding", "Storytelling"
    ]
}
