import streamlit as st
import google.generativeai as genai
import os
import re
import time # For retry delay
import google.api_core.exceptions # For specific retry exception

# ------------------------
# 🎯 PAGE CONFIG (MUST BE FIRST Streamlit command)
# ------------------------
# Set page configuration first thing after imports
st.set_page_config(
    page_title="Math Master AI",
    page_icon="🧮",
    layout="centered" # Centered layout is generally better for mobile
)

# ------------------------
# 🔐 Secure API Key Config
# ------------------------
# Attempt to get the API key from Streamlit secrets first, then environment variables
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

# Check for API key AFTER page config is set
if not GEMINI_API_KEY:
    st.error("🔐 Gemini API key is missing. Please configure it via Streamlit Secrets (key: GEMINI_API_KEY) or environment variable.")
    st.stop() # It's okay to use st.stop here now

# Configure the Gemini client
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
     st.error(f"❌ Failed to configure Gemini API: {e}") # Okay here
     st.stop() # Okay here


# ------------------------
# 🚀 Initialize Gemini Model
# ------------------------
SELECTED_MODEL = "models/gemini-2.0-flash" # Using 2.0 Flash as requested
try:
    model = genai.GenerativeModel(SELECTED_MODEL)
    # It's okay to call st.caption here now
    st.caption(f"Using model: {SELECTED_MODEL}")

except Exception as e:
    # Okay to call st.error / st.stop here now
    st.error(f"❌ Failed to initialize Gemini model ({SELECTED_MODEL}): {e}")
    st.stop()

# ------------------------
# 🧠 Solve Math Prompt (Streaming with Retries)
# ------------------------
def solve_math_problem_streamed(prompt, max_retries=3, initial_delay=1.5):
    """Generates content from the Gemini model with streaming, error handling, and retries for overload."""
    retries = 0
    delay = initial_delay
    last_yielded_text = "" # Keep track of what was last sent

    while retries <= max_retries:
        try:
            response_stream = model.generate_content(prompt, stream=True)
            streamed_text = ""
            if retries > 0 and last_yielded_text:
                 # If retrying, maybe clear previous message or indicate retry start
                 yield "" # Clear previous retry message / status
                 streamed_text = "" # Reset accumulated text if needed

            # --- Streaming logic ---
            for chunk in response_stream:
                if hasattr(chunk, 'text') and chunk.text:
                    streamed_text += chunk.text
                    last_yielded_text = streamed_text
                    yield streamed_text # Yield the accumulated text

            # If successful, exit the loop
            return # Successfully finished generation

        except google.api_core.exceptions.ResourceExhausted as e: # Specific exception for 503/overload/quota
             error_str = str(e).lower()
             if "overloaded" in error_str or "resource has been exhausted" in error_str or "quota" in error_str or "503" in error_str:
                 retries += 1
                 if retries > max_retries:
                     retry_error_msg = f"❌ Error: Model overloaded after {max_retries} retries. Please try again later. Details: {e}"
                     last_yielded_text = retry_error_msg
                     yield retry_error_msg
                     return
                 retry_info_msg = f"⏳ Model overloaded, retrying in {int(delay)}s... (Attempt {retries}/{max_retries})"
                 last_yielded_text = retry_info_msg
                 yield retry_info_msg # Show retry message
                 time.sleep(delay)
                 delay *= 2 # Exponential backoff
                 # Continue loop to retry
             else:
                 error_message = f"❌ Error during generation (Resource Exhausted): {e}"
                 last_yielded_text = error_message
                 yield error_message
                 return # Exit

        except Exception as e:
             error_message = f"❌ Error during generation: {str(e)}"
             last_yielded_text = error_message
             yield error_message
             return # Exit after non-retryable error

    # Fallback error if loop finishes unexpectedly
    final_error = "❌ Error: Max retries exceeded without specific error capture."
    yield final_error


# ------------------------
# 🖋️ Render Output Nicely (Mobile Optimized)
# ------------------------
def clean_and_render_math(text):
    """Cleans and renders text with Markdown and LaTeX, optimized for mobile."""
    # Simple heuristic for exponents (e.g., x2 -> x^2), avoid changing things like H2O
    text = re.sub(r'(?<![A-Za-z0-9])([a-zA-Z])(\d+)', r'\1^\2', text)
    text = text.replace("sqrt", r"\sqrt").replace("int", r"\int")
    text = re.sub(r"([=><+\-*/])", r" \1 ", text) # Add spacing around operators
    text = re.sub(r'\s+', ' ', text) # Clean up potential double spacing

    # Split by LaTeX delimiters ($$...$$ for display, $...$ for inline)
    parts = re.split(r'(\$\$[^\$]+\$\$|\$[^\$]+\$)', text)

    # Style for wrapping LaTeX in a scrollable container on mobile
    latex_wrapper_style = "overflow-x: auto; padding: 0.5em 0.2em; border: 1px solid #eee; background-color: #f9f9f9; border-radius: 4px; margin-bottom: 0.5rem;"
    # Style for regular text parts - good font size, line height, and word wrapping
    text_style = "font-size: 17px; line-height: 1.7; margin-bottom: 0.5rem; overflow-wrap: break-word; word-wrap: break-word;"

    with st.container():
        for part in parts:
            part = part.strip()
            if not part:
                continue

            try:
                # Display Math $$...$$
                if part.startswith("$$") and part.endswith("$$"):
                    content = part[2:-2].strip()
                    if content:
                        st.markdown(f"<div style='{latex_wrapper_style}'>{st.latex(content)}</div>", unsafe_allow_html=True)

                # Inline Math $...$
                elif part.startswith("$") and part.endswith("$"):
                    content = part[1:-1].strip()
                    if content:
                        st.latex(content) # Render inline directly

                # Regular Text Parts
                else:
                    st.markdown(f"<div style='{text_style}'>{part}</div>", unsafe_allow_html=True)
            except Exception as render_error:
                st.warning(f"⚠️ Could not render part: '{part[:50]}...' Error: {render_error}")

# ------------------------
# 🎨 Streamlit UI (Rest of the UI)
# ------------------------

# --- Header ---
st.title("🧮 Math Master AI")
st.write("Get step-by-step solutions to your math problems!")

# --- Example Prompts ---
examples = [
    "Area of ellipse x^2/a^2 + y^2/b^2 = 1?",
    "Derivative of sin(x^2)?",
    "Solve 2x^2 + 3x - 5 = 0.",
    "Integral of 1 / (1 + x^2)?",
    "Area: y=3√x, x=2 to x=4, x-axis.",
]

with st.expander("💡 See Example Questions"):
    for i, example in enumerate(examples):
        if st.button(f"Ex {i+1}: {example}", key=f"example_{i}"):
            st.session_state["user_input"] = example
            st.rerun() # Update text area immediately

# --- User Input ---
if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

user_input = st.text_area(
    "✍️ Enter your math problem:",
    value=st.session_state["user_input"],
    height=100, # Reduced height for better mobile fit
    key="math_input_area"
)

# --- Solve Button ---
col1, col2, col3 = st.columns([1, 2, 1]) # Centering trick
with col2:
    solve_button = st.button("📌 Solve Now", use_container_width=True)

# --- Processing and Output ---
if solve_button:
    current_input = st.session_state.get("math_input_area", "").strip()
    if current_input:
        st.markdown("---")
        st.markdown("### ✅ Solution:")

        # Enhanced prompt for detailed explanations
        detailed_prompt = f"""You are a helpful and skilled math tutor AI. Solve the following math problem with a complete, step-by-step explanation suitable for a student.
Use clear LaTeX for all equations (using $...$ for inline math like variables $x$ or simple terms $a^2+b^2$, and $$...$$ for important display equations or formulas).
Explain the logic behind each step, define variables used, state any theorems or rules applied, and provide reasoning clearly.
Format the output using Markdown for text explanations, bullet points, or numbered steps where appropriate for clarity.

Problem: {current_input}
"""

        # Placeholder for smooth streaming updates
        placeholder = st.empty()
        full_response_text = "" # Initialize to store the full response

        with st.spinner("🧠 Solving... Please wait."):
            try:
                solution_generator = solve_math_problem_streamed(detailed_prompt)
                for partial_text in solution_generator:
                    full_response_text = partial_text # Update with the latest text/status
                    # Update the placeholder with the rendered content or status message
                    with placeholder.container():
                         if partial_text.startswith("❌") or partial_text.startswith("⏳"):
                              st.info(partial_text) # Display status/error messages directly
                         else:
                              clean_and_render_math(partial_text) # Render math content

                # Final render/state check after loop (optional but good practice)
                with placeholder.container():
                     if full_response_text.startswith("❌") or full_response_text.startswith("⏳"):
                           st.info(full_response_text) # Ensure final status is shown
                     elif full_response_text:
                           clean_and_render_math(full_response_text) # Ensure final content is shown

            except Exception as gen_e:
                st.error(f"An unexpected error occurred while trying to generate the solution: {gen_e}")

    else:
        st.warning("⚠️ Please enter a math problem first.")

# --- Footer (Optional) ---
st.markdown("---")
st.caption(f"Powered by Google Gemini ({SELECTED_MODEL})")
