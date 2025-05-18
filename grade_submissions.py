import os
import requests
import re
import csv
import json

# Updated endpoint to /api/generate for LLaMA2:7B if using Ollama correctly
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
MODEL_NAME = "deepseek-r1:8b"

CODE_FOLDER = r"C:\Users\Nikhil\Desktop\PROJECT_GRADER\submissions"
MODEL_ANSWER_PATH = "./model_solution.py"
USE_MODEL_ANSWER = False    

OUTPUT_BASE = os.path.join(CODE_FOLDER, "graded_submissions")


def read_code_files(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith((".c", ".cpp", ".py"))]


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def generate_prompt(student_code, model_answer=None):
    prompt = (
        "You are a strict but fair programming examiner.\n"
        "Grade the following code out of 10. Just give one final score in the format 'X/10' anywhere in the response — no decimals or sub-scores.\n"
        "After the score, give a short justification (a few lines).\n\n"
        "Student's Code:\n```c\n" + student_code.strip() + "\n```\n"
    )
    if model_answer:
        prompt += "\nModel Answer:\n```c\n" + model_answer.strip() + "\n```\n"
    return prompt


def query_ollama(prompt):
    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": True}
    try:
        resp = requests.post(OLLAMA_ENDPOINT, json=payload, stream=True)
        resp.raise_for_status()
        full_response = ""
        for line in resp.iter_lines():
            if line:
                chunk = line.decode("utf-8")
                try:
                    data = json.loads(chunk)
                    full_response += data.get("response", "")
                except Exception as e:
                    print(f"Failed to parse chunk: {chunk}\nError: {e}")
        return full_response
    except Exception as e:
        return f"ERROR: Failed to get response from LLM.\nDetails: {e}"


'''
def extract_score(feedback):
    match = re.search(r"(?i)(score|total)\s*[:\-]?\s*(\d+(\.\d+)?)\s*/\s*10", feedback)
    return match.group(2) if match else "Not found"
'''
def extract_score(feedback: str) -> str:
    # Find all occurrences of a number followed by /10 (allow optional spaces)
    matches = re.findall(r'\b(\d{1,2})\s*/\s*10\b', feedback)
    
    valid_scores = []
    for score_str in matches:
        try:
            score = int(score_str)
            if 0 <= score <= 10:  # validate range
                valid_scores.append(score)
        except ValueError:
            continue

    if valid_scores:
        return str(min(valid_scores))
    else:
        return "Not found"

def save_results(student_file, feedback):
    base = os.path.splitext(os.path.basename(student_file))[0]
    folder = os.path.join(OUTPUT_BASE, f"{base}_sol_score")
    feedback_dir = os.path.join(folder, "feedback")
    score_dir = os.path.join(folder, "score")
    os.makedirs(feedback_dir, exist_ok=True)
    os.makedirs(score_dir, exist_ok=True)

    with open(os.path.join(feedback_dir, f"feedback_{base}.txt"), "w", encoding="utf-8") as f:
        f.write(feedback)

    score = extract_score(feedback)
    with open(os.path.join(score_dir, "score.txt"), "w", encoding="utf-8") as f:
        f.write(f"{base}: {score}/10")

    return base, score


def main():
    os.makedirs(OUTPUT_BASE, exist_ok=True)
    files = read_code_files(CODE_FOLDER)
    model_answer = read_file(MODEL_ANSWER_PATH) if USE_MODEL_ANSWER else None
    combined_scores = []

    for i, file in enumerate(files, 1):
        base = os.path.splitext(os.path.basename(file))[0]
        print(f"[{i}/{len(files)}] Grading {base}...")
        student_code = read_file(file)
        prompt = generate_prompt(student_code, model_answer)
        feedback = query_ollama(prompt)
        print(feedback)
        base, score = save_results(file, feedback)
        combined_scores.append((base, score))
        print(f"  Done: {base} => {score}/10\n")

    csv_path = os.path.join(OUTPUT_BASE, "combined_scores.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Filename", "Score"])
        writer.writerows(combined_scores)

    print(f"All scores saved to {csv_path}")


if __name__ == "__main__":
    main()
