#!/usr/bin/env python3
"""
Script to fix the remaining button text
"""


def fix_remaining_button():
    # Read the file
    with open("src/gui.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Find and replace the problematic line
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if "Save As" in line and "text=" in line and "t(" not in line:
            lines[i] = line.replace(
                'text="� Save As"', 'text=t("button_save_as", "💾 Save As")'
            )
            print(f"Fixed line {i+1}: {lines[i]}")

    # Write back
    with open("src/gui.py", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("Fixed remaining button text")


if __name__ == "__main__":
    fix_remaining_button()
