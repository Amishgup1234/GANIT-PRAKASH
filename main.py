import streamlit as st
import openai
import os

# Get OpenAI API Key securely from Streamlit Secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]  # Ensure you set this in Streamlit secrets

# Title of the app
st.title("Ganit Prakash 🧮")
st.write("Enter any math question, and I'll solve it with step-by-step solutions!")

# User input for math question
user_input = st.text_area("Enter your math question:")

# Function to call OpenAI's API with new format
def ask_chatgpt(prompt):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)  # Initialize OpenAI client
        response = client.chat.completions.create(
            model="gpt-4",  # Use GPT-4 for better reasoning
            messages=[
                {"role": "system", "content": "You are a math expert. Solve the problem step by step."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Solve button
if st.button("Solve"):  
    if user_input.strip():
        gpt_solution = ask_chatgpt(user_input)
        st.write("**ChatGPT Solution:**")
        st.write(gpt_solution)
    else:
        st.warning("Please enter a math question before clicking Solve.")
