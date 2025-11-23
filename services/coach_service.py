"""
Career coach service - AI-powered career coaching
"""
import json
from typing import List, Dict, Optional
from database.connection import execute_query
from ai.provider_factory import ProviderFactory
from config.prompts import CAREER_COACH_SYSTEM_PROMPT, QUICK_ADVICE_PROMPTS

class CoachService:
    """Handle career coach operations"""
    
    @staticmethod
    def create_conversation(user_id: int, title: str = "New Conversation") -> Optional[int]:
        """Create a new conversation"""
        try:
            query = """
            INSERT INTO coach_conversations (user_id, title) 
            VALUES (%s, %s)
            """
            return execute_query(query, (user_id, title), commit=True)
        except Exception as e:
            print(f"Error creating conversation: {e}")
            return None
    
    @staticmethod
    def get_conversation(conversation_id: int) -> Optional[Dict]:
        """Get conversation by ID"""
        query = "SELECT * FROM coach_conversations WHERE conversation_id = %s"
        return execute_query(query, (conversation_id,), fetch_one=True)
    
    @staticmethod
    def get_conversations(user_id: int, limit: int = 20) -> List[Dict]:
        """Get user's conversations"""
        query = """
        SELECT * FROM coach_conversations 
        WHERE user_id = %s AND is_archived = FALSE 
        ORDER BY last_message_at DESC 
        LIMIT %s
        """
        return execute_query(query, (user_id, limit), fetch_all=True) or []
    
    @staticmethod
    def get_messages(conversation_id: int) -> List[Dict]:
        """Get messages in a conversation"""
        query = """
        SELECT * FROM coach_messages 
        WHERE conversation_id = %s 
        ORDER BY created_at ASC
        """
        return execute_query(query, (conversation_id,), fetch_all=True) or []
    
    @staticmethod
    def add_message(conversation_id: int, role: str, content: str) -> Optional[int]:
        """Add a message to conversation"""
        try:
            query = """
            INSERT INTO coach_messages (conversation_id, role, content) 
            VALUES (%s, %s, %s)
            """
            message_id = execute_query(query, (conversation_id, role, content), commit=True)
            
            # Update conversation
            execute_query(
                """UPDATE coach_conversations 
                   SET message_count = message_count + 1, 
                       last_message_at = CURRENT_TIMESTAMP 
                   WHERE conversation_id = %s""",
                (conversation_id,),
                commit=True
            )
            
            return message_id
        except Exception as e:
            print(f"Error adding message: {e}")
            return None
    
    @staticmethod
    def get_user_context(user_id: int) -> str:
        """Get user context for personalized coaching"""
        try:
            context_parts = []
            
            # Get resume info
            from services.resume_service import ResumeService
            resume = ResumeService.get_active_resume(user_id)
            if resume and resume.get('parsed_data'):
                parsed = json.loads(resume['parsed_data'])
                context_parts.append(f"Skills: {', '.join(parsed.get('skills', []))}")
                if parsed.get('years_experience'):
                    context_parts.append(f"Experience: {parsed['years_experience']} years")
            
            # Get recent job applications
            recent_jobs = execute_query(
                """SELECT title, company FROM job_descriptions 
                   WHERE user_id = %s 
                   ORDER BY created_at DESC LIMIT 3""",
                (user_id,),
                fetch_all=True
            )
            
            if recent_jobs:
                jobs_list = [f"{j['title']} at {j['company']}" for j in recent_jobs]
                context_parts.append(f"Recent job interests: {', '.join(jobs_list)}")
            
            return "\n".join(context_parts) if context_parts else "No context available yet."
            
        except Exception as e:
            print(f"Error getting user context: {e}")
            return "No context available."
    
    @staticmethod
    def chat(user_id: int, conversation_id: int, user_message: str, 
            provider_settings: Dict) -> Optional[str]:
        """
        Send a message and get AI response
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
            user_message: User's message
            provider_settings: LLM provider settings
            
        Returns:
            AI response or None
        """
        try:
            # Add user message
            CoachService.add_message(conversation_id, 'user', user_message)
            
            # Get conversation history
            messages = CoachService.get_messages(conversation_id)
            
            # Build message history for LLM
            llm_messages = []
            
            # Add system prompt with context
            user_context = CoachService.get_user_context(user_id)
            system_prompt = CAREER_COACH_SYSTEM_PROMPT.format(user_context=user_context)
            llm_messages.append({"role": "system", "content": system_prompt})
            
            # Add conversation history
            for msg in messages:
                if msg['role'] in ['user', 'assistant']:
                    llm_messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })
            
            # Get LLM provider
            provider = ProviderFactory.create_provider(
                provider_name=provider_settings['provider'],
                api_key=provider_settings['api_key'],
                model=provider_settings['model'],
                temperature=provider_settings.get('temperature', 0.7),
                max_tokens=provider_settings.get('max_tokens', 2000)
            )
            
            # Generate response
            response = provider.chat(llm_messages)
            
            # Add assistant response
            CoachService.add_message(conversation_id, 'assistant', response)
            
            return response
            
        except Exception as e:
            print(f"Error in chat: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def get_quick_advice_prompt(advice_type: str, target_role: str = "your target role",
                                industry: str = "your industry") -> str:
        """Get a quick advice prompt"""
        prompt_template = QUICK_ADVICE_PROMPTS.get(advice_type, "")
        return prompt_template.format(target_role=target_role, industry=industry)
