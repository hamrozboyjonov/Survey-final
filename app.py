import json
import csv
import re
import io
import os
from datetime import datetime, timezone, timedelta
import streamlit as st

QUESTIONS_FILE: str = "questions.json"

HARDCODED_QUESTIONS: list = [
    {
        "text": "How important is a completely quiet environment for you to study effectively?",
        "options": [
            ["Absolutely essential — I cannot study without silence", 0],
            ["Very important — I strongly prefer it", 1],
            ["Somewhat important — I can manage with low noise", 2],
            ["Not very important — background noise rarely bothers me", 3],
            ["Not important at all — noise has no effect on me", 4],
        ],
    },
    {
        "text": "How deeply can you concentrate when studying in a completely silent room?",
        "options": [
            ["Extremely deeply — I lose track of time entirely", 0],
            ["Very deeply — I stay focused for long periods", 1],
            ["Moderately — I focus well but take regular breaks", 2],
            ["Lightly — my mind still wanders despite the silence", 3],
            ["I struggle to concentrate even in total silence", 4],
        ],
    },
    {
        "text": "How quickly does background noise (e.g. conversations, music) break your concentration?",
        "options": [
            ["I never notice it once I am focused", 0],
            ["It takes a significant disturbance to break my focus", 1],
            ["Moderate noise gradually pulls my attention away", 2],
            ["Even low noise interrupts me within minutes", 3],
            ["Any noise immediately destroys my concentration", 4],
        ],
    },
    {
        "text": "How long can you maintain deep focus before losing concentration?",
        "options": [
            ["More than 90 minutes without any break", 0],
            ["60 to 90 minutes before needing a short pause", 1],
            ["30 to 60 minutes before my attention drifts", 2],
            ["15 to 30 minutes before I lose focus", 3],
            ["Less than 15 minutes before I become distracted", 4],
        ],
    },
    {
        "text": "How often do you actively seek out a quiet zone (library, empty room) to study seriously?",
        "options": [
            ["Always — it is part of my standard study routine", 0],
            ["Often — I do so for most important study sessions", 1],
            ["Sometimes — only when the task is particularly demanding", 2],
            ["Rarely — I usually study wherever I happen to be", 3],
            ["Never — I do not seek quiet zones at all", 4],
        ],
    },
    {
        "text": "How does studying in a noisy environment affect the quality of your work?",
        "options": [
            ["It has no effect — my output is the same regardless", 0],
            ["Slight effect — minor drop in quality under noise", 1],
            ["Noticeable effect — I make more errors and work slower", 2],
            ["Significant effect — the quality of my work drops sharply", 3],
            ["Severe effect — I am practically unable to produce good work", 4],
        ],
    },
    {
        "text": "How comfortable are you studying in shared spaces such as open libraries or common rooms?",
        "options": [
            ["Very comfortable — shared spaces work perfectly for me", 0],
            ["Fairly comfortable — minor distractions are manageable", 1],
            ["Somewhat uncomfortable — I tolerate it but prefer otherwise", 2],
            ["Quite uncomfortable — shared spaces drain my concentration", 3],
            ["Very uncomfortable — I avoid them entirely for study", 4],
        ],
    },
    {
        "text": "How often do you use tools such as noise-cancelling headphones or earplugs while studying?",
        "options": [
            ["Never — my environment is naturally quiet enough", 0],
            ["Occasionally — only in unusually noisy situations", 1],
            ["Sometimes — for medium-difficulty tasks", 2],
            ["Often — I rely on them for most study sessions", 3],
            ["Always — I cannot study at all without them", 4],
        ],
    },
    {
        "text": "How well do you retain information studied in a quiet environment compared to a noisy one?",
        "options": [
            ["Equally well — the environment makes no difference", 0],
            ["Slightly better in quiet — a small but noticeable difference", 1],
            ["Moderately better — quiet clearly improves my retention", 2],
            ["Much better — retention is significantly higher in silence", 3],
            ["Dramatically better — I barely retain anything in noisy settings", 4],
        ],
    },
    {
        "text": "How often do unexpected sounds (a door slamming, a phone ringing) cause you to lose your train of thought?",
        "options": [
            ["Never — I remain focused regardless of sudden sounds", 0],
            ["Rarely — only very loud or startling sounds affect me", 1],
            ["Sometimes — moderate unexpected sounds break my focus", 2],
            ["Often — even small sounds regularly disrupt my thinking", 3],
            ["Always — any unexpected sound resets my concentration entirely", 4],
        ],
    },
    {
        "text": "How would you describe your ability to enter a state of deep focus (flow) in your usual study setting?",
        "options": [
            ["Very easy — I enter a flow state quickly and regularly", 0],
            ["Fairly easy — I usually get there within a few minutes", 1],
            ["Moderate — it takes effort and the right conditions", 2],
            ["Difficult — I rarely reach a genuine state of deep focus", 3],
            ["Very difficult — I have almost never experienced deep focus", 4],
        ],
    },
    {
        "text": "How much does low-level ambient sound (e.g. air conditioning, distant traffic) affect your study?",
        "options": [
            ["Not at all — I find it neutral or even helpful", 0],
            ["Very slightly — I notice it but it does not bother me", 1],
            ["Somewhat — it is mildly distracting over time", 2],
            ["Considerably — it noticeably reduces my concentration", 3],
            ["Greatly — even soft ambient sound makes studying very hard", 4],
        ],
    },
    {
        "text": "How often do you feel mentally exhausted after studying in a noisy environment?",
        "options": [
            ["Never — environmental noise does not tire me", 0],
            ["Rarely — only after very long sessions in noisy places", 1],
            ["Sometimes — moderate fatigue after a few hours", 2],
            ["Often — I regularly feel drained after studying in noise", 3],
            ["Always — even short noisy sessions leave me mentally depleted", 4],
        ],
    },
    {
        "text": "How satisfied are you with the quiet study options currently available to you?",
        "options": [
            ["Very satisfied — I always have access to an ideal quiet space", 0],
            ["Fairly satisfied — adequate quiet spaces are usually available", 1],
            ["Neutral — access is inconsistent but I manage", 2],
            ["Fairly dissatisfied — quiet spaces are difficult to find", 3],
            ["Very dissatisfied — I almost never have access to a quiet space", 4],
        ],
    },
    {
        "text": "How effectively can you switch between topics while remaining in deep concentration?",
        "options": [
            ["Very effectively — I transition smoothly without losing focus", 0],
            ["Fairly effectively — brief adjustment time but focus is maintained", 1],
            ["Moderately — switching topics disrupts my concentration noticeably", 2],
            ["With difficulty — task-switching significantly breaks my focus", 3],
            ["Very poorly — any switch essentially ends my concentration session", 4],
        ],
    },
    {
        "text": "How often do you plan your study sessions around the availability of a quiet environment?",
        "options": [
            ["Never — I study whenever and wherever it is convenient", 0],
            ["Rarely — only for major deadlines or exams", 1],
            ["Sometimes — I consider it for important tasks", 2],
            ["Often — quiet availability is a key factor in my planning", 3],
            ["Always — I will not begin a study session without securing a quiet space", 4],
        ],
    },
    {
        "text": "How does studying with background music (without lyrics) affect your concentration?",
        "options": [
            ["It helps me focus — I concentrate better with instrumental music", 0],
            ["It is neutral — no noticeable positive or negative effect", 1],
            ["It mildly distracts me — I prefer silence over music", 2],
            ["It noticeably distracts me — music reduces my concentration", 3],
            ["It severely distracts me — any music makes studying very hard", 4],
        ],
    },
    {
        "text": "How well do you perform on complex tasks (problem-solving, essay writing) in your usual study environment?",
        "options": [
            ["Excellently — I consistently produce high-quality work", 0],
            ["Well — my performance is generally strong with minor lapses", 1],
            ["Adequately — I complete tasks but not always to my best ability", 2],
            ["Poorly — I frequently struggle to think clearly during tasks", 3],
            ["Very poorly — my cognitive performance is consistently low", 4],
        ],
    },
    {
        "text": "How aware are you of other people's movements or activities around you while studying?",
        "options": [
            ["Not aware at all — I am fully absorbed in my work", 0],
            ["Slightly aware — I notice them but am not distracted", 1],
            ["Moderately aware — they occasionally pull my attention", 2],
            ["Very aware — I frequently lose focus due to others nearby", 3],
            ["Extremely aware — I cannot ignore what others around me are doing", 4],
        ],
    },
    {
        "text": "How confident are you that your current study environment supports your best academic performance?",
        "options": [
            ["Very confident — my environment is ideal for my needs", 0],
            ["Fairly confident — it meets most of my requirements", 1],
            ["Uncertain — it is acceptable but far from ideal", 2],
            ["Not very confident — my environment often works against me", 3],
            ["Not confident at all — my environment significantly hinders my performance", 4],
        ],
    },
]

OUTCOMES: tuple = (
    (0, 15,
     "Ideal Match — Deep Concentration",
     "You have an exceptionally strong preference for quiet and achieve deep, sustained concentration. "
     "Your study habits and environment are well-aligned for peak academic performance.",
     "🟢", "#1a7a4a"),
    (16, 30,
     "Strong Preference — High Focus Ability",
     "Quiet zones significantly boost your performance. You focus deeply when conditions are right. "
     "Seek out silent spaces and protect your study time to maintain this strong output.",
     "🟩", "#2d9e5f"),
    (31, 45,
     "Moderate Preference — Good Concentration",
     "You benefit noticeably from quiet environments but can manage moderate noise levels. "
     "Consider using noise-cancelling headphones and scheduling study in quieter periods.",
     "🟡", "#b8860b"),
    (46, 55,
     "Low Sensitivity — Partial Quiet Preference",
     "Noise affects you but you adapt reasonably well. Structured quiet time will improve "
     "your retention and reduce mental fatigue during demanding study sessions.",
     "🟠", "#cc6600"),
    (56, 68,
     "Adaptive Studier — Flexible Concentration",
     "You are largely adaptable to different environments. While quiet is not critical for you, "
     "experimenting with silent study sessions may reveal untapped concentration potential.",
     "🔵", "#1a5a99"),
    (69, 80,
     "Environment-Independent — Highly Flexible",
     "Your concentration is largely unaffected by noise levels. You perform consistently "
     "across environments. Focus on task structure and time management to further optimise performance.",
     "⚪", "#555555"),
)

VALID_FORMATS: frozenset = frozenset({"txt", "csv", "json"})


def load_questions() -> list:
    if os.path.exists(QUESTIONS_FILE):
        try:
            with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, KeyError):
            pass
    return HARDCODED_QUESTIONS


def validate_name(name: str) -> bool:
    pattern: str = r"^[a-zA-Z][a-zA-Z '\-]*[a-zA-Z]$|^[a-zA-Z]$"
    return bool(re.match(pattern, name.strip()))


def validate_dob(dob_str: str) -> bool:
    try:
        dob = datetime.strptime(dob_str.strip(), "%d/%m/%Y")
        today = datetime.now(timezone(timedelta(hours=5))).replace(tzinfo=None)
        age: int = today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )
        return 5 <= age <= 120
    except ValueError:
        return False


def validate_student_id(sid: str) -> bool:
    cleaned: str = sid.strip()
    if len(cleaned) < 4:
        return False
    idx: int = 0
    while idx < len(cleaned):
        if not cleaned[idx].isdigit():
            return False
        idx += 1
    return True


def get_outcome(total_score: int) -> dict:
    for (low, high, label, desc, emoji, color) in OUTCOMES:
        if low <= total_score <= high:
            return {"label": label, "description": desc, "emoji": emoji, "color": color}
    return {"label": "Unknown", "description": "Score out of range.", "emoji": "❓", "color": "#888"}


def build_json_bytes(result: dict, answers: list) -> bytes:
    full: dict = {**result, "answers": answers}
    return json.dumps(full, indent=2, ensure_ascii=False).encode("utf-8")


def build_csv_bytes(result: dict, answers: list) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Field", "Value"])
    for key, value in result.items():
        writer.writerow([key, value])
    writer.writerow([])
    writer.writerow(["No", "Question", "Answer", "Score"])
    for idx, ans in enumerate(answers, start=1):
        writer.writerow([idx, ans["question"], ans["answer"], ans["score"]])
    return output.getvalue().encode("utf-8")


def build_txt_bytes(result: dict, answers: list) -> bytes:
    lines: list = [
        "QUIET STUDY ZONE PREFERENCE & CONCENTRATION DEPTH SURVEY",
        "=" * 60,
    ]
    for key, value in result.items():
        lines.append(f"{key.replace('_', ' ').title()}: {value}")
    lines.append("")
    lines.append("-" * 60)
    lines.append("DETAILED ANSWERS")
    lines.append("-" * 60)
    for idx, ans in enumerate(answers, start=1):
        lines.append(f"{idx}. {ans['question']}")
        lines.append(f"   -> {ans['answer']}  (score: {ans['score']})")
        lines.append("")
    return "\n".join(lines).encode("utf-8")


st.set_page_config(
    page_title="Quiet Study Zone Survey",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.banner {
    background: linear-gradient(135deg, #0d2137 0%, #1a4a7a 55%, #0d6efd 100%);
    border-radius: 14px;
    padding: 2rem 2rem 1.6rem;
    margin-bottom: 1.6rem;
    text-align: center;
}
.banner h1 { color: #fff; font-size: 1.65rem; font-weight: 700; margin: 0 0 0.3rem; }
.banner p  { color: #a8c8f0; font-size: 0.9rem; margin: 0; }

.badge {
    display: inline-block;
    background: #e8f0fe;
    color: #1a4a7a;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 3px 12px;
    border-radius: 20px;
    margin-bottom: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.card {
    background: #ffffff;
    border: 1px solid #dde8f8;
    border-radius: 12px;
    padding: 1.4rem 1.6rem 1rem;
    margin-bottom: 1.2rem;
}

.q-card {
    background: #fff;
    border: 1px solid #e2eaf8;
    border-left: 4px solid #0d6efd;
    border-radius: 10px;
    padding: 1.2rem 1.4rem 0.6rem;
    margin-bottom: 1.1rem;
}
.q-num  { font-size: 0.72rem; font-weight: 700; color: #0d6efd;
          text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.25rem; }
.q-text { font-size: 1rem; font-weight: 600; color: #1a2a3a; line-height: 1.5; }

.result-box {
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin: 1rem 0;
    text-align: center;
}
.r-score { font-size: 3.2rem; font-weight: 800; line-height: 1; }
.r-label { font-size: 1.15rem; font-weight: 700; margin-top: 0.4rem; }
.r-desc  { font-size: 0.92rem; margin-top: 0.7rem; line-height: 1.6; opacity: 0.92; }

.metric-row { display: flex; gap: 10px; margin: 0.8rem 0; }
.metric-box {
    flex: 1; background: #f0f5ff;
    border: 1px solid #c8d8f8; border-radius: 10px;
    padding: 0.8rem; text-align: center;
}
.m-label { font-size: 0.7rem; color: #556; text-transform: uppercase; letter-spacing: 0.05em; }
.m-value { font-size: 1.35rem; font-weight: 700; color: #0d2137; }

.info-box {
    background: #f0f7ff; border: 1px solid #b8d4f8;
    border-radius: 8px; padding: 0.65rem 1rem;
    color: #1a4a7a; font-size: 0.88rem; margin-bottom: 0.8rem;
}
.err-box {
    background: #fff0f0; border: 1px solid #ffcccc;
    border-radius: 8px; padding: 0.55rem 0.9rem;
    color: #cc2222; font-size: 0.87rem; margin-top: 0.25rem;
}

.scale-bar { display: flex; gap: 3px; margin: 0.4rem 0 0.9rem; }
.scale-seg { flex: 1; height: 7px; border-radius: 4px; }

.ans-bar-bg  { background: #eee; border-radius: 4px; height: 5px; margin: 3px 0 10px; }
.ans-bar-fg  { height: 5px; border-radius: 4px; }

div.stButton > button {
    background: linear-gradient(135deg, #0d6efd, #0052cc);
    color: white; border: none; border-radius: 8px;
    font-weight: 600; padding: 0.5rem 1.3rem; transition: opacity 0.15s;
}
div.stButton > button:hover { opacity: 0.86; }

div[data-testid="stProgress"] > div { border-radius: 10px; }

#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


def _init():
    defaults: dict = {
        "page":       "home",
        "surname":    "",
        "given_name": "",
        "dob":        "",
        "student_id": "",
        "answers":    [],
        "current_q":  0,
        "total_score": 0,
        "result":     {},
        "questions":  [],
        "errors":     {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

if not st.session_state["questions"]:
    st.session_state["questions"] = load_questions()

QUESTIONS: list = st.session_state["questions"]
MAX_SCORE: int  = len(QUESTIONS) * 4

st.markdown("""
<div class="banner">
  <h1>📚 Quiet Study Zone Survey</h1>
  <p>Preference &amp; Concentration Depth Assessment</p>
</div>
""", unsafe_allow_html=True)


if st.session_state["page"] == "home":

    st.markdown('<div class="info-box">Answer all <b>20 questions</b> honestly. '
                'Each has <b>5 options</b> scored 0–4. Your total (0–80) maps to '
                'one of <b>6 psychological states</b> describing your study profile.</div>',
                unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🆕  Start New Survey", use_container_width=True):
            for k in ("answers", "current_q", "total_score", "result", "errors"):
                st.session_state[k] = [] if k == "answers" else ({} if k in ("result", "errors") else 0)
            st.session_state["page"] = "details"
            st.rerun()
    with c2:
        if st.button("📂  Load Existing Results", use_container_width=True):
            st.session_state["page"] = "load"
            st.rerun()


elif st.session_state["page"] == "details":

    st.markdown('<div class="badge">Step 1 of 3 — Personal Details</div>', unsafe_allow_html=True)
    st.markdown("### Enter Your Details")
    st.markdown('<div class="info-box">All fields are required and validated before you can proceed.</div>',
                unsafe_allow_html=True)

    errors: dict = st.session_state.get("errors", {})

    name_fields: list = [
        ("surname",    "Surname",    "e.g. Boyjonov"),
        ("given_name", "Given Name", "e.g. Hamrozbek"),
    ]

    for field_key, field_label, placeholder in name_fields:
        val: str = st.text_input(field_label, value=st.session_state[field_key],
                                 placeholder=placeholder, key=f"inp_{field_key}")
        st.session_state[field_key] = val
        if field_key in errors:
            st.markdown(f'<div class="err-box">⚠ {errors[field_key]}</div>', unsafe_allow_html=True)

    dob_val: str = st.text_input("Date of Birth", value=st.session_state["dob"],
                                  placeholder="e.g. 12/10/2006", key="inp_dob")
    st.session_state["dob"] = dob_val
    if "dob" in errors:
        st.markdown(f'<div class="err-box">⚠ {errors["dob"]}</div>', unsafe_allow_html=True)

    sid_val: str = st.text_input("Student ID", value=st.session_state["student_id"],
                                  placeholder="e.g. 00020922", key="inp_sid")
    st.session_state["student_id"] = sid_val
    if "student_id" in errors:
        st.markdown(f'<div class="err-box">⚠ {errors["student_id"]}</div>', unsafe_allow_html=True)

    st.markdown("")
    col_b, col_n = st.columns([1, 2])

    with col_b:
        if st.button("← Back", use_container_width=True):
            st.session_state["page"] = "home"
            st.rerun()

    with col_n:
        if st.button("Continue to Survey →", use_container_width=True):

            new_errors: dict = {}

            for fk, fl, _ in name_fields:
                v: str = st.session_state[fk].strip()
                if not v:
                    new_errors[fk] = f"{fl} is required."
                elif not validate_name(v):
                    new_errors[fk] = (f"{fl} may only contain letters, hyphens (-), "
                                      "apostrophes (') and spaces.")

            dob_in: str = st.session_state["dob"].strip()
            if not dob_in:
                new_errors["dob"] = "Date of birth is required."
            elif not validate_dob(dob_in):
                new_errors["dob"] = "Enter a valid date in DD/MM/YYYY format (age must be 5–120)."

            sid_in: str = st.session_state["student_id"].strip()
            if not sid_in:
                new_errors["student_id"] = "Student ID is required."
            elif not validate_student_id(sid_in):
                new_errors["student_id"] = "Student ID must contain digits only (minimum 4 digits)."

            st.session_state["errors"] = new_errors

            if not new_errors:
                st.session_state["answers"]    = []
                st.session_state["current_q"]  = 0
                st.session_state["total_score"] = 0
                st.session_state["page"]       = "survey"
            st.rerun()


elif st.session_state["page"] == "survey":

    q_idx: int   = st.session_state["current_q"]
    total_q: int = len(QUESTIONS)
    question: dict = QUESTIONS[q_idx]
    options_raw: list = question["options"]
    option_labels: list = [o[0] for o in options_raw]
    option_scores: list = [o[1] for o in options_raw]

    st.markdown(f'<div class="badge">Step 2 of 3 — Question {q_idx + 1} of {total_q}</div>',
                unsafe_allow_html=True)
    st.progress(q_idx / total_q)

    st.markdown(
        f'<div class="q-card">'
        f'<div class="q-num">Question {q_idx + 1}</div>'
        f'<div class="q-text">{question["text"]}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    chosen_label: str = st.radio(
        "Select your answer:",
        options=option_labels,
        key=f"q_{q_idx}",
        label_visibility="collapsed"
    )

    chosen_idx: int   = option_labels.index(chosen_label)
    chosen_score: int = option_scores[chosen_idx]

    st.markdown("")
    col_prev, col_next = st.columns([1, 2])

    with col_prev:
        if q_idx > 0:
            if st.button("← Previous", use_container_width=True):
                if st.session_state["answers"]:
                    removed: dict = st.session_state["answers"].pop()
                    st.session_state["total_score"] -= removed["score"]
                st.session_state["current_q"] -= 1
                st.rerun()

    with col_next:
        btn_lbl: str = "Next Question →" if q_idx < total_q - 1 else "Submit Survey ✓"
        if st.button(btn_lbl, use_container_width=True):

            answer_record: dict = {
                "question": question["text"],
                "answer":   chosen_label,
                "score":    chosen_score,
            }

            answers_list: list = st.session_state["answers"]
            existing_indices: list = list(range(len(answers_list)))

            if q_idx in existing_indices:
                old_score: int = answers_list[q_idx]["score"]
                st.session_state["total_score"] += (chosen_score - old_score)
                answers_list[q_idx] = answer_record
            else:
                st.session_state["total_score"] += chosen_score
                answers_list.append(answer_record)

            if q_idx < total_q - 1:
                st.session_state["current_q"] += 1
                st.rerun()
            else:
                score: int     = st.session_state["total_score"]
                pct: float     = round((score / MAX_SCORE) * 100, 1)
                outcome: dict  = get_outcome(score)
                is_complete: bool = len(answers_list) == total_q

                st.session_state["result"] = {
                    "name":               f"{st.session_state['given_name']} {st.session_state['surname']}",
                    "student_id":         st.session_state["student_id"],
                    "dob":                st.session_state["dob"],
                    "date_taken":         datetime.now(timezone(timedelta(hours=5))).strftime("%d/%m/%Y %H:%M"),
                    "total_score":        score,
                    "max_score":          MAX_SCORE,
                    "percentage":         pct,
                    "survey_complete":    is_complete,
                    "psychological_state": outcome["label"],
                    "description":        outcome["description"],
                }
                st.session_state["page"] = "result"
                st.rerun()


elif st.session_state["page"] == "result":

    result: dict   = st.session_state["result"]
    answers: list  = st.session_state["answers"]
    score: int     = result["total_score"]
    pct: float     = result["percentage"]
    outcome: dict  = get_outcome(score)
    color: str     = outcome["color"]

    st.markdown('<div class="badge">Step 3 of 3 — Your Results</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="result-box" style="background:{color}18;border:2px solid {color}44;">'
        f'<div class="r-score" style="color:{color};">'
        f'{outcome["emoji"]} {score}'
        f'<span style="font-size:1.4rem;color:#778;"> / {MAX_SCORE}</span></div>'
        f'<div class="r-label" style="color:{color};">{outcome["label"]}</div>'
        f'<div class="r-desc" style="color:#334;">{outcome["description"]}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="metric-row">'
        f'<div class="metric-box"><div class="m-label">Score</div>'
        f'<div class="m-value">{score} / {MAX_SCORE}</div></div>'
        f'<div class="metric-box"><div class="m-label">Percentage</div>'
        f'<div class="m-value">{pct}%</div></div>'
        f'<div class="metric-box"><div class="m-label">Questions</div>'
        f'<div class="m-value">{len(answers)} / {len(QUESTIONS)}</div></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    with st.expander("📋 Personal Details"):
        st.markdown(f"**Name:** {result['name']}")
        st.markdown(f"**Student ID:** {result['student_id']}")
        st.markdown(f"**Date of Birth:** {result['dob']}")
        st.markdown(f"**Date Taken:** {result['date_taken']}")

    with st.expander("📝 Full Answer Breakdown"):
        bar_colors: list = ["#1a7a4a", "#5aaa6a", "#b8860b", "#cc6600", "#cc2222"]
        for idx, ans in enumerate(answers, start=1):
            sc: int = ans["score"]
            bar_w: int = int((sc / 4) * 100)
            st.markdown(f"**Q{idx}.** {ans['question']}  \n→ *{ans['answer']}*")
            st.markdown(
                f'<div class="ans-bar-bg">'
                f'<div class="ans-bar-fg" style="width:{bar_w}%;background:{bar_colors[sc]};"></div>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown("### 💾 Save Your Results")
    st.markdown('<div class="info-box">Choose a format and click Download. '
                'The file saves to your device automatically.</div>',
                unsafe_allow_html=True)

    ts: str        = datetime.now(timezone(timedelta(hours=5))).strftime("%Y%m%d_%H%M%S")
    sid: str       = result.get("student_id", "000")
    base_name: str = f"result_{sid}_{ts}"

    col_j, col_c, col_t = st.columns(3)

    with col_j:
        st.download_button(
            label="⬇ Download JSON",
            data=build_json_bytes(result, answers),
            file_name=base_name + ".json",
            mime="application/json",
            use_container_width=True,
        )
        st.caption("Full nested data — best format")

    with col_c:
        st.download_button(
            label="⬇ Download CSV",
            data=build_csv_bytes(result, answers),
            file_name=base_name + ".csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.caption("Spreadsheet compatible")

    with col_t:
        st.download_button(
            label="⬇ Download TXT",
            data=build_txt_bytes(result, answers),
            file_name=base_name + ".txt",
            mime="text/plain",
            use_container_width=True,
        )
        st.caption("Plain text report")

    with st.expander("📊 All Possible Outcomes"):
        for (lo, hi, lbl, desc, emoji, c) in OUTCOMES:
            marker: str = "◀ YOUR RESULT" if lo <= score <= hi else ""
            st.markdown(
                f'<div style="background:{c}11;border-left:4px solid {c};'
                f'border-radius:6px;padding:8px 12px;margin:5px 0;">'
                f'<b style="color:{c};">{emoji} {lo}–{hi}: {lbl}</b> '
                f'<span style="color:#c03;font-size:0.78rem;font-weight:700;">{marker}</span><br>'
                f'<span style="font-size:0.84rem;color:#334;">{desc}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown("")
    if st.button("🔄  Take the Survey Again", use_container_width=True):
        for k in ("answers", "current_q", "total_score", "result",
                  "surname", "given_name", "dob", "student_id", "errors"):
            if k == "answers":
                st.session_state[k] = []
            elif k in ("current_q", "total_score"):
                st.session_state[k] = 0
            elif k in ("result", "errors"):
                st.session_state[k] = {}
            else:
                st.session_state[k] = ""
        st.session_state["page"] = "home"
        st.rerun()


elif st.session_state["page"] == "load":

    st.markdown('<div class="badge">Load Existing Results</div>', unsafe_allow_html=True)
    st.markdown("### Upload a Previously Saved Results File")
    st.markdown('<div class="info-box">Upload a <b>.json</b>, <b>.csv</b>, or <b>.txt</b> '
                'file saved from a previous survey session.</div>',
                unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Choose a result file",
        type=["json", "csv", "txt"],
        label_visibility="collapsed"
    )

    if uploaded is not None:
        ext: str       = uploaded.name.rsplit(".", 1)[-1].lower()
        raw_bytes: bytes = uploaded.read()
        allowed_ext: set = {"json", "csv", "txt"}
        is_valid_ext: bool = ext in allowed_ext

        if not is_valid_ext:
            st.error("Unsupported file type. Please upload a .json, .csv or .txt file.")

        elif ext == "json":
            try:
                data: dict = json.loads(raw_bytes.decode("utf-8"))
                st.success("JSON file loaded successfully.")
                summary_keys: set = {"name", "student_id", "dob", "date_taken",
                                     "total_score", "max_score", "percentage",
                                     "psychological_state", "description"}
                st.markdown("#### Summary")
                for key in summary_keys:
                    if key in data:
                        st.markdown(f"**{key.replace('_', ' ').title()}:** {data[key]}")
                if "answers" in data:
                    st.markdown(f"**Questions Answered:** {len(data['answers'])}")
                    with st.expander("View All Answers"):
                        for i, a in enumerate(data["answers"], 1):
                            st.markdown(f"**Q{i}.** {a.get('question', '')}")
                            st.markdown(f"→ *{a.get('answer', '')}* (score: {a.get('score', '')})")
            except (json.JSONDecodeError, KeyError) as e:
                st.error(f"Could not parse JSON file: {e}")

        elif ext == "csv":
            text: str = raw_bytes.decode("utf-8")
            reader = csv.reader(io.StringIO(text))
            rows: list = list(reader)
            st.success("CSV file loaded successfully.")
            for row in rows:
                if len(row) == 2:
                    st.markdown(f"**{row[0]}:** {row[1]}")
                elif len(row) == 4 and row[0].isdigit():
                    st.markdown(f"Q{row[0]}: {row[1]} → *{row[2]}* (score: {row[3]})")

        else:
            content: str = raw_bytes.decode("utf-8")
            st.success("TXT file loaded successfully.")
            st.text(content)

    st.markdown("")
    if st.button("← Back to Home", use_container_width=True):
        st.session_state["page"] = "home"
        st.rerun()


st.markdown("---")
st.markdown(
    '<div style="text-align:center;font-size:0.78rem;color:#888;">'
    'Quiet Study Zone Preference Survey'
    '</div>',
    unsafe_allow_html=True
)
