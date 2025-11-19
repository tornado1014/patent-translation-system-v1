import streamlit as st
from docx import Document
from pathlib import Path
import io
from src.graph import app

st.set_page_config(page_title="Patent-Mind Translator", layout="wide")

st.title("Patent-Mind: AI-Powered Patent Translation System")

uploaded_file = st.file_uploader("Upload a Patent Document (.txt or .docx)", type=['txt', 'docx'])

if uploaded_file is not None:
    file_extension = Path(uploaded_file.name).suffix.lower()
    
    if file_extension == '.docx':
        doc = Document(io.BytesIO(uploaded_file.getvalue()))
        source_text = '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
    else: # .txt
        source_text = uploaded_file.getvalue().decode("utf-8")

    st.subheader("Original Text")
    st.text_area("Source", source_text, height=200)

    use_flash = st.checkbox("Use faster model for review (Gemini Flash)")

    if st.button("Translate Document"):
        initial_state = {
            "original_text": source_text,
            "document_type": "claim", # This could be an option in the UI
            "use_flash_review": use_flash,
            "messages": []
        }
        
        with st.spinner('Translating... This may take a moment.'):
            final_state = app.invoke(initial_state)

        translation = final_state.get("final_translation")
        if not translation:
            translation = final_state.get("draft_translation", "No translation generated.")
            
        review = final_state.get("review_result", {})

        st.subheader("Translated Text")
        st.text_area("Translation", translation, height=300)

        if review:
            st.subheader("QA Review")
            if review.get("passed"):
                st.success(f"**Review Passed:** {review.get('feedback')}")
            else:
                st.error(f"**Review Failed:** {review.get('feedback')}")
