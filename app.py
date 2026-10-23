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
    "Physics — Hamza Tariq (10/10 Perfect)": {
        "question": "State Ohm's Law and calculate the current flowing through a resistor if V = 12V and R = 4 Ω.",
        "rubric": """1. Correct statement of Ohm's Law including temperature/physical state condition (4 marks)
2. Mathematical Formula (V = I * R or I = V / R) (2 marks)
3. Step-by-step substitution and numerical calculation (3 marks)
4. Correct SI unit (Amperes / A) (1 mark)
Total: 10 Marks""",
        "student_name": "Hamza Tariq",
        "roll_no": "2026-PHY-042",
        "subject": "Physics I",
        "mock_score": 10.0,
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
    "Physics — Ali Raza (5.5/10 Flawed Arithmetic & Units)": {
        "question": "State Ohm's Law and calculate the current flowing through a resistor if V = 12V and R = 4 Ω.",
        "rubric": """1. Correct statement of Ohm's Law including temperature/physical state condition (4 marks)
2. Mathematical Formula (V = I * R or I = V / R) (2 marks)
3. Step-by-step substitution and numerical calculation (3 marks)
4. Correct SI unit (Amperes / A) (1 mark)
Total: 10 Marks""",
        "student_name": "Ali Raza",
        "roll_no": "2026-PHY-088",
        "subject": "Physics I",
        "mock_score": 5.5,
        "handwritten_lines": [
            "Student: Ali Raza  |  Roll: 2026-PHY-088  |  Sub: Physics",
            "Q1. State Ohm's Law & find current for V = 12V, R = 4 Ohm.",
            "Ans: Ohm's law says voltage is proportional to current.",
            "Formula: V = I * R",
            "Calculation: I = 12 / 4 = 4",
            "Result = 4 (no units written)"
        ]
    },
    "CS: Binary Search — Sarah Khan (10/10 Perfect)": {
        "question": "Explain the Binary Search algorithm, state its preconditions, and derive its worst-case time complexity.",
        "rubric": """1. Definition of Binary Search and divide-and-conquer approach (3 marks)
2. Crucial precondition: array must be sorted (2 marks)
3. Step-by-step search procedure (mid-point calculation and range halving) (3 marks)
4. Time complexity derivation: O(log n) with justification (2 marks)
Total: 10 Marks""",
        "student_name": "Sarah Khan",
        "roll_no": "2026-CS-109",
        "subject": "Data Structures & Algorithms",
        "mock_score": 10.0,
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
    "CS: Binary Search — Usman Farooq (5/10 Incomplete)": {
        "question": "Explain the Binary Search algorithm, state its preconditions, and derive its worst-case time complexity.",
        "rubric": """1. Definition of Binary Search and divide-and-conquer approach (3 marks)
2. Crucial precondition: array must be sorted (2 marks)
3. Step-by-step search procedure (mid-point calculation and range halving) (3 marks)
4. Time complexity derivation: O(log n) with justification (2 marks)
Total: 10 Marks""",
        "student_name": "Usman Farooq",
        "roll_no": "2026-CS-214",
        "subject": "Data Structures & Algorithms",
        "mock_score": 5.0,
        "handwritten_lines": [
            "Student: Usman Farooq  |  Roll: 2026-CS-214  |  Sub: CS - DSA",
            "Q: Explain Binary Search, preconditions, & time complexity.",
            "Ans: Binary search splits an array into two halves to search faster.",
            "Procedure: check the middle element. If not equal, check other parts.",
            "Time complexity is O(log n)."
        ]
    },
    "Math: Quadratic Formula — Bilal Ahmed (10/10 Perfect)": {
        "question": "Solve the quadratic equation 2x^2 + 5x - 3 = 0 using the quadratic formula, showing all substitution steps.",
        "rubric": """1. Identification of coefficients a = 2, b = 5, c = -3 (2 marks)
2. Correct Quadratic Formula: x = (-b ± √(b² - 4ac)) / (2a) (2 marks)
3. Step-by-step discriminant evaluation: 5² - 4(2)(-3) = 25 + 24 = 49 (3 marks)
4. Accurate roots computation: x = 0.5 and x = -3 (3 marks)
Total: 10 Marks""",
        "student_name": "Bilal Ahmed",
        "roll_no": "2026-MATH-015",
        "subject": "Applied Mathematics",
        "mock_score": 10.0,
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
    },
    "Math: Quadratic Formula — Zainab Malik (6/10 Sign Error)": {
        "question": "Solve the quadratic equation 2x^2 + 5x - 3 = 0 using the quadratic formula, showing all substitution steps.",
        "rubric": """1. Identification of coefficients a = 2, b = 5, c = -3 (2 marks)
2. Correct Quadratic Formula: x = (-b ± √(b² - 4ac)) / (2a) (2 marks)
3. Step-by-step discriminant evaluation: 5² - 4(2)(-3) = 25 + 24 = 49 (3 marks)
4. Accurate roots computation: x = 0.5 and x = -3 (3 marks)
Total: 10 Marks""",
        "student_name": "Zainab Malik",
        "roll_no": "2026-MATH-051",
        "subject": "Applied Mathematics",
        "mock_score": 6.0,
        "handwritten_lines": [
            "Student: Zainab Malik  |  Roll: 2026-MATH-051  |  Sub: Math",
            "Q: Solve 2x^2 + 5x - 3 = 0 using quadratic formula.",
            "Ans: 2x^2 + 5x - 3 = 0. Here a = 2, b = 5, c = -3.",
            "Formula: x = [-b +- sqrt(b^2 - 4ac)] / 2a",
            "Discriminant = 25 - 24 = 1",
            "x = [-5 +- 1] / 4",
            "Root 1: (-5 + 1)/4 = -4/4 = -1",
            "Root 2: (-5 - 1)/4 = -6/4 = -1.5. Roots are {-1, -1.5}."
        ]
    },
    "AI / ML: Gradient Descent — Ayesha Siddiqui (10/10 Perfect)": {
        "question": "Explain the Gradient Descent algorithm for optimizing model weights. State the weight update rule formula, describe the effect of a learning rate that is too high versus too low, and state when the algorithm terminates.",
        "rubric": """1. Definition & objective: iterative optimization algorithm to minimize cost/loss function (3 marks)
2. Mathematical update rule: w = w - α * ∇J(w) with definitions of α and gradient (3 marks)
3. Analysis of learning rate: too high causes divergence/overshooting; too low causes slow convergence (2 marks)
4. Termination condition: gradient approaches zero or change in loss falls below threshold ε (2 marks)
Total: 10 Marks""",
        "student_name": "Ayesha Siddiqui",
        "roll_no": "2026-AI-019",
        "subject": "Machine Learning",
        "mock_score": 10.0,
        "handwritten_lines": [
            "Student Name: Ayesha Siddiqui   |   Roll: 2026-AI-019   |   Exam: Machine Learning",
            "Q: Explain Gradient Descent, weight update rule, learning rate effects, & stopping criteria.",
            "Ans: Gradient Descent is an iterative optimization algorithm used to minimize a loss function J(w).",
            "Weight Update Formula: w = w - α * ∇J(w)",
            "Here, w is parameter vector, α is learning rate, and ∇J(w) is gradient of loss function.",
            "Learning Rate Effects: High α overshoots minimum/diverges; Low α causes slow convergence.",
            "Stopping Conditions: Algorithm halts when ||∇J(w)|| < ε or max iterations reached."
        ]
    },
    "AI / ML: Gradient Descent — Danial Shah (4.5/10 Flawed Formula & Omissions)": {
        "question": "Explain the Gradient Descent algorithm for optimizing model weights. State the weight update rule formula, describe the effect of a learning rate that is too high versus too low, and state when the algorithm terminates.",
        "rubric": """1. Definition & objective: iterative optimization algorithm to minimize cost/loss function (3 marks)
2. Mathematical update rule: w = w - α * ∇J(w) with definitions of α and gradient (3 marks)
3. Analysis of learning rate: too high causes divergence/overshooting; too low causes slow convergence (2 marks)
4. Termination condition: gradient approaches zero or change in loss falls below threshold ε (2 marks)
Total: 10 Marks""",
        "student_name": "Danial Shah",
        "roll_no": "2026-AI-077",
        "subject": "Machine Learning",
        "mock_score": 4.5,
        "handwritten_lines": [
            "Student Name: Danial Shah   |   Roll: 2026-AI-077   |   Exam: Machine Learning",
            "Q: Explain Gradient Descent, weight update rule, learning rate effects, & stopping criteria.",
            "Ans: Gradient descent optimizes loss to make machine learning models accurate.",
            "Update Formula: w = w + α * J(w)",
            "Learning Rate: Small learning rate is slow."
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
def generate_mock_evaluation(identifier, exam_question="", rubric_criteria=""):
    """
    Intelligent mock evaluator for live testing without an active Gemini API connection.
    Recognizes uploaded filenames and preset selections to award exact matching scores:
    • Usman Farooq / Incomplete / 5 out of 10 -> 5.0 / 10.0
    • Ali Raza / Flawed / 6 out of 10 -> 5.5 / 10.0
    • Zainab Malik / Sign Error / 6 out of 10 -> 6.0 / 10.0
    • Sarah Khan / Perfect CS -> 10.0 / 10.0
    • Bilal Ahmed / Perfect Math -> 10.0 / 10.0
    • Hamza Tariq / Perfect Physics -> 10.0 / 10.0
    """
    ident = (str(identifier) + " " + str(exam_question)).lower()

    # Case 1: Math - Zainab Malik (6.0 / 10 Sign Error)
    if any(k in ident for k in ["zainab", "math_sample_sign_error", "sign_error", "zainab malik"]):
        return {
            "transcribed_handwriting": (
                "Student: Zainab Malik | Roll: 2026-MATH-051 | Sub: Math\n"
                "Q: Solve 2x^2 + 5x - 3 = 0 using quadratic formula.\n"
                "Ans: 2x^2 + 5x - 3 = 0. Here a = 2, b = 5, c = -3.\n"
                "Formula: x = [-b +- sqrt(b^2 - 4ac)] / 2a\n"
                "Discriminant = 25 - 24 = 1\n"
                "x = [-5 +- 1] / 4\n"
                "Root 1: (-5 + 1)/4 = -4/4 = -1\n"
                "Root 2: (-5 - 1)/4 = -6/4 = -1.5. Roots are {-1, -1.5}."
            ),
            "student_info": "Zainab Malik (Roll No: 2026-MATH-051)",
            "total_marks_awarded": 6.0,
            "max_marks_possible": 10.0,
            "criteria_breakdown": [
                {"criterion": "Identification of coefficients a = 2, b = 5, c = -3", "marks_awarded": 2.0, "max_marks": 2.0, "deduction_reason": "Coefficients correctly identified from standard form."},
                {"criterion": "Correct Quadratic Formula", "marks_awarded": 2.0, "max_marks": 2.0, "deduction_reason": "Formula accurately stated."},
                {"criterion": "Step-by-step discriminant evaluation", "marks_awarded": 1.0, "max_marks": 3.0, "deduction_reason": "Algebraic sign error: -4(2)(-3) is +24, but student evaluated as -24, yielding discriminant 1 instead of 49."},
                {"criterion": "Accurate roots computation", "marks_awarded": 1.0, "max_marks": 3.0, "deduction_reason": "Derived roots {-1, -1.5} are incorrect due to propagated discriminant error."}
            ],
            "strengths": [
                "Accurately extracted quadratic parameters a, b, and c",
                "Flawless recall of the quadratic formula"
            ],
            "mistakes_or_missing_steps": [
                "Sign error in discriminant: (-4) * (2) * (-3) = +24, not -24",
                "Final solution set is incorrect due to the arithmetic sign blunder"
            ],
            "knowledge_gaps": [
                "Negative number multiplication rules in algebraic discriminants"
            ],
            "examiner_feedback": "Score: 6/10. Solid procedural setup, but a fundamental negative sign error in the discriminant (-4ac) contaminated the final roots calculation."
        }

    # Case 2: CS - Usman Farooq (5 / 10 Incomplete)
    elif any(k in ident for k in ["usman", "cs_sample_incomplete", "usman farooq"]):
        return {
            "transcribed_handwriting": (
                "Student: Usman Farooq | Roll: 2026-CS-214 | Sub: CS - DSA\n"
                "Q: Explain Binary Search, preconditions, & time complexity.\n"
                "Ans: Binary search splits an array into two halves to search faster.\n"
                "Procedure: check the middle element. If not equal, check other parts.\n"
                "Time complexity is O(log n)."
            ),
            "student_info": "Usman Farooq (Roll No: 2026-CS-214)",
            "total_marks_awarded": 5.0,
            "max_marks_possible": 10.0,
            "criteria_breakdown": [
                {"criterion": "Definition of Binary Search & divide-and-conquer", "marks_awarded": 3.0, "max_marks": 3.0, "deduction_reason": "Correct high-level intuition of dividing search space."},
                {"criterion": "Precondition: Array MUST be sorted", "marks_awarded": 0.0, "max_marks": 2.0, "deduction_reason": "CRITICAL OMISSION: Failed to state that Binary Search strictly requires a sorted array."},
                {"criterion": "Step-by-step search procedure (mid calculation)", "marks_awarded": 2.0, "max_marks": 3.0, "deduction_reason": "Described concept informally without explicit midpoint formula mid = (low+high)/2."},
                {"criterion": "Mathematical Time Complexity derivation", "marks_awarded": 0.0, "max_marks": 2.0, "deduction_reason": "Stated O(log n) as a fact but provided zero derivation steps (N/2^k = 1)."}
            ],
            "strengths": [
                "Understands the intuitive concept of dividing the search space",
                "Correctly memorized that the final complexity is O(log n)"
            ],
            "mistakes_or_missing_steps": [
                "CRITICAL: Failed to state the mandatory precondition that array must be sorted",
                "Did not provide the formula for index calculation: mid = (low + high) / 2",
                "Omitted the logarithmic mathematical proof showing why k = log2(N)"
            ],
            "knowledge_gaps": [
                "Algorithmic prerequisites and invariant guarantees",
                "Recurrence relations and mathematical Big-O derivation"
            ],
            "examiner_feedback": "Score: 5/10. The student understands the high-level concept, but failed to mention the most critical requirement for binary search (a sorted array) and provided no derivation for the time complexity."
        }

    # Case 3: Physics - Ali Raza (5.5 / 10 Flawed Calculation & Missing Units)
    elif any(k in ident for k in ["ali raza", "physics_sample_flawed"]):
        return {
            "transcribed_handwriting": (
                "Student: Ali Raza | Roll: 2026-PHY-088 | Sub: Physics\n"
                "Q1. State Ohm's Law & find current for V = 12V, R = 4 Ohm.\n"
                "Ans: Ohm's law says voltage is proportional to current.\n"
                "Formula: V = I * R\n"
                "Calculation: I = 12 / 4 = 4\n"
                "Result = 4"
            ),
            "student_info": "Ali Raza (Roll No: 2026-PHY-088)",
            "total_marks_awarded": 5.5,
            "max_marks_possible": 10.0,
            "criteria_breakdown": [
                {"criterion": "Ohm's Law statement with constant temperature condition", "marks_awarded": 2.0, "max_marks": 4.0, "deduction_reason": "Incomplete law: Omitted mandatory condition that temperature/physical state must remain constant."},
                {"criterion": "Mathematical Formula (V = IR)", "marks_awarded": 2.0, "max_marks": 2.0, "deduction_reason": "Correct relationship formula stated."},
                {"criterion": "Substitution and numerical arithmetic", "marks_awarded": 1.5, "max_marks": 3.0, "deduction_reason": "Arithmetic calculation error: 12 / 4 = 3, student erroneously wrote 4."},
                {"criterion": "Correct SI units (Amperes / A)", "marks_awarded": 0.0, "max_marks": 1.0, "deduction_reason": "No SI unit specified for the calculated current."}
            ],
            "strengths": [
                "Correctly remembered the algebraic formula V = I * R",
                "Substituted the given values into the formula"
            ],
            "mistakes_or_missing_steps": [
                "Omitted the constant temperature condition in the definition of Ohm's Law",
                "Basic arithmetic error: 12 / 4 was calculated as 4 instead of 3",
                "Missing SI unit (Amperes / A) in final answer"
            ],
            "knowledge_gaps": [
                "Conditions of validity for Ohm's Law (temperature dependency)",
                "Physical dimensions and mandatory scientific unit notation"
            ],
            "examiner_feedback": "Score: 5.5/10. Points were heavily deducted for an arithmetic error in dividing 12 by 4, omitting scientific units, and leaving out the physical condition under which Ohm's law holds true."
        }


    # Case 4: CS - Sarah Khan (10 / 10 Perfect)
    elif any(k in ident for k in ["sarah", "cs_sample_perfect", "binary search"]):
        return {
            "transcribed_handwriting": (
                "Student: Sarah Khan | Roll: 2026-CS-109 | Sub: CS - DSA\n"
                "Q: Explain Binary Search, preconditions, & time complexity.\n"
                "Ans: Binary Search is a divide-and-conquer algorithm to find an element in a list. "
                "Precondition: Array MUST be sorted.\n"
                "Procedure: Compute mid = (low + high)/2. If key == arr[mid], found. "
                "If key < arr[mid], search left half, else search right half.\n"
                "Complexity: Search space halves each step: N, N/2, N/4 ... N/2^k = 1. "
                "Thus k = log2(N). Time Complexity is O(log n)."
            ),
            "student_info": "Sarah Khan (Roll No: 2026-CS-109)",
            "total_marks_awarded": 10.0,
            "max_marks_possible": 10.0,
            "criteria_breakdown": [
                {"criterion": "Definition of Binary Search and divide-and-conquer", "marks_awarded": 3.0, "max_marks": 3.0, "deduction_reason": "Clear and accurate definition."},
                {"criterion": "Crucial precondition: array must be sorted", "marks_awarded": 2.0, "max_marks": 2.0, "deduction_reason": "Explicitly highlighted as mandatory."},
                {"criterion": "Step-by-step procedure & mid calculation", "marks_awarded": 3.0, "max_marks": 3.0, "deduction_reason": "Precise algorithm mechanics and branching logic."},
                {"criterion": "Mathematical Time Complexity derivation", "marks_awarded": 2.0, "max_marks": 2.0, "deduction_reason": "Rigorous derivation from N/2^k = 1 to O(log n)."}
            ],
            "strengths": [
                "Emphasized sorted array requirement",
                "Clear mathematical proof of logarithmic complexity",
                "Well-structured recursive halving logic"
            ],
            "mistakes_or_missing_steps": ["None detected."],
            "knowledge_gaps": ["No conceptual gaps found. Exemplary mastery of Binary Search."],
            "examiner_feedback": "Perfect 10/10 submission! Demonstrates complete mastery of algorithm theory, preconditions, and complexity analysis."
        }

    # Case 5: ML - Danial Shah (4.5 / 10 Flawed Formula & Omissions)
    elif any(k in ident for k in ["danial", "ml_sample_flawed", "gradient descent flawed", "4.5"]):
        return {
            "transcribed_handwriting": (
                "Student Name: Danial Shah | Roll: 2026-AI-077 | Exam: Machine Learning\n"
                "Q: Explain Gradient Descent, weight update rule, learning rate effects, & stopping criteria.\n"
                "Ans: Gradient descent optimizes loss to make machine learning models accurate.\n"
                "Update Formula: w = w + α * J(w)\n"
                "Learning Rate: Small learning rate is slow."
            ),
            "student_info": "Danial Shah (Roll No: 2026-AI-077)",
            "total_marks_awarded": 4.5,
            "max_marks_possible": 10.0,
            "criteria_breakdown": [
                {"criterion": "Definition & objective of Gradient Descent", "marks_awarded": 2.5, "max_marks": 3.0, "deduction_reason": "Basic understanding stated, but lacked detail on calculating gradient of loss function."},
                {"criterion": "Mathematical weight update rule", "marks_awarded": 1.0, "max_marks": 3.0, "deduction_reason": "CRITICAL MATHEMATICAL ERROR: Wrote w + α*J(w) instead of w - α*∇J(w). Used addition instead of subtraction and omitted the gradient operator."},
                {"criterion": "Analysis of learning rate effects (high vs low)", "marks_awarded": 1.0, "max_marks": 2.0, "deduction_reason": "Mentioned small learning rate is slow, but completely omitted the consequences of a high learning rate (divergence, oscillation, overshooting)."},
                {"criterion": "Stopping / termination conditions", "marks_awarded": 0.0, "max_marks": 2.0, "deduction_reason": "Omitted any stopping criteria (e.g. gradient magnitude < ε or max iterations)."}
            ],
            "strengths": [
                "Understands that Gradient Descent is used to optimize ML model loss"
            ],
            "mistakes_or_missing_steps": [
                "CRITICAL: Sign mistake in update rule (w + α J(w) performs gradient ascent, maximizing error instead of minimizing)",
                "Omitted the gradient operator ∇ in the update formula",
                "Did not describe the impact of a learning rate that is too large (overshooting/divergence)",
                "No stopping or termination criteria provided"
            ],
            "knowledge_gaps": [
                "Vector calculus: Distinction between objective value J(w) and gradient vector ∇J(w)",
                "Gradient descent directionality (subtraction moves opposite to steepest ascent)",
                "Hyperparameter convergence dynamics and stopping conditions"
            ],
            "examiner_feedback": "Score: 4.5/10. Writing a '+' sign in the update rule is a critical failure because it maximizes loss instead of minimizing it. Stopping criteria were completely omitted."
        }

    # Case 6: ML - Ayesha Siddiqui (10 / 10 Perfect)
    elif any(k in ident for k in ["ayesha", "ml_sample_perfect", "gradient descent", "machine learning"]):
        return {
            "transcribed_handwriting": (
                "Student Name: Ayesha Siddiqui | Roll: 2026-AI-019 | Exam: Machine Learning\n"
                "Q: Explain Gradient Descent, weight update rule, learning rate effects, & stopping criteria.\n"
                "Ans: Gradient Descent is an iterative optimization algorithm used to minimize a loss function J(w). "
                "Weight Update Formula: w = w - α * ∇J(w). "
                "Here, w is parameter vector, α is learning rate, and ∇J(w) is gradient of loss function. "
                "Learning Rate Effects: High α overshoots minimum/diverges; Low α causes slow convergence. "
                "Stopping Conditions: Algorithm halts when ||∇J(w)|| < ε or max iterations reached."
            ),
            "student_info": "Ayesha Siddiqui (Roll No: 2026-AI-019)",
            "total_marks_awarded": 10.0,
            "max_marks_possible": 10.0,
            "criteria_breakdown": [
                {"criterion": "Definition & objective of Gradient Descent", "marks_awarded": 3.0, "max_marks": 3.0, "deduction_reason": "Complete and accurate formulation of iterative loss minimization."},
                {"criterion": "Mathematical weight update rule", "marks_awarded": 3.0, "max_marks": 3.0, "deduction_reason": "Flawless formula w = w - α∇J(w) with all symbols defined."},
                {"criterion": "Analysis of learning rate effects (high vs low)", "marks_awarded": 2.0, "max_marks": 2.0, "deduction_reason": "Accurately contrasted overshooting/divergence with slow convergence."},
                {"criterion": "Stopping / termination conditions", "marks_awarded": 2.0, "max_marks": 2.0, "deduction_reason": "Correctly cited gradient norm threshold ε and iteration limits."}
            ],
            "strengths": [
                "Mathematically precise vector notation",
                "Clear distinction between divergence vs slow convergence dynamics",
                "Explicitly stated standard convergence tolerance threshold ε"
            ],
            "mistakes_or_missing_steps": ["None detected."],
            "knowledge_gaps": ["No conceptual gaps found. Exemplary mastery of optimization theory."],
            "examiner_feedback": "Perfect 10/10 submission! Mathematically rigorous, clear diagrams and notation, and complete coverage of hyperparameter effects."
        }

    # Case 7: Math - Bilal Ahmed (10 / 10 Perfect)
    elif any(k in ident for k in ["bilal", "math_sample_perfect", "quadratic"]):
        return {
            "transcribed_handwriting": (
                "Student: Bilal Ahmed | Roll: 2026-MATH-015 | Sub: Math\n"
                "Q: Solve 2x^2 + 5x - 3 = 0 using quadratic formula.\n"
                "Ans: Given 2x^2 + 5x - 3 = 0. Here a = 2, b = 5, c = -3.\n"
                "Formula: x = [-b +- sqrt(b^2 - 4ac)] / (2a)\n"
                "Discriminant = (5)^2 - 4*(2)*(-3) = 25 + 24 = 49.\n"
                "x = [-5 +- sqrt(49)] / (2*2) = [-5 +- 7] / 4.\n"
                "Root 1: (-5 + 7)/4 = 2/4 = 0.5\n"
                "Root 2: (-5 - 7)/4 = -12/4 = -3. Roots are {0.5, -3}."
            ),
            "student_info": "Bilal Ahmed (Roll No: 2026-MATH-015)",
            "total_marks_awarded": 10.0,
            "max_marks_possible": 10.0,
            "criteria_breakdown": [
                {"criterion": "Identification of coefficients a = 2, b = 5, c = -3", "marks_awarded": 2.0, "max_marks": 2.0, "deduction_reason": "Accurately extracted."},
                {"criterion": "Correct Quadratic Formula", "marks_awarded": 2.0, "max_marks": 2.0, "deduction_reason": "Standard formula correctly stated."},
                {"criterion": "Step-by-step discriminant evaluation", "marks_awarded": 3.0, "max_marks": 3.0, "deduction_reason": "Flawless arithmetic: 25 - (-24) = 49."},
                {"criterion": "Accurate roots computation", "marks_awarded": 3.0, "max_marks": 3.0, "deduction_reason": "Accurate final roots {0.5, -3}."}
            ],
            "strengths": [
                "Clean step-by-step algebraic substitution",
                "Correct handling of double negative multiplication in discriminant",
                "Both roots accurately calculated"
            ],
            "mistakes_or_missing_steps": ["None."],
            "knowledge_gaps": ["No knowledge gaps identified."],
            "examiner_feedback": "Excellent work (10/10). Clean handwriting, mathematically rigorous substitution, and completely accurate final roots."
        }

    # Case 6: Physics - Hamza Tariq (10 / 10 Perfect)
    else:
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
            "examiner_feedback": "Outstanding work (10/10)! The student demonstrates thorough conceptual grasp and precise mathematical execution."
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
    preset_names = list(PRESETS.keys())
    selected_preset = st.selectbox("Choose a pre-built exam:", preset_names)

    if st.button("📥 Load Selected Preset Exam", use_container_width=True):
        preset_data = PRESETS[selected_preset]
        st.session_state["exam_q"] = preset_data["question"]
        st.session_state["rubric"] = preset_data["rubric"]
        sample_buf = generate_handwritten_sheet_image(preset_data["handwritten_lines"])
        st.session_state["current_image"] = sample_buf.getvalue()
        st.session_state["preset_key"] = selected_preset
        st.session_state["uploaded_filename"] = ""
        # Reset stale results when loading a new preset
        if "eval_results" in st.session_state:
            del st.session_state["eval_results"]
        st.success(f"Loaded: {selected_preset}")
        st.rerun()

    st.markdown("---")
    st.caption("🏆 Built for DITE Hackathon 2026-27 | Theme: Education")

# ----------------- MAIN INTERFACE -----------------
st.markdown('<div class="main-header">📝 ScanGrade AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multimodal Computer Vision • Handwriting Deciphering • Automated Step-by-Step Exam Grading</div>', unsafe_allow_html=True)

# Layout: Step 1 (Question & Rubric) + Step 2 (Exam Paper Input)
col_setup, col_paper = st.columns([1, 1], gap="large")

first_key = list(PRESETS.keys())[0]
default_q = PRESETS[first_key]["question"]
default_rubric = PRESETS[first_key]["rubric"]

with col_setup:
    st.subheader("1️⃣ Exam Question & Marking Rubric")
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

    # Automatically clear stale evaluation if user switches input mode
    if st.session_state.get("prev_source") != paper_source:
        st.session_state["prev_source"] = paper_source
        if "eval_results" in st.session_state:
            del st.session_state["eval_results"]

    image_bytes_to_grade = None

    if paper_source == "Sample Preset Sheet":
        if "current_image" not in st.session_state:
            default_preset = PRESETS[first_key]
            buf = generate_handwritten_sheet_image(default_preset["handwritten_lines"])
            st.session_state["current_image"] = buf.getvalue()
            st.session_state["preset_key"] = first_key

        image_bytes_to_grade = st.session_state["current_image"]
        st.image(image_bytes_to_grade, caption=f"Active Sheet: {st.session_state.get('preset_key', first_key)}", use_container_width=True)

    elif paper_source == "Upload Photo (PNG/JPG)":
        uploaded = st.file_uploader("Upload student answer sheet image", type=["png", "jpg", "jpeg"])
        if uploaded:
            image_bytes_to_grade = uploaded.read()
            st.session_state["uploaded_filename"] = uploaded.name
            # Reset stale evaluation if user uploads a new/different file
            if st.session_state.get("last_uploaded_name") != uploaded.name:
                st.session_state["last_uploaded_name"] = uploaded.name
                if "eval_results" in st.session_state:
                    del st.session_state["eval_results"]
            st.image(image_bytes_to_grade, caption=f"Uploaded Sheet: {uploaded.name}", use_container_width=True)
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
                    # Dynamically determine the test case identifier
                    lookup_identifier = ""
                    if paper_source == "Upload Photo (PNG/JPG)":
                        lookup_identifier = st.session_state.get("uploaded_filename", "")
                    elif paper_source == "Sample Preset Sheet":
                        lookup_identifier = st.session_state.get("preset_key", "")
                    else:
                        lookup_identifier = exam_question

                    results = generate_mock_evaluation(lookup_identifier, exam_question, rubric_criteria)
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


