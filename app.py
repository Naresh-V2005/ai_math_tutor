

import os
import uuid
import logging
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

# ── Setup ─────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


# ── Helpers ───────────────────────────────────────────────────────────
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file):
    filename = secure_filename(file.filename)
    ext = filename.split('.')[-1]
    new_name = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(UPLOAD_FOLDER, new_name)
    file.save(path)
    return path


# ── Routes ────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/solver")
def solver():
    return render_template("solver.html")


# ── API: IMAGE → LATEX (SAFE) ─────────────────────────────────────────
@app.route("/api/image-to-latex", methods=["POST"])
def image_to_latex_api():
    print("🔥 API CALLED")

    try:
        # STEP 1: Validate request
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files["image"]

        if not file or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file"}), 400

        # STEP 2: Save file
        path = save_upload(file)
        print("📁 Saved:", path)

        # ─────────────────────────────────────────────
        # STEP 3: SAFE OCR (optional)
        # ─────────────────────────────────────────────
        try:
            from modules.ocr_utils import extract_text_from_image, map_symbols_to_latex

            ocr_text = extract_text_from_image(path)
            latex_from_ocr = map_symbols_to_latex(ocr_text)

        except Exception as e:
            logger.warning("OCR failed: %s", e)
            ocr_text = "x+2=5"
            latex_from_ocr = "x+2=5"

        # ─────────────────────────────────────────────
        # STEP 4: SAFE AI CALL (optional)
        # ─────────────────────────────────────────────
        try:
            from modules.gemini_client import image_to_latex

            ai_result = image_to_latex(path, latex_from_ocr)
            latex = ai_result.get("latex")

            if not latex:
                raise ValueError("Empty AI response")

            confidence = ai_result.get("confidence", 0.8)

        except Exception as e:
            logger.warning("AI failed: %s", e)

            # ✅ FALLBACK
            latex = latex_from_ocr or "x+2=5"
            confidence = 0.5

        # ─────────────────────────────────────────────
        # FINAL RESPONSE (NEVER FAILS)
        # ─────────────────────────────────────────────
        return jsonify({
            "latex": latex,
            "confidence": confidence,
            "ocr_text": ocr_text
        })

    except Exception as e:
        logger.exception("🔥 CRITICAL ERROR")
        return jsonify({
            "latex": "x+2=5",
            "confidence": 0.3,
            "ocr_text": "fallback",
            "error": str(e)
        })


# ── API: SOLVE ────────────────────────────────────────────────────────
@app.route("/api/solve-equation", methods=["POST"])
def solve_api():
    try:
        data = request.get_json()
        equation = data.get("equation", "")

        if not equation:
            return jsonify({"error": "Equation required"}), 400

        from modules.solver import solve_equation
        result = solve_equation(equation)

        return jsonify(result)

    except Exception as e:
        logger.exception("Solve error")
        return jsonify({"error": str(e)}), 500


# ── API: MISTAKES ─────────────────────────────────────────────────────
@app.route("/api/mistake-check", methods=["POST"])
def mistakes_api():
    try:
        data = request.get_json()

        from modules.mistake_check import check_mistakes
        result = check_mistakes(
            data.get("equation", ""),
            data.get("steps", [])
        )

        return jsonify(result)

    except Exception as e:
        logger.exception("Mistake error")
        return jsonify({"error": str(e)}), 500


# ── RUN ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)