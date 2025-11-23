"""Test file picker functionality"""
import flet as ft

def main(page: ft.Page):
    page.title = "File Picker Test"
    page.window_width = 600
    page.window_height = 400
    
    status_text = ft.Text("No file selected", size=14)
    
    def on_file_pick_result(e: ft.FilePickerResultEvent):
        print(f"Result: {e}")
        print(f"Path: {e.path}")
        print(f"Files: {e.files}")
        if e.files:
            file = e.files[0]
            print(f"File name: {file.name}")
            print(f"File path: {getattr(file, 'path', 'N/A')}")
            status_text.value = f"Selected: {file.name}"
            status_text.color = "green"
        elif e.path:
            status_text.value = f"Selected: {e.path}"
            status_text.color = "green"
        else:
            status_text.value = "No file selected"
            status_text.color = "grey"
        status_text.update()
    
    file_picker = ft.FilePicker(on_result=on_file_pick_result)
    page.overlay.append(file_picker)
    page.update()
    
    def pick_file(e):
        print("Pick file clicked")
        print(f"File picker file_type: {file_picker.file_type}")
        file_picker.pick_files(
            allow_multiple=False
        )
    
    page.add(
        ft.Column([
            ft.Text("File Picker Test", size=24, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("Pick File", on_click=pick_file),
            status_text
        ], spacing=20, padding=50)
    )

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)

