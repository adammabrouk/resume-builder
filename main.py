import streamlit as st
from pylatex import Document, Section, Command
import io
import subprocess
import base64
import requests
import os
import tempfile
import shutil
import openai
from openai import OpenAI
import logging

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Modular AI Provider Handling
class AIProvider:
    def __init__(self, name, api_key=None):
        self.name = name
        self.api_key = api_key

    def tailor_resume(self, job_offer, current_latex, language='en'):
        raise NotImplementedError("This method should be implemented by subclasses.")

class OpenAIProvider(AIProvider):
    def tailor_resume(self, job_offer, current_latex, language='en'):
        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional assistant working with LaTeX."},
                {"role": "user", "content": f"""
                You are a professional LaTeX assistant. Here is a LaTeX resume template and a job description. 
                Your task is to detect the Resume Language, slightly reorganize or adapt the content of the resume to highlight the relevant keywords from the job offer, and produce a result in the same language of the input.
                Note: You must not alter the factual information in the resume, just prioritize the elements that interest the recruiter.

                --- Job Description ---
                {job_offer}

                --- Current Template ---
                {current_latex}

                --- Expected Result ---
                Provide only the modified LaTeX code. Do not give any explanation.
                """},
            ],
        )
        return response.choices[0].message.content

class OllamaProvider(AIProvider):
    def tailor_resume(self, job_offer, current_latex, language='en'):
        response = requests.post(
            "http://localhost:11434/api/completions",
            json={
                "model": "gpt-4",
                "prompt": f"""
                You are a professional LaTeX assistant. Here is a LaTeX resume template and a job description. 
                Your task is to slightly reorganize or adapt the content of the resume to highlight the relevant keywords from the job offer.
                Note: You must not alter the factual information in the resume, just prioritize the elements that interest the recruiter.

                --- Job Description ---
                {job_offer}

                --- Current Template ---
                {current_latex}

                --- Expected Result ---
                Provide only the modified LaTeX code. Do not give any explanation.
                """
            }
        )
        return response.json()["choices"][0]["text"]

# Streamlit App Layout
st.title("Resume Tailoring Tool")
st.subheader("Paste a job description and generate a tailored resume")

# Configuration inputs
st.sidebar.header("Configuration")
ai_provider_name = st.sidebar.radio("Select AI Provider", ["OpenAI", "Ollama"])
api_key_input = st.sidebar.text_input(f"{ai_provider_name} API Key", type="password")

# Profile image upload with session state handling
if "profile_image" not in st.session_state:
    st.session_state["profile_image"] = None

uploaded_profile_image = st.sidebar.file_uploader("Upload Profile Image", type=["jpg", "png"])
if uploaded_profile_image:
    st.session_state["profile_image"] = uploaded_profile_image

# Display the name of the uploaded profile image if it exists
if st.session_state["profile_image"]:
    st.sidebar.write(f"Uploaded Profile Image: {st.session_state['profile_image'].name}")

latex_template = st.sidebar.text_area("Paste LaTeX Template", height=300)

def compile_latex(latex_code, profile_image_file):
    logger.info("Creating a temporary directory for LaTeX compilation.")
    temp_dir = tempfile.mkdtemp()
    try:
        # Save the LaTeX code to a temporary file
        latex_path = os.path.join(temp_dir, "resume.tex")
        logger.info("LaTeX code length: %d characters", len(latex_code))
        logger.info("LaTeX code snippet: %s", latex_code[:100])  # Log the first 100 characters 
        logger.info("Saving LaTeX code to temporary file: %s", latex_path)
        with open(latex_path, "w") as f:
            f.write(latex_code)

        # Save the profile image to the temporary directory
        if profile_image_file:
            profile_image_path = os.path.join(temp_dir, profile_image_file.name)
            logger.info("Saving profile image to temporary file: %s", profile_image_path)
            with open(profile_image_path, "wb") as f:
                f.write(profile_image_file.read())

        # Compile the LaTeX file to PDF using pdflatex
        logger.info("Compiling LaTeX file to PDF.")
        result = subprocess.run(["lualatex", "-interaction=nonstopmode", "-output-directory", temp_dir, latex_path])
        logger.info("LaTeX compilation finished with return code: %d", result.returncode)

        # Read the generated PDF file
        pdf_path = os.path.join(temp_dir, "resume.pdf")
        logger.info("Reading generated PDF file: %s", pdf_path)
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        return pdf_bytes
    finally:
        logger.info("Cleaning up temporary directory: %s", temp_dir)
        shutil.rmtree(temp_dir)

def get_pdf_base64(pdf_bytes):
    logger.info("Encoding PDF bytes to Base64.")
    return base64.b64encode(pdf_bytes).decode('utf-8')

# Initialize AI Provider
logger.info("Initializing AI provider: %s", ai_provider_name)
if ai_provider_name == "OpenAI":
    ai_provider = OpenAIProvider(name="OpenAI", api_key=api_key_input)
elif ai_provider_name == "Ollama":
    ai_provider = OllamaProvider(name="Ollama", api_key=api_key_input)

# App Layout with two columns
col1, col2 = st.columns(2)

with col1:
    # Input box for job offer
    job_offer = st.text_area("Paste the job offer here", height=300)

    # Button to generate the PDF
    if st.button("Generate Resume"):
        try:
            logger.info("Step 1: Checking inputs.")
            if not latex_template:
                st.error("Please provide a LaTeX template.")
                logger.error("LaTeX template is missing.")
            elif not api_key_input:
                st.error(f"Please provide an API key for {ai_provider_name}.")
                logger.error("API key is missing for provider: %s", ai_provider_name)
            elif not st.session_state["profile_image"]:
                st.error("Please upload a profile image.")
                logger.error("Profile image is missing.")
            else:
                logger.info("Step 2: Validating LaTeX template and profile image.")
                # Ensure the LaTeX template references the uploaded profile image
                profile_image_name = st.session_state["profile_image"].name
                if profile_image_name not in latex_template:
                    st.error(f"The LaTeX template must reference the profile image '{profile_image_name}'.")
                    logger.error("Profile image '%s' not referenced in LaTeX template.", profile_image_name)
                else:
                    logger.info("Step 3: Tailoring the resume using AI provider.")
                    # Update the LaTeX with job offer details
                    tailored_latex = ai_provider.tailor_resume(job_offer, latex_template, language='en')
                    # Strip the tailored latex fron the ```latex ```
                    tailored_latex = tailored_latex.replace("```latex", "").replace("```", "").strip()
                    logger.info("Step 4: Compiling the LaTeX to generate the PDF.")
                    # Compile the LaTeX to a PDF
                    pdf_bytes = compile_latex(tailored_latex, st.session_state["profile_image"])
                    
                    logger.info("Step 5: Storing the generated PDF in session state.")
                    # Store the PDF bytes in memory
                    st.session_state['pdf'] = pdf_bytes
                    
                    st.success("Resume generated! Check the preview on the right.")
                    
                    logger.info("Step 6: Providing the PDF for download.")
                    # Provide the PDF for download
                    st.download_button(
                        "Download Resume",
                        data=pdf_bytes,
                        file_name="tailored_resume.pdf",
                        mime="application/pdf"
                    )
        except Exception as e:
            import traceback
            logger.error("An error occurred: %s", traceback.format_exc())
            # Display the error message in a red box
            st.error(f"An error occurred: {traceback.format_exc()}")

with col2:
    st.subheader("Preview PDF")
    # Show the PDF if it exists in session state
    if 'pdf' in st.session_state:
        logger.info("Step 7: Displaying the generated PDF preview.")
        # Convert PDF bytes to Base64
        pdf_base64 = get_pdf_base64(st.session_state['pdf'])
        # Use an iframe to preview the PDF
        pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="100%" height="400"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        logger.info("No PDF generated yet.")
        st.info("Generate a resume to preview it here.")
