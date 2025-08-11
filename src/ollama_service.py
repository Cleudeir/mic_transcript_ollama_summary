"""
Ollama integration for generating meeting minutes from transcripts
"""

import ollama
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any


class OllamaService:
    """Service class for interacting with Ollama to generate meeting minutes"""

    def __init__(self, model_name: str = None, base_url: str = None):
        """
        Initialize Ollama service

        Args:
            model_name: Name of the Ollama model to use (default: from config or llama3.2)
            base_url: Base URL for Ollama API (default: from config or https://api.apps.tec.br/ollama)
        """
        # Load configuration
        self.config = self._load_config()

        self.model_name = model_name or self.config.get("ollama", {}).get(
            "model_name", "llama3.2"
        )
        self.base_url = base_url or self.config.get("ollama", {}).get(
            "base_url", "http://localhost:11434"
        )
        self.logger = logging.getLogger(__name__)

        # Configure Ollama client with custom base URL and timeout
        self.client = ollama.Client(host=self.base_url, timeout=3000)

    def _load_config(self) -> dict:
        """Load configuration from config.json file"""
        try:
            import os

            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "config.json"
            )
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logging.getLogger(__name__).warning(f"Could not load config: {e}")

        # Return default configuration if loading fails
        return {
            "ollama": {
                "base_url": "http://localhost:11434",
                "model_name": "llama3.2",
                "temperature": 0.3,
                "top_p": 0.8,
                "num_predict": 2048,
            },
            "auto_generate_ata": True,
            "language": "pt-BR",
        }

    def _save_config(self, config: dict) -> bool:
        """Save configuration to config.json file"""
        try:
            import os

            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "config.json"
            )
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Could not save config: {e}")
            return False

    def update_config(self, ollama_url: str = None, model_name: str = None) -> bool:
        """Update configuration with new values"""
        config = self._load_config()

        if ollama_url is not None:
            config.setdefault("ollama", {})["base_url"] = ollama_url
            self.base_url = ollama_url
            # Reinitialize client with new URL and timeout
            self.client = ollama.Client(host=self.base_url, timeout=30)

        if model_name is not None:
            config.setdefault("ollama", {})["model_name"] = model_name
            self.model_name = model_name

        return self._save_config(config)

    def is_ollama_available(self) -> bool:
        """
        Check if Ollama is available and running

        Returns:
            bool: True if Ollama is available, False otherwise
        """
        try:
            # Create a temporary client with shorter timeout for testing
            test_client = ollama.Client(
                host=self.base_url, timeout=5
            )  # Reduced timeout
            # List available models to test connection
            models = test_client.list()
            return True
        except Exception as e:
            self.logger.error(f"Ollama not available at {self.base_url}: {e}")
            return False

    def is_model_available(self) -> bool:
        """
        Check if the specified model is available in Ollama

        Returns:
            bool: True if model is available, False otherwise
        """
        try:
            response = self.client.list()

            # Handle different response formats
            if hasattr(response, "models"):
                # New format with models attribute
                models = response.models
                model_names = [model.model for model in models]
            elif isinstance(response, dict) and "models" in response:
                # Dict format with 'models' key
                model_names = [
                    model.get("name", model.get("model", ""))
                    for model in response["models"]
                ]
            elif isinstance(response, list):
                # Direct list format
                model_names = [
                    model.get("name", model.get("model", "")) for model in response
                ]
            else:
                self.logger.warning(f"Unexpected models response format: {response}")
                return False

            # Check if our model is available (allowing partial matches like 'llama3.2' in 'llama3.2:latest')
            return any(self.model_name in name for name in model_names if name)
        except Exception as e:
            self.logger.error(f"Error checking model availability: {e}")
            return False

    def get_available_models(self) -> list:
        """
        Get list of available models from Ollama

        Returns:
            list: List of available model names
        """
        try:
            response = self.client.list()
            model_names = []

            if hasattr(response, "models"):
                # New format with models attribute
                models = response.models
                model_names = [model.model for model in models]
            elif isinstance(response, dict) and "models" in response:
                # Standard format with 'models' key
                model_names = [
                    model.get("name", model.get("model", ""))
                    for model in response["models"]
                ]
            elif isinstance(response, list):
                # Direct list format
                model_names = [
                    model.get("name", model.get("model", "")) for model in response
                ]
            else:
                self.logger.warning(f"Unexpected models response format: {response}")
                return []

            return [name for name in model_names if name]
        except Exception as e:
            self.logger.error(f"Error getting available models: {e}")
            return []

    def pull_model(self) -> bool:
        """
        Pull the model if it's not available

        Returns:
            bool: True if model is available after pull, False otherwise
        """
        try:
            self.logger.info(f"Pulling model {self.model_name} from {self.base_url}...")
            self.client.pull(self.model_name)
            return True
        except Exception as e:
            self.logger.error(f"Error pulling model: {e}")
            return False

    def test_model_with_hello(self) -> Dict[str, Any]:
        """
        Test the model by sending a simple 'hi' message

        Returns:
            Dict containing success status and response
        """
        try:
            self.logger.info(
                f"Testing model {self.model_name} with a simple message..."
            )

            response = self.client.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": "hi"}],
                options={
                    "temperature": 0.3,
                    "num_predict": 50,  # Short response for testing
                },
            )

            generated_content = response["message"]["content"]

            return {
                "success": True,
                "response": generated_content,
                "model_used": self.model_name,
                "base_url": self.base_url,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error testing model: {e}")
            return {
                "success": False,
                "error": str(e),
                "model_used": self.model_name,
                "base_url": self.base_url,
                "timestamp": datetime.now().isoformat(),
            }

    def generate_meeting_minutes(
        self, markdown_content: str, language: str = "pt-BR"
    ) -> Dict[str, Any]:
        """
        Generate meeting minutes from markdown transcript content

        Args:
            markdown_content: Raw markdown content from the meeting transcript
            language: Language for the output (default: pt-BR)

        Returns:
            Dict containing the generated meeting minutes with topics and summaries
        """
        # Determine language for prompts
        if language.startswith("pt"):
            prompt_template = self._get_portuguese_prompt()
        else:
            prompt_template = self._get_english_prompt()

        # Prepare the prompt with the transcript content
        full_prompt = prompt_template.format(transcript=markdown_content)

        try:
            self.logger.info("Generating meeting minutes with Ollama...")

            # Generate response using Ollama
            response = self.client.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": full_prompt}],
                options={
                    "temperature": self.config.get("ollama", {}).get(
                        "temperature", 0.3
                    ),
                    "top_p": self.config.get("ollama", {}).get("top_p", 0.8),
                    "num_predict": self.config.get("ollama", {}).get(
                        "num_predict", 2048
                    ),
                },
            )

            # Extract the generated content
            generated_content = response["message"]["content"]

            # Parse the generated minutes
            parsed_minutes = self._parse_generated_minutes(generated_content, language)

            return {
                "success": True,
                "content": parsed_minutes,
                "raw_response": generated_content,
                "timestamp": datetime.now().isoformat(),
                "model_used": self.model_name,
            }

        except Exception as e:
            self.logger.error(f"Error generating meeting minutes: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _get_portuguese_prompt(self) -> str:
        """Get the Portuguese prompt template"""
        return """
Você é um assistente especializado em criar atas de reunião. Analise a transcrição de áudio fornecida e crie uma ata de reunião bem estruturada seguindo estas diretrizes:

1. IDENTIFIQUE E ORGANIZE POR TEMAS:
   - Agrupe as discussões por tópicos/temas abordados
   - Cada tema deve ter um título claro e descritivo
   - Ordene os temas por ordem de importância ou cronológica

2. PARA CADA TEMA, FORNEÇA:
   - Um resumo conciso dos pontos principais discutidos
   - Decisões tomadas (se houver)
   - Ações definidas e responsáveis (se mencionados)
   - Prazos estabelecidos (se mencionados)

3. ESTRUTURA DA ATA:
   - Título: "Ata da Reunião"
   - Data e horário (extrair da transcrição se disponível)
   - Participantes identificados (extrair da transcrição)
   - Temas abordados (organizados por seções)
   - Resumo de cada tema
   - Próximos passos e ações (se aplicável)

4. FORMATO DE SAÍDA:
   Use markdown para formatação com:
   - Cabeçalhos (##) para cada tema
   - Listas com bullets (-) para pontos principais
   - **Negrito** para decisões importantes
   - *Itálico* para ações e responsáveis

TRANSCRIÇÃO DA REUNIÃO:
{transcript}

GERE A ATA DA REUNIÃO:
"""

    def _get_english_prompt(self) -> str:
        """Get the English prompt template"""
        return """
You are an assistant specialized in creating meeting minutes. Analyze the provided audio transcription and create a well-structured meeting minutes following these guidelines:

1. IDENTIFY AND ORGANIZE BY THEMES:
   - Group discussions by topics/themes addressed
   - Each theme should have a clear and descriptive title
   - Order themes by importance or chronologically

2. FOR EACH THEME, PROVIDE:
   - A concise summary of main points discussed
   - Decisions made (if any)
   - Actions defined and responsible parties (if mentioned)
   - Deadlines established (if mentioned)

3. MINUTES STRUCTURE:
   - Title: "Meeting Minutes"
   - Date and time (extract from transcription if available)
   - Identified participants (extract from transcription)
   - Topics addressed (organized by sections)
   - Summary of each theme
   - Next steps and actions (if applicable)

4. OUTPUT FORMAT:
   Use markdown formatting with:
   - Headers (##) for each theme
   - Bullet lists (-) for main points
   - **Bold** for important decisions
   - *Italic* for actions and responsible parties

MEETING TRANSCRIPTION:
{transcript}

GENERATE THE MEETING MINUTES:
"""

    def _parse_generated_minutes(self, content: str, language: str) -> Dict[str, Any]:
        """
        Parse the generated minutes content into structured data

        Args:
            content: Raw generated content from Ollama
            language: Language used for parsing

        Returns:
            Dict with structured meeting minutes data
        """
        lines = content.split("\n")
        parsed_data = {
            "title": "",
            "date": "",
            "participants": [],
            "themes": [],
            "actions": [],
            "full_content": content,
        }

        current_theme = None
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Extract title
            if line.startswith("# ") and not parsed_data["title"]:
                parsed_data["title"] = line[2:].strip()

            # Extract date patterns
            elif any(
                word in line.lower() for word in ["data:", "date:", "horário:", "time:"]
            ):
                parsed_data["date"] = (
                    line.split(":", 1)[1].strip() if ":" in line else line
                )

            # Extract participants
            elif any(
                word in line.lower()
                for word in ["participantes:", "participants:", "presentes:"]
            ):
                current_section = "participants"

            # Detect new themes (headers)
            elif line.startswith("## "):
                if current_theme:
                    parsed_data["themes"].append(current_theme)
                current_theme = {
                    "title": line[3:].strip(),
                    "content": [],
                    "decisions": [],
                    "actions": [],
                }
                current_section = "theme"

            # Process content based on current section
            elif current_section == "participants" and line.startswith("-"):
                participant = line[1:].strip()
                if participant:
                    parsed_data["participants"].append(participant)

            elif current_section == "theme" and current_theme:
                if line.startswith("**") and line.endswith("**"):
                    # Extract decisions (bold text)
                    decision = line[2:-2].strip()
                    current_theme["decisions"].append(decision)
                elif line.startswith("*") and line.endswith("*"):
                    # Extract actions (italic text)
                    action = line[1:-1].strip()
                    current_theme["actions"].append(action)
                    parsed_data["actions"].append(action)
                elif line.startswith("-"):
                    # Regular content points
                    current_theme["content"].append(line[1:].strip())
                else:
                    # Any other content
                    if line and not line.startswith("#"):
                        current_theme["content"].append(line)

        # Add the last theme if exists
        if current_theme:
            parsed_data["themes"].append(current_theme)

        return parsed_data

    def save_meeting_minutes(
        self, minutes_data: Dict[str, Any], file_path: str
    ) -> bool:
        """
        Save meeting minutes to a file

        Args:
            minutes_data: Structured meeting minutes data
            file_path: Path to save the file

        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                if minutes_data.get("success"):
                    f.write(minutes_data["content"]["full_content"])
                else:
                    f.write(
                        f"Erro ao gerar ata: {minutes_data.get('error', 'Erro desconhecido')}"
                    )

            self.logger.info(f"Meeting minutes saved to: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving meeting minutes: {e}")
            return False

    def generate_and_save_minutes(
        self, markdown_file_path: str, output_file_path: str, language: str = "pt-BR"
    ) -> Dict[str, Any]:
        """
        Complete workflow: read transcript, generate minutes, and save to file

        Args:
            markdown_file_path: Path to the markdown transcript file
            output_file_path: Path to save the generated minutes
            language: Language for generation

        Returns:
            Dict with operation results
        """
        try:
            # Read the transcript file
            with open(markdown_file_path, "r", encoding="utf-8") as f:
                transcript_content = f.read()

            # Generate minutes
            minutes_result = self.generate_meeting_minutes(transcript_content, language)

            if minutes_result["success"]:
                # Save to file
                saved = self.save_meeting_minutes(minutes_result, output_file_path)
                minutes_result["saved"] = saved
                minutes_result["output_file"] = output_file_path if saved else None

            return minutes_result

        except Exception as e:
            self.logger.error(f"Error in complete workflow: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }


def test_ollama_connection():
    """Test function to check Ollama connectivity and model functionality"""
    service = OllamaService()

    print(f"🔧 Configuration loaded from config.json:")
    print(f"   Base URL: {service.base_url}")
    print(f"   Model: {service.model_name}")
    print(
        f"   Temperature: {service.config.get('ollama', {}).get('temperature', 'default')}"
    )
    print()

    print(f"🔌 Testing Ollama connection to {service.base_url}...")
    if not service.is_ollama_available():
        print(
            f"❌ Ollama is not available at {service.base_url}. Please check the connection."
        )
        return False

    print("✅ Ollama is available!")

    print(f"🤖 Checking if model {service.model_name} is available...")
    if not service.is_model_available():
        print(f"⚠️ Model {service.model_name} is not available. Attempting to pull...")
        if service.pull_model():
            print(f"✅ Model {service.model_name} pulled successfully!")
        else:
            print(f"❌ Failed to pull model {service.model_name}")
            return False
    else:
        print(f"✅ Model {service.model_name} is available!")

    # Test the model with a simple message
    print(f"💬 Testing model with 'hi' message...")
    test_result = service.test_model_with_hello()

    if test_result["success"]:
        print(f"✅ Model test successful!")
        print(
            f"   Response: {test_result['response'][:100]}{'...' if len(test_result['response']) > 100 else ''}"
        )
        print(f"   Model used: {test_result['model_used']}")
    else:
        print(f"❌ Model test failed: {test_result['error']}")
        return False

    print("\n🎉 All tests passed! Ollama service is working correctly.")
    return True


if __name__ == "__main__":
    # Test the service
    test_ollama_connection()
