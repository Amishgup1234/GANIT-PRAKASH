import streamlit as st
import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyAXAEAtDYHkurCjLf21T1kwfct60AMb5Fw"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

def solve_math_problem(prompt):
    """Solves a math problem using Gemini, with a student-like step-by-step approach."""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        detailed_prompt = f"""
        Solve the following math problem step-by-step, showing all your work and explaining each step as if you were a student solving it:

        {prompt}
        """
        response = model.generate_content(detailed_prompt)
        return response.text
    except Exception as e:
        models = genai.list_models()
        available_models = [model.name for model in models if 'generateContent' in model.supported_generation_methods]
        if len(available_models) == 0:
            return f"❌ Error: {str(e)} \n Gemini-2.0-flash is not available, and no other models are available."
        else:
            return f"❌ Error: {str(e)} \n Gemini-2.0-flash is not available. Available Models: {available_models}"

def format_gemini_response(text):
    """Formats the Gemini response for better readability."""
    lines = text.split('\n')
    formatted_lines = []
    for line in lines:
        line = line.strip()
        if line:
            # Remove $ signs surrounding non-equation text
            if not line.startswith('$') and not line.endswith('$'):
                line = line.replace('$', '')
            formatted_lines.append(line)
    return "\n".join(formatted_lines)

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
        formatted_solution = format_gemini_response(solution)
        st.markdown(f"<div style='font-size: 20px; font-weight: bold;'>{formatted_solution}</div>", unsafe_allow_html=True)
    else:
        st.warning("⚠ Please enter a math question before clicking Solve.")
