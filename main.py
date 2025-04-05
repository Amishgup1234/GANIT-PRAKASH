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
# 🚀 Initialize Gemini Model
# ------------------------
try:
    model = genai.GenerativeModel("gemini-1.5-pro")
except Exception as e:
    st.error(f"❌ Failed to initialize Gemini model: {e}")
    st.stop()

# ------------------------
# 🧠 Solve Math Prompt (Streaming)
# ------------------------
def solve_math_problem_streamed(prompt):
    try:
        response_stream = model.generate_content(prompt, stream=True)
        streamed_text = ""
        for chunk in response_stream:
            if chunk.text:
                streamed_text += chunk.text
                yield streamed_text
    except Exception as e:
        try:
            models = genai.list_models()
            available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
            yield f"❌ Error: {str(e)}\n\nAvailable Models: {available_models}"
        except Exception as inner_e:
            yield f"❌ Critical Error: {str(inner_e)}"

# ------------------------
# 🖋️ Render Output Nicely for Mobile
# ------------------------
def clean_and_render_math(text):
    text = re.sub(r'\bsqrt\((.*?)\)', r'\\sqrt{\1}', text)
    text = re.sub(r'\bint\b', r'\\int', text)
    text = re.sub(r'\bdx\b', r'\,dx', text)
    text = re.sub(r'\bdy\b', r'\,dy', text)
    text = re.sub(r'\bsum\b', r'\\sum', text)
    text = re.sub(r"([=<>+\-*/^])", r" \1 ", text)
    text = re.sub(r'(?<![\^\\])([a-zA-Z])(\d+)', r'\1^\2', text)

    parts = re.split(r"(\$\$.*?\$\$|\$.*?\$)", text, flags=re.DOTALL)

    with st.container():
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if part.startswith("$$") and part.endswith("$$"):
                st.latex(part.strip("$$"))
            elif part.startswith("$") and part.endswith("$"):
                st.latex(part.strip("$"))
            else:
                st.markdown(
                    f"<div style='font-size: 16px; line-height: 1.6; margin: 0.5rem 0;'>{part}</div>",
                    unsafe_allow_html=True
                )

# ------------------------
# 🎨 Streamlit UI Setup
# ------------------------
st.set_page_config(page_title="Math Master - AI Math Solver", layout="centered")

# Hide Streamlit Footer for Mobile
st.markdown("""
    <style>
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 id="top">🧮 Math Master - AI Math Solver</h1>', unsafe_allow_html=True)
st.write("Enter any math problem below, and get a full notebook-style explanation!")

# 🔎 Example Prompts
examples = [
    "Find the area enclosed by the ellipse x^2/a^2 + y^2/b^2 = 1.",
    "What is the derivative of sin(x^2)?",
    "Solve the equation 2x^2 + 3x - 5 = 0.",
    "What is the integral of 1 / (1 + x^2)?",
    "Find the area between the curve y = 3√x, x=2 to x=4, and the x-axis.",
]

with st.expander("💡 Tap to see Example Problems"):
    for i, example in enumerate(examples):
        if st.button(f"Example {i+1}: {example}"):
            st.session_state["user_input"] = example

# ✍ User Input
user_input = st.text_area("✍ Enter your math problem:", value=st.session_state.get("user_input", ""), height=100)

# 📌 Solve Button
if st.button("🧠 Solve"):
    if user_input.strip():
        st.markdown("---")
        st.markdown("### ✅ Solution:")

        detailed_prompt = f"""
You are a highly skilled math tutor. Solve the following math problem using step-by-step reasoning. 
Each step must be well-explained and justified, not just calculated.

✅ Use proper LaTeX formatting for all mathematical expressions.
✅ Use notebook-style explanation: alternate text and equations, showing logic and structure.
✅ Begin by analyzing the problem type (e.g., integral, derivative, equation solving).
✅ End with a final boxed or clearly labeled answer.

Problem: {user_input}
"""

        placeholder = st.empty()
        with st.spinner("🧠 Solving..."):
            solution_generator = solve_math_problem_streamed(detailed_prompt)
            for partial in solution_generator:
                placeholder.empty()
                with placeholder.container():
                    clean_and_render_math(partial)

        # 🔝 Back to top
        st.markdown('<a href="#top" style="font-size:14px;">🔝 Back to Top</a>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ Please enter a math problem first.")
