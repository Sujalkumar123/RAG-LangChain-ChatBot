import os
from datetime import date

from flask import Flask, jsonify, request
from flask_cors import CORS

from core import llm, run_general_llm, run_llm_from_docs

# create the app
app = Flask(__name__)
# Optional: Load environment variables from a .env file if running locally (not needed in Docker)
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret")


CORS(
    app,
    origins=["http://localhost:5173", "http://localhost:5174"],
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.route("/answer", methods=["POST"])
def answer():

    data = request.get_json(silent=True) or {}
    query = data.get("query")
    chat_history = data.get("chat_history", [])

    if not query:
        return jsonify({"error": "Missing query"}), 400

    # 1) Try docs pipeline
    docs_result = run_llm_from_docs(query, chat_history)
    sources = [doc.metadata["source"] for doc in docs_result.get("context", [])]

    if sources:  # ✅ Docs mode succeeded
        answer = docs_result.get("answer", "")
        provenance = "docs"
    else:  # ❌ Fallback to general LLM
        general_result = run_general_llm(query, chat_history)
        answer = general_result.content

        sources = []
        provenance = "model_only"
    model_name = getattr(llm, "model_name", getattr(llm, "model", "gemini"))

    # 2) Update history (same shape for both)
    updated_history = chat_history + [
        {"role": "human", "content": query},
        {"role": "ai", "content": answer},
    ]

    # 3) Unified response
    return jsonify(
        {
            "answer": answer,
            "chat_history": updated_history,
            "sources": sources,
            "provenance": provenance,
            "model_name": model_name,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
