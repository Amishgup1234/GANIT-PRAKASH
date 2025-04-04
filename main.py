import streamlit as st
import openai

# Get API Key from Streamlit Secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]  # Store your key securely

# Initialize OpenAI Client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Customize Streamlit Page
st.set_page_config(page_title="Ganit Prakash - AI Math Solver", layout="wide")

# Title and Instructions
st.title("🧮 Ganit Prakash - AI Math Solver")
st.write("Enter any math question below, and I'll solve it with step-by-step explanations!")

# User Input
user_input = st.text_area("✍ Enter your math question:")

# Function to Get AI-Generated Solution
def solve_math_problem(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a math expert. Solve the problem step by step."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Solve Button
if st.button("📌 Solve Now"):
    if user_input.strip():
        solution = solve_math_problem(user_input)
        
        # Remove OpenAI/ChatGPT Name
        clean_solution = solution.replace("ChatGPT", "Ganit Prakash").replace("OpenAI", "")
        
        # Display Solution Full Page
        st.markdown(f"""
        <style>
        .big-text {{
            font-size: 20px;
            font-weight: bold;
            line-height: 1.6;
        }}
        </style>
        <div class="big-text">{clean_solution}</div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠ Please enter a math question before clicking Solve.")
