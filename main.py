import streamlit as st
import google.generativeai as genai
import os
import re

# 🔐 API Key Config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("🔐 Gemini API key is missing. Please set it via environment variable `GEMINI_API_KEY`.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# 🚀 Load Gemini Model
try:
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    st.error(f"❌ Failed to initialize Gemini model: {e}")
    st.stop()

# 🧠 Solve with Streaming
def solve_math_problem_streamed(prompt):
    try:
        response_stream = model.generate_content(prompt, stream=True)
        streamed_text = ""
        for chunk in response_stream:
            if chunk.text:
                streamed_text += chunk.text
                yield streamed_text
    except Exception as e:
        yield f"❌ Error: {str(e)}"

# 📐 Render math expressions nicely
def render_mixed_output(full_text):
    lines = full_text.splitlines()
    for line in lines:
        if re.search(r'(sin|cos|tan|log|ln|sqrt|\^|∫|dx)', line, re.IGNORECASE):
            try:
                st.latex(line)
            except:
                st.markdown(line)
        else:
            st.markdown(line)

# 🎨 UI Setup
st.set_page_config(page_title="Ganit Prakash - AI Math Solver", layout="wide")
st.title("🧮 Ganit Prakash - AI Math Solver")
st.write("Enter any math question below, and I'll solve it step-by-step!")

# 💡 Example Prompts
examples = [
    "What is the derivative of sin(x^2)?",
    "Solve the equation 2x^2 + 3x - 5 = 0.",
    "What is the integral of 1 / (1 + x^2)?",
    "How do you find the area of a triangle given 3 sides?",
]

with st.expander("💡 Example Questions"):
    for i, example in enumerate(examples):
        if st.button(f"Example {i+1}: {example}"):
            st.session_state["user_input"] = example

# ✍ Input Area
user_input = st.text_area("✍ Enter your math question:", value=st.session_state.get("user_input", ""))

# 📌 Solve
if st.button("📌 Solve Now"):
    if user_input.strip():
        with st.spinner("🤔 Thinking..."):
            st.markdown("---")
            st.markdown("### ✅ Solution")
            placeholder = st.empty()
            solution_generator = solve_math_problem_streamed(user_input)
            full_text = ""
            for partial in solution_generator:
                full_text = partial
                placeholder.markdown(
                    f"<div style='font-size: 18px; white-space: pre-wrap;'>{partial}</div>",
                    unsafe_allow_html=True
                )
            placeholder.empty()
            render_mixed_output(full_text)
    else:
        st.warning("⚠ Please enter a math question before clicking Solve.")
