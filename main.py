import streamlit as st
import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyAXAEAtDYHkurCjLf21T1kwfct60AMb5Fw"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

def solve_math_problem(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")  # Use the 2.0-flash model
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        models = genai.list_models()
        available_models = [model.name for model in models if 'generateContent' in model.supported_generation_methods]
        if len(available_models) == 0:
            return f"❌ Error: {str(e)} \n Gemini-2.0-flash is not available, and no other models are available."
        else:
            return f"❌ Error: {str(e)} \n Gemini-2.0-flash is not available. Available Models: {available_models}"

# Streamlit UI
st.set_page_config(page_title="Ganit Prakash - AI Math Solver", layout="wide")
st.title("🧮 Ganit Prakash - AI Math Solver")
st.write("Enter any math question below, and I'll solve it step-by-step!")

# User Input
user_input = st.text_area("✍ Enter your math question:")

# Solve Button
if st.button("📌 Solve Now"):
    if user_input.strip():
        solution = solve_math_problem(user_input)
        st.markdown(f"<div style='font-size: 20px; font-weight: bold;'>{solution}</div>", unsafe_allow_html=True)
    else:
        st.warning("⚠ Please enter a math question before clicking Solve.")
