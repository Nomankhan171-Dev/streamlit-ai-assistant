
import ast
import operator
import re
import streamlit as st

st.set_page_config(page_title="Nexa AI Assistant", page_icon="🤖", layout="centered")

st.markdown("""
<style>
.stApp{background:radial-gradient(circle at 10% 0%,rgba(38,99,235,.16),transparent 30%),#07111f;color:#f8fafc}
[data-testid="stHeader"]{background:transparent}
.main-title{font-size:2.4rem;font-weight:800;margin-bottom:.2rem}
.sub-title{color:#94a3b8;font-size:1rem;margin-bottom:1.4rem}
.tech-badges{display:flex;gap:10px;margin:8px 0 18px;flex-wrap:wrap}
.badge{background:#12233a;color:#22d3ee;border:1px solid #1e3a5f;padding:7px 12px;border-radius:9px;font-size:.78rem;font-weight:700;letter-spacing:.04em}
.small-note{color:#64748b;font-size:.78rem;text-align:center;margin-top:12px}
</style>
""", unsafe_allow_html=True)

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def safe_eval(expr):
    def _eval(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
            return OPS[type(node.op)](_eval(node.operand))
        raise ValueError("Unsupported expression")
    return _eval(ast.parse(expr, mode="eval").body)

def calculator_answer(text):
    q = text.lower().strip()

    pct = re.fullmatch(r"\s*(-?\d+(?:\.\d+)?)\s*%\s*(?:of|ka)\s*(-?\d+(?:\.\d+)?)\s*", q)
    if pct:
        p = float(pct.group(1))
        n = float(pct.group(2))
        result = (p / 100) * n
        return f"{p:g}% of {n:g} = **{result:g}**"

    replacements = {
        "plus": "+",
        "minus": "-",
        "times": "*",
        "multiply by": "*",
        "multiplied by": "*",
        "divide by": "/",
        "divided by": "/",
    }

    cleaned = q
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)

    cleaned = re.sub(r"\b(calculate|solve|what is|answer|please|kitna|kitni|hai|hy)\b", "", cleaned)
    cleaned = cleaned.strip().replace("?", "")

    if not re.fullmatch(r"[0-9\.\+\-\*\/%\(\)\s]+", cleaned):
        return None
    if not re.search(r"[\+\-\*\/%]", cleaned):
        return None

    try:
        result = safe_eval(cleaned)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return f"Answer: **{result}**"
    except Exception:
        return None

def smart_answer(text):
    calc = calculator_answer(text)
    if calc:
        return calc

    q = text.lower().strip()

    if any(x in q for x in ["hello", "hi", "hey", "aoa", "assalam", "salam"]):
        return "Hello! I’m Nexa AI Assistant. Ask me a question or give me a calculation."

    if "how are you" in q:
        return "I’m ready to help. Ask me anything about design, development, AI basics, or calculations."

    if "who are you" in q or "your name" in q:
        return "I’m **Nexa AI Assistant**, built with Python and Streamlit."

    if "what can you do" in q:
        return "I can handle basic conversations, solve calculations, calculate percentages, and answer built-in questions about AI, UI/UX, Python, Streamlit, GitHub, HTML, CSS, and JavaScript."

    knowledge = [
        (["what is ai", "artificial intelligence"], "Artificial Intelligence is technology that enables software to recognize patterns, process information, and generate useful outputs such as text, predictions, recommendations, or images."),
        (["ui ux", "ui/ux"], "UI means **User Interface** — how a product looks. UX means **User Experience** — how easy, useful, and smooth the product feels to use."),
        (["python"], "Python is a popular programming language used for AI, automation, web apps, data science, scripting, and backend development."),
        (["streamlit"], "Streamlit is a Python framework for quickly building interactive web apps, dashboards, and AI interfaces."),
        (["github"], "GitHub is a platform for storing Git repositories, tracking changes, collaborating on code, and showcasing development projects."),
        (["html"], "HTML gives a webpage its structure — headings, text, buttons, images, forms, and sections."),
        (["css"], "CSS controls the visual design of a webpage — colors, spacing, typography, layouts, and responsive styling."),
        (["javascript"], "JavaScript adds logic and interactivity to websites, such as dynamic content, menus, forms, and calculations."),
        (["portfolio"], "A strong portfolio should show your best projects, your role, the problem, process, final result, tools used, and a live demo or GitHub link."),
        (["capital of pakistan"], "The capital of Pakistan is **Islamabad**."),
    ]

    for keys, answer in knowledge:
        if any(k in q for k in keys):
            return answer

    return "I can answer built-in questions and calculations directly. For unlimited open-ended answers like ChatGPT, connect this Streamlit interface to a real AI model or API."

st.markdown('<div class="main-title">Nexa AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Smart assistant built with Python, Streamlit, and AI-style logic.</div>', unsafe_allow_html=True)
st.markdown("""
<div class="tech-badges">
<span class="badge">PYTHON</span>
<span class="badge">STREAMLIT</span>
<span class="badge">AI</span>
</div>
""", unsafe_allow_html=True)

with st.expander("What can this assistant do?"):
    st.write("• Basic conversation")
    st.write("• Plus / minus / multiply / divide")
    st.write("• Percentage calculations")
    st.write("• Built-in tech and design questions")
    st.write("• Chat history during the session")

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I’m Nexa AI Assistant. Try `1250 + 875`, `15% of 8000`, or ask `What is UI/UX?`"
    }]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask Nexa anything...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    answer = smart_answer(prompt)
    st.session_state.messages.append({"role": "assistant", "content": answer})

    with st.chat_message("assistant"):
        st.markdown(answer)

st.markdown('<div class="small-note">Python • Streamlit • Smart Assistant Portfolio Project</div>', unsafe_allow_html=True)
