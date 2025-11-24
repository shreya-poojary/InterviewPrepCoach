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
                        on_click=lambda e: self.show_add_dialog(e),
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
        
        # Stats cards (will be refreshed)
        self.stats_row = self._build_stats_row()
        
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
        if not hasattr(self, 'applications_container'):
            self.applications_container = ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
                expand=True
            )
        
        # Load applications
        self.load_applications()
        
        # Main layout
        content = ft.Column([
            header,
            self.stats_row,
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
    
    def _build_stats_row(self) -> ft.Row:
        """Build stats row with current data"""
        stats = ApplicationService.get_stats_by_status(self.user_id)
        total_stats = ApplicationService.get_application_stats(self.user_id)
        
        return ft.Row([
            self.build_stat_card("Total", total_stats.get('total', 0), ft.Icons.APPS, ft.Colors.BLUE),
            self.build_stat_card("Saved", stats.get('saved', 0), ft.Icons.BOOKMARK, ft.Colors.GREY),
            self.build_stat_card("Applied", stats.get('applied', 0), ft.Icons.SEND, ft.Colors.GREEN),
            self.build_stat_card("Interview", stats.get('interview', 0), ft.Icons.PERSON, ft.Colors.ORANGE),
            self.build_stat_card("Offers", stats.get('offer', 0), ft.Icons.CELEBRATION, ft.Colors.PURPLE),
        ], spacing=15, wrap=True)
    
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
        # Ensure container exists before using it
        if not hasattr(self, 'applications_container'):
            print(f"[DEBUG] applications_container not initialized yet, skipping load")
            return
        
        self.applications_container.controls.clear()
        
        print(f"[DEBUG] Loading applications for user_id={self.user_id}, status={status}")
        
        try:
            apps = ApplicationService.get_applications(self.user_id, status)
            print(f"[DEBUG] get_applications returned {len(apps) if apps else 0} applications")
            
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
                    print(f"[DEBUG] Building card for app_id={app.get('application_id')}, company={app.get('company_name')}")
                    self.applications_container.controls.append(
                        self.build_application_card(app)
                    )
        except Exception as e:
            print(f"[ERROR] Error loading applications: {e}")
            import traceback
            traceback.print_exc()
            self.applications_container.controls.append(
                ft.Container(
                    content=ft.Text(f"Error loading applications: {str(e)}", color="red"),
                    padding=20
                )
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
        
        # Format dates - handle multiple formats
        def format_date(date_value):
            if not date_value:
                return None
            try:
                if isinstance(date_value, str):
                    # Handle MySQL DATETIME format: '2024-01-15 10:30:00'
                    if ' ' in date_value:
                        dt = datetime.strptime(date_value.split()[0], '%Y-%m-%d')
                    # Handle ISO format with T
                    elif 'T' in date_value:
                        dt = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                    # Handle DATE format: '2024-01-15'
                    else:
                        dt = datetime.strptime(date_value, '%Y-%m-%d')
                elif isinstance(date_value, datetime):
                    dt = date_value
                elif hasattr(date_value, 'strftime'):  # date object
                    dt = datetime.combine(date_value, datetime.min.time())
                else:
                    return None
                return dt.strftime('%b %d, %Y')
            except Exception as e:
                print(f"[DEBUG] Date formatting error: {e}, value: {date_value}, type: {type(date_value)}")
                return None
        
        applied_date_str = format_date(app.get('applied_date'))
        interview_date_str = format_date(app.get('interview_date'))
        created_date_str = format_date(app.get('created_at'))
        
        # Notes preview
        notes = app.get('notes', '')
        notes_preview = (notes[:100] + '...') if notes and len(notes) > 100 else notes
        
        # Salary info
        salary = app.get('salary_offered')
        salary_text = f"${salary:,.0f}" if salary else None
        
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
                                f"Added {created_date_str or 'Unknown'}", 
                                size=11,
                                color="grey"
                            )
                        ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=5)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    # Date and salary info row
                    ft.Row([
                        ft.Row([
                            ft.Icon(ft.Icons.CALENDAR_TODAY, size=14, color="grey"),
                            ft.Text(f"Applied: {applied_date_str}", size=11, color="grey") if applied_date_str else ft.Text("Not applied yet", size=11, color="grey", italic=True)
                        ], spacing=5) if applied_date_str or status != 'saved' else ft.Container(),
                        ft.Row([
                            ft.Icon(ft.Icons.EVENT, size=14, color="grey"),
                            ft.Text(f"Interview: {interview_date_str}", size=11, color="grey")
                        ], spacing=5) if interview_date_str else ft.Container(),
                        ft.Row([
                            ft.Icon(ft.Icons.ATTACH_MONEY, size=14, color="green"),
                            ft.Text(f"Salary: {salary_text}", size=11, color="green", weight=ft.FontWeight.BOLD)
                        ], spacing=5) if salary_text else ft.Container()
                    ], spacing=15, wrap=True) if (applied_date_str or interview_date_str or salary_text) else ft.Container(),
                    
                    # Notes preview
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Notes:", size=12, weight=ft.FontWeight.BOLD, color="grey"),
                            ft.Text(notes_preview or "No notes", size=11, color="grey", italic=not notes)
                        ], spacing=3, tight=True),
                        visible=bool(notes),
                        padding=ft.padding.only(top=5)
                    ),
                    
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
        self._refresh_stats()
    
    def _refresh_stats(self):
        """Refresh stats row"""
        if hasattr(self, 'stats_row'):
            # Find stats row in parent and replace it
            # This is a simplified approach - in production, you might want to use a ref
            pass  # Stats will refresh on next build
    
    def _open_dialog(self, dialog: ft.AlertDialog):
        """Open dialog helper - matches working pattern from opportunities_view"""
        try:
            print(f"[DEBUG] _open_dialog called, page={self.page}, has dialog attr={hasattr(self.page, 'dialog')}")
            
            # Close any existing dialog first
            if hasattr(self.page, 'dialog') and self.page.dialog:
                print(f"[DEBUG] Closing existing dialog")
                self.page.dialog.open = False
                self.page.dialog = None
                self.page.update()
            
            # Set and open dialog
            print(f"[DEBUG] Setting page.dialog and opening")
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
            print(f"[DEBUG] Dialog opened successfully, dialog.open={dialog.open}, page.dialog={self.page.dialog}")
        except Exception as ex:
            print(f"[ERROR] Error in _open_dialog: {ex}")
            import traceback
            traceback.print_exc()
            # Try direct assignment as fallback
            try:
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
            except Exception as ex2:
                print(f"[ERROR] Fallback also failed: {ex2}")
    
    def _close_dialog(self, dialog: ft.AlertDialog):
        """Close dialog helper - simple and reliable"""
        try:
            # Close the dialog
            dialog.open = False
            
            # Clear page.dialog - this removes the modal backdrop
            if hasattr(self.page, 'dialog'):
                self.page.dialog = None
            
            # Update page to apply changes
            self.page.update()
            
            print(f"[DEBUG] Dialog closed")
        except Exception as ex:
            print(f"[DEBUG] Error closing dialog: {ex}")
            try:
                # Fallback: simple close
                dialog.open = False
                if hasattr(self.page, 'dialog'):
                    self.page.dialog = None
                self.page.update()
            except:
                pass
    
    def show_add_dialog(self, e):
        """Show dialog to add new application"""
        print(f"[DEBUG] show_add_dialog called, e={e}, e.page={getattr(e, 'page', None)}, self.page={self.page}")
        
        # Always use self.page (the page passed to __init__)
        page = self.page
        
        if not page:
            print(f"[ERROR] Page is None!")
            return
        
        company_field = ft.TextField(label="Company Name *", autofocus=True, width=350)
        job_title_field = ft.TextField(label="Job Title *", width=350)
        location_field = ft.TextField(label="Location", width=350)
        job_url_field = ft.TextField(label="Job URL", width=350)
        applied_date_field = ft.TextField(
            label="Applied Date (YYYY-MM-DD)",
            hint_text="2024-01-15",
            width=350
        )
        interview_date_field = ft.TextField(
            label="Interview Date (YYYY-MM-DD)",
            hint_text="2024-01-20",
            width=350
        )
        salary_field = ft.TextField(
            label="Salary Offered",
            hint_text="100000",
            width=350
        )
        notes_field = ft.TextField(label="Notes", multiline=True, min_lines=3, max_lines=5, width=350)
        
        def save_application(e):
            # Validate required fields (strip whitespace)
            company = company_field.value.strip() if company_field.value else ""
            job_title = job_title_field.value.strip() if job_title_field.value else ""
            
            if not company or not job_title:
                self.show_error("Company and Job Title are required")
                return
            
            # Parse dates
            applied_date = None
            interview_date = None
            salary = None
            
            if applied_date_field.value:
                try:
                    applied_date = datetime.strptime(applied_date_field.value, '%Y-%m-%d').date()
                except:
                    self.show_error("Invalid applied date format. Use YYYY-MM-DD")
                    return
            
            if interview_date_field.value:
                try:
                    interview_date = datetime.strptime(interview_date_field.value, '%Y-%m-%d')
                except:
                    self.show_error("Invalid interview date format. Use YYYY-MM-DD")
                    return
            
            if salary_field.value:
                try:
                    salary = float(salary_field.value)
                except:
                    self.show_error("Invalid salary. Enter a number.")
                    return
            
            print(f"[DEBUG] Creating application: user_id={self.user_id}, company={company}, title={job_title}")
            
            try:
                app_id = ApplicationService.create_application(
                    user_id=self.user_id,
                    company_name=company,
                    job_title=job_title,
                    location=location_field.value.strip() if location_field.value and location_field.value.strip() else None,
                    job_url=job_url_field.value.strip() if job_url_field.value and job_url_field.value.strip() else None,
                    notes=notes_field.value.strip() if notes_field.value and notes_field.value.strip() else None,
                    status='saved',
                    applied_date=applied_date,
                    interview_date=interview_date,
                    salary_offered=salary
                )
                
                print(f"[DEBUG] create_application returned: {app_id} (type: {type(app_id)})")
                
                if app_id and app_id > 0:
                    # Use _close_dialog for consistent cleanup
                    self._close_dialog(dialog)
                    # Reload applications and refresh stats
                    self.load_applications(self.selected_status_filter)
                    self._refresh_stats()
                    self.show_success(f"✅ Application added successfully! (ID: {app_id})")
                else:
                    error_msg = f"❌ Failed to add application. Returned ID: {app_id}. Check console for details."
                    print(f"[ERROR] {error_msg}")
                    self.show_error(error_msg)
            except Exception as ex:
                error_msg = f"❌ Error creating application: {str(ex)}"
                print(f"[ERROR] {error_msg}")
                import traceback
                traceback.print_exc()
                self.show_error(error_msg)
        
        # Create dialog with simpler structure
        dialog_content = ft.Column([
            company_field,
            job_title_field,
            location_field,
            job_url_field,
            applied_date_field,
            interview_date_field,
            salary_field,
            notes_field
        ], spacing=15, scroll=ft.ScrollMode.AUTO, tight=True)
        
        dialog = ft.AlertDialog(
            title=ft.Text("➕ New Application", size=18, weight=ft.FontWeight.BOLD),
            content=dialog_content,
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_dialog(dialog)),
                ft.ElevatedButton("Add Application", on_click=save_application, icon=ft.Icons.ADD)
            ],
            modal=True
        )
        
        print(f"[DEBUG] Opening add dialog")
        # Open dialog with same pattern as working dialogs (status, edit)
        try:
            if hasattr(self.page, 'dialog'):
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
                print(f"[DEBUG] Dialog opened via page.dialog")
            else:
                if not hasattr(self.page, 'overlay') or self.page.overlay is None:
                    self.page.overlay = []
                if dialog not in self.page.overlay:
                    self.page.overlay.append(dialog)
                dialog.open = True
                self.page.update()
                print(f"[DEBUG] Dialog opened via overlay")
        except Exception as ex:
            print(f"[ERROR] Failed to open add dialog: {ex}")
            import traceback
            traceback.print_exc()
    
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
                self._close_dialog(dialog)
                self.load_applications(self.selected_status_filter)
                self.show_success("Status updated successfully!")
            else:
                self.show_error("Failed to update status")
        
        dialog = ft.AlertDialog(
            title=ft.Text("Update Status"),
            content=status_dropdown,
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_dialog(dialog)),
                ft.ElevatedButton("Update", on_click=update_status)
            ],
            modal=True
        )
        
        # Open dialog with fallback
        print(f"[DEBUG] Opening status dialog")
        try:
            if hasattr(self.page, 'dialog'):
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
            else:
                if not hasattr(self.page, 'overlay') or self.page.overlay is None:
                    self.page.overlay = []
                if dialog not in self.page.overlay:
                    self.page.overlay.append(dialog)
                dialog.open = True
                self.page.update()
        except Exception as ex:
            print(f"[ERROR] Failed to open status dialog: {ex}")
    
    def show_edit_dialog(self, app: dict):
        """Show dialog to edit application"""
        def format_date_for_input(date_value):
            if not date_value:
                return ""
            try:
                if isinstance(date_value, str):
                    if 'T' in date_value:
                        dt = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                    else:
                        dt = datetime.strptime(date_value, '%Y-%m-%d')
                elif isinstance(date_value, datetime):
                    dt = date_value
                else:
                    return ""
                return dt.strftime('%Y-%m-%d')
            except:
                return ""
        
        company_field = ft.TextField(label="Company Name", value=app.get('company_name', ''), width=300)
        job_title_field = ft.TextField(label="Job Title", value=app.get('job_title', ''), width=300)
        location_field = ft.TextField(label="Location", value=app.get('location', ''), width=300)
        job_url_field = ft.TextField(label="Job URL", value=app.get('job_url', ''), width=300)
        applied_date_field = ft.TextField(
            label="Applied Date (YYYY-MM-DD)",
            value=format_date_for_input(app.get('applied_date')),
            hint_text="2024-01-15",
            width=300
        )
        interview_date_field = ft.TextField(
            label="Interview Date (YYYY-MM-DD)",
            value=format_date_for_input(app.get('interview_date')),
            hint_text="2024-01-20",
            width=300
        )
        salary_field = ft.TextField(
            label="Salary Offered",
            value=str(app.get('salary_offered', '')) if app.get('salary_offered') else '',
            hint_text="100000",
            width=300
        )
        notes_field = ft.TextField(label="Notes", value=app.get('notes', ''), multiline=True, min_lines=3, width=300)
        
        def save_changes(e):
            # Parse dates
            applied_date = None
            interview_date = None
            salary = None
            
            if applied_date_field.value:
                try:
                    applied_date = datetime.strptime(applied_date_field.value, '%Y-%m-%d').date()
                except:
                    self.show_error("Invalid applied date format. Use YYYY-MM-DD")
                    return
            
            if interview_date_field.value:
                try:
                    interview_date = datetime.strptime(interview_date_field.value, '%Y-%m-%d')
                except:
                    self.show_error("Invalid interview date format. Use YYYY-MM-DD")
                    return
            
            if salary_field.value:
                try:
                    salary = float(salary_field.value)
                except:
                    self.show_error("Invalid salary. Enter a number.")
                    return
            
            if ApplicationService.update_application(
                app['application_id'],
                company_name=company_field.value,
                job_title=job_title_field.value,
                location=location_field.value,
                job_url=job_url_field.value,
                notes=notes_field.value,
                applied_date=applied_date,
                interview_date=interview_date,
                salary_offered=salary
            ):
                # Close dialog first, then reload and show success
                self._close_dialog(dialog)
                # Small delay to ensure dialog is fully closed before reloading
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
                applied_date_field,
                interview_date_field,
                salary_field,
                notes_field
            ], tight=True, spacing=15, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_dialog(dialog)),
                ft.ElevatedButton("Save Changes", on_click=save_changes)
            ],
            modal=True
        )
        
        # Open dialog with fallback
        print(f"[DEBUG] Opening edit dialog")
        try:
            if hasattr(self.page, 'dialog'):
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
            else:
                if not hasattr(self.page, 'overlay') or self.page.overlay is None:
                    self.page.overlay = []
                if dialog not in self.page.overlay:
                    self.page.overlay.append(dialog)
                dialog.open = True
                self.page.update()
        except Exception as ex:
            print(f"[ERROR] Failed to open edit dialog: {ex}")
    
    def delete_application(self, app_id: int):
        """Delete an application with confirmation"""
        def confirm_delete(e):
            if ApplicationService.delete_application(app_id):
                self._close_dialog(dialog)
                self.load_applications(self.selected_status_filter)
                self.show_success("Application deleted")
            else:
                self.show_error("Failed to delete application")
        
        dialog = ft.AlertDialog(
            title=ft.Text("⚠️ Confirm Delete"),
            content=ft.Text("Are you sure you want to delete this application? This cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_dialog(dialog)),
                ft.ElevatedButton("Delete", on_click=confirm_delete, bgcolor=ft.Colors.RED_400)
            ],
            modal=True
        )
        
        # Open dialog with fallback
        print(f"[DEBUG] Opening delete confirmation dialog")
        try:
            if hasattr(self.page, 'dialog'):
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
            else:
                if not hasattr(self.page, 'overlay') or self.page.overlay is None:
                    self.page.overlay = []
                if dialog not in self.page.overlay:
                    self.page.overlay.append(dialog)
                dialog.open = True
                self.page.update()
        except Exception as ex:
            print(f"[ERROR] Failed to open delete dialog: {ex}")
    
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

