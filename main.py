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
    model = genai.GenerativeModel("gemini-2.0-flash")
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
# 🧾 Render Math Notebook Style
# ------------------------
def render_math_blocks(text):
    # Split into LaTeX and plain parts
    parts = re.split(r"(\$\$.*?\$\$|\$.*?\$)", text, flags=re.DOTALL)
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part.startswith("$$") and part.endswith("$$"):
            st.latex(part.strip("$$"))
        elif part.startswith("$") and part.endswith("$"):
            st.latex(part.strip("$"))
        else:
            st.markdown(f"<div style='font-size: 18px; line-height: 1.6;'>{part}</div>", unsafe_allow_html=True)

# ------------------------
# 🎨 Streamlit Frontend
# ------------------------
st.set_page_config(page_title="Ganit Prakash - AI Math Solver", layout="wide")
st.title("🧮 Ganit Prakash - AI Math Solver")
st.write("Enter any math question below, and I'll solve it step-by-step!")

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
user_input = st.text_area("✍ Enter your math question:", value=st.session_state.get("user_input", ""), height=150)

# 📌 Solve Button
if st.button("📌 Solve Now"):
    if user_input.strip():
        st.session_state["user_input"] = user_input
        with st.spinner("🤔 Thinking..."):
            st.markdown("---")
            placeholder = st.empty()
            solution_generator = solve_math_problem_streamed(user_input)
            final_solution = ""

            for partial in solution_generator:
                final_solution = partial
                placeholder.markdown("📝 Rendering solution...", unsafe_allow_html=True)

        # Render notebook-style
        with st.container():
            st.subheader("🧾 Notebook-style Solution")
            render_math_blocks(final_solution)
    else:
        st.warning("⚠ Please enter a math question before clicking Solve.")
