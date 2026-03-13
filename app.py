import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO

# --- PAGE SETUP ---
st.set_page_config(page_title="Agency Content Writer AI", page_icon="✍️")
st.title("✍️ Agency Content Writer AI")

# --- API KEY SETUP (From Secrets) ---
# Ye line aapke Streamlit Settings se key uthayegi
api_key = st.secrets["GEMINI_API_KEY"]

if not api_key:
    st.error("⚠️ API Key nahi mili! Streamlit Settings -> Secrets mein 'GEMINI_API_KEY' set karein.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')

    # --- INTERFACE ---
    topic = st.text_input("📝 Article ka Topic ya Keyword daaliye:")

    if st.button("Generate Article 🚀"):
        if not topic:
            st.warning("⚠️ Please koi topic enter kariye.")
        else:
            prompt = f"""
            You are a professional SEO content writer. Write a detailed article on: '{topic}'.
            Guidelines:
            1. Length: Exactly around 1500 words.
            2. SEO: Use keywords naturally, meta-description inclusion, and H1, H2, H3 tags.
            3. Tone: Human-like, engaging, no robotic AI language.
            4. Structure: Introduction, Bullet points, Subheadings, and a Conclusion.
            """
            
            with st.spinner("✨ Aapka professional article likha ja raha hai..."):
                try:
                    response = model.generate_content(prompt)
                    article_text = response.text
                    
                    st.success("🎉 Article Ready!")
                    st.text_area("Copy Text Here:", value=article_text, height=400)
                    
                    # Word File Download
                    doc = Document()
                    doc.add_heading(topic, 0)
                    doc.add_paragraph(article_text)
                    bio = BytesIO()
                    doc.save(bio)
                    
                    st.download_button(
                        label="📄 Download Word File",
                        data=bio.getvalue(),
                        file_name=f"{topic}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                except Exception as e:
                    st.error(f"Error: {e}")
