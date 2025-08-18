import os
import threading
import tkinter as tk
from tkinter import messagebox


class OllamaIntegrationMixin:
    def load_config_tab_values(self):
        try:
            config = {}
            if os.path.exists(self.config_file):
                import json

                with open(self.config_file, "r") as f:
                    config = json.load(f)
            ollama_config = config.get("ollama", {})
            if "base_url" in ollama_config:
                current_url = ollama_config["base_url"]
                if current_url and current_url != self.ollama_service.base_url:
                    import ollama as _ollama

                    self.ollama_service.base_url = current_url
                    self.ollama_service.client = _ollama.Client(
                        host=current_url, timeout=30
                    )
                self.ollama_url_var.set(current_url)
                if hasattr(self, "url_status_label"):
                    self.url_status_label.config(
                        text="✓ URL loaded from configuration", fg="green"
                    )
            else:
                self.ollama_url_var.set("")
                if hasattr(self, "url_status_label"):
                    self.url_status_label.config(text="No URL configured", fg="orange")
            if "model_name" in ollama_config:
                current_model = ollama_config["model_name"]
                if current_model and current_model != self.ollama_service.model_name:
                    self.ollama_service.model_name = current_model
                self.model_var.set(current_model)
            else:
                self.model_var.set("")
            if "base_url" in ollama_config and ollama_config["base_url"]:
                self.root.after(100, self._auto_test_connection_and_load_models)
        except Exception as e:
            self.status_var.set(f"Error loading config: {e}")

    def ensure_config_loaded_in_ui(self):
        try:
            if hasattr(self, "ollama_url_var") and hasattr(self, "model_var"):
                config = {}
                if os.path.exists(self.config_file):
                    import json

                    with open(self.config_file, "r") as f:
                        config = json.load(f)
                ollama_config = config.get("ollama", {})
                if "base_url" in ollama_config:
                    url = ollama_config["base_url"]
                    self.ollama_url_var.set(url)
                    if hasattr(self, "url_status_label"):
                        self.url_status_label.config(
                            text="✓ URL loaded from configuration", fg="green"
                        )
                    self.status_var.set(f"Configuration loaded: {url}")
                else:
                    self.status_var.set("No URL found in configuration")
                self.root.update_idletasks()
        except Exception as e:
            self.status_var.set(f"Error ensuring config in UI: {e}")

    def sync_ollama_service_with_config(self):
        try:
            ollama_config = self.config.get("ollama", {})
            if "base_url" in ollama_config:
                config_url = ollama_config["base_url"]
                if config_url and config_url != self.ollama_service.base_url:
                    import ollama as _ollama

                    self.ollama_service.base_url = config_url
                    self.ollama_service.client = _ollama.Client(
                        host=config_url, timeout=30
                    )
            if "model_name" in ollama_config:
                config_model = ollama_config["model_name"]
                if config_model and config_model != self.ollama_service.model_name:
                    self.ollama_service.model_name = config_model
        except Exception as e:
            print(f"Error syncing Ollama service with config: {e}")

    def _auto_test_connection_and_load_models(self):
        try:
            self.connection_status_label.config(
                text="🔄 Testing connection...", fg="orange"
            )
            self.model_status_label.config(
                text="Waiting for connection test...", fg="gray"
            )
            self.root.update_idletasks()
            if self.ollama_service.is_ollama_available():
                self.connection_status_label.config(
                    text="✅ Connection successful", fg="green"
                )
                self.model_status_label.config(text="Loading models...", fg="orange")
                self.root.update_idletasks()
                self.refresh_ollama_models()
            else:
                self.connection_status_label.config(
                    text="⚠️ Connection not available", fg="gray"
                )
                self.model_status_label.config(
                    text="Test connection to load models", fg="gray"
                )
        except Exception:
            self.connection_status_label.config(
                text="⚠️ Connection test failed", fg="gray"
            )
            self.model_status_label.config(
                text="Check URL and test connection", fg="gray"
            )

    def on_ollama_url_change(self, *args):
        try:
            new_url = self.ollama_url_var.get().strip()
            if new_url and new_url != self.ollama_service.base_url:
                success = self.ollama_service.update_config(ollama_url=new_url)
                if success:
                    self.config.setdefault("ollama", {})["base_url"] = new_url
                    self.save_main_config()
                    self.status_var.set("Ollama URL updated and saved")
                    self.model_combobox["values"] = []
                    self.model_var.set("")
                    self.root.after(200, self._auto_test_connection_and_load_models)
                else:
                    self.status_var.set("Failed to save Ollama URL")
        except Exception as e:
            self.status_var.set(f"Error updating Ollama URL: {e}")

    def on_model_change(self, event=None):
        try:
            new_model = self.model_var.get()
            if new_model and new_model != self.ollama_service.model_name:
                success = self.ollama_service.update_config(model_name=new_model)
                if success:
                    self.config.setdefault("ollama", {})["model_name"] = new_model
                    self.save_main_config()
                    self.status_var.set(f"Model updated and saved: {new_model}")
                    self.model_status_label.config(
                        text=f"Active model: {new_model}", fg="green"
                    )
                else:
                    self.status_var.set(f"Failed to save model: {new_model}")
        except Exception as e:
            self.status_var.set(f"Error updating model: {e}")

    def test_ollama_connection(self):
        try:
            self.connection_status_label.config(
                text="Testing connection...", fg="orange"
            )
            self.root.update_idletasks()
            if self.ollama_service.is_ollama_available():
                self.connection_status_label.config(
                    text="✅ Connection successful", fg="green"
                )
                self.refresh_ollama_models()
            else:
                self.connection_status_label.config(
                    text="❌ Connection failed", fg="red"
                )
                self.model_combobox["values"] = []
                self.model_var.set("")
                self.model_status_label.config(
                    text="Fix connection to load models", fg="red"
                )
        except Exception as e:
            self.connection_status_label.config(
                text=f"❌ Error: {str(e)[:30]}...", fg="red"
            )

    def refresh_ollama_models(self):
        try:
            self.model_status_label.config(text="Loading models...", fg="orange")
            self.root.update_idletasks()
            models = self.ollama_service.get_available_models()
            if models:
                self.model_combobox["values"] = models
                current_model = self.ollama_service.model_name
                if current_model in models:
                    self.model_var.set(current_model)
                    self.model_status_label.config(
                        text=f"Active model: {current_model}", fg="green"
                    )
                else:
                    self.model_var.set(models[0])
                    self.model_status_label.config(
                        text=f"Available models loaded ({len(models)})", fg="blue"
                    )
            else:
                self.model_combobox["values"] = []
                self.model_var.set("")
                self.model_status_label.config(text="No models available", fg="red")
        except Exception as e:
            self.model_status_label.config(
                text=f"Error loading models: {str(e)[:30]}...", fg="red"
            )

    def initialize_ollama_on_startup(self):
        try:
            if (
                not hasattr(self.ollama_service, "base_url")
                or not self.ollama_service.base_url
            ):
                self.status_var.set(
                    "Configure Ollama URL in the Ollama Configuration tab"
                )
                return
            self.status_var.set("Initializing Ollama connection...")
            self.root.update_idletasks()
            if self.ollama_service.is_ollama_available():
                self.status_var.set("Ollama connected! Loading models...")
                self.root.update_idletasks()
                if hasattr(self, "connection_status_label"):
                    self.connection_status_label.config(
                        text="✅ Connection successful", fg="green"
                    )
                models = self.ollama_service.get_available_models()
                if models:
                    if hasattr(self, "model_combobox"):
                        self.model_combobox["values"] = models
                        current_model = self.ollama_service.model_name
                        if current_model in models:
                            self.model_var.set(current_model)
                            if hasattr(self, "model_status_label"):
                                self.model_status_label.config(
                                    text=f"Active model: {current_model}", fg="green"
                                )
                        else:
                            self.model_var.set(models[0])
                            if hasattr(self, "model_status_label"):
                                self.model_status_label.config(
                                    text=f"Available models loaded ({len(models)})",
                                    fg="blue",
                                )
                    self.status_var.set(f"Models loaded! ({len(models)} available)")
                    self.root.update_idletasks()
                    self.root.after(500, self.send_greeting_to_model)
                else:
                    self.status_var.set("Ollama connected but no models available")
                    if hasattr(self, "model_status_label"):
                        self.model_status_label.config(
                            text="No models available", fg="red"
                        )
            else:
                self.status_var.set("Could not connect to Ollama service")
                if hasattr(self, "connection_status_label"):
                    self.connection_status_label.config(
                        text="❌ Connection failed", fg="red"
                    )
                if hasattr(self, "model_status_label"):
                    self.model_status_label.config(
                        text="Fix connection to load models", fg="red"
                    )
        except Exception as e:
            self.status_var.set(f"Error initializing Ollama: {str(e)[:50]}...")
            print(f"Ollama initialization error: {e}")

    def send_greeting_to_model(self):
        """Send a greeting to the model in background without blocking UI"""
        try:
            self.status_var.set("Testing model with greeting (background)...")
            self.root.update_idletasks()

            def worker():
                try:
                    result = self.ollama_service.test_model_with_hello()

                    def apply_result():
                        if result.get("success", False):
                            response = result.get("response", "")
                            # Response already sanitized in service
                            self.status_var.set(
                                f"✅ Model ready! Response: {response[:60]}..."
                            )
                            print(f"Model greeting response: {response}")
                        else:
                            error = result.get("error", "Unknown error")
                            self.status_var.set(f"Model test failed: {error[:40]}...")
                            print(f"Model greeting error: {error}")

                    self.root.after(0, apply_result)
                except Exception as e:

                    def apply_error():
                        self.status_var.set(f"Model test error: {str(e)[:40]}...")
                        print(f"Model greeting error: {e}")

                    self.root.after(0, apply_error)

            threading.Thread(target=worker, daemon=True, name="OllamaGreeting").start()
        except Exception as e:
            self.status_var.set(f"Model test error: {str(e)[:40]}...")
            print(f"Model greeting error (setup): {e}")
