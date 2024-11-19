import time
import tkinter as tk
from tkinter import filedialog
from file_converter import convert_to_docx

def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        label.config(text=f"Selected file: {file_path}")
        convert_to_docx(file_path)
        docx_file = file_path.replace('.pdf', '.docx')
        label.config(text=f"Converted to: {docx_file}")

# Create the main window
root = tk.Tk()
root.title("PDF to DOCX Converter")

# Create a label widget
label = tk.Label(root, text="No file selected")
label.pack()

# Create an upload button
upload_button = tk.Button(root, text="Upload PDF", command=upload_file)
upload_button.pack()

# Run the application
root.mainloop()