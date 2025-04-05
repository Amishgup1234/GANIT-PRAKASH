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
# 🖋️ Render Output Nicely with Math Symbols
# ------------------------
def clean_and_render_math(text):
    replacements = {
        "sqrt": "√",
        "int": "∫",
        "pi": "π",
        "infty": "∞",
        "->": "→",
        "<=": "≤",
        ">=": "≥",
    }

    for ascii_key, symbol in replacements.items():
        text = re.sub(rf"\b{ascii_key}\b", symbol, text)

    # Handle LaTeX + plain text sections
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
                    f"<div style='font-size: 17px; line-height: 1.7; margin-bottom: 0.5rem;'>{part}</div>",
                    unsafe_allow_html=True
                )

# ------------------------
# 🎨 Streamlit UI
# ------------------------
st.set_page_config(page_title="Ganit Prakash - AI Math Solver", layout="wide")
st.title("🧮 Ganit Prakash - AI Math Solver")
st.write("Enter any math problem below, and get a full notebook-style explanation!")

# ✍ User Input
user_input = st.text_area("✍ Enter your math problem:", value=st.session_state.get("user_input", ""), height=150)

# 📌 Solve Button
if st.button("📌 Solve Now"):
    if user_input.strip():
        st.markdown("---")
        st.markdown("### ✅ Solution:")

        # Enhanced Prompt for Gemini
        detailed_prompt = f"""You are a helpful and skilled math tutor. Solve the following math problem with a complete, step-by-step explanation.
Use clear LaTeX for all equations, explain the logic behind each step, and include reasoning like a real human tutor would.
Use proper math symbols like √, ∫, π, and ∞.

Problem: {user_input}
"""

        placeholder = st.empty()
        full_text = ""
        with st.spinner("🧠 Solving..."):
            solution_generator = solve_math_problem_streamed(detailed_prompt)
            for partial in solution_generator:
                full_text = partial
                placeholder.empty()
                with placeholder.container():
                    clean_and_render_math(partial)
    else:
        st.warning("⚠️ Please enter a math problem first.")
