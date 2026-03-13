import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO

# --- PAGE SETUP ---
st.set_page_config(page_title="AgencyWriter Elite v3", page_icon="🚀", layout="wide")
st.title("🚀 Agency Content Writer Elite (2026 Edition)")

# --- API KEY ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

if not api_key:
    st.info("👋 Swagat hai! Shuru karne ke liye Sidebar mein API Key daalein.")
    st.stop()

# --- ENGINEERING CORE: SMART MODEL DISCOVERY ---
genai.configure(api_key=api_key)

def get_best_model():
    """Ye function aapke account mein available sabse best model dhoondega"""
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority List: Pehle hum 2.0 Flash try karenge, fir 1.5 Flash
        priority_models = [
            'models/gemini-2.0-flash-exp', 
            'models/gemini-2.0-flash', 
            'models/gemini-1.5-flash-latest', 
            'models/gemini-1.5-flash'
        ]
        
        for p_model in priority_models:
            if p_model in available_models:
                return p_model
        
        # Agar koi priority model nahi mila toh jo pehla model hai wo le lo
        return available_models[0] if available_models else None
    except Exception as e:
        st.error(f"Model Discovery Error: {e}")
        return None

# Model select karna
working_model_name = get_best_model()

if working_model_name:
    st.sidebar.success(f"Connected to: {working_model_name}")
    model = genai.GenerativeModel(working_model_name)
else:
    st.error("API Key sahi hai par koi model nahi mil raha. Please check Google AI Studio billing/status.")
    st.stop()

# --- INTERFACE ---
topic = st.text_input("📝 Enter Topic (e.g., 'Future of AI in 2026'):")

if st.button("Generate 1500-Word SEO Article 🚀"):
    if not topic:
        st.warning("⚠️ Topic toh likhiye!")
    else:
        # High-End Engineering Prompt
        prompt = f"""
        Write a professional, 1500-word SEO article on the topic: '{topic}'.
        
        Structure:
        1. Compelling H1 Title.
        2. Introduction with a hook.
        3. Table of Contents (Markdown).
        4. 6-7 Detailed H2 and H3 sections with deep insights.
        5. Use Bullet points, Tables, and Bold text for readability.
        6. SEO Guidelines: Naturally integrate keywords, meta-description suggestion at the end.
        7. Tone: Human-written, expert, and conversational. NO AI-GENERIC PHRASES.
        """
        
        with st.spinner(f"✨ {working_model_name} is writing your masterpiece..."):
            try:
                response = model.generate_content(prompt)
                article_text = response.text
                
                st.success("🎉 Article Generated Successfully!")
                
                # Copy area
                st.text_area("Copy Content:", value=article_text, height=500)
                
                # Word Export
                doc = Document()
                doc.add_heading(topic, 0)
                doc.add_paragraph(article_text)
                bio = BytesIO()
                doc.save(bio)
                
                st.download_button(
                    label="📥 Download Word File",
                    data=bio.getvalue(),
                    file_name=f"{topic.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as e:
                if "429" in str(e):
                    st.error("Quota Exceeded! Aap free limit cross kar chuke hain. 1 minute baad try karein ya doosri API Key use karein.")
                else:
                    st.error(f"Error: {e}")
