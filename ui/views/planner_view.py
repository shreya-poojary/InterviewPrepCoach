"""Application Planner View"""

import flet as ft
from typing import Optional
from services.application_service import ApplicationService
from core.auth import SessionManager
from datetime import datetime

class PlannerView:
    """View for tracking job applications"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.user_id = SessionManager.get_user_id()
        self.selected_status_filter = None
        
    def build(self) -> ft.Container:
        """Build the planner view"""
        
        # Header
        header = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("📅 Application Planner", size=32, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton(
                        "➕ New Application",
                        icon=ft.Icons.ADD,
                        on_click=self.show_add_dialog,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.PRIMARY,
                            color=ft.Colors.ON_PRIMARY
                        )
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text("Track your job applications and manage follow-ups", size=14, color="grey")
            ], spacing=8),
            padding=ft.padding.only(bottom=20)
        )
        
        # Stats cards
        stats = ApplicationService.get_stats_by_status(self.user_id)
        total_stats = ApplicationService.get_application_stats(self.user_id)
        
        stats_row = ft.Row([
            self.build_stat_card("Total", total_stats.get('total', 0), ft.Icons.APPS, ft.Colors.BLUE),
            self.build_stat_card("Saved", stats.get('saved', 0), ft.Icons.BOOKMARK, ft.Colors.GREY),
            self.build_stat_card("Applied", stats.get('applied', 0), ft.Icons.SEND, ft.Colors.GREEN),
            self.build_stat_card("Interview", stats.get('interview', 0), ft.Icons.PERSON, ft.Colors.ORANGE),
            self.build_stat_card("Offers", stats.get('offer', 0), ft.Icons.CELEBRATION, ft.Colors.PURPLE),
        ], spacing=15, wrap=True)
        
        # Status filter buttons
        filter_buttons = ft.Row([
            ft.TextButton("All", on_click=lambda _: self.filter_applications(None)),
            ft.TextButton("Saved", on_click=lambda _: self.filter_applications('saved')),
            ft.TextButton("Applied", on_click=lambda _: self.filter_applications('applied')),
            ft.TextButton("Screening", on_click=lambda _: self.filter_applications('screening')),
            ft.TextButton("Interview", on_click=lambda _: self.filter_applications('interview')),
            ft.TextButton("Offer", on_click=lambda _: self.filter_applications('offer')),
            ft.TextButton("Rejected", on_click=lambda _: self.filter_applications('rejected')),
        ], spacing=5, wrap=True)
        
        # Applications list
        self.applications_container = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            expand=True
        )
        self.load_applications()
        
        # Main layout
        content = ft.Column([
            header,
            stats_row,
            ft.Divider(height=20),
            ft.Text("Filter by Status:", size=14, weight=ft.FontWeight.BOLD),
            filter_buttons,
            ft.Divider(),
            self.applications_container
        ], spacing=20, scroll=ft.ScrollMode.AUTO, expand=True)
        
        return ft.Container(
            content=content,
            padding=30,
            expand=True
        )
    
    def build_stat_card(self, title: str, value: int, icon: str, color: str) -> ft.Container:
        """Build a stat card"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=color, size=32),
                ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD),
                ft.Text(title, size=12, color="grey")
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            width=120,
            padding=15,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=10,
            bgcolor=ft.Colors.GREY_100
        )
    
    def load_applications(self, status: Optional[str] = None):
        """Load and display applications"""
        self.applications_container.controls.clear()
        
        apps = ApplicationService.get_applications(self.user_id, status)
        
        if not apps:
            self.applications_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX, size=64, color="grey"),
                        ft.Text("No applications yet", size=18, color="grey"),
                        ft.Text("Click 'New Application' to track your first job application", size=14, color="grey"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    alignment=ft.alignment.center,
                    padding=50
                )
            )
        else:
            for app in apps:
                self.applications_container.controls.append(
                    self.build_application_card(app)
                )
        
        self.page.update()
    
    def build_application_card(self, app: dict) -> ft.Card:
        """Build an application card"""
        status_colors = {
            'saved': ft.Colors.GREY_400,
            'applied': ft.Colors.BLUE_400,
            'screening': ft.Colors.LIGHT_BLUE_400,
            'interview': ft.Colors.ORANGE_400,
            'final_round': ft.Colors.DEEP_ORANGE_400,
            'offer': ft.Colors.GREEN_400,
            'rejected': ft.Colors.RED_400,
            'withdrawn': ft.Colors.GREY_600
        }
        
        status = app.get('status', 'saved')
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text(app.get('job_title', 'Untitled'), size=18, weight=ft.FontWeight.BOLD),
                            ft.Text(app.get('company_name', 'Unknown Company'), size=14, color="grey"),
                            ft.Row([
                                ft.Icon(ft.Icons.LOCATION_ON, size=14, color="grey"),
                                ft.Text(app.get('location', 'Not specified'), size=12, color="grey")
                            ], spacing=5) if app.get('location') else ft.Row([], spacing=0),
                        ], spacing=5, expand=True),
                        ft.Column([
                            ft.Container(
                                content=ft.Text(
                                    status.replace('_', ' ').title(),
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE
                                ),
                                bgcolor=status_colors.get(status, ft.Colors.GREY),
                                padding=ft.padding.symmetric(10, 5),
                                border_radius=5
                            ),
                            ft.Text(
                                f"Added {app.get('created_at', datetime.now()).strftime('%b %d, %Y') if isinstance(app.get('created_at'), datetime) else 'Unknown'}",
                                size=11,
                                color="grey"
                            )
                        ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=5)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(),
                    ft.Row([
                        ft.ElevatedButton(
                            "Update Status",
                            icon=ft.Icons.UPDATE,
                            on_click=lambda _, app_id=app['application_id']: self.show_status_dialog(app_id),
                            style=ft.ButtonStyle(padding=10)
                        ),
                        ft.TextButton(
                            "Edit",
                            icon=ft.Icons.EDIT,
                            on_click=lambda _, a=app: self.show_edit_dialog(a)
                        ),
                        ft.TextButton(
                            "Delete",
                            icon=ft.Icons.DELETE,
                            on_click=lambda _, app_id=app['application_id']: self.delete_application(app_id)
                        ),
                        ft.TextButton(
                            "View URL",
                            icon=ft.Icons.OPEN_IN_NEW,
                            on_click=lambda _, url=app.get('job_url'): self.page.launch_url(url) if url else self.page.update(),
                            disabled=not app.get('job_url')
                        )
                    ], spacing=10, wrap=True)
                ], spacing=15),
                padding=20
            ),
            elevation=2
        )
    
    def filter_applications(self, status: Optional[str]):
        """Filter applications by status"""
        self.selected_status_filter = status
        self.load_applications(status)
    
    def show_add_dialog(self, e):
        """Show dialog to add new application"""
        company_field = ft.TextField(label="Company Name *", autofocus=True, width=300)
        job_title_field = ft.TextField(label="Job Title *", width=300)
        location_field = ft.TextField(label="Location", width=300)
        job_url_field = ft.TextField(label="Job URL", width=300)
        notes_field = ft.TextField(label="Notes", multiline=True, min_lines=3, max_lines=5, width=300)
        
        def save_application(e):
            if not company_field.value or not job_title_field.value:
                self.show_error("Company and Job Title are required")
                return
            
            app_id = ApplicationService.create_application(
                user_id=self.user_id,
                company_name=company_field.value,
                job_title=job_title_field.value,
                location=location_field.value,
                job_url=job_url_field.value,
                notes=notes_field.value,
                status='saved'
            )
            
            if app_id:
                dialog.open = False
                self.page.update()
                self.load_applications(self.selected_status_filter)
                self.show_success("Application added successfully!")
            else:
                self.show_error("Failed to add application")
        
        dialog = ft.AlertDialog(
            title=ft.Text("➕ New Application"),
            content=ft.Column([
                company_field,
                job_title_field,
                location_field,
                job_url_field,
                notes_field
            ], tight=True, spacing=15, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: setattr(dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton("Add Application", on_click=save_application)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def show_status_dialog(self, app_id: int):
        """Show dialog to update application status"""
        status_dropdown = ft.Dropdown(
            label="New Status",
            options=[
                ft.dropdown.Option("saved", "💾 Saved"),
                ft.dropdown.Option("applied", "📤 Applied"),
                ft.dropdown.Option("screening", "📋 Screening"),
                ft.dropdown.Option("interview", "👤 Interview"),
                ft.dropdown.Option("final_round", "🎯 Final Round"),
                ft.dropdown.Option("offer", "🎉 Offer"),
                ft.dropdown.Option("rejected", "❌ Rejected"),
                ft.dropdown.Option("withdrawn", "🚫 Withdrawn"),
            ],
            width=300
        )
        
        def update_status(e):
            if not status_dropdown.value:
                self.show_error("Please select a status")
                return
            
            if ApplicationService.update_status(app_id, status_dropdown.value):
                dialog.open = False
                self.page.update()
                self.load_applications(self.selected_status_filter)
                self.show_success("Status updated successfully!")
            else:
                self.show_error("Failed to update status")
        
        dialog = ft.AlertDialog(
            title=ft.Text("Update Status"),
            content=status_dropdown,
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: setattr(dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton("Update", on_click=update_status)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def show_edit_dialog(self, app: dict):
        """Show dialog to edit application"""
        company_field = ft.TextField(label="Company Name", value=app.get('company_name', ''), width=300)
        job_title_field = ft.TextField(label="Job Title", value=app.get('job_title', ''), width=300)
        location_field = ft.TextField(label="Location", value=app.get('location', ''), width=300)
        job_url_field = ft.TextField(label="Job URL", value=app.get('job_url', ''), width=300)
        notes_field = ft.TextField(label="Notes", value=app.get('notes', ''), multiline=True, min_lines=3, width=300)
        
        def save_changes(e):
            if ApplicationService.update_application(
                app['application_id'],
                company_name=company_field.value,
                job_title=job_title_field.value,
                location=location_field.value,
                job_url=job_url_field.value,
                notes=notes_field.value
            ):
                dialog.open = False
                self.page.update()
                self.load_applications(self.selected_status_filter)
                self.show_success("Application updated!")
            else:
                self.show_error("Failed to update application")
        
        dialog = ft.AlertDialog(
            title=ft.Text("✏️ Edit Application"),
            content=ft.Column([
                company_field,
                job_title_field,
                location_field,
                job_url_field,
                notes_field
            ], tight=True, spacing=15, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: setattr(dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton("Save Changes", on_click=save_changes)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def delete_application(self, app_id: int):
        """Delete an application with confirmation"""
        def confirm_delete(e):
            if ApplicationService.delete_application(app_id):
                dialog.open = False
                self.page.update()
                self.load_applications(self.selected_status_filter)
                self.show_success("Application deleted")
            else:
                self.show_error("Failed to delete application")
        
        dialog = ft.AlertDialog(
            title=ft.Text("⚠️ Confirm Delete"),
            content=ft.Text("Are you sure you want to delete this application? This cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: setattr(dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton("Delete", on_click=confirm_delete, bgcolor=ft.Colors.RED_400)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def show_error(self, message: str):
        """Show error snackbar"""
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=ft.Colors.RED_400)
        self.page.snack_bar.open = True
        self.page.update()
    
    def show_success(self, message: str):
        """Show success snackbar"""
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=ft.Colors.GREEN_400)
        self.page.snack_bar.open = True
        self.page.update()

