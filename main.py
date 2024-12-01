import streamlit as st
from pylatex import Document, Section, Command
import io
import subprocess
import base64
from openai import OpenAI

openai_client = OpenAI(api_key="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")

# Path to the local image
image_path = "background.jpg"

# Read and encode the image to Base64
with open(image_path, "rb") as file:
    encoded_image = base64.b64encode(file.read()).decode()

# Inject CSS with Base64 background
background_css = f"""
<style>
body {{
    background-image: url("blob:https://wallpapers.com/f9152b86-ae83-431c-8a45-b5bfaf37883b");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}
</style>
"""

# Apply the CSS
st.markdown(background_css, unsafe_allow_html=True)

# Sample LaTeX resume template
with open("template_en.tex", "r") as f:
    latex_template = f.read()

def compile_latex(latex_code):
    # Save the LaTeX code to a temporary file
    with open("resume.tex", "w") as f:
        f.write(latex_code)
    
    # Compile the LaTeX file to PDF using pdflatex
    subprocess.run(["lualatex", "resume.tex"])
    
    # Read the generated PDF file
    with open("resume.pdf", "rb") as f:
        pdf_bytes = f.read()
    
    return pdf_bytes

def get_pdf_base64(pdf_bytes):
    # Encode the PDF binary data as Base64
    return base64.b64encode(pdf_bytes).decode('utf-8')

def tailor_resume(job_offer, current_latex, language='en'):
    if language == 'fr':
        prompt = f"""
        Vous êtes un assistant LaTeX professionnel. Voici un modèle de CV en LaTeX et une description de poste. 
        Votre tâche est de réorganiser ou d'adapter légèrement le contenu du CV pour mettre en avant les mots-clés pertinents de l'offre d'emploi.
        Attention : vous ne devez pas modifier la réalité citée dans le CV mais juste prioriser les éléments qui intéressent le recruteur.

        --- Description de poste ---
        {job_offer}

        --- Modèle actuel ---
        {current_latex}

        --- Résultat attendu ---
        Fournissez uniquement le code LaTeX modifié. Ne donnez aucune explication.
        """
    else:
        prompt = f"""
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

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional assistant working with LaTeX." if language == 'en' else "Vous êtes un assistant professionnel qui travaille avec LaTeX."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7
    )
    return response.choices[0].message.content[8:-3]

# Streamlit App Layout
st.title("Resume Tailoring Tool")
st.subheader("Paste a job description and generate a tailored resume")

# App Layout with two columns
col1, col2 = st.columns(2)

with col1:
    # Input box for job offer
    job_offer = st.text_area("Paste the job offer here", height=300)

    # Button to generate the PDF
    if st.button("Generate Resume"):
        # Update the LaTeX with job offer details
        tailored_latex = tailor_resume(job_offer, latex_template, language='en')
        
        # Compile the LaTeX to a PDF
        pdf_bytes = compile_latex(tailored_latex)
        
        # Store the PDF bytes in memory
        st.session_state['pdf'] = pdf_bytes
        
        st.success("Resume generated! Check the preview on the right.")
        
        # Provide the PDF for download
        st.download_button(
            "Download Resume",
            data=pdf_bytes,
            file_name="tailored_resume.pdf",
            mime="application/pdf"
        )

with col2:
    st.subheader("Preview PDF")
    # Show the PDF if it exists in session state
    if 'pdf' in st.session_state:
        # Convert PDF bytes to Base64
        pdf_base64 = get_pdf_base64(st.session_state['pdf'])
        # Use an iframe to preview the PDF
        pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="100%" height="400"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.info("Generate a resume to preview it here.")
