# 📝 ScanGrade AI — Multimodal Handwritten Exam Evaluator

> **DITE Hackathon 2026-27 Submission**  
> **Theme:** Education  
> **Repository:** [https://github.com/salmanhyder850/scangrade-ai](https://github.com/salmanhyder850/scangrade-ai)  
> **Live Web App:** [https://scangrade-ai.streamlit.app](https://scangrade-ai.streamlit.app)  


---

## 📌 Problem Statement & Impact
In educational institutions, professors and teaching assistants spend **15–25 hours per exam cycle** manually marking subjective handwritten answer sheets. This manual workflow suffers from:
1. **Grading Fatigue & Inconsistency:** Criteria applied to the 1st paper often drift by the 50th paper.
2. **Delayed Feedback:** Students receive numerical scores weeks later with zero explanation of *where* or *why* points were deducted.
3. **Failure of Traditional OCR:** Traditional OCR tools (e.g. Tesseract) fail completely on messy student handwriting, irregular pen pressure, and mathematical equations.

**ScanGrade AI** solves this by providing an end-to-end multimodal grading and diagnostic engine that takes camera photos or scans of student handwriting, deciphers the ink with state-of-the-art vision AI, and strictly evaluates the work against the teacher's customizable marking rubric.

---

## 🤖 AI Architecture: Beyond Just a Chatbot
ScanGrade AI is **not** a chatbot. It is a multi-stage automated document intelligence pipeline:

```
[Student Handwritten Paper] (Photo/Scan/Webcam)
            │
            ▼
┌────────────────────────────────────────────────────────┐
│  Stage 1: Multimodal Computer Vision (Gemini 2.5)      │
│  • Reads raw handwriting ink directly from pixels       │
│  • Transcribes formulas, cursive text, and numbers    │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  Stage 2: Strict Structured Rubric Reasoner            │
│  • Cross-checks each step against teacher criteria    │
│  • Computes point allocation & deductions with reasons │
│  • Generates structured JSON schema output             │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  Stage 3: Pedagogical Diagnostic Engine & Analytics    │
│  • Identifies cognitive knowledge gaps                 │
│  • Plotly interactive score distribution & charts      │
│  • Generates digital student marksheets & CSV report   │
└────────────────────────────────────────────────────────┘
```

---

## 💻 Tech Stack
- **Web Application & UI:** Streamlit (`>=1.35.0`)
- **Multimodal AI Engine:** Google GenAI SDK (`google-genai>=0.1.1`, Gemini 2.5 Flash / 2.0 Flash)
- **Computer Vision & Graphics:** Pillow (`PIL`)
- **Data & Analytics:** Pandas, Plotly Express & Graph Objects
- **Deployment Platform:** Streamlit Community Cloud (Zero-cost hosting)

---

## 🚀 Quickstart: Run Locally on Your Computer

### Prerequisites
- Python 3.10+ installed
- Git installed
- Google Gemini API Key (free from [Google AI Studio](https://aistudio.google.com))

### Step 1: Clone Repository & Move Into Folder
```bash
git clone https://github.com/salmanhyder850/scangrade-ai.git
cd scangrade-ai
```

### Step 2: Create and Activate Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
streamlit run app.py
```
Your default browser will launch at `http://localhost:8501`.

> **Tip for Instant Testing:** The app includes a built-in **"Demo / Mock Mode"** switch and pre-rendered sample exam papers (Physics, CS, Math). You can evaluate right away even before entering an API key!




## 👥 Team Details
- **Team Name:** [Triple Helix]
- **Members:** [Sharjeel Arain, Salman Hyder, Usama Ali]
- **Event:** DITE Hackathon 2026-27
