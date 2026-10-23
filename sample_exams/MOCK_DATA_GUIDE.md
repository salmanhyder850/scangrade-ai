# 🧪 ScanGrade AI — Mock Data & Testing Guide

This folder contains pre-rendered handwritten exam answer sheets and test scenarios to test **ScanGrade AI** locally or present live during your hackathon demo.

---

## 📁 Sample Answer Sheet Files in this Directory

| File Name | Subject | Student | Expected Marks | Scenario Tested |
| :--- | :--- | :--- | :---: | :--- |
| [`physics_sample_perfect_10_out_of_10.png`](./physics_sample_perfect_10_out_of_10.png) | Physics | Hamza Tariq | **10 / 10** | Perfect answer: constant temperature mentioned, formula, substitution, correct units. |
| [`physics_sample_flawed_6_out_of_10.png`](./physics_sample_flawed_6_out_of_10.png) | Physics | Ali Raza | **5–6 / 10** | Missing condition, calculation error (12/4=4), omitted units (Amperes). |
| [`cs_sample_perfect_10_out_of_10.png`](./cs_sample_perfect_10_out_of_10.png) | CS / DSA | Sarah Khan | **10 / 10** | Explicitly mentions sorted precondition, midpoint halving, mathematical Big-O derivation. |
| [`cs_sample_incomplete_5_out_of_10.png`](./cs_sample_incomplete_5_out_of_10.png) | CS / DSA | Usman Farooq | **5 / 10** | Missed sorted array precondition, skipped mathematical derivation. |
| [`math_sample_perfect_10_out_of_10.png`](./math_sample_perfect_10_out_of_10.png) | Mathematics | Bilal Ahmed | **10 / 10** | Correct identification of a, b, c; discriminant evaluation (49); accurate roots (0.5 and -3). |
| [`math_sample_sign_error_6_out_of_10.png`](./math_sample_sign_error_6_out_of_10.png) | Mathematics | Zainab Malik | **6–7 / 10** | Formula correct, but sign error in -4(2)(-3) led to wrong roots. |

---

## 📋 Ready-to-Copy Exam Scenarios

### Scenario 1: Physics (Ohm's Law & Circuit Analysis)
**Exam Question:**
```text
State Ohm's Law and calculate the current flowing through a resistor if V = 12V and R = 4 Ω.
```

**Teacher's Marking Rubric:**
```text
1. Correct statement of Ohm's Law including constant temperature condition (4 marks)
2. Mathematical Formula (V = I * R or I = V / R) (2 marks)
3. Step-by-step substitution and numerical calculation (3 marks)
4. Correct SI unit (Amperes / A) (1 mark)
Total: 10 Marks
```

**Images to test:**
- Upload `physics_sample_perfect_10_out_of_10.png` ➔ Expected: **10/10 (Grade A+)**
- Upload `physics_sample_flawed_6_out_of_10.png` ➔ Expected: **5-6/10** with diagnostic points:
  - Deduct 2 marks for missing temperature condition
  - Deduct 1.5 marks for arithmetic mistake (12/4 = 4 instead of 3)
  - Deduct 1 mark for missing SI unit

---

### Scenario 2: Computer Science (Binary Search & Big-O)
**Exam Question:**
```text
Explain the Binary Search algorithm, state its preconditions, and derive its worst-case time complexity.
```

**Teacher's Marking Rubric:**
```text
1. Definition of Binary Search and divide-and-conquer approach (3 marks)
2. Crucial precondition: array must be sorted (2 marks)
3. Step-by-step search procedure (mid-point calculation and range halving) (3 marks)
4. Time complexity derivation: O(log n) with mathematical steps (2 marks)
Total: 10 Marks
```

**Images to test:**
- Upload `cs_sample_perfect_10_out_of_10.png` ➔ Expected: **10/10 (Grade A+)**
- Upload `cs_sample_incomplete_5_out_of_10.png` ➔ Expected: **5/10** with diagnostic points:
  - Deduct 2 marks for failing to mention sorted array requirement
  - Deduct 2 marks for missing Big-O derivation steps

---

### Scenario 3: Mathematics (Quadratic Formula & Roots)
**Exam Question:**
```text
Solve the quadratic equation 2x^2 + 5x - 3 = 0 using the quadratic formula, showing all substitution steps.
```

**Teacher's Marking Rubric:**
```text
1. Identification of coefficients a = 2, b = 5, c = -3 (2 marks)
2. Correct Quadratic Formula: x = (-b ± √(b² - 4ac)) / (2a) (2 marks)
3. Step-by-step discriminant evaluation: 5² - 4(2)(-3) = 25 + 24 = 49 (3 marks)
4. Accurate roots computation: x = 0.5 and x = -3 (3 marks)
Total: 10 Marks
```

**Images to test:**
- Upload `math_sample_perfect_10_out_of_10.png` ➔ Expected: **10/10 (Grade A+)**
- Upload `math_sample_sign_error_6_out_of_10.png` ➔ Expected: **6-7/10** with diagnostic points:
  - Full marks for coefficients and formula
  - Deduct 3 marks for calculation sign mistake in discriminant (calculated 1 instead of 49)

---

## 🎯 How to Test in the Live Web App

1. Open your browser at **[http://localhost:8501](http://localhost:8501)**.
2. In the sidebar:
   - Make sure **"Demo / Mock Mode"** is toggled ON if testing without an API key, OR enter your **Gemini API Key** to run live multimodal AI vision.
3. In **Step 1 (Left Column)**:
   - Paste any Exam Question & Marking Rubric from above.
4. In **Step 2 (Right Column)**:
   - Select **"Upload Photo (PNG/JPG)"**.
   - Browse to `D:\scangrade-ai\sample_exams\` and select any sample image.
5. Click **"🚀 Scan Handwriting & Grade Exam"**.
6. Check all 4 analysis tabs:
   - **Rubric Scorecard**: Marks per criterion and deduction reasons.
   - **Deciphered Handwriting**: OCR transcription of the handwritten ink.
   - **Analytics & Visuals**: Score breakdown charts.
   - **Knowledge Gap Diagnosis**: Pedagogical recommendations.
