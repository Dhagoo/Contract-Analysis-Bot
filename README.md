# 🛡️ LexGuard ULTRA | Forensic Legal AI for Indian SMEs

LexGuard ULTRA is a premium, AI-powered contract analysis platform designed specifically for Indian Small and Medium Enterprises (SMEs). It leverages GPT-4o architecture to decode complex legalese, identify hidden liabilities, and ensure compliance with Indian law.

## 🚀 Key Features

- **Forensic Contract Audit**: Upload PDF, DOCX, or TXT contracts for instant risk assessment.
- **Visual Risk Index**: Dynamic gauge showing composite risk scores (1-10).
- **Intelligent Clause Analysis**: Granular breakdown of clauses into "Business Meaning," "The Trap," and "Actionable Advice."
- **Entity Extraction**: Automatically identifies Parties, Dates, Jurisdictions, and Financial Amounts.
- **Cyber-Industrial UI**: A high-performance, glassmorphic dashboard built for clarity and speed.

## 🛠️ Architecture

- **Frontend**: Streamlit (Python) with custom CSS injection for premium aesthetics.
- **Backend**: FastAPI (Python) orchestrating the NLP and LLM pipelines.
- **NLP Engine**: spaCy (`en_core_web_sm`) for entity extraction and pattern-based segmentation.
- **LLM Engine**: GPT-4o / Claude 3 integration for deep legal reasoning (includes heuristic demo mode).

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Dhagoo/Contract-Analysis-Bot.git
   cd Contract-Analysis-Bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

3. **Configure Environment**:
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_key_here
   LLM_PROVIDER=openai
   ```

## 🏃 Launching the Application

Start the **Backend API** (Port 8001):
```bash
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8001
```

Start the **Frontend Dashboard** (Port 8501):
```bash
streamlit run frontend/app.py
```

## 🛡️ Security & Privacy
- **Automatic .gitignore**: Ensures `.env` and uploaded contracts are never pushed to version control.
- **Audit Trails**: Local logs maintained in `logs/audit_trail.json` for internal review.

---
*Developed for Bharat's growing business ecosystem.*
