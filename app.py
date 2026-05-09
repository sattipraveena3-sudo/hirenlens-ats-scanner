import streamlit as st
from groq import Groq
import json
import re

# ───────────────────────── PAGE CONFIG ─────────────────────────
st.set_page_config(
    page_title="HireLens",
    page_icon="📑",
    layout="wide"
)

# ───────────────────────── CSS ─────────────────────────
st.markdown("""
<style>
body { background-color:#0f172a; }
.stApp { background-color:#0f172a; color:white; }

.stTextArea textarea {
    background:#1e293b !important;
    color:#fff !important;
    border-radius:12px;
}

.stButton > button {
    width:100%;
    background:linear-gradient(135deg,#6366f1,#8b5cf6);
    color:white;
    font-weight:800;
    padding:14px;
    border-radius:12px;
}

.score-card {
    background:#1e293b;
    padding:25px;
    border-radius:18px;
    text-align:center;
    margin-top:20px;
}

.card {
    background:#1e293b;
    padding:16px;
    border-radius:14px;
    margin-top:12px;
}

.tag {
    display:inline-block;
    padding:5px 10px;
    margin:4px;
    border-radius:20px;
    font-size:12px;
    font-weight:700;
}

.green { background:#10b98122; color:#10b981; }
.red { background:#ef444422; color:#ef4444; }
.blue { background:#6366f122; color:#818cf8; }
.yellow { background:#f59e0b22; color:#f59e0b; }

</style>
""", unsafe_allow_html=True)

# ───────────────────────── API KEY ─────────────────────────
api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

# ───────────────────────── SYSTEM PROMPT ─────────────────────────
SYSTEM_PROMPT = """
Return ONLY valid JSON. No HTML. No markdown.

Format:
{
 "match_score": 0-100,
 "verdict": "",
 "summary": "",
 "matched_keywords": [],
 "missing_keywords": [],
 "matched_skills": [],
 "missing_skills": [],
 "strengths": [],
 "improvements": [],
 "ats_tips": []
}
"""

# ───────────────────────── UI ─────────────────────────
st.title(" ATS Resume Scanner")

col1, col2 = st.columns(2)

with col1:
    resume = st.text_area("Resume", height=300)

with col2:
    job_desc = st.text_area("Job Description", height=300)

btn = st.button("Analyze Resume ")

# ───────────────────────── CLEAN FUNCTION ─────────────────────────
def clean_json(text):
    text = re.sub(r"```json|```", "", text)
    return text.strip()

# ───────────────────────── ANALYSIS ─────────────────────────
if btn:
    if not resume or not job_desc:
        st.warning("Please fill both fields")
    else:
        with st.spinner("Analyzing..."):
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role":"system","content":SYSTEM_PROMPT},
                    {"role":"user","content":f"RESUME:\n{resume}\n\nJOB:\n{job_desc}"}
                ],
                temperature=0.2
            )

            raw = res.choices[0].message.content
            clean = clean_json(raw)

            try:
                data = json.loads(clean)
            except:
                st.error("Model returned invalid JSON")
                st.stop()

            score = data.get("match_score",0)

            color = "#10b981" if score > 75 else "#f59e0b" if score > 50 else "#ef4444"

            # ───────── SCORE CARD ─────────
            st.markdown(f"""
            <div class="score-card">
                <h1 style="color:{color};font-size:64px;">{score}%</h1>
                <h3>ATS MATCH SCORE</h3>
                <h2>{data.get("verdict","")}</h2>
                <p>{data.get("summary","")}</p>
            </div>
            """, unsafe_allow_html=True)

            # ───────── KEYWORDS ─────────
            colA, colB = st.columns(2)

            with colA:
                st.markdown("### ✅ Matched Keywords")
                st.write(" ".join([f"`{x}`" for x in data.get("matched_keywords",[])]))

            with colB:
                st.markdown("### ❌ Missing Keywords")
                st.write(" ".join([f"`{x}`" for x in data.get("missing_keywords",[])]))

            # ───────── SKILLS ─────────
            colC, colD = st.columns(2)

            with colC:
                st.markdown("### 💪 Matched Skills")
                st.write(" ".join([f"`{x}`" for x in data.get("matched_skills",[])]))

            with colD:
                st.markdown("### ⚠️ Missing Skills")
                st.write(" ".join([f"`{x}`" for x in data.get("missing_skills",[])]))

            # ───────── LISTS ─────────
            st.markdown("### 🌟 Strengths")
            for i in data.get("strengths",[]):
                st.write("✔", i)

            st.markdown("### 🔧 Improvements")
            for i in data.get("improvements",[]):
                st.write("➡", i)

            st.markdown("### 💡 ATS Tips")
            for i in data.get("ats_tips",[]):
                st.write("💡", i)