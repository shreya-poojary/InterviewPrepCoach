"""Career Coach view - AI-powered career guidance"""

import flet as ft
from ui.styles.theme import AppTheme
from services.coach_service import CoachService
from core.auth import SessionManager

class CoachView:
    """Career Coach view with chat interface"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.user_id = SessionManager.get_user_id()
        self.current_session_id = None
        self.chat_messages = []
        
    def build(self) -> ft.Container:
        """Build coach view"""
        # Header
        header = ft.Container(
            content=ft.Column([
                ft.Text("🧠 AI Career Coach", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("Get personalized career advice and guidance",
                       size=14, color="grey")
            ], spacing=8),
            padding=AppTheme.PADDING_MEDIUM
        )
        
        # Quick advice buttons
        quick_advice_buttons = ft.Row([
            ft.ElevatedButton(
                "Resume Advice",
                icon=ft.Icons.DESCRIPTION,
                on_click=lambda _: self._get_quick_advice("resume")
            ),
            ft.ElevatedButton(
                "Interview Tips",
                icon=ft.Icons.PSYCHOLOGY,
                on_click=lambda _: self._get_quick_advice("interview")
            ),
            ft.ElevatedButton(
                "Job Search Strategy",
                icon=ft.Icons.SEARCH,
                on_click=lambda _: self._get_quick_advice("job_search")
            ),
            ft.ElevatedButton(
                "Skills Plan",
                icon=ft.Icons.SCHOOL,
                on_click=lambda _: self._get_quick_advice("skills")
            ),
        ], wrap=True, spacing=8)
        
        # Chat messages container
        self.messages_container = ft.ListView(
            spacing=10,
            padding=AppTheme.PADDING_MEDIUM,
            expand=True,
            auto_scroll=True
        )
        
        # Message input
        self.message_input = ft.TextField(
            label="Type your message...",
            multiline=True,
            min_lines=1,
            max_lines=3,
            expand=True,
            on_submit=self._send_message
        )
        
        send_button = ft.IconButton(
            icon=ft.Icons.SEND,
            icon_color=AppTheme.PRIMARY,
            on_click=self._send_message
        )
        
        input_row = ft.Row([
            self.message_input,
            send_button
        ], spacing=8)
        
        # Chat section
        chat_section = ft.Container(
            content=ft.Column([
                self.messages_container,
                ft.Divider(),
                input_row
            ], spacing=10, expand=True),
            **AppTheme.card_style(),
            expand=True
        )
        
        # Start session button
        self.start_button = ft.ElevatedButton(
            "Start New Coaching Session",
            icon=ft.Icons.CHAT,
            on_click=self._start_session,
            style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color="white")
        )
        
        # Main content
        content = ft.Column([
            header,
            ft.Text("Quick Advice:", size=16, weight=ft.FontWeight.BOLD),
            quick_advice_buttons,
            ft.Divider(),
            ft.Row([
                ft.Text("Coaching Session", size=16, weight=ft.FontWeight.BOLD),
                self.start_button
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            chat_section
        ], spacing=16, expand=True)
        
        return ft.Container(
            content=content,
            padding=AppTheme.PADDING_MEDIUM,
            expand=True
        )
    
    def _start_session(self, e):
        """Start a new coaching session"""
        result = CoachService.create_session(self.user_id)
        
        if "error" not in result:
            self.current_session_id = result['session_id']
            self.chat_messages.clear()
            self.messages_container.controls.clear()
            
            # Add greeting
            self._add_message("assistant", result['greeting'])
            
            self.start_button.disabled = True
            self.page.update()
        else:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Error: {result['error']}"), bgcolor="red")
            )
    
    def _send_message(self, e):
        """Send user message"""
        message = self.message_input.value
        
        if not message or not message.strip():
            return
        
        if not self.current_session_id:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Please start a session first"), bgcolor="orange")
            )
            return
        
        # Add user message to UI
        self._add_message("user", message)
        self.message_input.value = ""
        self.message_input.update()
        
        # Show loading
        loading = ft.ProgressRing(width=16, height=16)
        self.messages_container.controls.append(loading)
        self.page.update()
        
        # Send to coach
        result = CoachService.send_message(self.user_id, self.current_session_id, message)
        
        # Remove loading
        self.messages_container.controls.remove(loading)
        
        if "error" not in result:
            self._add_message("assistant", result['response'])
        else:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Error: {result['error']}"), bgcolor="red")
            )
    
    def _add_message(self, role: str, content: str):
        """Add message to chat"""
        is_user = role == "user"
        
        message_container = ft.Container(
            content=ft.Column([
                ft.Text(
                    "You" if is_user else "Career Coach",
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.PRIMARY if is_user else AppTheme.SECONDARY
                ),
                ft.Text(content, size=14, selectable=True)
            ], spacing=4),
            bgcolor=AppTheme.SURFACE_LIGHT if is_user else "#E3F2FD",
            padding=12,
            border_radius=AppTheme.RADIUS_MEDIUM,
            alignment=ft.alignment.center_left if not is_user else ft.alignment.center_right
        )
        
        self.messages_container.controls.append(message_container)
        self.page.update()
    
    def _get_quick_advice(self, advice_type: str):
        """Get quick advice"""
        # Show loading dialog
        loading_dialog = ft.AlertDialog(
            title=ft.Text("Generating advice..."),
            content=ft.ProgressRing()
        )
        self.page.open(loading_dialog)
        self.page.update()
        
        # Get advice
        advice = CoachService.get_quick_advice(self.user_id, advice_type)
        
        # Close loading and show result
        self.page.close(loading_dialog)
        
        result_dialog = ft.AlertDialog(
            title=ft.Text(f"{advice_type.replace('_', ' ').title()} Advice"),
            content=ft.Container(
                content=ft.Text(advice, size=14, selectable=True),
                width=600,
                height=400,
                padding=10
            ),
            actions=[
                ft.TextButton("Close", on_click=lambda _: self.page.close(result_dialog))
            ]
        )
        
        self.page.open(result_dialog)

