import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import grade_submissions  # import your grade_submissions.py file (make sure it's in the same folder or PYTHONPATH)

def select_code_folder():
    folder = filedialog.askdirectory(title="Select Code Folder")
    if folder:
        code_folder_var.set(folder)

def select_model_answer_file():
    file = filedialog.askopenfilename(title="Select Model Answer File", filetypes=[("Python files", "*.py"), ("All files", "*.*")])
    if file:
        model_answer_file_var.set(file)

def toggle_question():
    if use_question_var.get():
        question_textbox.config(state="normal")
    else:
        question_textbox.delete("1.0", "end")
        question_textbox.config(state="disabled")

def toggle_guidelines():
    if use_guidelines_var.get():
        guidelines_textbox.config(state="normal")
    else:
        guidelines_textbox.delete("1.0", "end")
        guidelines_textbox.config(state="disabled")

def run_grading_thread():
    def task():
        try:
            # Set variables in grade_submissions module
            grade_submissions.CODE_FOLDER = code_folder_var.get()
            grade_submissions.MODEL_ANSWER_PATH = model_answer_file_var.get()
            grade_submissions.USE_MODEL_ANSWER = use_model_answer_var.get()
            grade_submissions.question = question_textbox.get("1.0", "end-1c") if use_question_var.get() else None
            grade_submissions.extra_guidelines = guidelines_textbox.get("1.0", "end-1c") if use_guidelines_var.get() else None

            grade_submissions.OUTPUT_BASE = grade_submissions.CODE_FOLDER + "/graded_submissions"

            run_button.config(state="disabled")
            grade_submissions.main()  # Call main grading function
            messagebox.showinfo("Done", "Grading completed!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")
        finally:
            run_button.config(state="normal")

    threading.Thread(target=task).start()

# --- UI Setup ---

root = tk.Tk()
root.title("Project grade_submissions UI")
root.geometry("600x520")

# Variables
code_folder_var = tk.StringVar(value=grade_submissions.CODE_FOLDER)
model_answer_file_var = tk.StringVar(value=grade_submissions.MODEL_ANSWER_PATH)
use_model_answer_var = tk.BooleanVar(value=grade_submissions.USE_MODEL_ANSWER)
use_question_var = tk.BooleanVar(value=grade_submissions.question is not None)
use_guidelines_var = tk.BooleanVar(value=grade_submissions.extra_guidelines is not None)

# Code folder
tk.Label(root, text="Code Folder (submissions):").pack(anchor="w", padx=10, pady=(10, 0))
frame_folder = tk.Frame(root)
frame_folder.pack(fill="x", padx=10)
tk.Entry(frame_folder, textvariable=code_folder_var, width=60).pack(side="left", fill="x", expand=True)
tk.Button(frame_folder, text="Browse", command=select_code_folder).pack(side="left", padx=5)

# Use model answer
model_frame = tk.Frame(root)
model_frame.pack(fill="x", padx=10, pady=10)
tk.Checkbutton(model_frame, text="Use Model Answer", variable=use_model_answer_var, command=lambda: model_answer_entry.config(state="normal" if use_model_answer_var.get() else "disabled")).pack(anchor="w")
model_answer_entry = tk.Entry(model_frame, textvariable=model_answer_file_var, width=60, state="normal" if use_model_answer_var.get() else "disabled")
model_answer_entry.pack(side="left", fill="x", expand=True)
tk.Button(model_frame, text="Browse", command=select_model_answer_file).pack(side="left", padx=5)

# Use question
question_check = tk.Checkbutton(root, text="Include Question", variable=use_question_var, command=toggle_question)
question_check.pack(anchor="w", padx=10)
question_textbox = tk.Text(root, height=5, width=70, state="normal" if use_question_var.get() else "disabled")
question_textbox.pack(padx=10)

# Use extra guidelines
guidelines_check = tk.Checkbutton(root, text="Include Extra Guidelines", variable=use_guidelines_var, command=toggle_guidelines)
guidelines_check.pack(anchor="w", padx=10, pady=(10, 0))
guidelines_textbox = tk.Text(root, height=5, width=70, state="normal" if use_guidelines_var.get() else "disabled")
guidelines_textbox.pack(padx=10)

# Run button
run_button = tk.Button(root, text="Run Grading", command=run_grading_thread, bg="#4CAF50", fg="white", font=("Arial", 14))
run_button.pack(pady=20)

root.mainloop()
