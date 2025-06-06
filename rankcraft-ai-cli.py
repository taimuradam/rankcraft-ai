import os
from openai import OpenAI
from dotenv import load_dotenv
import urllib.request
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def read_article_from_link(link):
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
        print(f"\nBot protection detected.")
        print(f"Fetched title: {title}")
        print("Try pasting the article manually into input.txt instead.\n")
        exit(1)

    return title, text



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

def rewrite_section(original, keyword, title):
    prompt = (
        f"The article is titled: \"{title}\".\n\n"
        f"Rewrite the following paragraph to improve SEO by naturally incorporating the keyword \"{keyword}\". "
        "Keep the tone consistent with the title and make sure it doesn’t sound robotic:\n\n"
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

def main():
    print("RankCraft CLI - AI SEO Optimizer")

    form = input("\nDo you want to read from input or a link? (input/link): ").lower()
    if form == 'input':
        title, article = read_article_from_file("input.txt")
        print(f"\nLoaded article: {title}\n")
    elif form == 'link':
        print("\nPaste the link:")
        link = input("> ")
        title, article = read_article_from_link(link)
        print(f"\nLoaded article: {title}\n")

    print("\nAnalyzing content for SEO...\n")
    analysis = analyze_content(title, article)
    print("SEO Analysis:\n")
    print(analysis)

    rewrite = input("\nDo you want to rewrite a section? (y/n): ").lower()
    if rewrite == 'y':
        print("\nPaste the paragraph you want to improve:\n")
        original = input("> ")
        keyword = input("Enter the main keyword to include: ")
        rewritten = rewrite_section(original, keyword)
        print("\nRewritten Paragraph:\n")
        print(rewritten)

if __name__ == "__main__":
    main()
