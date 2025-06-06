import os
import tkinter as tk
from tkinter import messagebox, scrolledtext
from openai import OpenAI
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def read_article_from_file(file_path="input.txt"):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        exit(1)
    with open(file_path, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]
        if not lines:
            print("File is empty.")
            exit(1)
        title = lines[0]
        body = "\n".join(lines[1:])
        return title, body

def read_article_from_link(link):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(link, timeout=60000)
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string.strip() if soup.title else "No title"
        paragraphs = soup.find_all('p')
        text = "\n\n".join(p.get_text() for p in paragraphs)

        if (
            "are you a robot" in title.lower()
            or "are you a robot" in text.lower()
            or "enable javascript" in text.lower()
            or len(text.strip()) < 500
        ):
            raise ValueError("Bot protection detected or content too short.")

        return title, text
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load article: {e}")
        return None, None

def analyze_content(title, article_text):
    prompt = (
        f"You are an SEO expert. Analyze the following article titled \"{title}\" for SEO quality. "
        "List:\n"
        "1. Overused or underused keywords\n"
        "2. Sections that are too vague or too short\n"
        "3. Suggestions for improving clarity and keyword optimization\n\n"
        f"{article_text}"
    )
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert SEO analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def rewrite_section(original, keyword, title=""):
    prompt = (
        f"The article is titled: \"{title}\".\n\n"
        f"Rewrite the following paragraph to improve SEO by naturally incorporating the keyword \"{keyword}\". "
        "Keep the tone consistent and make sure it doesn’t sound robotic:\n\n"
        f"{original}"
    )
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an SEO content rewriter."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def start_analysis():
    link = link_entry.get().strip()
    if not link:
        messagebox.showwarning("Missing Input", "Please paste a URL first.")
        return

    result_box.delete("1.0", tk.END)
    title, article = read_article_from_link(link)
    if title and article:
        result_box.insert(tk.END, f"Loaded article: {title}\n\n")
        result_box.insert(tk.END, "Analyzing content...\n\n")
        analysis = analyze_content(title, article)
        result_box.insert(tk.END, analysis)
        title_var.set(title)

def start_analysis_from_file():
    try:
        title, article = read_article_from_file("input.txt")
        title_var.set(title)
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, f"Loaded article from input.txt: {title}\n\n")
        result_box.insert(tk.END, "Analyzing content...\n\n")
        analysis = analyze_content(title, article)
        result_box.insert(tk.END, analysis)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load input.txt: {e}")

def start_analysis_from_manual():
    article = manual_input.get("1.0", tk.END).strip()
    if not article:
        messagebox.showwarning("Empty Text", "Please paste some article text before analyzing.")
        return

    title = "Manual Entry"
    title_var.set(title)
    result_box.delete("1.0", tk.END)
    result_box.insert(tk.END, f"Loaded article from pasted text: {title}\n\n")
    result_box.insert(tk.END, "Analyzing content...\n\n")
    analysis = analyze_content(title, article)
    result_box.insert(tk.END, analysis)

def start_rewrite():
    paragraph = rewrite_input.get("1.0", tk.END).strip()
    keyword = keyword_entry.get().strip()
    title = title_var.get()

    if not paragraph or not keyword:
        messagebox.showwarning("Missing Input", "Please fill both the paragraph and keyword.")
        return

    result_box.insert(tk.END, "\n\nRewriting Paragraph...\n")
    rewritten = rewrite_section(paragraph, keyword, title)
    result_box.insert(tk.END, f"\nRewritten Paragraph:\n\n{rewritten}\n")

# GUI Setup
root = tk.Tk()
root.title("RankCraft - SEO Optimizer")
root.geometry("1000x850")

title_var = tk.StringVar()

tk.Label(root, text="Paste Article URL (Optional):", font=("Arial", 12)).pack(pady=5)
link_entry = tk.Entry(root, width=100, font=("Arial", 12))
link_entry.pack(pady=5)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Analyze from URL", command=start_analysis, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Analyze from input.txt", command=start_analysis_from_file, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Analyze from Pasted Text", command=start_analysis_from_manual, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)

tk.Label(root, text="Paste Full Article Text (Optional):", font=("Arial", 11)).pack()
manual_input = scrolledtext.ScrolledText(root, height=8, font=("Arial", 11), wrap=tk.WORD)
manual_input.pack(padx=10, pady=5, fill="x")

result_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 11), height=20)
result_box.pack(padx=10, pady=10, expand=True, fill='both')

tk.Label(root, text="--- Rewrite Section ---", font=("Arial", 12, "bold")).pack(pady=5)

tk.Label(root, text="Paragraph to Rewrite:", font=("Arial", 11)).pack()
rewrite_input = scrolledtext.ScrolledText(root, height=5, font=("Arial", 11), wrap=tk.WORD)
rewrite_input.pack(padx=10, pady=5, fill="x")

tk.Label(root, text="Keyword to Use:", font=("Arial", 11)).pack()
keyword_entry = tk.Entry(root, font=("Arial", 11), width=40)
keyword_entry.pack(pady=5)

tk.Button(root, text="Rewrite Paragraph", command=start_rewrite, font=("Arial", 12)).pack(pady=10)

root.mainloop()
