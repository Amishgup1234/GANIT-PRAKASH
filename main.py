import streamlit as st
import google.generativeai as genai
import os
import re

# ------------------------
# 🔐 Secure API Key Config
# ------------------------
# Attempt to get the API key from Streamlit secrets first, then environment variables
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

if not GEMINI_API_KEY:
    st.error("🔐 Gemini API key is missing. Please configure it via Streamlit Secrets (key: GEMINI_API_KEY) or environment variable.")
    st.stop()

try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
     st.error(f"❌ Failed to configure Gemini API: {e}")
     st.stop()


# ------------------------
# 🚀 Initialize Gemini Model
# ------------------------
try:
    # Using a generally available model, ensure it fits your use case.
    # Consider gemini-1.5-flash if speed/cost is more critical than capability for some tasks.
    model = genai.GenerativeModel("gemini-1.5-flash") # Or stick with "gemini-1.5-pro" if needed
except Exception as e:
    st.error(f"❌ Failed to initialize Gemini model: {e}")
    st.stop()

# ------------------------
# 🧠 Solve Math Prompt (Streaming)
# ------------------------
def solve_math_problem_streamed(prompt):
    """Generates content from the Gemini model with streaming and error handling."""
    try:
        response_stream = model.generate_content(prompt, stream=True)
        streamed_text = ""
        for chunk in response_stream:
            # Handle potential empty chunks or chunks without text gracefully
            if hasattr(chunk, 'text') and chunk.text:
                streamed_text += chunk.text
                yield streamed_text
            # Add a small delay perhaps, if streaming feels too fast or choppy (optional)
            # import time
            # time.sleep(0.01)

        # Ensure the final complete text is yielded if the loop finishes
        # (sometimes the last part might not trigger a yield inside the loop)
        # This might not be strictly necessary depending on how the stream ends,
        # but can be a safeguard. Check if needed based on observed behavior.
        # yield streamed_text # Commented out for now, uncomment if needed

    except Exception as e:
        error_message = f"❌ Error during generation: {str(e)}"
        try:
            # Attempt to list models only if the primary generation fails
            models = genai.list_models()
            available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
            error_message += f"\n\nAvailable Models: {', '.join(available_models)}"
        except Exception as inner_e:
            error_message += f"\n❌ Additional Error listing models: {str(inner_e)}"
        yield error_message

# ------------------------
# 🖋️ Render Output Nicely (Mobile Optimized)
# ------------------------
def clean_and_render_math(text):
    """Cleans and renders text with Markdown and LaTeX, optimized for mobile."""
    # --- Pre-processing Steps ---
    # Simple heuristic for exponents (e.g., x2 -> x^2), avoid changing things like H2O
    text = re.sub(r'(?<![A-Za-z0-9])([a-zA-Z])(\d+)', r'\1^\2', text)
    # Standard LaTeX commands
    text = text.replace("sqrt", r"\sqrt").replace("int", r"\int")
    # Add spacing around common operators for better LaTeX rendering sometimes
    text = re.sub(r"([=><+\-*/])", r" \1 ", text)
    # Clean up potential double spacing
    text = re.sub(r'\s+', ' ', text)

    # --- Splitting Content ---
    # Split by LaTeX delimiters ($$...$$ for display, $...$ for inline)
    # This regex handles nested dollars better potentially, but test thoroughly
    parts = re.split(r'(\$\$[^\$]+\$\$|\$[^\$]+\$)', text)

    # --- Rendering Logic ---
    with st.container():
        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Style for wrapping LaTeX in a scrollable container on mobile
            latex_wrapper_style = "overflow-x: auto; padding: 0.5em 0; border: 1px solid #eee; background-color: #f9f9f9; border-radius: 4px; margin-bottom: 0.5rem;"
            # Style for regular text parts - good font size, line height, and word wrapping
            text_style = "font-size: 17px; line-height: 1.7; margin-bottom: 0.5rem; overflow-wrap: break-word; word-wrap: break-word;" # Added word-wrap for broader compatibility

            try:
                if part.startswith("$$") and part.endswith("$$"):
                    content = part[2:-2].strip() # Extract content
                    if content: # Render only if there's content inside $$
                         # Wrap display math in a scrollable div
                        st.markdown(f"<div style='{latex_wrapper_style}'>{st.latex(content)}</div>", unsafe_allow_html=True)
                elif part.startswith("$") and part.endswith("$"):
                    content = part[1:-1].strip() # Extract content
                    if content: # Render only if there's content inside $
                        # Inline math - usually wraps, but apply same wrapper for consistency / edge cases
                        # Using st.markdown allows text to flow around it better potentially than st.latex directly
                        st.markdown(f"<span style='{text_style}'>{st.latex(content)}</span>", unsafe_allow_html=True)
                        # Alternative: Keep as pure latex, might cause less optimal line breaks with surrounding text
                        # st.latex(content)

                else:
                    # Render regular text parts using the defined text style
                    st.markdown(f"<div style='{text_style}'>{part}</div>", unsafe_allow_html=True)
            except Exception as render_error:
                st.warning(f"⚠️ Could not render part: {part[:50]}... Error: {render_error}")


# ------------------------
# 🎨 Streamlit UI (Mobile Optimized)
# ------------------------

# --- Page Configuration ---
# Use "centered" layout - better for mobile by default as it limits width.
# Add an emoji for the tab icon.
st.set_page_config(
    page_title="Math Master AI",
    page_icon="🧮",
    layout="centered" # Changed from "wide" to "centered" for better mobile constraints
)

# --- Header ---
st.title("🧮 Math Master AI")
st.write("Get step-by-step solutions to your math problems!") # Slightly more concise

# --- Example Prompts ---
# Kept the expander, it works reasonably well on mobile.
examples = [
    "Area of ellipse x^2/a^2 + y^2/b^2 = 1?", # Shortened slightly
    "Derivative of sin(x^2)?",
    "Solve 2x^2 + 3x - 5 = 0.",
    "Integral of 1 / (1 + x^2)?",
    "Area: y=3√x, x=2 to x=4, x-axis.", # Shortened
]

with st.expander("💡 See Example Questions"): # Changed text slightly
    # Using columns within expander can help organize if needed, but for buttons, direct layout is fine
    for i, example in enumerate(examples):
        # Use a key for buttons if state needs to be tracked more reliably
        if st.button(f"Ex {i+1}: {example}", key=f"example_{i}"):
            st.session_state["user_input"] = example
            # Optional: Rerun to instantly populate the text area after button click
            st.rerun()


# --- User Input ---
# Use st.session_state to preserve input across reruns (e.g., after clicking example)
if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

# Reduced height for the text area - more suitable for mobile screens
user_input = st.text_area(
    "✍️ Enter your math problem:",
    value=st.session_state["user_input"],
    height=100, # Reduced height from 150
    key="math_input_area" # Added a key for better state management
)

# --- Solve Button ---
# Using columns to center the button slightly - adjust width ratio as needed
col1, col2, col3 = st.columns([1, 2, 1]) # Ratio for centering effect
with col2:
    solve_button = st.button("📌 Solve Now", use_container_width=True) # Make button fill column

# --- Processing and Output ---
if solve_button:
    if user_input.strip():
        st.markdown("---")
        st.markdown("### ✅ Solution:")

        # Enhance prompt for detailed explanations (Your prompt is good)
        detailed_prompt = f"""You are a helpful and skilled math tutor. Solve the following math problem with a complete, step-by-step explanation.
Use clear LaTeX for all equations (using $...$ for inline and $$...$$ for display math). Explain the logic behind each step, define variables, and provide reasoning like a real human tutor would. Format the output clearly using Markdown for text.

Problem: {user_input}
"""

        # Placeholder for smooth streaming updates
        placeholder = st.empty()
        full_text = "" # Initialize empty string to accumulate text

        with st.spinner("🧠 Solving... Please wait."):
            try:
                solution_generator = solve_math_problem_streamed(detailed_prompt)
                for partial_text in solution_generator:
                    full_text = partial_text # Keep track of the full text received so far
                    # Update the placeholder with the rendered content of the latest partial text
                    with placeholder.container():
                         clean_and_render_math(full_text) # Render the accumulated text

                # Optional: Final render outside the loop if needed, but usually handled by last yield
                # placeholder.empty() # Clear placeholder if doing a final static render
                # clean_and_render_math(full_text) # Final render

            except Exception as gen_e:
                st.error(f"An error occurred while generating the solution: {gen_e}")

    else:
        st.warning("⚠️ Please enter a math problem first.")

# --- Footer (Optional) ---
st.markdown("---")
st.caption("Powered by Google Gemini")
