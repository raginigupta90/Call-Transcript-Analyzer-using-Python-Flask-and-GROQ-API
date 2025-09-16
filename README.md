**📞Call Transcript Analyzer**

A simple Python + Flask web application that analyzes customer call transcripts using the Groq API.

It automatically:

Summarizes the transcript in 2–3 sentences

Detects customer sentiment (Positive / Neutral / Negative)

Saves results into a CSV file (call_analysis.csv)

**🚀Features**

Web form to paste call transcripts

REST API endpoint for JSON input/output

Uses Groq LLM for summarization & sentiment analysis

Stores transcript, summary, sentiment, and timestamp in a CSV file

Easy to run locally with Python

**🛠️ Tech Stack**

Python 3

Flask

Groq API

CSV file storage

📂** Project Structure**
call-analyser/
│── app.py              # Main Flask application
│── call_analysis.csv   # Output CSV (auto-created after analysis)
│── venv/               # Virtual environment (optional)
│── README.md           # Project documentation

**⚙️Installation & Setup**

Clone the repository

git clone https://github.com/your-username/call-analyser.git
cd call-analyser


Create virtual environment (optional but recommended)

python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows


Install dependencies

pip install flask requests


Set your Groq API Key

export GROQ_API_KEY="your_api_key_here"   # Linux/Mac
set GROQ_API_KEY="your_api_key_here"      # Windows (cmd)


Run the Flask server

python app.py


Open in browser
Go to → http://127.0.0.1:5000/

**🔑 API Usage**
Endpoint:
POST /api/analyze

Example Request (JSON)
{
  "transcript": "Hi, I was trying to book a slot yesterday but the payment failed."
}

Example Response (JSON)
{
  "transcript": "Hi, I was trying to book a slot yesterday but the payment failed.",
  "summary": "Customer faced a payment failure while booking a slot.",
  "sentiment": "Negative",
  "timestamp": "2025-09-15 22:45:27"
}

**📊Output File**

All results are saved into call_analysis.csv with 4 columns:

Transcript	Summary	Sentiment	Timestamp
Hi, I was trying to book a slot yesterday but the payment failed…	Customer faced a payment failure while booking a slot.	Negative	2025-09-15 22:45:27

**📽️ Demo Video**

👉 https://drive.google.com/file/d/1qpSQDeW4f_fO3pwYQR0MIxrb9EBXkgfj/view?usp=sharing

**🙌Acknowledgements**

Flask

Groq API
