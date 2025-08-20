# Document Windows — Save behavior

What changed

- Transcript and ATA files now open in an internal editable document window instead of launching the external application. This window supports:
  - Save (overwrite original file)
  - Save As (save to a new location)
  - Ctrl+S keyboard shortcut
  - Prompt to save changes when closing

Files changed

- `src/gui/mixins/files_mixin.py` — added `_open_document_window` and updated `open_selected_transcript_file` / `open_selected_ata_file` to use it.

How to use

1. Open the application and go to the Transcripts or ATA tab.
2. Select a file and click Open (or double-click the list item).
3. Edit the content in the window. Use Save or Ctrl+S to save back to the original file, or Save As to write to a new path.
4. If you close the window with unsaved changes, you'll be prompted to save.

Notes and troubleshooting

- If internal editor fails for any reason, the code falls back to opening the file with the OS default application.
- The editor loads/saves files using UTF-8 encoding. If you see encoding errors, ensure the file is UTF-8 or convert it.

Next steps (optional)

- Add undo/redo and search inside the editor.
- Add syntax highlighting for Markdown.
- Move the editor into a reusable module if more features are needed.
