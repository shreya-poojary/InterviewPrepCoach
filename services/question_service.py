"""
Question generation and management service
"""
from typing import List, Dict, Optional, Any
from database.connection import execute_query
from services.resume_service import ResumeService
from services.jd_service import JobDescriptionService
from services.llm_service import LLMService
from config.prompts import Prompts
import json

class QuestionService:
    """Handle interview question generation and management"""
    
    @staticmethod
    def generate_questions(user_id: int, resume_id: int, jd_id: int,
                          question_type: str = 'behavioral',
                          count: int = 5,
                          set_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Generate interview questions using LLM
        
        Args:
            user_id: User ID
            resume_id: Resume ID
            jd_id: Job description ID
            question_type: Type of questions (behavioral, technical, situational)
            count: Number of questions to generate
            set_name: Optional name for the question set
            
        Returns:
            Dict with set_id and questions, or None if failed
        """
        try:
            # 1. Get resume and JD
            resume = ResumeService.get_resume_by_id(resume_id)
            jd = JobDescriptionService.get_job_description(jd_id)
            
            if not resume or not jd:
                print("[ERROR] Resume or JD not found")
                return None
            
            # 2. Get LLM provider
            llm_service = LLMService.get_instance()
            provider = llm_service.get_provider(user_id)
            
            if not provider:
                print("[ERROR] No LLM provider configured")
                return None
            
            # 3. Format prompt
            prompt = Prompts.QUESTION_GENERATION.format(
                count=count,
                difficulty='medium',
                question_type=question_type,
                resume_summary=resume.get('resume_text', '')[:2000],
                job_description=jd.get('jd_text', '')[:2000]
            )
            
            print(f"[INFO] Generating {count} {question_type} questions...")
            
            # 4. Generate with LLM using generate_json to handle text before JSON
            # Use generate_json if available, otherwise fall back to generate
            if hasattr(provider, 'generate_json'):
                response_data = provider.generate_json(prompt)
                
                # Check for errors
                if isinstance(response_data, dict) and 'error' in response_data:
                    print(f"[ERROR] LLM error: {response_data['error']}")
                    return None
                
                # Extract questions from response
                if isinstance(response_data, list):
                    questions_data = response_data
                elif isinstance(response_data, dict):
                    questions_data = response_data.get('questions', [])
                else:
                    print(f"[ERROR] Unexpected response format: {type(response_data)}")
                    return None
            else:
                # Fallback to generate() and manual parsing
                response = provider.generate(prompt)
                
                # Try to extract JSON from response (may have text before JSON)
                response_clean = response.strip()
                
                # Remove markdown code blocks if present
                if response_clean.startswith("```json"):
                    response_clean = response_clean[7:]
                if response_clean.startswith("```"):
                    response_clean = response_clean[3:]
                if response_clean.endswith("```"):
                    response_clean = response_clean[:-3]
                response_clean = response_clean.strip()
                
                # Try to find JSON array/object in the response
                # Look for first [ or { that starts valid JSON
                json_start = -1
                for i, char in enumerate(response_clean):
                    if char in ['[', '{']:
                        json_start = i
                        break
                
                if json_start > 0:
                    # Extract JSON part
                    response_clean = response_clean[json_start:]
                
                # 5. Parse JSON response
                try:
                    questions_data = json.loads(response_clean)
                    if not isinstance(questions_data, list):
                        questions_data = questions_data.get('questions', [])
                except json.JSONDecodeError as e:
                    print(f"[ERROR] Failed to parse LLM response as JSON: {e}")
                    print(f"[DEBUG] Response: {response[:500]}")
                    return None
            
            if not questions_data:
                print("[ERROR] No questions generated")
                return None
            
            # 6. Create question set
            if not set_name:
                set_name = f"{question_type.title()} Questions - {jd.get('job_title', 'Unknown')}"
            
            set_query = """
                INSERT INTO question_sets (user_id, set_name, jd_id, resume_id, question_count)
                VALUES (%s, %s, %s, %s, %s)
            """
            set_id = execute_query(
                set_query, 
                (user_id, set_name, jd_id, resume_id, len(questions_data)),
                commit=True
            )
            
            if not set_id:
                print("[ERROR] Failed to create question set")
                return None
            
            print(f"[INFO] Created question set with ID: {set_id}")
            
            # 7. Save questions
            saved_questions = []
            for q_data in questions_data:
                question_text = q_data.get('question', '') if isinstance(q_data, dict) else str(q_data)
                
                if not question_text:
                    continue
                
                question_query = """
                    INSERT INTO questions 
                    (set_id, question_text, question_type, difficulty, category, ideal_answer_points)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                question_id = execute_query(
                    question_query,
                    (set_id, 
                     question_text,
                     question_type, 
                     q_data.get('difficulty', 'medium') if isinstance(q_data, dict) else 'medium',
                     q_data.get('category', '') if isinstance(q_data, dict) else '',
                     json.dumps(q_data.get('ideal_answer_points', [])) if isinstance(q_data, dict) else '[]'),
                    commit=True
                )
                
                if question_id:
                    saved_questions.append({
                        'question_id': question_id,
                        'question': question_text,
                        'difficulty': q_data.get('difficulty', 'medium') if isinstance(q_data, dict) else 'medium',
                        'category': q_data.get('category', '') if isinstance(q_data, dict) else '',
                        'ideal_answer_points': q_data.get('ideal_answer_points', []) if isinstance(q_data, dict) else []
                    })
            
            print(f"[INFO] Saved {len(saved_questions)} questions")
            
            return {
                'set_id': set_id,
                'set_name': set_name,
                'questions': saved_questions,
                'count': len(saved_questions)
            }
            
        except Exception as e:
            print(f"[ERROR] Error generating questions: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def get_question_sets(user_id: int, limit: int = 20) -> List[Dict]:
        """Get user's question sets"""
        query = """
        SELECT qs.*, jd.job_title, jd.company_name 
        FROM question_sets qs
        LEFT JOIN job_descriptions jd ON qs.jd_id = jd.jd_id
        WHERE qs.user_id = %s 
        ORDER BY qs.created_at DESC
        LIMIT %s
        """
        return execute_query(query, (user_id, limit), fetch_all=True) or []
    
    @staticmethod
    def get_questions(set_id: int) -> List[Dict]:
        """Get questions in a set"""
        query = """
        SELECT * FROM questions 
        WHERE set_id = %s 
        ORDER BY question_id ASC
        """
        return execute_query(query, (set_id,), fetch_all=True) or []
    
    @staticmethod
    def get_question_set_with_questions(set_id: int) -> Optional[Dict]:
        """Get a question set with all its questions"""
        set_query = "SELECT * FROM question_sets WHERE set_id = %s"
        question_set = execute_query(set_query, (set_id,), fetch_one=True)
        
        if not question_set:
            return None
        
        questions = QuestionService.get_questions(set_id)
        question_set['questions'] = questions
        
        return question_set
    
    @staticmethod
    def delete_question_set(set_id: int) -> bool:
        """Delete a question set and all its questions"""
        try:
            # Questions will be deleted automatically due to CASCADE
            query = "DELETE FROM question_sets WHERE set_id = %s"
            execute_query(query, (set_id,), commit=True)
            return True
        except Exception as e:
            print(f"Error deleting question set: {e}")
            return False
