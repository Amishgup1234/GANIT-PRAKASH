import streamlit as st
import openai
import os

# Set OpenAI API Key
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Title
st.title("Ganit Prakash 🧮")
st.write("Enter any math question, and I'll solve it with steps!")

# User input
user_input = st.text_area("Enter your math question:")

# Function to call OpenAI's ChatGPT API
def ask_chatgpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use GPT-4 for better reasoning
            messages=[{"role": "system", "content": "You are a math expert. Solve the problem step by step."},
                      {"role": "user", "content": prompt}],
            api_key=OPENAI_API_KEY
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error: {str(e)}"

if st.button("Solve"):  
    gpt_solution = ask_chatgpt(user_input)
    st.write("**ChatGPT Solution:**")
    st.write(gpt_solution)
