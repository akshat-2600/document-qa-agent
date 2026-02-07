import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from src.query_engine import QueryEngine
from pathlib import Path


UPLOAD_FOLDER = "data/pdfs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
# Initialize Query Engine
engine = QueryEngine(llm_provider="gemini")
documents_ready = False

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    global documents_ready

    if not documents_ready:
        return jsonify({
            "answer": "📄 Please upload and process a PDF first."
        })

    data = request.get_json()
    question = data.get("question", "")

    if not question.strip():
        return jsonify({"answer": "Please enter a valid question."})

    try:
        response = engine.query(question)
        return jsonify({"answer": response})
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"})


    
@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    global documents_ready
    if "pdf" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["pdf"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files allowed"}), 400

    pdf_dir = Path("data/pdfs")
    pdf_dir.mkdir(parents=True, exist_ok=True)

    save_path = pdf_dir / file.filename
    file.save(save_path)

    # Ingesting documents after upload
    engine.ingest_documents("data/pdfs")
    documents_ready = True

    return jsonify({
        "message": "PDF uploaded and processed successfully",
        "filename": file.filename
    })



if __name__ == "__main__":
    app.run(port=8080, debug=True, use_reloader=False)

