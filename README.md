# 🧮 AI Math Tutor

An intelligent algebra problem solver powered by **Gemini 2.5 Flash**, **EasyOCR**, and **SymPy**.

Upload a handwritten or printed algebra problem image → get LaTeX conversion, step-by-step solution, mistake detection, and PDF/Word export.

---

## 📁 Project Structure

```
ai_math_tutor/
├── app.py                   ← Flask backend (all API routes)
├── .env                     ← API keys & config (not committed)
├── requirements.txt         ← Python dependencies
├── modules/
│   ├── ocr_utils.py         ← Image preprocessing + EasyOCR
│   ├── gemini_client.py     ← Gemini 2.5 Flash API wrapper
│   ├── solver.py            ← SymPy equation solver
│   ├── mistake_check.py     ← Algebra mistake detection
│   ├── export_utils.py      ← PDF & Word document export
│   └── response_utils.py    ← JSON response helpers
├── templates/
│   ├── index.html           ← Landing page
│   ├── solver.html          ← Main solver UI
│   └── about.html           ← About page
├── static/
│   ├── css/style.css        ← Full responsive stylesheet
│   └── js/
│       ├── main.js          ← Shared utilities
│       └── solver.js        ← Solver page interactions
├── tests/
│   ├── test_solver.py
│   ├── test_mistake_check.py
│   └── test_response_utils.py
├── uploads/                 ← Temp image storage (gitignored)
└── exports/                 ← Generated files (gitignored)
```

---

## 🚀 Quick Start

### 1. Clone and enter project
```bash
git clone https://github.com/yourname/ai-math-tutor.git
cd ai-math-tutor
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up API key
```bash
cp .env.example .env
# Edit .env and add your Gemini API key:
# GEMINI_API_KEY=your_key_here
```
Get your key at: https://makersuite.google.com/app/apikey

### 5. Run
```bash
python app.py
```
Visit: **http://localhost:5000**

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/image-to-latex` | POST | Upload image → LaTeX equation |
| `/api/solve-equation` | POST | Equation text → step-by-step solution |
| `/api/mistake-check` | POST | Equation + steps → mistake list |
| `/api/export-pdf` | POST | Solution data → PDF download |
| `/api/export-word` | POST | Solution data → .docx download |

### Example: Solve an Equation
```bash
curl -X POST http://localhost:5000/api/solve-equation \
  -H "Content-Type: application/json" \
  -d '{"equation": "2x + 3 = 7"}'
```

### Example: Upload Image
```bash
curl -X POST http://localhost:5000/api/image-to-latex \
  -F "image=@/path/to/equation.jpg"
```

---

## 🧪 Running Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask 3.x |
| AI / Vision | Gemini 2.5 Flash (Google) |
| OCR | EasyOCR + OpenCV |
| Symbolic Math | SymPy |
| PDF Export | ReportLab |
| Word Export | python-docx |
| Frontend | HTML5 + CSS3 + Vanilla JS |
| Math Rendering | MathJax 3 |

---

## 📋 Requirements

- Python 3.9+
- Gemini API key
- Camera or image file of algebra problem
- Internet connection (for Gemini API)

---

## 🗺 Git Commit History

| Commit | Message |
|---|---|
| 1 | `chore: initialise project structure and .gitignore` |
| 2 | `chore: add requirements.txt with all dependencies` |
| 3 | `chore: add .env config template for API keys` |
| 4 | `feat(ocr): add image preprocessing, EasyOCR extraction, symbol-to-LaTeX mapping` |
| 5 | `feat(ai): integrate Gemini 2.5 Flash for image-to-LaTeX and step-by-step solving` |
| 6 | `feat(solver): implement SymPy-based equation parser and algebraic solver` |
| 7 | `feat(mistakes): add heuristic detectors for sign, distribution, and arithmetic errors` |
| 8 | `feat(export): add PDF and Word export with formatted layout` |
| 9 | `feat(utils): add JSON response wrappers, filename generator, confidence labels` |
| 10 | `feat(backend): define all Flask API routes with error handling and logging` |
| 11 | `feat(ui): build landing page with hero section and feature cards` |
| 12 | `feat(ui): build solver page with image upload, LaTeX display, step output` |
| 13 | `feat(ui): build about page with tech stack and architecture diagram` |
| 14 | `feat(styles): add full responsive CSS with cards, steps, mistake alerts` |
| 15 | `feat(js): add shared JS utilities — toast, loading state, API helper` |
| 16 | `feat(js): add solver.js — upload, preview, API calls, step/mistake rendering, export` |
| 17 | `test: add unit tests for solver, mistake_check, and response_utils` |
| 18 | `docs: add comprehensive README with setup guide and API reference` |

---

## 📄 License

MIT License — free for educational use.
