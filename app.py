from flask import Flask, render_template, request, jsonify
from groq import Groq
from pypdf import PdfReader
from adzuna_api import fetch_live_internships
import json, io

app = Flask(__name__)
client = Groq(api_key="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")

def extract_pdf_text(file_bytes):
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text[:3000]
    except:
        return ""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/parse-resume", methods=["POST"])
def parse_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files["resume"]
    text = extract_pdf_text(file.read())
    if not text.strip():
        return jsonify({"error": "Could not read PDF"}), 400
    prompt = f"""Extract student profile from this resume.
Resume: {text}
Return ONLY valid JSON (no markdown):
{{"name":"","education":"","skills":"","gpa":"","interests":"","goals":"","experience":"Beginner"}}"""
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":"Extract resume info. Return only valid JSON, no markdown."},
                      {"role":"user","content":prompt}],
            max_tokens=600, temperature=0.3
        )
        text_out = res.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
        return jsonify(json.loads(text_out))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/analyze", methods=["POST"])
def analyze():
    profile = request.json

    # ── Step 1: Fetch LIVE internships from Adzuna ──
    live_results = fetch_live_internships(profile, top_n=15)

    # ── Step 2: Groq AI → Profile insights ──
    internship_list = "\n".join([
        f"{i['title']} @ {i['company']} | {i['location']} | Apply: {i['apply_url']}"
        for i in live_results[:8]
    ])

    prompt = f"""You are an expert internship advisor for Indian students.

STUDENT PROFILE:
- Name: {profile.get('name')}
- Education: {profile.get('education')}
- Skills: {profile.get('skills')}
- GPA: {profile.get('gpa')}
- Interests: {profile.get('interests')}
- Goals: {profile.get('goals')}

Live internships found for this student:
{internship_list if internship_list else "Searching live internships..."}

Return ONLY valid JSON (no markdown):
{{
  "profileScore": 75,
  "strengthSummary": "2-3 sentences about student strengths",
  "careerPath": "Career trajectory in 2-3 sentences",
  "skillGaps": ["skill1", "skill2", "skill3"],
  "quickTips": ["tip1", "tip2", "tip3"]
}}"""

    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":"Expert internship advisor. Return valid JSON only. No markdown."},
                      {"role":"user","content":prompt}],
            max_tokens=800, temperature=0.6
        )
        text = res.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
        ai_data = json.loads(text)
    except:
        ai_data = {
            "profileScore": 70,
            "strengthSummary": f"{profile.get('name','Student')} has good potential.",
            "careerPath": "Strong foundation for internship opportunities.",
            "skillGaps": ["Portfolio Projects", "Communication", "Industry Tools"],
            "quickTips": ["Apply to 5+ internships", "Build a portfolio", "Improve LinkedIn"]
        }

    return jsonify({
        "matchedInternships": live_results,
        "profileScore":       ai_data.get("profileScore", 70),
        "strengthSummary":    ai_data.get("strengthSummary", ""),
        "careerPath":         ai_data.get("careerPath", ""),
        "skillGaps":          ai_data.get("skillGaps", []),
        "quickTips":          ai_data.get("quickTips", []),
        "totalLive":          len(live_results),
        "source":             "Adzuna Live API"
    })

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content":f"Expert internship advisor. Student profile: {json.dumps(data.get('profile',{}))}. Results are from Adzuna live API — real internships with direct apply links."},
                {"role":"user","content":data.get("message","")}
            ],
            max_tokens=600, temperature=0.7
        )
        return jsonify({"reply": res.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🚀 InternMatch AI — 100% Live Internships")
    print("🌐 Source: Adzuna Live API (Real jobs, Direct apply links)")
    app.run(debug=True)
