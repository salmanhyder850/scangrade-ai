import io
import json
import os
import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Load local environment variables if present
load_dotenv()

# ----------------- PAGE CONFIGURATION -----------------
st.set_page_config(
    page_title="ScanGrade AI — Handwritten Exam Evaluator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for polished hackathon presentation
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #4B5563;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: pre-wrap;
        background-color: #F1F5F9;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563EB !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- API & CONFIGURATION -----------------
API_KEY = os.getenv("GEMINI_API_KEY", "")
try:
    if not API_KEY and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

# ----------------- PRESET EXAM SAMPLES -----------------
PRESETS = {
    "Physics (Ohm's Law & Circuit Calculation)": {
        "question": "State Ohm's Law and calculate the current flowing through a resistor if V = 12V and R = 4 Ω.",
        "rubric": """1. Correct statement of Ohm's Law including temperature/physical state condition (4 marks)
2. Mathematical Formula (V = I * R or I = V / R) (2 marks)
3. Step-by-step substitution and numerical calculation (3 marks)
4. Correct SI unit (Amperes / A) (1 mark)
Total: 10 Marks""",
        "student_name": "Hamza Tariq",
        "roll_no": "2026-PHY-042",
        "subject": "Physics I",
        "handwritten_lines": [
            "Student: Hamza Tariq  |  Roll: 2026-PHY-042  |  Sub: Physics",
            "Q1. State Ohm's Law & find current for V = 12V, R = 4 Ohm.",
            "Ans: Ohm's law states that current flowing through a conductor",
            "is directly proportional to potential difference across ends,",
            "provided temperature remains constant. Formula: V = I * R",
            "Calculation: I = V / R  =>  I = 12 / 4 = 3 Amperes.",
            "Hence the calculated current through circuit is 3 A."
        ]
    },
    "Computer Science (Binary Search Algorithm)": {
        "question": "Explain the Binary Search algorithm, state its preconditions, and derive its worst-case time complexity.",
        "rubric": """1. Definition of Binary Search and divide-and-conquer approach (3 marks)
2. Crucial precondition: array must be sorted (2 marks)
3. Step-by-step search procedure (mid-point calculation and range halving) (3 marks)
4. Time complexity derivation: O(log n) with justification (2 marks)
Total: 10 Marks""",
        "student_name": "Sarah Khan",
        "roll_no": "2026-CS-109",
        "subject": "Data Structures & Algorithms",
        "handwritten_lines": [
            "Student: Sarah Khan  |  Roll: 2026-CS-109  |  Sub: CS - DSA",
            "Q: Explain Binary Search, preconditions, & time complexity.",
            "Ans: Binary Search is a divide-and-conquer algorithm to find",
            "an element in a list. Precondition: Array MUST be sorted.",
            "Procedure: Compute mid = (low + high)/2. If key == arr[mid], found.",
            "If key < arr[mid], search left half, else search right half.",
            "Complexity: Search space halves each step: N, N/2, N/4 ... N/2^k = 1.",
            "Thus k = log2(N). Time Complexity is O(log n)."
        ]
    },
    "Mathematics (Quadratic Formula Derivation)": {
        "question": "Solve the quadratic equation 2x^2 + 5x - 3 = 0 using the quadratic formula, showing all substitution steps.",
        "rubric": """1. Identification of coefficients a = 2, b = 5, c = -3 (2 marks)
2. Correct Quadratic Formula: x = (-b ± √(b² - 4ac)) / (2a) (2 marks)
3. Step-by-step discriminant evaluation: 5² - 4(2)(-3) = 25 + 24 = 49 (3 marks)
4. Accurate roots computation: x = 0.5 and x = -3 (3 marks)
Total: 10 Marks""",
        "student_name": "Bilal Ahmed",
        "roll_no": "2026-MATH-015",
        "subject": "Applied Mathematics",
        "handwritten_lines": [
            "Student: Bilal Ahmed  |  Roll: 2026-MATH-015  |  Sub: Math",
            "Q: Solve 2x^2 + 5x - 3 = 0 using quadratic formula.",
            "Ans: Given 2x^2 + 5x - 3 = 0. Here a = 2, b = 5, c = -3.",
            "Formula: x = [-b +- sqrt(b^2 - 4ac)] / (2a)",
            "Discriminant = (5)^2 - 4*(2)*(-3) = 25 + 24 = 49.",
            "x = [-5 +- sqrt(49)] / (2*2) = [-5 +- 7] / 4.",
            "Root 1: (-5 + 7)/4 = 2/4 = 0.5",
            "Root 2: (-5 - 7)/4 = -12/4 = -3. Roots are {0.5, -3}."
        ]
    }
}

# ----------------- HELPER: GENERATE REALISTIC HANDWRITTEN EXAM IMAGE -----------------
def generate_handwritten_sheet_image(lines_of_text):
    """
    Generates an in-memory realistic lined notebook exam answer sheet.
    Simulates ruled student paper with red margin and blue ruling lines.
    """
    width, height = 900, 600
    img = Image.new("RGB", (width, height), color=(253, 252, 248))
    draw = ImageDraw.Draw(img)

    # Ruled notebook lines (horizontal blue lines)
    for y in range(90, height - 20, 36):
        draw.line([(40, y), (width - 40, y)], fill=(215, 230, 248), width=1)

    # Red vertical margin line
    margin_x = 120
    draw.line([(margin_x, 30), (margin_x, height - 30)], fill=(255, 175, 175), width=2)
    # Secondary faint guideline
    draw.line([(margin_x - 6, 30), (margin_x - 6, height - 30)], fill=(255, 215, 215), width=1)

    # Attempt to load a default font
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    # Draw header and text with subtle handwriting variation
    header = lines_of_text[0] if lines_of_text else "Student Answer Sheet"
    draw.text((margin_x + 15, 45), header, fill=(65, 75, 90), font=font)

    current_y = 100
    for idx, line in enumerate(lines_of_text[1:]):
        # Slightly vary indentation and color tone to mimic blue ballpoint pen
        pen_color = (18, 38, 115) if idx % 2 == 0 else (12, 30, 95)
        indent = margin_x + 15 + ((idx % 3) * 2)
        draw.text((indent, current_y), line, fill=pen_color, font=font)
        current_y += 36

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# ----------------- AI MULTIMODAL EVALUATION ENGINE -----------------
def evaluate_exam_with_gemini(api_key, model_name, image_bytes, exam_question, rubric_criteria):
    """
    Calls Google GenAI SDK (Gemini Multimodal Vision) to decipher handwriting,
    verify academic reasoning, and score against the teacher's rubric criteria.
    """
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    prompt = f"""You are a senior academic examiner and grading specialist.
You are given an image of a student's HANDWRITTEN examination answer sheet.

EXAM QUESTION:
{exam_question}

TEACHER'S MARKING RUBRIC & CRITERIA:
{rubric_criteria}

INSTRUCTIONS:
1. Carefully inspect the handwritten ink in the image and transcribe the student's answer verbatim.
2. Read the student details (name, roll number, subject) if present.
3. Compare the handwritten solution step-by-step against each criterion in the teacher's rubric.
4. Award accurate numerical marks for each criterion, providing clear academic justification for deductions or points awarded.
5. Identify specific strengths and any missing mathematical steps, formulas, or conceptual errors.
6. Provide constructive feedback remarks.

Return ONLY a valid JSON object matching this schema:
{{
    "transcribed_handwriting": "Complete text deciphered from the handwritten answer sheet",
    "student_info": "Student Name / Roll / Subject extracted from image (or 'Unknown Student')",
    "total_marks_awarded": 8.5,
    "max_marks_possible": 10.0,
    "criteria_breakdown": [
        {{
            "criterion": "Criterion Name",
            "marks_awarded": 3.5,
            "max_marks": 4.0,
            "deduction_reason": "Specific reason for points awarded or deducted"
        }}
    ],
    "strengths": ["Clear definition", "Correct formula stated"],
    "mistakes_or_missing_steps": ["Minor calculation error in step 3"],
    "knowledge_gaps": ["Missed temperature dependency condition"],
    "examiner_feedback": "Strong conceptual understanding. Pay closer attention to final unit notation."
}}
"""

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type="image/png"
    )

    response = client.models.generate_content(
        model=model_name,
        contents=[image_part, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1
        )
    )

    clean_text = response.text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    if clean_text.startswith("```"):
        clean_text = clean_text[3:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]

    return json.loads(clean_text.strip())

# ----------------- MOCK / DEMO SIMULATION FALLBACK -----------------
def generate_mock_evaluation(selected_preset_key, exam_question, rubric_criteria):
    """
    Fallback mock evaluator to ensure the app works 100% reliably
    even during a live pitch if API keys or network are temporarily unavailable.
    """
    if "Physics" in selected_preset_key:
        return {
            "transcribed_handwriting": (
                "Student: Hamza Tariq | Roll: 2026-PHY-042 | Sub: Physics\n"
                "Q1. State Ohm's Law & find current for V = 12V, R = 4 Ohm.\n"
                "Ans: Ohm's law states that current flowing through a conductor is directly "
                "proportional to potential difference across ends, provided temperature remains constant. "
                "Formula: V = I * R\nCalculation: I = V / R => I = 12 / 4 = 3 Amperes.\n"
                "Hence the calculated current through circuit is 3 A."
            ),
            "student_info": "Hamza Tariq (Roll No: 2026-PHY-042)",
            "total_marks_awarded": 10.0,
            "max_marks_possible": 10.0,
            "criteria_breakdown": [
                {"criterion": "Ohm's Law statement with constant temperature condition", "marks_awarded": 4.0, "max_marks": 4.0, "deduction_reason": "Complete and accurate scientific definition."},
                {"criterion": "Mathematical Formula (V = IR or I = V/R)", "marks_awarded": 2.0, "max_marks": 2.0, "deduction_reason": "Correct mathematical relationship stated."},
                {"criterion": "Step-by-step substitution and numerical answer", "marks_awarded": 3.0, "max_marks": 3.0, "deduction_reason": "Flawless arithmetic: 12 / 4 = 3."},
                {"criterion": "Correct SI units (Amperes / A)", "marks_awarded": 1.0, "max_marks": 1.0, "deduction_reason": "Properly denoted unit as 'Amperes' and 'A'."}
            ],
            "strengths": [
                "Mentioned the critical temperature constancy condition",
                "Clean derivation from V = IR to I = V/R",
                "Explicitly stated standard SI units"
            ],
            "mistakes_or_missing_steps": ["None detected in this answer sheet."],
            "knowledge_gaps": ["No conceptual gaps found. Exemplary mastery of Ohm's Law."],
            "examiner_feedback": "Outstanding work! The student demonstrates thorough conceptual grasp and precise mathematical execution."
        }
    else:
        return {
            "transcribed_handwriting": "Student answer successfully deciphered from handwritten sheet.",
            "student_info": "Assessed Student",
            "total_marks_awarded": 9.0,
            "max_marks_possible": 10.0,
            "criteria_breakdown": [
                {"criterion": "Conceptual Foundation", "marks_awarded": 3.5, "max_marks": 4.0, "deduction_reason": "Good understanding, minor detail omitted."},
                {"criterion": "Formulas & Equations", "marks_awarded": 2.0, "max_marks": 2.0, "deduction_reason": "Exact formulas used."},
                {"criterion": "Procedural Execution", "marks_awarded": 2.5, "max_marks": 3.0, "deduction_reason": "All steps followed clearly."},
                {"criterion": "Final Accuracy & Units", "marks_awarded": 1.0, "max_marks": 1.0, "deduction_reason": "Accurate final answer."}
            ],
            "strengths": ["Well-structured answer", "Clear handwriting", "Accurate formula application"],
            "mistakes_or_missing_steps": ["Could elaborate slightly more on edge conditions."],
            "knowledge_gaps": ["Minor edge cases in boundary conditions."],
            "examiner_feedback": "Very strong performance overall with neat presentation."
        }

# ----------------- SIDEBAR CONTROLS -----------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/exam.png", width=64)
    st.header("⚙️ Evaluation Setup")

    api_key_input = st.text_input(
        "Gemini API Key",
        value=API_KEY,
        type="password",
        help="Get a free API key at https://aistudio.google.com"
    )

    model_choice = st.selectbox(
        "Multimodal AI Model",
        ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"],
        index=0,
        help="Gemini 2.5 Flash is recommended for fastest OCR & handwriting vision."
    )

    mock_mode = st.toggle("🧪 Demo / Mock Mode (No Key Needed)", value=(not bool(api_key_input)))
    if mock_mode:
        st.info("💡 Running in instant demo mode. Great for testing without an API key!")

    st.markdown("---")
    st.subheader("📚 Quick Test Exam Presets")
    selected_preset = st.selectbox("Choose a pre-built exam:", list(PRESETS.keys()))

    if st.button("📥 Load Selected Preset Exam", use_container_width=True):
        preset_data = PRESETS[selected_preset]
        st.session_state["exam_q"] = preset_data["question"]
        st.session_state["rubric"] = preset_data["rubric"]
        sample_buf = generate_handwritten_sheet_image(preset_data["handwritten_lines"])
        st.session_state["current_image"] = sample_buf.getvalue()
        st.session_state["preset_key"] = selected_preset
        st.success(f"Loaded: {selected_preset}")
        st.rerun()

    st.markdown("---")
    st.caption("🏆 Built for DITE Hackathon 2026-27 | Theme: Education")

# ----------------- MAIN INTERFACE -----------------
st.markdown('<div class="main-header">📝 ScanGrade AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multimodal Computer Vision • Handwriting Deciphering • Automated Step-by-Step Exam Grading</div>', unsafe_allow_html=True)

# Layout: Step 1 (Question & Rubric) + Step 2 (Exam Paper Input)
col_setup, col_paper = st.columns([1, 1], gap="large")

with col_setup:
    st.subheader("1️⃣ Exam Question & Marking Rubric")
    default_q = PRESETS["Physics (Ohm's Law & Circuit Calculation)"]["question"]
    default_rubric = PRESETS["Physics (Ohm's Law & Circuit Calculation)"]["rubric"]

    current_q = st.session_state.get("exam_q", default_q)
    current_rubric = st.session_state.get("rubric", default_rubric)

    exam_question = st.text_area("Question Paper Prompt", value=current_q, height=100)
    rubric_criteria = st.text_area(
        "Teacher's Strict Marking Rubric (Criteria & Points)",
        value=current_rubric,
        height=170,
        help="Define criteria and marks distribution. The AI enforces these exact points."
    )

with col_paper:
    st.subheader("2️⃣ Student's Handwritten Exam Sheet")

    paper_source = st.radio(
        "Source of Exam Sheet:",
        ["Sample Preset Sheet", "Upload Photo (PNG/JPG)", "Webcam / Camera"],
        horizontal=True
    )

    image_bytes_to_grade = None

    if paper_source == "Sample Preset Sheet":
        if "current_image" not in st.session_state:
            default_preset = PRESETS["Physics (Ohm's Law & Circuit Calculation)"]
            buf = generate_handwritten_sheet_image(default_preset["handwritten_lines"])
            st.session_state["current_image"] = buf.getvalue()
            st.session_state["preset_key"] = "Physics (Ohm's Law & Circuit Calculation)"

        image_bytes_to_grade = st.session_state["current_image"]
        st.image(image_bytes_to_grade, caption="Active Handwritten Answer Sheet", use_container_width=True)

    elif paper_source == "Upload Photo (PNG/JPG)":
        uploaded = st.file_uploader("Upload student answer sheet image", type=["png", "jpg", "jpeg"])
        if uploaded:
            image_bytes_to_grade = uploaded.read()
            st.image(image_bytes_to_grade, caption="Uploaded Answer Sheet", use_container_width=True)
        else:
            st.info("👆 Upload an image of student handwriting, or switch to 'Sample Preset Sheet' above.")

    elif paper_source == "Webcam / Camera":
        camera_img = st.camera_input("Capture handwritten page with your laptop camera")
        if camera_img:
            image_bytes_to_grade = camera_img.read()
            st.image(image_bytes_to_grade, caption="Live Captured Answer Sheet", use_container_width=True)

# Evaluation Trigger
st.markdown("---")
eval_col1, eval_col2, eval_col3 = st.columns([1, 2, 1])
with eval_col2:
    start_eval = st.button("🚀 Scan Handwriting & Grade Exam", type="primary", use_container_width=True)

if start_eval:
    if not image_bytes_to_grade:
        st.error("⚠️ Please provide a handwritten answer sheet (upload, sample, or camera).")
    elif not mock_mode and not api_key_input:
        st.error("⚠️ Please enter a Gemini API Key in the sidebar or enable 'Demo / Mock Mode'.")
    else:
        with st.spinner("🔍 Reading handwriting ink, cross-checking rubric criteria, and computing mark distribution..."):
            try:
                if mock_mode or not api_key_input:
                    preset_name = st.session_state.get("preset_key", "Physics")
                    results = generate_mock_evaluation(preset_name, exam_question, rubric_criteria)
                else:
                    results = evaluate_exam_with_gemini(
                        api_key=api_key_input,
                        model_name=model_choice,
                        image_bytes=image_bytes_to_grade,
                        exam_question=exam_question,
                        rubric_criteria=rubric_criteria
                    )
                st.session_state["eval_results"] = results
                st.session_state["last_graded_image"] = image_bytes_to_grade
                st.toast("✅ Grading complete!", icon="🎉")
            except Exception as e:
                st.error(f"❌ Error during evaluation: {e}")
                st.info("Tip: You can enable 'Demo / Mock Mode' in the sidebar to test without an external API connection.")

# ----------------- DISPLAY GRADED RESULTS -----------------
if "eval_results" in st.session_state:
    res = st.session_state["eval_results"]
    st.markdown("---")
    st.markdown("## 📊 Official Evaluation & Diagnostic Report")

    # High-level Metrics Row
    marks = float(res.get("total_marks_awarded", 0))
    max_m = float(res.get("max_marks_possible", 10))
    pct = (marks / max_m * 100) if max_m > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("👤 Student Candidate", res.get("student_info", "Verified Candidate"))
    with m2:
        st.metric("🎯 Marks Awarded", f"{marks:g} / {max_m:g}")
    with m3:
        st.metric("📈 Percentage", f"{pct:.1f}%")
    with m4:
        status_label = "Grade: A+ (Distinction)" if pct >= 90 else ("Grade: A (Pass)" if pct >= 80 else ("Grade: B (Satisfactory)" if pct >= 60 else "Needs Remediation"))
        st.metric("🏆 Evaluation Status", status_label)

    # Multi-tab Dashboard
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Rubric Scorecard",
        "🖋️ Deciphered Handwriting",
        "📈 Analytics & Visuals",
        "💡 Knowledge Gap Diagnosis"
    ])

    with tab1:
        st.subheader("Step-by-Step Rubric Criteria Breakdown")
        crit_data = res.get("criteria_breakdown", [])
        if crit_data:
            df_crit = pd.DataFrame(crit_data)
            df_crit = df_crit.rename(columns={
                "criterion": "Rubric Criterion",
                "marks_awarded": "Marks Awarded",
                "max_marks": "Max Marks",
                "deduction_reason": "Examiner Justification / Deduction Reason"
            })
            st.dataframe(df_crit, use_container_width=True, hide_index=True)

        st.markdown("---")
        col_s, col_w = st.columns(2)
        with col_s:
            st.markdown("#### ✅ Demonstrated Academic Competencies")
            for strength in res.get("strengths", []):
                st.markdown(f"• **{strength}**")
        with col_w:
            st.markdown("#### ⚠️ Missing Steps / Point Deductions")
            for mistake in res.get("mistakes_or_missing_steps", []):
                st.markdown(f"• {mistake}")

        st.markdown("---")
        st.info(f"👨‍🏫 **Examiner's Remarks:** {res.get('examiner_feedback', 'Candidate showed good engagement with the problem.')}")

    with tab2:
        st.subheader("Multimodal AI Optical Handwriting Transcription")
        st.caption("Side-by-side comparison of physical handwritten ink vs. decoded digital text:")

        col_orig, col_trans = st.columns([1, 1], gap="medium")
        with col_orig:
            st.markdown("##### 📷 Physical Answer Sheet")
            if "last_graded_image" in st.session_state:
                st.image(st.session_state["last_graded_image"], use_container_width=True)
        with col_trans:
            st.markdown("##### 🔤 Transcribed Text")
            st.text_area(
                "Decoded Verbatim Text",
                value=res.get("transcribed_handwriting", "No handwriting text extracted."),
                height=350,
                disabled=True
            )

    with tab3:
        st.subheader("Visual Mark Allocation & Performance")
        chart_col1, chart_col2 = st.columns([1, 1])

        with chart_col1:
            # Donut chart
            fig_pie = go.Figure(data=[go.Pie(
                labels=["Marks Obtained", "Marks Lost"],
                values=[marks, max(0.0, max_m - marks)],
                hole=0.6,
                marker=dict(colors=["#22C55E", "#EF4444"])
            )])
            fig_pie.update_layout(title="Overall Score Distribution", margin=dict(t=40, b=10, l=10, r=10))
            st.plotly_chart(fig_pie, use_container_width=True)

        with chart_col2:
            # Criteria bar chart
            if crit_data:
                crit_names = [c.get("criterion", f"C{i+1}")[:25] + "..." if len(c.get("criterion", "")) > 25 else c.get("criterion", f"C{i+1}") for i, c in enumerate(crit_data)]
                obtained = [c.get("marks_awarded", 0) for c in crit_data]
                max_pts = [c.get("max_marks", 1) for c in crit_data]

                fig_bar = go.Figure(data=[
                    go.Bar(name='Marks Awarded', x=crit_names, y=obtained, marker_color='#3B82F6'),
                    go.Bar(name='Max Marks', x=crit_names, y=max_pts, marker_color='#E2E8F0')
                ])
                fig_bar.update_layout(
                    barmode='group',
                    title="Score per Rubric Criterion",
                    margin=dict(t=40, b=10, l=10, r=10),
                    yaxis=dict(title="Points")
                )
                st.plotly_chart(fig_bar, use_container_width=True)

    with tab4:
        st.subheader("💡 Knowledge Gap & Pedagogical Diagnostics")
        st.markdown("""
        Unlike traditional grading that only gives a number, ScanGrade AI isolates the exact cognitive 
        and conceptual gaps so educators can personalize revision sessions:
        """)
        gaps = res.get("knowledge_gaps", [])
        if gaps:
            for g in gaps:
                st.warning(f"📌 **Concept to Reinforce:** {g}")
        else:
            st.success("🎉 No significant knowledge gaps detected! Candidate has mastered the topic.")

    # Export & Download Section
    st.markdown("---")
    st.subheader("📥 Export Examination Records")
    export_col1, export_col2 = st.columns([1, 1])

    with export_col1:
        # CSV Export
        summary_df = pd.DataFrame([{
            "Student": res.get("student_info", "Candidate"),
            "Question": exam_question,
            "Marks Awarded": marks,
            "Max Marks": max_m,
            "Percentage": f"{pct:.1f}%",
            "Status": status_label,
            "Examiner Feedback": res.get("examiner_feedback", "")
        }])
        st.download_button(
            label="📄 Download Student Result Card (CSV)",
            data=summary_df.to_csv(index=False),
            file_name="scangrade_result_card.csv",
            mime="text/csv",
            use_container_width=True
        )

    with export_col2:
        # Full JSON Export
        st.download_button(
            label="💾 Download Full Audit Audit Trail (JSON)",
            data=json.dumps(res, indent=2),
            file_name="scangrade_audit_log.json",
            mime="application/json",
            use_container_width=True
        )
