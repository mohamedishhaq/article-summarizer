# 📰 Article Summarizer & Q&A Tool  

A Python CLI tool that uses **Google Gemini 2.5 Flash** to:  
- Summarize news/articles in **3–4 factual sentences** at different temperatures.  
- Provide **interactive Q&A** about the article (minimum 3 questions).  
- Save outputs and observations in `observations.md`.  

---

## 🚀 Features
- Summarizes the same article at **three temperatures** (0.1, 0.7, 1.0).  
- Provides an **interactive Q&A session** with at least 3 required questions.  
- Generates a ready-to-fill **observations.md** file with summaries, answers, and notes.  
- Handles long articles with **automatic truncation** to fit Gemini’s context window.  

---

## 📂 Project Structure
```week-4/
│── article_summarizer.py # Main script
│── article.txt # Input article text (user-provided)
│── observations.md # Auto-generated after running
```

---

## 🛠️ Requirements
- Python 3.8+  
- Google Generative AI Python SDK  

Install dependencies:
```bash
pip install google-generativeai
