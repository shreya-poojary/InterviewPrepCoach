"""Simple Flet test to verify it's working"""
import flet as ft

def main(page: ft.Page):
    page.title = "Flet Test"
    page.add(
        ft.Text("Hello! Flet is working!", size=30),
        ft.ElevatedButton("Click Me", on_click=lambda e: print("Button clicked!"))
    )
    print("Flet app is running!")

if __name__ == "__main__":
    print("Starting simple Flet test...")
    print("Opening browser at http://localhost:8550")
    ft.app(target=main, port=8550, view=ft.AppView.WEB_BROWSER)
    print("App closed")

