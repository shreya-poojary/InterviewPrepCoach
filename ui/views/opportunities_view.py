"""Job opportunities view with JSearch integration"""

import flet as ft
from ui.styles.theme import AppTheme
from ui.components.job_card import JobCard
from services.jsearch_service import JSearchService
from services.resume_service import ResumeService
from services.jd_service import JobDescriptionService
from core.auth import SessionManager

class OpportunitiesView:
    """Job search and opportunities view"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.user_id = SessionManager.get_user_id()
        self.current_jobs = []
        
    def build(self) -> ft.Container:
        """Build opportunities view"""
        # Header
        header = ft.Container(
            content=ft.Column([
                ft.Text("💼 Job Opportunities", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("Search and find jobs ranked by compatibility",
                       size=14, color="grey")
            ], spacing=8),
            padding=AppTheme.PADDING_MEDIUM
        )
        
        # Search section
        self.search_query = ft.TextField(
            label="Search keywords (e.g., 'Python Developer')",
            expand=True,
            on_submit=self._on_search
        )
        
        self.location_field = ft.TextField(
            label="Location (optional)",
            width=300,
            on_submit=self._on_search
        )
        
        self.remote_only_checkbox = ft.Checkbox(
            label="Remote only",
            value=False
        )
        
        self.search_button = ft.ElevatedButton(
            text="Search Jobs",
            icon=ft.Icons.SEARCH,
            on_click=self._on_search,
            style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color="white")
        )
        
        search_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    self.search_query,
                    self.location_field
                ], spacing=12),
                ft.Row([
                    self.remote_only_checkbox,
                    self.search_button
                ], spacing=12)
            ], spacing=12),
            **AppTheme.card_style()
        )
        
        # Results section
        self.results_title = ft.Text("", size=18, weight=ft.FontWeight.BOLD)
        self.results_container = ft.Column([], spacing=12)
        self.loading_indicator = ft.ProgressRing(visible=False)
        
        results_section = ft.Container(
            content=ft.Column([
                self.results_title,
                self.loading_indicator,
                self.results_container
            ], spacing=12, scroll=ft.ScrollMode.AUTO),
            **AppTheme.card_style(),
            visible=False
        )
        
        # Main content
        content = ft.Column([
            header,
            ft.Divider(),
            search_section,
            results_section
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
        
        return ft.Container(
            content=content,
            padding=AppTheme.PADDING_MEDIUM,
            expand=True
        )
    
    def _on_search(self, e):
        """Handle search"""
        query = self.search_query.value
        location = self.location_field.value
        remote_only = self.remote_only_checkbox.value
        
        if not query:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Please enter search keywords"), bgcolor="orange")
            )
            return
        
        # Show loading
        self.loading_indicator.visible = True
        self.results_container.controls.clear()
        self.results_title.value = "Searching..."
        self.search_button.disabled = True
        self.page.update()
        
        # Search jobs
        result = JSearchService.search_jobs(
            query=query,
            location=location,
            remote_only=remote_only
        )
        
        # Hide loading
        self.loading_indicator.visible = False
        self.search_button.disabled = False
        
        if "error" in result:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Error: {result['error']}"), bgcolor="red")
            )
            self.results_title.value = "Search failed"
            self.page.update()
            return
        
        jobs = result.get('jobs', [])
        
        if not jobs:
            self.results_title.value = "No jobs found"
            self.results_container.controls.append(
                ft.Text("Try different keywords or location", color="grey")
            )
            self.page.update()
            return
        
        # Rank by compatibility if user has resume
        resume = ResumeService.get_active_resume(self.user_id)
        if resume:
            jobs = JSearchService.rank_jobs_by_compatibility(
                jobs,
                resume['resume_text'],
                self.user_id
            )
        
        # Save search
        JSearchService.save_search(self.user_id, query, location, remote_only, len(jobs))
        
        # Display results
        self.current_jobs = jobs
        self.results_title.value = f"Found {len(jobs)} jobs"
        
        for job in jobs:
            job_card = JobCard.build(
                job=job,
                on_save=self._on_save_job,
                on_view_details=self._on_view_job_details
            )
            self.results_container.controls.append(job_card)
        
        self.page.update()
    
    def _on_save_job(self, job: dict):
        """Handle save job button"""
        # Save JD
        jd_id = JobDescriptionService.save_jd_from_jsearch(self.user_id, job)
        
        if jd_id:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Job saved successfully!"), bgcolor="green")
            )
        else:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Error saving job"), bgcolor="red")
            )
    
    def _on_view_job_details(self, job: dict):
        """Handle view job details"""
        # Show job details in a dialog
        description = job.get('job_description', 'No description available')
        
        dialog = ft.AlertDialog(
            title=ft.Text(job.get('job_title', 'Job Details')),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"Company: {job.get('employer_name', 'N/A')}", weight=ft.FontWeight.BOLD),
                    ft.Text(f"Location: {job.get('job_city', 'N/A')}"),
                    ft.Text(f"Type: {job.get('job_employment_type', 'N/A')}"),
                    ft.Divider(),
                    ft.Text("Description:", weight=ft.FontWeight.BOLD),
                    ft.Text(description[:500] + "..." if len(description) > 500 else description,
                           size=12)
                ], spacing=8, scroll=ft.ScrollMode.AUTO),
                height=400
            ),
            actions=[
                ft.TextButton("Close", on_click=lambda _: self.page.close(dialog)),
                ft.ElevatedButton(
                    "Apply",
                    icon=ft.Icons.OPEN_IN_NEW,
                    on_click=lambda _: self._open_job_url(job.get('job_apply_link'))
                )
            ]
        )
        
        self.page.open(dialog)
    
    def _open_job_url(self, url: str):
        """Open job URL in browser"""
        if url:
            self.page.launch_url(url)

