import os
import json
import csv
from flask import Flask, request, jsonify, render_template_string
import requests
from datetime import datetime

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
CSV_FILE = "call_analysis.csv"

INDEX_HTML = """
<!doctype html>
<title>Call Transcript Analyzer</title>
<h2>Call Transcript Analyzer</h2>
<form method=post action="/analyze">
  <textarea name=transcript rows=10 cols=80 placeholder="Paste transcript here..."></textarea><br>
  <button type=submit>Analyze</button>
</form>
{% if result %}
  <h3>Result</h3>
  <b>Transcript:</b>
  <pre>{{ result.transcript }}</pre>
  <b>Summary:</b> {{ result.summary }}<br>
  <b>Sentiment:</b> {{ result.sentiment }}<br>
  <p>Saved to <code>{{ csv_file }}</code> at {{ result.timestamp }}</p>
{% endif %}
"""

def call_groq_for_summary_and_sentiment(transcript: str, timeout=30):
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not set in environment")

    system_prompt = (
        "You are a concise assistant. Given a customer call transcript, return a VALID JSON object "
        "with exactly two fields: \"summary\" and \"sentiment\".\n"
        "- \"summary\": 2-3 short sentences summarizing the customer's issue.\n"
        "- \"sentiment\": one of \"positive\", \"neutral\", or \"negative\" (you may also add a one-word adjective like 'frustrated' before the label, e.g. 'frustrated/negative').\n"
        "Output ONLY the JSON object and nothing else."
    )

    user_prompt = f"Transcript:\n{transcript}\n\nReturn JSON only."

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.0,
        "max_completion_tokens": 300
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    resp = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    content = None
    try:
        content = data["choices"][0]["message"]["content"]
    except Exception:
        content = data["choices"][0].get("text") if "choices" in data else None

    if not content:
        raise ValueError("No content returned from Groq API")

    parsed = None
    try:
        parsed = json.loads(content)
    except Exception:
        import re
        m = re.search(r"(\{.*\})", content, re.S)
        if m:
            try:
                parsed = json.loads(m.group(1))
            except Exception:
                parsed = None

    if not parsed or "summary" not in parsed or "sentiment" not in parsed:
        parsed = {
            "summary": content.strip()[:400],
            "sentiment": "unknown"
        }

    return parsed["summary"], parsed["sentiment"], content

def save_to_csv(transcript, summary, sentiment, csv_file=CSV_FILE):
    header = ["Transcript", "Summary", "Sentiment", "AnalyzedAt"]
    exists = os.path.exists(csv_file)
    now = datetime.utcnow().isoformat() + "Z"
    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(header)
        writer.writerow([transcript, summary, sentiment, now])
    return now

@app.route("/", methods=["GET"])
def index():
    return render_template_string(INDEX_HTML, result=None, csv_file=CSV_FILE)

@app.route("/analyze", methods=["POST"])
def analyze():
    transcript = None
    if request.form and "transcript" in request.form:
        transcript = request.form.get("transcript")
    elif request.is_json:
        data = request.get_json(silent=True)
        if data and "transcript" in data:
            transcript = data["transcript"]

    if not transcript or transcript.strip() == "":
        return "Please provide a 'transcript' (form or JSON)", 400

    try:
        summary, sentiment, raw = call_groq_for_summary_and_sentiment(transcript)
    except Exception as e:
        return f"Error calling Groq API: {e}", 500

    ts = save_to_csv(transcript, summary, sentiment)

    result = {"transcript": transcript, "summary": summary, "sentiment": sentiment, "raw": raw, "timestamp": ts}
    return render_template_string(INDEX_HTML, result=result, csv_file=CSV_FILE)

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    body = request.get_json(force=True, silent=True)
    if not body or "transcript" not in body:
        return jsonify({"error": "send JSON with key 'transcript'"}), 400
    transcript = body["transcript"]
    try:
        summary, sentiment, raw = call_groq_for_summary_and_sentiment(transcript)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    ts = save_to_csv(transcript, summary, sentiment)
    return jsonify({"transcript": transcript, "summary": summary, "sentiment": sentiment, "analyzed_at": ts})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
