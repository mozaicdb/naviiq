# One time script to upload career categories to MongoDB
# Run this once to populate the career_categories collection
# After running you can delete this file or keep for reference

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = "naviiq_db"

# Career categories data
CAREER_DATA = [
    {
        "category": "Software Development",
        "description": "Building applications, websites, and software systems",
        "roles": [
            "Frontend Developer", "Backend Developer", "Full-Stack Developer",
            "Mobile App Developer", "Android Developer", "iOS Developer",
            "Game Developer", "Software Engineer", "API Developer"
        ],
        "key_skills": ["HTML/CSS", "JavaScript", "Python", "Git", "Databases"],
        "entry_stack": ["HTML", "CSS", "JavaScript", "Python", "Git"],
        "time_to_first_job": "6 to 12 months",
        "market": "Both local and global",
        "offline_friendly": True
    },
    {
        "category": "Artificial Intelligence",
        "description": "Building AI systems, machine learning models, and intelligent agents",
        "roles": [
            "AI Engineer", "Machine Learning Engineer", "Generative AI Engineer",
            "AI Agent Developer", "Prompt Engineer", "RAG Engineer",
            "NLP Engineer", "Computer Vision Engineer"
        ],
        "key_skills": ["Python", "Machine Learning", "LangChain", "LangGraph", "APIs"],
        "entry_stack": ["Python", "NumPy", "Pandas", "Scikit-learn", "HuggingFace"],
        "time_to_first_job": "9 to 18 months",
        "market": "Primarily global",
        "offline_friendly": False
    },
    {
        "category": "Data",
        "description": "Collecting, analyzing, and interpreting data to drive decisions",
        "roles": [
            "Data Analyst", "Data Scientist", "Data Engineer",
            "Business Intelligence Analyst", "Analytics Engineer",
            "Database Administrator"
        ],
        "key_skills": ["Python", "SQL", "Excel", "Power BI", "Statistics"],
        "entry_stack": ["Excel", "SQL", "Python", "Pandas", "Matplotlib"],
        "time_to_first_job": "6 to 12 months",
        "market": "Both local and global",
        "offline_friendly": True
    },
    {
        "category": "Cloud and DevOps",
        "description": "Managing infrastructure, deployments, and cloud systems",
        "roles": [
            "Cloud Engineer", "DevOps Engineer", "Site Reliability Engineer",
            "Platform Engineer", "Infrastructure Engineer", "Kubernetes Engineer"
        ],
        "key_skills": ["Linux", "Docker", "AWS/Azure/GCP", "Python", "CI/CD"],
        "entry_stack": ["Linux", "Git", "Docker", "Python", "Alibaba Cloud"],
        "time_to_first_job": "9 to 15 months",
        "market": "Primarily global",
        "offline_friendly": False
    },
    {
        "category": "Cybersecurity",
        "description": "Protecting systems, networks, and data from attacks",
        "roles": [
            "Cybersecurity Analyst", "Ethical Hacker", "Penetration Tester",
            "SOC Analyst", "Network Security Engineer", "Digital Forensics Specialist"
        ],
        "key_skills": ["Networking", "Linux", "Python", "Security Tools", "Risk Assessment"],
        "entry_stack": ["Linux", "Networking basics", "Python", "Kali Linux"],
        "time_to_first_job": "9 to 18 months",
        "market": "Both local and global",
        "offline_friendly": True
    },
    {
        "category": "Design",
        "description": "Creating visual experiences, interfaces, and brand identities",
        "roles": [
            "UI Designer", "UX Designer", "Product Designer",
            "Graphic Designer", "Brand Designer", "Motion Designer"
        ],
        "key_skills": ["Figma", "Adobe XD", "User Research", "Prototyping", "Visual Design"],
        "entry_stack": ["Figma", "Canva", "Adobe Photoshop", "User research basics"],
        "time_to_first_job": "3 to 9 months",
        "market": "Both local and global",
        "offline_friendly": True
    },
    {
        "category": "Digital Marketing and Creator Economy",
        "description": "Growing brands online through content, ads, and social media",
        "roles": [
            "Digital Marketer", "Content Creator", "SEO Specialist",
            "Social Media Manager", "Growth Marketer", "AI Content Creator"
        ],
        "key_skills": ["Content Creation", "SEO", "Social Media", "Analytics", "Copywriting"],
        "entry_stack": ["Canva", "Google Analytics", "Meta Ads", "WordPress", "Email tools"],
        "time_to_first_job": "3 to 6 months",
        "market": "Both local and global",
        "offline_friendly": True
    },
    {
        "category": "Product and Management",
        "description": "Leading teams and products from idea to launch",
        "roles": [
            "Product Manager", "Technical Product Manager", "Project Manager",
            "Scrum Master", "Business Analyst"
        ],
        "key_skills": ["Communication", "Agile", "Data Analysis", "Roadmapping", "Stakeholder Management"],
        "entry_stack": ["Notion", "Jira", "Figma basics", "SQL basics", "Agile methodology"],
        "time_to_first_job": "12 to 24 months",
        "market": "Both local and global",
        "offline_friendly": True
    },
    {
        "category": "Blockchain and Web3",
        "description": "Building decentralized applications and smart contracts",
        "roles": [
            "Blockchain Developer", "Smart Contract Developer",
            "Web3 Engineer", "Blockchain Architect"
        ],
        "key_skills": ["Solidity", "JavaScript", "Python", "Ethereum", "Web3.js"],
        "entry_stack": ["JavaScript", "Solidity", "Hardhat", "Metamask", "Ethereum basics"],
        "time_to_first_job": "12 to 18 months",
        "market": "Primarily global",
        "offline_friendly": False
    },
    {
        "category": "Freelance and Entrepreneurship",
        "description": "Building your own business or offering services independently",
        "roles": [
            "Freelance Developer", "Freelance Designer", "SaaS Founder",
            "Tech Consultant", "Agency Owner", "Startup Founder"
        ],
        "key_skills": ["Any technical skill", "Business development", "Marketing", "Client management"],
        "entry_stack": ["Any core technical skill", "LinkedIn", "Upwork", "Basic business knowledge"],
        "time_to_first_job": "1 to 6 months",
        "market": "Both local and global",
        "offline_friendly": True
    }
]

async def upload_career_data():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db["career_categories"]

    # Clear existing data
    await collection.delete_many({})
    print("Cleared existing career categories")

    # Upload new data
    result = await collection.insert_many(CAREER_DATA)
    print(f"Uploaded {len(result.inserted_ids)} career categories successfully")

    # Confirm
    count = await collection.count_documents({})
    print(f"Total career categories in database: {count}")

    client.close()
    print("Done. Career data is ready.")

if __name__ == "__main__":
    asyncio.run(upload_career_data())