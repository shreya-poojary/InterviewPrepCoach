"""
JSearch API integration service for job opportunities
"""
import os
import json
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv
from database.connection import execute_query

load_dotenv()

class JSearchService:
    """Handle JSearch API integration"""
    
    API_URL = "https://jsearch.p.rapidapi.com/search"
    API_KEY = os.getenv('JSEARCH_API_KEY', '')
    
    @staticmethod
    def search_jobs(user_id: int, query: str, location: str = "", 
                   remote_only: bool = False, num_pages: int = 1) -> List[Dict]:
        """
        Search for jobs using JSearch API
        
        Args:
            user_id: User ID
            query: Search query (job title, skills, etc.)
            location: Location filter
            remote_only: Only return remote jobs
            num_pages: Number of pages to fetch
            
        Returns:
            List of job listings
        """
        try:
            # Save search history
            execute_query(
                """INSERT INTO jsearch_history 
                   (user_id, search_query, location, remote_only, results_count) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (user_id, query, location, remote_only, 0),
                commit=True
            )
            
            if not JSearchService.API_KEY:
                # Return mock data if no API key
                return JSearchService._get_mock_jobs(query)
            
            headers = {
                "X-RapidAPI-Key": JSearchService.API_KEY,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
            }
            
            params = {
                "query": query,
                "num_pages": str(num_pages)
            }
            
            if location:
                params["location"] = location
            
            if remote_only:
                params["remote_jobs_only"] = "true"
            
            response = requests.get(JSearchService.API_URL, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            jobs = data.get('data', [])
            
            # Save jobs to database
            saved_jobs = []
            for job in jobs:
                job_data = JSearchService._save_job(user_id, job)
                if job_data:
                    saved_jobs.append(job_data)
            
            # Update search history with results count
            execute_query(
                """UPDATE jsearch_history 
                   SET results_count = %s 
                   WHERE user_id = %s 
                   ORDER BY searched_at DESC LIMIT 1""",
                (len(saved_jobs), user_id),
                commit=True
            )
            
            return saved_jobs
            
        except Exception as e:
            print(f"Error searching jobs: {e}")
            return JSearchService._get_mock_jobs(query)
    
    @staticmethod
    def _save_job(user_id: int, job_data: Dict) -> Optional[Dict]:
        """Save job to database"""
        try:
            # Check if job already exists
            existing = execute_query(
                "SELECT id FROM jsearch_jobs WHERE job_id = %s AND user_id = %s",
                (job_data.get('job_id'), user_id),
                fetch_one=True
            )
            
            if existing:
                return JSearchService.get_job_by_id(existing['id'])
            
            # Extract salary info
            salary_min = None
            salary_max = None
            if job_data.get('job_salary_min'):
                salary_min = float(job_data['job_salary_min'])
            if job_data.get('job_salary_max'):
                salary_max = float(job_data['job_salary_max'])
            
            query = """
            INSERT INTO jsearch_jobs 
            (user_id, job_id, title, company, location, description, 
             salary_min, salary_max, is_remote, job_url, apply_url, 
             posted_date, job_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            job_id = execute_query(
                query,
                (user_id, job_data.get('job_id'), job_data.get('job_title'),
                 job_data.get('employer_name'), job_data.get('job_city'),
                 job_data.get('job_description'), salary_min, salary_max,
                 job_data.get('job_is_remote', False),
                 job_data.get('job_apply_link'),
                 job_data.get('job_apply_link'),
                 job_data.get('job_posted_at_date'),
                 json.dumps(job_data)),
                commit=True
            )
            
            return JSearchService.get_job_by_id(job_id)
            
        except Exception as e:
            print(f"Error saving job: {e}")
            return None
    
    @staticmethod
    def get_job_by_id(job_id: int) -> Optional[Dict]:
        """Get job by ID"""
        query = "SELECT * FROM jsearch_jobs WHERE job_id = %s"
        return execute_query(query, (job_id,), fetch_one=True)
    
    @staticmethod
    def get_saved_jobs(user_id: int) -> List[Dict]:
        """Get user's saved jobs"""
        query = """
        SELECT * FROM jsearch_jobs 
        WHERE user_id = %s AND is_saved = TRUE 
        ORDER BY created_at DESC
        """
        return execute_query(query, (user_id,), fetch_all=True) or []
    
    @staticmethod
    def save_job(job_id: int, is_saved: bool = True) -> bool:
        """Mark job as saved"""
        try:
            execute_query(
                "UPDATE jsearch_jobs SET is_saved = %s WHERE job_id = %s",
                (is_saved, job_id),
                commit=True
            )
            return True
        except Exception as e:
            print(f"Error saving job: {e}")
            return False
    
    @staticmethod
    def calculate_compatibility(user_id: int, job_id: int) -> float:
        """
        Calculate compatibility score between user's resume and job
        
        Args:
            user_id: User ID
            job_id: Job ID
            
        Returns:
            Compatibility score (0-100)
        """
        try:
            # Get user's resume skills
            from services.resume_service import ResumeService
            resume = ResumeService.get_active_resume(user_id)
            
            if not resume or not resume.get('parsed_data'):
                return 0.0
            
            resume_data = json.loads(resume['parsed_data'])
            resume_skills = set(skill.lower() for skill in resume_data.get('skills', []))
            
            # Get job requirements
            job = JSearchService.get_job_by_id(job_id)
            if not job or not job.get('description'):
                return 0.0
            
            # Extract skills from job description
            from core.text_extractor import TextExtractor
            job_skills = set(skill.lower() for skill in TextExtractor.extract_skills(job['description']))
            
            if not job_skills:
                return 50.0  # Default if no skills found
            
            # Calculate match percentage
            matched_skills = resume_skills.intersection(job_skills)
            score = (len(matched_skills) / len(job_skills)) * 100
            
            # Update in database
            execute_query(
                "UPDATE jsearch_jobs SET compatibility_score = %s WHERE job_id = %s",
                (score, job_id),
                commit=True
            )
            
            return round(score, 2)
            
        except Exception as e:
            print(f"Error calculating compatibility: {e}")
            return 0.0
    
    @staticmethod
    def _get_mock_jobs(query: str) -> List[Dict]:
        """Get mock jobs for demo purposes"""
        return [
            {
                'id': 1,
                'title': f'{query} - Senior',
                'company': 'TechCorp Inc.',
                'location': 'San Francisco, CA',
                'description': f'Looking for an experienced {query} professional...',
                'salary_min': 120000,
                'salary_max': 180000,
                'is_remote': True,
                'job_url': 'https://example.com/job1',
                'compatibility_score': 85.0
            },
            {
                'id': 2,
                'title': f'{query}',
                'company': 'StartupHub',
                'location': 'Remote',
                'description': f'Join our team as a {query}...',
                'salary_min': 90000,
                'salary_max': 130000,
                'is_remote': True,
                'job_url': 'https://example.com/job2',
                'compatibility_score': 75.0
            },
            {
                'id': 3,
                'title': f'Junior {query}',
                'company': 'BigTech Corp',
                'location': 'New York, NY',
                'description': f'Entry level position for {query}...',
                'salary_min': 70000,
                'salary_max': 95000,
                'is_remote': False,
                'job_url': 'https://example.com/job3',
                'compatibility_score': 65.0
            }
        ]
