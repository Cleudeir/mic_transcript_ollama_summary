#!/usr/bin/env python3
"""
Demo script to show the markdown saving functionality
This script simulates transcript creation and saves to markdown format
"""

import datetime
import os
from src.gui import MicrophoneTranscriberGUI


def demo_markdown_functionality():
    """Demonstrate the markdown saving functionality without GUI"""

    # Create output directory if it doesn't exist
    if not os.path.exists("src/output"):
        os.makedirs("src/output")

    # Create a demo session
    session_start_time = datetime.datetime.now()
    timestamp = session_start_time.strftime("%Y%m%d_%H%M%S")
    markdown_file_path = f"src/output/demo_meeting_transcripts_{timestamp}.md"

    print(f"Creating demo markdown file: {markdown_file_path}")

    # Simulate a meeting transcript
    with open(markdown_file_path, "w", encoding="utf-8") as f:
        # Write header
        f.write(f"# Meeting Transcripts - Live Session\n\n")
        f.write(
            f"**Session Started:** {session_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )
        f.write("**Participants:** Microphone 1, Microphone 2\n\n")
        f.write("---\n\n")
        f.write("## Live Transcript\n\n")

        # Simulate some transcripts
        demo_transcripts = [
            ("09:30:15", "Microphone 1", "Olá, vamos começar a reunião de hoje."),
            ("09:30:18", "Microphone 2", "Perfeito, estou pronto para começar."),
            (
                "09:30:25",
                "Microphone 1",
                "Primeiro item da agenda é sobre o projeto de transcriptação em tempo real.",
            ),
            (
                "09:30:32",
                "Microphone 2",
                "Excelente, temos algumas melhorias para discutir.",
            ),
            (
                "09:30:40",
                "Microphone 1",
                "Agora estamos salvando tudo em formato Markdown automaticamente.",
            ),
            (
                "09:30:45",
                "Microphone 2",
                "Isso vai facilitar muito a documentação das reuniões.",
            ),
        ]

        for timestamp, mic_name, text in demo_transcripts:
            f.write(f"**[{timestamp}] {mic_name}:** {text}\n\n")
            f.flush()  # Simulate real-time writing

        # Write session end info
        end_time = datetime.datetime.now()
        duration = end_time - session_start_time

        f.write("\n---\n\n")
        f.write(f"**Session Ended:** {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Duration:** {str(duration).split('.')[0]}\n\n")

    print(f"Demo file created successfully!")
    print(f"File location: {markdown_file_path}")

    # Display the content
    print("\n" + "=" * 60)
    print("GENERATED MARKDOWN CONTENT:")
    print("=" * 60)

    with open(markdown_file_path, "r", encoding="utf-8") as f:
        print(f.read())


if __name__ == "__main__":
    demo_markdown_functionality()
