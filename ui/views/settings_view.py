"""Settings view for LLM configuration"""

import flet as ft
from ui.styles.theme import AppTheme
from services.llm_service import LLMService
from ai.providers.ollama_provider import OllamaProvider
from core.auth import SessionManager
from config.settings import Settings

class SettingsView:
    """Application settings view"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.user_id = SessionManager.get_user_id()
        self.llm_service = LLMService.get_instance()
        
    def build(self) -> ft.Container:
        """Build settings view"""
        try:
            print("[INFO] Building Settings view...")
            
            # Header
            header = ft.Container(
                content=ft.Column([
                    ft.Text("⚙️ Settings", size=28, weight=ft.FontWeight.BOLD),
                    ft.Text("Configure LLM providers and application settings",
                           size=14, color="grey")
                ], spacing=8),
                padding=AppTheme.PADDING_MEDIUM
            )
            
            # LLM Provider selection
            self.provider_dropdown = ft.Dropdown(
                label="LLM Provider",
                options=[
                    ft.dropdown.Option("openai", "OpenAI"),
                    ft.dropdown.Option("anthropic", "Anthropic (Claude)"),
                    ft.dropdown.Option("bedrock", "AWS Bedrock"),
                    ft.dropdown.Option("ollama", "Ollama (Local)"),
                ],
                on_change=self._on_provider_change,
                width=300
            )
            
            # Model selection
            self.model_dropdown = ft.Dropdown(
                label="Model",
                width=300
            )
            
            # API Key
            self.api_key_field = ft.TextField(
                label="API Key",
                password=True,
                can_reveal_password=True,
                width=400
            )
            
            # Endpoint URL (for Ollama/Bedrock)
            self.endpoint_field = ft.TextField(
                label="Endpoint URL",
                width=400,
                visible=False
            )
            
            # Temperature
            self.temperature_slider = ft.Slider(
                label="Temperature",
                min=0,
                max=1,
                divisions=10,
                value=0.7,
                width=400
            )
            
            self.temperature_value = ft.Text("0.7")
            self.temperature_slider.on_change = lambda e: self._update_slider_value(
                self.temperature_value, e.control.value
            )
            
            # Max tokens
            self.max_tokens_field = ft.TextField(
                label="Max Tokens",
                value="2000",
                keyboard_type=ft.KeyboardType.NUMBER,
                width=200
            )
            
            # Save button
            self.save_button = ft.ElevatedButton(
                text="Save Settings",
                icon=ft.Icons.SAVE,
                on_click=self._on_save,
                style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color="white")
            )
            
            # Test connection button
            self.test_button = ft.OutlinedButton(
                text="Test Connection",
                icon=ft.Icons.CABLE,
                on_click=self._on_test_connection
            )
            
            # LLM Settings form
            llm_settings = ft.Container(
                content=ft.Column([
                    ft.Text("LLM Provider Configuration", size=20, weight=ft.FontWeight.BOLD),
                    self.provider_dropdown,
                    self.model_dropdown,
                    self.api_key_field,
                    self.endpoint_field,
                    ft.Row([
                        ft.Column([
                            ft.Text("Temperature"),
                            self.temperature_slider,
                            self.temperature_value
                        ], spacing=4),
                    ]),
                    self.max_tokens_field,
                    ft.Row([
                        self.save_button,
                        self.test_button
                    ], spacing=12)
                ], spacing=16),
                **AppTheme.card_style()
            )
            
            # About section
            about_section = ft.Container(
                content=ft.Column([
                    ft.Text("About", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Interview Prep AI v1.0", size=14),
                    ft.Text("Your AI-powered career companion", size=12, color="grey"),
                    ft.Divider(),
                    ft.Text("Supported Providers:", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text("• OpenAI (GPT-4, GPT-3.5)", size=12),
                    ft.Text("• Anthropic (Claude 3)", size=12),
                    ft.Text("• AWS Bedrock", size=12),
                    ft.Text("• Ollama (Local LLMs)", size=12),
                ], spacing=8),
                **AppTheme.card_style()
            )
            
            # Load current settings
            try:
                self._load_current_settings()
            except Exception as load_error:
                print(f"[ERROR] Error loading settings: {load_error}")
                import traceback
                traceback.print_exc()
            
            # Main content
            content = ft.Column([
                header,
                ft.Divider(),
                llm_settings,
                about_section
            ], spacing=20, scroll=ft.ScrollMode.AUTO, expand=True)
            
            print("[INFO] Settings view built successfully")
            
            return ft.Container(
                content=content,
                padding=AppTheme.PADDING_MEDIUM,
                expand=True
            )
        except Exception as e:
            print(f"[ERROR] Error building Settings view: {e}")
            import traceback
            traceback.print_exc()
            # Return error container
            return ft.Container(
                content=ft.Column([
                    ft.Text("⚙️ Settings", size=28, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Error loading settings: {str(e)}", color=ft.Colors.RED),
                    ft.Text("Please refresh the page", color="grey")
                ], spacing=16),
                padding=AppTheme.PADDING_MEDIUM,
                expand=True
            )
    
    def _on_provider_change(self, e):
        """Handle provider selection change"""
        provider = e.control.value if hasattr(e, 'control') else e
        
        if provider:
            self._update_provider_options(provider)
            
            # Select first option
            if self.model_dropdown.options:
                self.model_dropdown.value = self.model_dropdown.options[0].key
            
            self.page.update()
    
    def _update_slider_value(self, text_control, value):
        """Update slider value display"""
        text_control.value = f"{value:.1f}"
        text_control.update()
    
    def _load_current_settings(self):
        """Load current LLM settings"""
        try:
            settings = self.llm_service.get_user_llm_settings(self.user_id)
            
            if settings:
                self.provider_dropdown.value = settings['provider']
                # Update model options based on provider
                self._update_provider_options(settings['provider'])
                self.model_dropdown.value = settings['model_name']
                self.temperature_slider.value = float(settings.get('temperature', 0.7))
                self.temperature_value.value = f"{self.temperature_slider.value:.1f}"
                self.max_tokens_field.value = str(settings.get('max_tokens', 2000))
                
                if settings.get('endpoint_url'):
                    self.endpoint_field.value = settings['endpoint_url']
            else:
                # Set defaults
                self.provider_dropdown.value = "ollama"  # Default to Ollama since user has it
                self._update_provider_options("ollama")
                if self.model_dropdown.options:
                    self.model_dropdown.value = self.model_dropdown.options[0].key
        except Exception as e:
            print(f"[ERROR] Error loading settings: {e}")
            import traceback
            traceback.print_exc()
            # Set safe defaults
            self.provider_dropdown.value = "ollama"
            self._update_provider_options("ollama")
    
    def _update_provider_options(self, provider: str):
        """Update model options and field visibility based on provider"""
        if provider == "openai":
            self.model_dropdown.options = [
                ft.dropdown.Option("gpt-4", "GPT-4"),
                ft.dropdown.Option("gpt-4-turbo-preview", "GPT-4 Turbo"),
                ft.dropdown.Option("gpt-3.5-turbo", "GPT-3.5 Turbo"),
            ]
            self.api_key_field.visible = True
            self.endpoint_field.visible = False
        elif provider == "anthropic":
            self.model_dropdown.options = [
                ft.dropdown.Option("claude-3-opus-20240229", "Claude 3 Opus"),
                ft.dropdown.Option("claude-3-sonnet-20240229", "Claude 3 Sonnet"),
                ft.dropdown.Option("claude-3-haiku-20240307", "Claude 3 Haiku"),
            ]
            self.api_key_field.visible = True
            self.endpoint_field.visible = False
        elif provider == "bedrock":
            self.model_dropdown.options = [
                ft.dropdown.Option("anthropic.claude-3-sonnet-20240229-v1:0", "Claude 3 Sonnet"),
                ft.dropdown.Option("anthropic.claude-v2", "Claude 2"),
                ft.dropdown.Option("amazon.titan-text-express-v1", "Titan Text Express"),
            ]
            self.api_key_field.visible = False
            self.endpoint_field.visible = True
            self.endpoint_field.label = "AWS Region"
        elif provider == "ollama":
            # Try to get available models from Ollama
            try:
                ollama = OllamaProvider(base_url=Settings.OLLAMA_BASE_URL)
                models = ollama.list_models()
                if models:
                    self.model_dropdown.options = [
                        ft.dropdown.Option(m, m) for m in models
                    ]
                else:
                    self.model_dropdown.options = [
                        ft.dropdown.Option("llama3.2", "Llama 3.2"),
                        ft.dropdown.Option("llama3", "Llama 3"),
                        ft.dropdown.Option("mistral", "Mistral"),
                    ]
            except:
                self.model_dropdown.options = [
                    ft.dropdown.Option("llama3.2", "Llama 3.2"),
                    ft.dropdown.Option("llama3", "Llama 3"),
                    ft.dropdown.Option("mistral", "Mistral"),
                ]
            self.api_key_field.visible = False
            self.endpoint_field.visible = True
            self.endpoint_field.label = "Ollama URL"
            self.endpoint_field.value = Settings.OLLAMA_BASE_URL
    
    def _on_save(self, e):
        """Save LLM settings"""
        provider = self.provider_dropdown.value
        model = self.model_dropdown.value
        api_key = self.api_key_field.value if self.api_key_field.visible else None
        endpoint = self.endpoint_field.value if self.endpoint_field.visible else None
        temperature = self.temperature_slider.value
        max_tokens = int(self.max_tokens_field.value) if self.max_tokens_field.value else 2000
        
        if not provider or not model:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Please select provider and model"), bgcolor=ft.Colors.ORANGE
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        print(f"[INFO] Saving LLM settings: provider={provider}, model={model}")
        
        success = self.llm_service.save_llm_settings(
            self.user_id,
            provider,
            model,
            api_key,
            endpoint,
            temperature,
            max_tokens
        )
        
        print(f"[INFO] Save result: {success}")
        
        if success:
            snackbar = ft.SnackBar(
                content=ft.Text("✅ Settings saved successfully!"), 
                bgcolor=ft.Colors.GREEN,
                duration=3000
            )
            self.page.snack_bar = snackbar
            self.page.snack_bar.open = True
            self.page.update()
            print("[INFO] Success snackbar shown")
        else:
            snackbar = ft.SnackBar(
                content=ft.Text("❌ Error saving settings. Please try again."), 
                bgcolor=ft.Colors.RED,
                duration=3000
            )
            self.page.snack_bar = snackbar
            self.page.snack_bar.open = True
            self.page.update()
            print("[INFO] Error snackbar shown")
    
    def _on_test_connection(self, e):
        """Test LLM connection"""
        self.test_button.disabled = True
        self.test_button.text = "Testing..."
        self.page.update()
        
        try:
            provider = self.llm_service.get_provider(self.user_id)
            if not provider:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("No LLM provider configured"), bgcolor=ft.Colors.RED
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            # Test connection - generate() doesn't take max_tokens as parameter
            response = provider.generate("Say 'Hello' if you can read this.")
            
            if response and "error" not in response.lower():
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Connection successful! ✓"), bgcolor=ft.Colors.GREEN
                )
                self.page.snack_bar.open = True
                self.page.update()
            else:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Connection failed"), bgcolor=ft.Colors.RED
                )
                self.page.snack_bar.open = True
                self.page.update()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error: {str(ex)}"), bgcolor=ft.Colors.RED
            )
            self.page.snack_bar.open = True
            self.page.update()
        
        self.test_button.text = "Test Connection"
        self.test_button.disabled = False
        self.page.update()
