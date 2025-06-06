# RankCraft – AI SEO Optimizer

RankCraft is an AI-powered SEO analysis tool built with Python and GPT-4.  
It helps improve blog content by analyzing keyword usage, identifying weak sections, and suggesting rewrites.

## Features
- Analyze SEO from:
  - URLs (via Playwright browser scraping)
  - `input.txt`
  - Manually pasted content
- GPT-powered section rewrite with keyword injection
- Tkinter GUI for easy use

## How to Run

1. Clone the repo:
   ```bash
   git clone https://github.com/taimuradam/rankcraft-ai.git
   cd rankcraft-seo-optimizer
   ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    playwright install
    ```

3. Create a .env file:
    ```bash
    OPENAI_API_KEY=your-key-here
    ```

4. Launch the GUI:
    ```bash
    python rankcraft_gui.py
    ```

## Requirements
- Python 3.9+
- openai
- playwright
- bs4
- tkinter (comes with Python)

## License
MIT

## Author
Taimur Adam