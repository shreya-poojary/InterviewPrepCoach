"""Compatibility analysis service - analyzes resume vs JD fit"""

from typing import Optional, Dict, Any
from database import DatabaseManager
from services.llm_service import LLMService
from services.resume_service import ResumeService
from services.jd_service import JobDescriptionService
from config.prompts import Prompts
import json

class CompatibilityService:
    """Analyzes compatibility between resume and job description"""
    
    @staticmethod
    def analyze_compatibility(user_id: int, resume_id: int, jd_id: int) -> Optional[Dict[str, Any]]:
        """Analyze compatibility between resume and JD
        
        Args:
            user_id: User ID
            resume_id: Resume ID
            jd_id: Job description ID
            
        Returns:
            Analysis results dict
        """
        try:
            # Get resume
            with DatabaseManager.get_cursor() as cursor:
                cursor.execute("""
                    SELECT resume_text FROM resumes
                    WHERE resume_id = %s AND user_id = %s
                """, (resume_id, user_id))
                resume_result = cursor.fetchone()
                
                if not resume_result:
                    return {"error": "Resume not found"}
                
                # Get JD
                cursor.execute("""
                    SELECT jd_text FROM job_descriptions
                    WHERE jd_id = %s
                """, (jd_id,))
                jd_result = cursor.fetchone()
                
                if not jd_result:
                    return {"error": "Job description not found"}
            
            resume_text = resume_result['resume_text']
            jd_text = jd_result['jd_text']
            
            print(f"[INFO] Resume text length: {len(resume_text)}, JD text length: {len(jd_text)}")
            
            # Call LLM for analysis
            llm_service = LLMService.get_instance()
            provider = llm_service.get_provider(user_id)
            
            if not provider:
                print("[ERROR] No LLM provider available")
                return {"error": "No LLM provider configured. Please configure an LLM in Settings."}
            
            print(f"[INFO] Using LLM provider: {type(provider).__name__}")
            
            prompt = Prompts.PROFILE_ANALYSIS.format(
                resume_text=resume_text,
                job_description=jd_text
            )
            
            print(f"[INFO] Calling LLM for analysis...")
            try:
                analysis = provider.generate_json(prompt)
                print(f"[INFO] LLM analysis complete: {analysis}")
            except Exception as llm_error:
                print(f"[ERROR] LLM generation failed: {llm_error}")
                import traceback
                traceback.print_exc()
                return {"error": f"LLM analysis failed: {str(llm_error)}"}
            
            if "error" in analysis:
                print(f"[ERROR] Analysis returned error: {analysis.get('error')}")
                return analysis
            
            if not analysis:
                return {"error": "Analysis returned empty result"}
            
            # Save to database
            # Handle both 'suggestions' and 'improvement_suggestions' keys
            suggestions = analysis.get('suggestions', []) or analysis.get('improvement_suggestions', [])
            
            with DatabaseManager.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO compatibility_analyses
                    (user_id, resume_id, jd_id, compatibility_score, matched_skills,
                     missing_skills, missing_qualifications, improvement_suggestions)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, resume_id, jd_id,
                      analysis.get('compatibility_score'),
                      json.dumps(analysis.get('matched_skills', [])),
                      json.dumps(analysis.get('missing_skills', [])),
                      json.dumps(analysis.get('missing_qualifications', [])),
                      json.dumps(suggestions)))
                
                analysis['analysis_id'] = cursor.lastrowid
            
            # Ensure 'suggestions' key exists in returned analysis
            if 'suggestions' not in analysis and suggestions:
                analysis['suggestions'] = suggestions
                
                analysis['analysis_id'] = cursor.lastrowid
            
            return analysis
        
        except Exception as e:
            print(f"Error analyzing compatibility: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def get_recent_analyses(user_id: int, limit: int = 10) -> list:
        """Get recent compatibility analyses
        
        Args:
            user_id: User ID
            limit: Number of results
            
        Returns:
            List of analyses
        """
        try:
            with DatabaseManager.get_cursor() as cursor:
                cursor.execute("""
                    SELECT ca.*, r.file_name as resume_name,
                           jd.company_name, jd.job_title
                    FROM compatibility_analyses ca
                    JOIN resumes r ON ca.resume_id = r.resume_id
                    JOIN job_descriptions jd ON ca.jd_id = jd.jd_id
                    WHERE ca.user_id = %s
                    ORDER BY ca.analyzed_at DESC
                    LIMIT %s
                """, (user_id, limit))
                
                return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching analyses: {e}")
            return []
    
    @staticmethod
    def get_analysis_by_id(analysis_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific analysis by ID
        
        Args:
            analysis_id: Analysis ID
            user_id: User ID (for security)
            
        Returns:
            Analysis dict or None
        """
        try:
            with DatabaseManager.get_cursor() as cursor:
                cursor.execute("""
                    SELECT ca.*, r.file_name as resume_name,
                           jd.company_name, jd.job_title
                    FROM compatibility_analyses ca
                    JOIN resumes r ON ca.resume_id = r.resume_id
                    JOIN job_descriptions jd ON ca.jd_id = jd.jd_id
                    WHERE ca.analysis_id = %s AND ca.user_id = %s
                """, (analysis_id, user_id))
                
                result = cursor.fetchone()
                if not result:
                    return None
                
                # Parse JSON fields
                analysis = dict(result)
                if analysis.get('matched_skills'):
                    try:
                        analysis['matched_skills'] = json.loads(analysis['matched_skills'])
                    except:
                        analysis['matched_skills'] = []
                
                if analysis.get('missing_skills'):
                    try:
                        analysis['missing_skills'] = json.loads(analysis['missing_skills'])
                    except:
                        analysis['missing_skills'] = []
                
                if analysis.get('missing_qualifications'):
                    try:
                        analysis['missing_qualifications'] = json.loads(analysis['missing_qualifications'])
                    except:
                        analysis['missing_qualifications'] = []
                
                # Parse suggestions
                suggestions_text = analysis.get('improvement_suggestions', '')
                if suggestions_text:
                    try:
                        # Try parsing as JSON first
                        analysis['suggestions'] = json.loads(suggestions_text)
                    except:
                        # If not JSON, split by newlines
                        analysis['suggestions'] = [s.strip() for s in suggestions_text.split('\n') if s.strip()]
                else:
                    analysis['suggestions'] = []
                
                return analysis
        except Exception as e:
            print(f"Error fetching analysis: {e}")
            return None

