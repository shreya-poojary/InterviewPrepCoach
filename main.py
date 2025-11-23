"""
Interview Prep AI - Main Application
Flet-based desktop application
"""

import flet as ft
from ui.views.home_view import HomeView
from ui.views.profile_analysis_view import ProfileAnalysisView
from ui.views.opportunities_view import OpportunitiesView
from ui.views.settings_view import SettingsView
from ui.views.placeholder_view import PlaceholderView
from ui.views.coach_view import CoachView
from ui.views.questions_view import QuestionsView
from ui.views.planner_view import PlannerView
from ui.components.navigation import NavigationRailComponent
from ui.styles.theme import AppTheme
from ui.styles.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from core.auth import SessionManager
from config.settings import Settings

# Initialize default user session
SessionManager.set_user(Settings.DEFAULT_USER_ID)

def main(page: ft.Page):
    """Main application entry point"""
    
    try:
        # Page configuration
        page.title = "Interview Prep AI"
        page.theme_mode = ft.ThemeMode.LIGHT
        # page.theme = AppTheme.get_theme()  # Comment out theme temporarily
        page.window_width = WINDOW_WIDTH
        page.window_height = WINDOW_HEIGHT
        page.window_min_width = 1000
        page.window_min_height = 600
        page.padding = 0
        page.spacing = 0
        page.bgcolor = "#FFFFFF"  # Explicit white background
        
    except Exception as e:
        print(f"[ERROR] Page configuration failed: {e}")
        page.add(ft.Text(f"Configuration Error: {e}", color="red"))
        return
    
    # Current view container
    current_view = ft.Container(expand=True)
    
    def route_change(e):
        """Handle route changes"""
        try:
            # Determine which view to show
            route = page.route if page.route else "/"
        except Exception as e:
            print(f"[ERROR] Route change error: {e}")
            return
        
        try:
            if route == "/":
                view = HomeView(page)
                nav_index = 0
            elif route == "/profile_analysis":
                view = ProfileAnalysisView(page)
                nav_index = 1
            elif route == "/questions":
                view = QuestionsView(page)
                nav_index = 2
            elif route == "/practice":
                view = PlaceholderView(
                    page,
                    "Practice Sessions",
                    "Practice interviews with AI feedback in written, audio, or video mode",
                    ft.Icons.PLAY_CIRCLE
                )
                nav_index = 3
            elif route == "/opportunities":
                view = OpportunitiesView(page)
                nav_index = 4
            elif route == "/writer":
                view = PlaceholderView(
                    page,
                    "Document Writer",
                    "Generate optimized resumes, cover letters, and cold emails",
                    ft.Icons.EDIT_DOCUMENT
                )
                nav_index = 5
            elif route == "/planner":
                view = PlannerView(page)
                nav_index = 6
            elif route == "/coach":
                view = CoachView(page)
                nav_index = 7
            elif route == "/settings":
                view = SettingsView(page)
                nav_index = 8
            else:
                view = HomeView(page)
                nav_index = 0
            
            # Update navigation selection
            navigation_rail.selected_index = nav_index
            
            # Update current view
            try:
                view_content = view.build()
                if view_content is None:
                    raise ValueError("View.build() returned None")
                current_view.content = view_content
            except Exception as build_error:
                print(f"[ERROR] Error building view content: {build_error}")
                current_view.content = ft.Container(
                    content=ft.Column([
                        ft.Text("Error Building View", size=24, color=ft.Colors.RED),
                        ft.Text(str(build_error), size=14, color=ft.Colors.RED_700),
                        ft.ElevatedButton("Go Home", on_click=lambda _: page.go("/"))
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=50
                )
            page.update()
            
        except Exception as e:
            print(f"[ERROR] Error loading view: {e}")
            import traceback
            traceback.print_exc()
            current_view.content = ft.Container(
                content=ft.Column([
                    ft.Text("Error Loading View", size=24, color=ft.Colors.RED),
                    ft.Text(str(e), size=14, color=ft.Colors.RED_700),
                    ft.ElevatedButton("Go Home", on_click=lambda _: page.go("/"))
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=50
            )
            page.update()
    
    def on_navigation_change(e):
        """Handle navigation rail selection"""
        routes = [
            "/",
            "/profile_analysis",
            "/questions",
            "/practice",
            "/opportunities",
            "/writer",
            "/planner",
            "/coach",
            "/settings"
        ]
        
        if e.control.selected_index < len(routes):
            page.go(routes[e.control.selected_index])
    
    try:
        # Create navigation rail
        nav_component = NavigationRailComponent(on_navigation_change)
        navigation_rail = nav_component.build()
        
        # Main layout
        main_layout = ft.Row([
            ft.Container(
                content=navigation_rail,
                bgcolor="#F5F5F5",
                padding=0
            ),
            ft.VerticalDivider(width=1),
            current_view
        ], spacing=0, expand=True)
        
        # Add layout to page
        page.add(main_layout)
        
        # Set up routing
        page.on_route_change = route_change
        
        # Initialize with home view
        page.go("/")
        
    except Exception as e:
        print(f"[ERROR] Fatal error in main(): {e}")
        import traceback
        traceback.print_exc()
        page.add(ft.Text(f"Fatal Error: {e}", color="red", size=20))

if __name__ == "__main__":
    # Check if database is set up
    try:
        from database import DatabaseManager
        if not DatabaseManager.test_connection():
            print("\n[WARNING] Database connection failed!")
            print("Please run: python database/create_db.py\n")
    except Exception as e:
        print(f"\n[WARNING] Database not initialized: {e}")
        print("Please run: python database/create_db.py\n")
    
    # Start the app in desktop mode
    print("[INFO] Starting Interview Prep AI...")
    print("[INFO] Launching desktop application...")
    print("[INFO] Close the window to exit")
    print("\n" + "="*50)
    print("Interview Prep AI - Desktop Application")
    print("="*50 + "\n")
    ft.app(target=main, view=ft.AppView.FLET_APP)
