from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse,parse_qs
import yt_dlp
import whisper

import fitz
import os
import requests

# Load API key from environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

app = Flask(__name__)
CORS(app, origins="http://localhost:3000")

def get_summary(text):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",  # or another model available on OpenRouter
        "messages": [
            {"role": "system", "content": "You are a helpful summarizer."},
            {"role": "user", "content": f"Summarize the following text:\n{text}"}
        ],
        "max_tokens": 300
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                             headers=headers, json=data)
    result = response.json()
      # Debugging: print the raw response
    print("OpenRouter response:", result)

    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    elif "error" in result:
        return f"Error from API: {result['error']}"
    else:
        return "Unexpected response format"
   

@app.route('/summarize/text', methods=['POST'])
def summarize_text():
    data = request.get_json()
    text = data['text']
    summary = get_summary(text)
    return jsonify({"summary": summary})

@app.route('/summarize/pdf', methods=['POST'])
def summarize_pdf():
    file = request.files['file']
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    summary = get_summary(text)
    return jsonify({"summary": summary})

     

if __name__ == '__main__':
    app.run(debug=True)
