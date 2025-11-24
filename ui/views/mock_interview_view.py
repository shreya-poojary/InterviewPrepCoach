from typing import Dict, List, Optional
"""Mock Interview View - Comprehensive practice hub"""

import json
from typing import Dict, List, Optional
import flet as ft
from datetime import datetime
from services.mock_interview_service import MockInterviewService
from services.question_service import QuestionService
from services.resume_service import ResumeService
from services.jd_service import JobDescriptionService
from services.practice_service import PracticeService
from core.auth import SessionManager
from ui.styles.theme import AppTheme

class MockInterviewView:
    """Mock Interview Practice Hub"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.user_id = SessionManager.get_user_id()
        self.current_session_id = None
        self.current_session = None
        self.session_questions = []
        self.current_question_index = 0
        self.session_config = {}
        
        # UI state
        self.setup_wizard_active = False
        self.live_session_active = False
        self.analytics_active = False
        
    def build(self) -> ft.Container:
        """Build mock interview view"""
        # Header
        header = ft.Container(
            content=ft.Column([
                ft.Text("🎯 Mock Interview Hub", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("Comprehensive interview practice with AI feedback", size=12, color="grey")
            ], spacing=4),
            padding=ft.padding.only(left=20, top=15, bottom=10)
        )
        
        # Main action buttons
        action_buttons = ft.Row([
            ft.ElevatedButton(
                "➕ New Mock Interview",
                icon=ft.Icons.ADD_CIRCLE,
                on_click=self._show_setup_wizard,
                style=ft.ButtonStyle(
                    bgcolor=AppTheme.PRIMARY,
                    color="white",
                    padding=15
                )
            ),
            ft.ElevatedButton(
                "📊 View Analytics",
                icon=ft.Icons.ANALYTICS,
                on_click=self._show_analytics,
                style=ft.ButtonStyle(
                    bgcolor=AppTheme.INFO,
                    color="white",
                    padding=15
                )
            ),
            ft.ElevatedButton(
                "📚 Practice Library",
                icon=ft.Icons.LIBRARY_BOOKS,
                on_click=self._show_library,
                style=ft.ButtonStyle(
                    bgcolor=AppTheme.SECONDARY,
                    color="white",
                    padding=15
                )
            )
        ], spacing=15, wrap=True)
        
        # Content area (will show setup wizard, live session, or library)
        self.content_area = ft.Container(
            content=self._build_welcome_screen(),
            expand=True,
            padding=20
        )
        
        # Main layout
        return ft.Container(
            content=ft.Column([
                header,
                ft.Divider(),
                action_buttons,
                ft.Divider(),
                self.content_area
            ], spacing=15, scroll=ft.ScrollMode.AUTO, expand=True),
            padding=10,
            expand=True
        )
    
    def _build_welcome_screen(self) -> ft.Column:
        """Build welcome screen"""
        return ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.RECORD_VOICE_OVER, size=80, color=AppTheme.PRIMARY),
                    ft.Text("Welcome to Mock Interview Hub", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("Practice realistic interviews with AI-powered feedback", size=14, color="grey"),
                    ft.Divider(),
                    ft.Text("Features:", size=18, weight=ft.FontWeight.BOLD),
                    ft.Column([
                        ft.Text("• Multiple interview formats (Traditional, Technical, Behavioral, Case)", size=12),
                        ft.Text("• Written, Audio, and Video response modes", size=12),
                        ft.Text("• Real-time AI evaluation with detailed feedback", size=12),
                        ft.Text("• Progress tracking and analytics", size=12),
                        ft.Text("• Practice library with searchable history", size=12)
                    ], spacing=5)
                ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40,
                alignment=ft.alignment.center,
                expand=True
            )
        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    def _show_setup_wizard(self, e):
        """Show session setup wizard"""
        self.setup_wizard_active = True
        self.content_area.content = self._build_setup_wizard()
        self.page.update()
    
    def _build_setup_wizard(self) -> ft.Column:
        """Build session setup wizard"""
        # Step 1: Format Selection
        format_options = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="traditional", label="📋 Traditional Interview"),
                ft.Radio(value="technical", label="💻 Technical Interview"),
                ft.Radio(value="behavioral", label="🧠 Behavioral Interview (STAR method)"),
                ft.Radio(value="case", label="📊 Case Study Interview")
            ], spacing=10),
            value="traditional"
        )
        
        # Step 2: Question Source
        question_source_options = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="generated", label="✨ Auto-generate from Resume & JD"),
                ft.Radio(value="set", label="📚 Use Existing Question Set"),
                ft.Radio(value="custom", label="✏️ Custom Questions (Coming Soon)")
            ], spacing=10),
            value="generated"
        )
        
        # Get available question sets
        question_sets = QuestionService.get_question_sets(self.user_id) or []
        question_set_dropdown = ft.Dropdown(
            label="Select Question Set",
            options=[
                ft.dropdown.Option(str(qs['set_id']), qs.get('set_name', 'Unknown'))
                for qs in question_sets
            ],
            disabled=len(question_sets) == 0,
            visible=False
        )
        
        # Get resumes and JDs
        resumes = ResumeService.get_all_resumes(self.user_id) or []
        jds = JobDescriptionService.get_user_job_descriptions(self.user_id) or []
        
        resume_dropdown = ft.Dropdown(
            label="Select Resume",
            options=[
                ft.dropdown.Option(str(r['resume_id']), r.get('file_name', 'Resume'))
                for r in resumes
            ],
            disabled=len(resumes) == 0
        )
        
        jd_dropdown = ft.Dropdown(
            label="Select Job Description",
            options=[
                ft.dropdown.Option(str(jd['jd_id']), jd.get('job_title', 'Job'))
                for jd in jds
            ],
            disabled=len(jds) == 0
        )
        
        # Step 3: Configuration
        session_name_field = ft.TextField(
            label="Session Name",
            hint_text="e.g., Amazon SDE Behavioral Practice",
            value=""
        )
        
        num_questions_slider = ft.Slider(
            min=3, max=15, value=5, divisions=12,
            label="{value} questions"
        )
        num_questions_text = ft.Text("5 questions", size=14, weight=ft.FontWeight.BOLD)
        
        difficulty_dropdown = ft.Dropdown(
            label="Difficulty Level",
            options=[
                ft.dropdown.Option("easy", "Easy"),
                ft.dropdown.Option("medium", "Medium"),
                ft.dropdown.Option("hard", "Hard")
            ],
            value="medium"
        )
        
        time_per_question_field = ft.TextField(
            label="Time per Question (seconds)",
            value="120",
            width=200
        )
        
        prep_time_field = ft.TextField(
            label="Prep Time (seconds)",
            value="30",
            width=200
        )
        
        feedback_mode_dropdown = ft.Dropdown(
            label="Feedback Mode",
            options=[
                ft.dropdown.Option("post_session", "After Session"),
                ft.dropdown.Option("per_question", "After Each Question"),
                ft.dropdown.Option("real_time", "Real-time Hints")
            ],
            value="post_session"
        )
        
        # Update slider text
        def update_slider_text(e):
            num_questions_text.value = f"{int(e.control.value)} questions"
            self.page.update()
        
        num_questions_slider.on_change = update_slider_text
        
        # Show/hide question set dropdown based on source
        def on_source_change(e):
            question_set_dropdown.visible = (question_source_options.value == "set")
            self.page.update()
        
        question_source_options.on_change = on_source_change
        
        # Create session button
        def create_session(e):
            if not session_name_field.value:
                self._show_error("Please enter a session name")
                return
            
            if question_source_options.value == "generated":
                if not resume_dropdown.value or not jd_dropdown.value:
                    self._show_error("Please select both resume and job description")
                    return
            elif question_source_options.value == "set":
                if not question_set_dropdown.value:
                    self._show_error("Please select a question set")
                    return
            
            config = {
                'num_questions': int(num_questions_slider.value),
                'difficulty': difficulty_dropdown.value,
                'time_per_question': int(time_per_question_field.value),
                'prep_time': int(prep_time_field.value),
                'feedback_mode': feedback_mode_dropdown.value
            }
            
            session_id = MockInterviewService.create_session(
                user_id=self.user_id,
                session_name=session_name_field.value,
                format_type=format_options.value,
                question_source=question_source_options.value,
                question_set_id=int(question_set_dropdown.value) if question_set_dropdown.value else None,
                resume_id=int(resume_dropdown.value) if resume_dropdown.value else None,
                jd_id=int(jd_dropdown.value) if jd_dropdown.value else None,
                config=config
            )
            
            if session_id:
                self.current_session_id = session_id
                self.session_config = config
                self._start_live_session()
            else:
                self._show_error("Failed to create session")
        
        create_button = ft.ElevatedButton(
            "🚀 Start Mock Interview",
            icon=ft.Icons.PLAY_ARROW,
            on_click=create_session,
            style=ft.ButtonStyle(
                bgcolor=AppTheme.SUCCESS,
                color="white",
                padding=15
            )
        )
        
        # Wizard content
        wizard_content = ft.Column([
            ft.Text("Session Setup", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.Text("Step 1: Interview Format", size=18, weight=ft.FontWeight.BOLD),
            format_options,
            ft.Divider(),
            
            ft.Text("Step 2: Question Source", size=18, weight=ft.FontWeight.BOLD),
            question_source_options,
            question_set_dropdown,
            ft.Row([resume_dropdown, jd_dropdown], spacing=20, wrap=True),
            ft.Divider(),
            
            ft.Text("Step 3: Configuration", size=18, weight=ft.FontWeight.BOLD),
            session_name_field,
            ft.Row([
                ft.Column([
                    num_questions_text,
                    num_questions_slider
                ]),
                difficulty_dropdown
            ], spacing=20, wrap=True),
            ft.Row([
                time_per_question_field,
                prep_time_field,
                feedback_mode_dropdown
            ], spacing=20, wrap=True),
            ft.Divider(),
            
            create_button
        ], spacing=15, scroll=ft.ScrollMode.AUTO)
        
        return wizard_content
    
    def _start_live_session(self):
        """Start the live interview session"""
        if not self.current_session_id:
            return
        
        self.live_session_active = True
        self.setup_wizard_active = False
        
        # Start session in database
        MockInterviewService.start_session(self.current_session_id)
        
        # Get session questions
        self.session_questions = MockInterviewService.get_session_questions(self.current_session_id)
        self.current_question_index = 0
        
        # Load session
        self.current_session = MockInterviewService.get_session(self.current_session_id)
        if self.current_session:
            config_str = self.current_session.get('config', '{}')
            try:
                self.session_config = json.loads(config_str) if isinstance(config_str, str) else config_str
            except:
                self.session_config = {}
        
        self.content_area.content = self._build_live_session()
        self.page.update()
    
    def _build_live_session(self) -> ft.Column:
        """Build live session interface"""
        # Reload questions if needed
        if not self.session_questions and self.current_session_id:
            self.session_questions = MockInterviewService.get_session_questions(self.current_session_id)
        
        if not self.session_questions:
            return ft.Column([
                ft.Text("No questions available", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("Please ensure you have selected a question set or have resume/JD for generation", size=12, color="grey"),
                ft.ElevatedButton("Back to Setup", on_click=lambda e: self._reset_view())
            ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        if self.current_question_index >= len(self.session_questions):
            # Session complete
            return ft.Column([
                ft.Text("✅ Session Complete!", size=24, weight=ft.FontWeight.BOLD, color=AppTheme.SUCCESS),
                ft.Text(f"You completed {len(self.session_questions)} questions", size=16),
                ft.ElevatedButton(
                    "View Results",
                    icon=ft.Icons.ANALYTICS,
                    on_click=lambda e: self._complete_session(),
                    style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color="white")
                ),
                ft.ElevatedButton("Back to Hub", on_click=lambda e: self._reset_view())
            ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        current_question = self.session_questions[self.current_question_index]
        total_questions = len(self.session_questions)
        
        # Progress indicator
        progress_text = ft.Text(
            f"Question {self.current_question_index + 1} of {total_questions}",
            size=16,
            weight=ft.FontWeight.BOLD
        )
        
        progress_bar = ft.ProgressBar(
            value=(self.current_question_index + 1) / total_questions,
            width=400
        )
        
        # Question display
        question_text = ft.Container(
            content=ft.Column([
                ft.Text("Question:", size=14, weight=ft.FontWeight.BOLD, color="grey"),
                ft.Text(
                    current_question.get('question_text', 'No question text'),
                    size=18,
                    weight=ft.FontWeight.BOLD
                )
            ], spacing=5),
            padding=20,
            bgcolor="#F5F5F5",
            border_radius=8,
            width=600
        )
        
        # Timer (placeholder - will be implemented)
        timer_text = ft.Text("00:00", size=24, weight=ft.FontWeight.BOLD, color=AppTheme.PRIMARY)
        
        # Response area (simplified for now - will expand with modes)
        response_text_field = ft.TextField(
            label="Your Response",
            multiline=True,
            min_lines=10,
            max_lines=20,
            width=600
        )
        
        # Notes area
        notes_field = ft.TextField(
            label="Notes / Keywords",
            hint_text="Jot down key points before responding...",
            multiline=True,
            min_lines=3,
            max_lines=5,
            width=600
        )
        
        # Action buttons
        flag_button = ft.OutlinedButton(
            "🚩 Flag for Review",
            icon=ft.Icons.FLAG,
            on_click=lambda e: self._flag_question()
        )
        
        skip_button = ft.OutlinedButton(
            "⏭ Skip",
            icon=ft.Icons.SKIP_NEXT,
            on_click=lambda e: self._skip_question()
        )
        
        submit_button = ft.ElevatedButton(
            "✓ Submit Response",
            icon=ft.Icons.CHECK_CIRCLE,
            on_click=lambda e: self._submit_response(response_text_field, notes_field),
            style=ft.ButtonStyle(
                bgcolor=AppTheme.PRIMARY,
                color="white"
            )
        )
        
        next_button = ft.ElevatedButton(
            "➡ Next Question",
            icon=ft.Icons.ARROW_FORWARD,
            on_click=lambda e: self._next_question(),
            visible=False
        )
        
        # Store button reference
        self.next_button = next_button
        
        # Session controls
        pause_button = ft.OutlinedButton(
            "⏸ Pause",
            icon=ft.Icons.PAUSE,
            on_click=lambda e: self._pause_session()
        )
        
        exit_button = ft.OutlinedButton(
            "Exit Session",
            icon=ft.Icons.EXIT_TO_APP,
            on_click=lambda e: self._exit_session()
        )
        
        # Live session layout
        return ft.Column([
            ft.Row([
                progress_text,
                ft.Container(expand=True),
                timer_text,
                pause_button,
                exit_button
            ], spacing=10),
            progress_bar,
            ft.Divider(),
            question_text,
            ft.Divider(),
            ft.Text("Notes:", size=14, weight=ft.FontWeight.BOLD),
            notes_field,
            ft.Divider(),
            ft.Text("Your Response:", size=14, weight=ft.FontWeight.BOLD),
            response_text_field,
            ft.Divider(),
            ft.Row([
                flag_button,
                skip_button,
                ft.Container(expand=True),
                submit_button,
                next_button
            ], spacing=10, wrap=True)
        ], spacing=15, scroll=ft.ScrollMode.AUTO)
    
    def _submit_response(self, response_field: ft.TextField, notes_field: ft.TextField):
        """Submit response for current question"""
        if not self.current_session_id or not self.session_questions:
            return
        
        current_question = self.session_questions[self.current_question_index]
        response_text = response_field.value.strip()
        
        if not response_text:
            self._show_error("Please enter your response")
            return
        
        # Save response
        response_id = MockInterviewService.save_response(
            session_id=self.current_session_id,
            question_id=current_question['question_id'],
            question_index=self.current_question_index,
            response_mode='written',
            response_text=response_text,
            notes=notes_field.value,
            duration_seconds=0  # Will implement timer later
        )
        
        if response_id:
            # Show success and enable next button
            self.next_button.visible = True
            response_field.disabled = True
            notes_field.disabled = True
            self.page.update()
        else:
            self._show_error("Failed to save response")
    
    def _next_question(self):
        """Move to next question"""
        if self.current_question_index < len(self.session_questions) - 1:
            self.current_question_index += 1
            self.content_area.content = self._build_live_session()
            self.page.update()
        else:
            # Session complete
            self._complete_session()
    
    def _flag_question(self):
        """Flag current question for review"""
        # Implementation for flagging
        self._show_success("Question flagged for review")
    
    def _skip_question(self):
        """Skip current question"""
        # Implementation for skipping
        self._next_question()
    
    def _pause_session(self):
        """Pause the session"""
        # Implementation for pausing
        self._show_success("Session paused")
    
    def _exit_session(self):
        """Exit session and return to main view"""
        self._reset_view()
    
    def _complete_session(self):
        """Complete the session and show results"""
        MockInterviewService.complete_session(self.current_session_id)
        self._show_analytics(None)
    
    def _show_analytics(self, e):
        """Show analytics dashboard"""
        self.analytics_active = True
        self.live_session_active = False
        
        # Get user sessions
        sessions = MockInterviewService.get_user_sessions(self.user_id, limit=10)
        
        # Build analytics view
        analytics_content = ft.Column([
            ft.Text("📊 Analytics Dashboard", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text(f"Total Sessions: {len(sessions)}", size=16),
            ft.Divider(),
            ft.Text("Recent Sessions:", size=18, weight=ft.FontWeight.BOLD),
            ft.Column([
                self._build_session_card(session) for session in sessions
            ], spacing=10, scroll=ft.ScrollMode.AUTO)
        ], spacing=15)
        
        self.content_area.content = analytics_content
        self.page.update()
    
    def _build_session_card(self, session: Dict) -> ft.Container:
        """Build a session card for display"""
        session_name = session.get('session_name', 'Unnamed Session')
        format_type = session.get('format_type', 'traditional')
        status = session.get('status', 'draft')
        created_at = session.get('created_at', '')
        
        return ft.Container(
            content=ft.Column([
                ft.Text(session_name, size=16, weight=ft.FontWeight.BOLD),
                ft.Text(f"Format: {format_type.title()} | Status: {status.title()}", size=12, color="grey"),
                ft.Text(f"Created: {created_at}", size=10, color="grey"),
                ft.ElevatedButton(
                    "View Details",
                    on_click=lambda e, sid=session['session_id']: self._view_session_details(sid),
                    height=30
                )
            ], spacing=5),
            padding=15,
            bgcolor="#F5F5F5",
            border_radius=8,
            border=ft.border.all(1, "#E0E0E0")
        )
    
    def _view_session_details(self, session_id: int):
        """View detailed session information"""
        # Implementation for viewing session details
        self._show_success(f"Viewing session {session_id}")
    
    def _show_library(self, e):
        """Show practice library"""
        sessions = MockInterviewService.get_user_sessions(self.user_id)
        
        library_content = ft.Column([
            ft.Text("📚 Practice Library", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text(f"Total Sessions: {len(sessions)}", size=16),
            ft.Divider(),
            ft.Column([
                self._build_session_card(session) for session in sessions
            ], spacing=10, scroll=ft.ScrollMode.AUTO)
        ], spacing=15)
        
        self.content_area.content = library_content
        self.page.update()
    
    def _reset_view(self):
        """Reset view to welcome screen"""
        self.setup_wizard_active = False
        self.live_session_active = False
        self.analytics_active = False
        self.current_session_id = None
        self.content_area.content = self._build_welcome_screen()
        self.page.update()
    
    def _show_error(self, message: str):
        """Show error dialog"""
        dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=lambda e: self._close_dialog(dialog))]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _show_success(self, message: str):
        """Show success message"""
        dialog = ft.AlertDialog(
            title=ft.Text("Success"),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=lambda e: self._close_dialog(dialog))]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _close_dialog(self, dialog: ft.AlertDialog):
        """Close dialog"""
        dialog.open = False
        self.page.dialog = None
        self.page.update()

