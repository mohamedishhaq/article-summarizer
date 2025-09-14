#!/usr/bin/env python3
"""
article_summarizer.py - Week 4 Assignment
News Summarizer & Q&A Tool using Google Gemini 2.5 Flash

Requirements:
    pip install google-generativeai

Usage:
    1. Save your article text in a file named "article.txt"
    2. Run: python article_summarizer.py
"""

import textwrap
import google.generativeai as genai
from pathlib import Path

# ---------------- CONFIG ----------------
API_KEY = "AIzaSyA7wqgOGl5T8BoUXH0j0GqHuAscFfMbo84"  # 🔑 Put your Gemini API key here
MODEL_NAME = "gemini-2.5-flash"
TEMPERATURES = [0.1, 0.7, 1.0]

# Find the folder where this script is located
SCRIPT_DIR = Path(__file__).resolve().parent
ARTICLE_FILE = SCRIPT_DIR / "article.txt"


# ---------------- HELPERS ----------------
def count_words(s: str) -> int:
    return len(s.split())


def safe_truncate(text: str, max_chars: int = 15000) -> str:
    """Truncate article if it's too long for Gemini context."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "\n\n[TRUNCATED - original article longer]"


# ---------------- LLM CALL ----------------
def call_llm_gemini(prompt: str, model: str = MODEL_NAME, temperature: float = 0.7, max_output_tokens: int = 1024):
    if not API_KEY or API_KEY.strip() == "":
        raise RuntimeError("❌ Please paste your Gemini API key into API_KEY in this script.")

    genai.configure(api_key=API_KEY)
    gen_model = genai.GenerativeModel(model)

    resp = gen_model.generate_content(
        prompt,
        generation_config={
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
        },
    )

    # --- Debug info ---
    if resp.prompt_feedback:
        print(f"[DEBUG] Prompt feedback: {resp.prompt_feedback}")
    if resp.candidates:
        print(f"[DEBUG] Finish reason: {resp.candidates[0].finish_reason}")

    # --- Extract output ---
    try:
        if hasattr(resp, "text") and resp.text:
            return resp.text.strip()
    except Exception:
        pass

    if resp.candidates:
        parts = []
        for c in resp.candidates:
            if c.content and c.content.parts:
                parts.extend([getattr(p, "text", "") for p in c.content.parts if getattr(p, "text", None)])
        if parts:
            return " ".join(parts).strip()

    return "[⚠️ No output received — likely cut off by max tokens]"

# ---------------- PROMPT BUILDERS ----------------
def summary_prompt(article_text: str, sentence_count_min: int = 3, sentence_count_max: int = 4):
    return textwrap.dedent(f"""
    Please provide a {sentence_count_min}-{sentence_count_max} sentence summary of the article below.
    Keep it factual and concise. Do not add invented facts or outside information.

    Article:
    {article_text}
    """)


def qa_prompt(article_text: str, question: str):
    return textwrap.dedent(f"""
    Based on the article below, answer the question. 
    Provide a concise, factual answer. 
    If the article doesn't contain the info, say "Not stated in article."

    Question: {question}

    Article:
    {article_text}
    """)


# ---------------- MAIN WORKFLOW ----------------
def run_summarization_flow(article_text: str):
    article_text = article_text.strip()
    article_text_trunc = safe_truncate(article_text, max_chars=14000)
    words = count_words(article_text)
    chars = len(article_text)

    print(f"\nArticle length: {words} words, {chars} characters.\n")

    summaries = {}
    for t in TEMPERATURES:
        prompt = summary_prompt(article_text_trunc)
        summary = call_llm_gemini(prompt, model=MODEL_NAME, temperature=t)
        summaries[str(t)] = summary
        print("=" * 60)
        print(f"Temperature {t} summary:\n")
        print(summary + "\n")

    # Interactive Q&A (at least 3 questions)
    print("=" * 60)
    print("Interactive Q&A: Ask at least 3 questions about the article.")
    answers = []
    q_count = 0
    try:
        while q_count < 3:
            q = input(f"Question {q_count+1}: ").strip()
            if not q:
                print("Please type a non-empty question.")
                continue
            prompt = qa_prompt(article_text_trunc, q)
            ans = call_llm_gemini(prompt, model=MODEL_NAME, temperature=0.2, max_output_tokens=400)
            answers.append({"question": q, "answer": ans})
            print("\nAnswer:\n" + ans + "\n")
            q_count += 1

        # Optional extra questions until user exits
        while True:
            extra = input("Ask another question or press Enter to finish (type 'quit' to exit): ").strip()
            if extra.lower() in ["", "quit", "q", "exit"]:
                break
            prompt = qa_prompt(article_text_trunc, extra)
            ans = call_llm_gemini(prompt, model=MODEL_NAME, temperature=0.2, max_output_tokens=400)
            answers.append({"question": extra, "answer": ans})
            print("\nAnswer:\n" + ans + "\n")

    except KeyboardInterrupt:
        print("\nInteractive Q&A aborted by user.\n")

    # Save observations
    obs_filename = SCRIPT_DIR / "observations.md"
    with open(obs_filename, "w", encoding="utf-8") as f:
        f.write("# observations.md\n\n")
        f.write(f"Article word count: {words}\n\n")
        f.write("## Summaries at different temperatures\n\n")
        for t, s in summaries.items():
            f.write(f"### Temperature {t}\n\n")
            f.write("Summary:\n\n")
            f.write(s + "\n\n")
            f.write("Observations (style / detail / factuality):\n\n- \n\n")
        f.write("## Q&A\n\n")
        for idx, qa in enumerate(answers, 1):
            f.write(f"### Q{idx}: {qa['question']}\n\nAnswer:\n\n{qa['answer']}\n\nNotes:\n\n- \n\n")
    print(f"Observations template written to {obs_filename}")


# ---------------- CLI ----------------
def main():
    if not ARTICLE_FILE.exists():
        print(f"❌ Could not find '{ARTICLE_FILE}'. Please create it with your article text.")
        return

    article_text = ARTICLE_FILE.read_text(encoding="utf-8").strip()
    if not article_text:
        print("❌ 'article.txt' is empty. Please add article text.")
        return

    run_summarization_flow(article_text)


if __name__ == "__main__":
    main()
