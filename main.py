import streamlit as st
import openai

# Get API Key securely from Streamlit Secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]  # Store your key in Streamlit Secrets

# Initialize OpenAI Client with a Project Key
client = openai.OpenAI(api_key=OPENAI_API_KEY)

st.title("Ganit Prakash 🧮")
st.write("Enter any math question, and I'll solve it with steps!")

# User input
user_input = st.text_area("Enter your math question:")

# Function to call OpenAI API
def ask_chatgpt(prompt):
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
        return f"Error: {str(e)}"

if st.button("Solve"):  
    if user_input.strip():
        gpt_solution = ask_chatgpt(user_input)
        st.write("**ChatGPT Solution:**")
        st.write(gpt_solution)
    else:
        st.warning("Please enter a math question before clicking Solve.")
