import streamlit as st
import google.generativeai as genai
import os
import re

# ------------------------
# 🔐 Secure API Key Config
# ------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("🔐 Gemini API key is missing. Please set it via environment variable `GEMINI_API_KEY`.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# ------------------------
# 🚀 Try Initializing Model
# ------------------------
try:
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
except Exception as e:
    st.error(f"❌ Failed to initialize Gemini model: {e}")
    st.stop()

# ------------------------
# 🧠 Solve Math Prompt (Streaming + Beautification)
# ------------------------
def beautify_math_symbols(text):
    replacements = [
        (r"\\sqrt\{([^}]+)\}", r"√(\1)"),
        (r"sqrt\(([^)]+)\)", r"√(\1)"),
        (r"int_", r"∫_"),
        (r"\\int", r"∫"),
        (r"\\pi", r"π"),
        (r"\\frac\{([^}]+)\}\{([^}]+)\}", r"(\1⁄\2)"),
        (r"frac\(([^,]+),([^)]+)\)", r"(\1⁄\2)"),
        (r"\\theta", r"θ"),
        (r"\\sin", r"sin"),
        (r"\\cos", r"cos"),
        (r"\\pm", r"±"),
        (r"\\left", ""),
        (r"\\right", ""),
        (r"\*\*", r"^")
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    return text

def solve_math_problem_streamed(prompt):
    try:
        response_stream = model.generate_content(prompt, stream=True)
        streamed_text = ""
        for chunk in response_stream:
            if chunk.text:
                clean = beautify_math_symbols(chunk.text)
                streamed_text += clean
                yield streamed_text
    except Exception as e:
        try:
            models = genai.list_models()
            available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
            yield f"❌ Error: {str(e)}\n\nAvailable Models: {available_models}"
        except Exception as inner_e:
            yield f"❌ Critical Error: {str(inner_e)}"

# ------------------------
# 🎨 Streamlit Frontend
# ------------------------
st.set_page_config(page_title="Ganit Prakash - AI Math Solver", layout="wide")
st.title("🧮 Ganit Prakash - AI Math Solver")
st.markdown("Enter any math question below, and get a detailed, step-by-step solution like you'd write in a notebook.")

# 🔎 Example Prompts
examples = [
    "What is the derivative of sin(x^2)?",
    "Solve the equation 2x^2 + 3x - 5 = 0.",
    "What is the integral of 1 / (1 + x^2)?",
    "Find the area enclosed by the ellipse x^2/a^2 + y^2/b^2 = 1.",
]

with st.expander("💡 Example Questions"):
    for i, example in enumerate(examples):
        if st.button(f"Example {i+1}: {example}"):
            st.session_state["user_input"] = example

# ✍ Input Area
user_input = st.text_area("✍ Enter your math question:", value=st.session_state.get("user_input", ""))

# 📌 Solve Button
if st.button("📌 Solve Now"):
    if user_input.strip():
        with st.spinner("🤔 Solving..."):
            st.markdown("---")
            st.markdown("### ✅ Solution")
            placeholder = st.empty()
            solution_generator = solve_math_problem_streamed(user_input)
            full_text = ""
            for partial in solution_generator:
                full_text = partial
                placeholder.markdown(
                    f"<div style='font-size: 18px; white-space: pre-wrap; font-family: monospace;'>{partial}</div>",
                    unsafe_allow_html=True
                )
    else:
        st.warning("⚠ Please enter a math question before clicking Solve.")
