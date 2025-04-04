import streamlit as st
import google.generativeai as genai

# Set Gemini API Key
GEMINI_API_KEY = "AIzaSyBPkqBNZ0oZqkEPOqncGpgyIazhLXqBupU"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

# Streamlit UI
st.set_page_config(page_title="Ganit Prakash - AI Math Solver", layout="wide")
st.title("🧮 Ganit Prakash - AI Math Solver")
st.write("Enter any math question below, and I'll solve it step-by-step!")

# User Input
user_input = st.text_area("✍ Enter your math question:")

# Function to Get AI Solution
def solve_math_problem(prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Solve Button
if st.button("📌 Solve Now"):
    if user_input.strip():
        solution = solve_math_problem(user_input)
        st.markdown(f"<div style='font-size: 20px; font-weight: bold;'>{solution}</div>", unsafe_allow_html=True)
    else:
        st.warning("⚠ Please enter a math question before clicking Solve.")
