import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
import time

# --- PROFESSIONAL UI SETUP ---
st.set_page_config(page_title="AgencyWriter Pro", page_icon="🖋️", layout="wide")
st.title("🖋️ Professional Agency Content Engine")
st.markdown("---")

# --- API KEY MANAGEMENT ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

if not api_key:
    st.info("👋 Swagat hai! Shuru karne ke liye Sidebar mein apni Google API Key daalein.")
    st.stop()

# --- THE ENGINEERING CORE (Model Selection) ---
# Hum 'gemini-1.5-flash' use karenge kyunki iska free quota sabse bada hai
genai.configure(api_key=api_key)

def generate_article(topic):
    # Stable models ki list
    models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro']
    
    prompt = f"""
    Write a high-quality, SEO-optimized article on: '{topic}'.
    Word Count: Approximately 1500 words.
    Style: Human-written, conversational, professional, No AI-cliches.
    Format: Use Markdown (H1, H2, H3), Bullet points, and a Summary.
    Include: Introduction, 5-6 Detailed Sections, and a FAQ section.
    """
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text, model_name
        except Exception as e:
            if "429" in str(e):
                st.warning(f"⚠️ {model_name} ki limit cross ho gayi. Agla model try kar raha hoon...")
                time.sleep(2) # Thoda gap
                continue
            else:
                raise e
    return None, None

# --- USER INTERFACE ---
topic = st.text_input("Topic likhiye (e.g., 'Digital Marketing Trends 2026'):")

if st.button("Generate Article 🚀"):
    if not topic:
        st.error("Topic toh daaliye!")
    else:
        with st.spinner("🔍 Deep Research aur Writing jaari hai... (1500 words mein 1-2 minute lagte hain)"):
            try:
                content, used_model = generate_article(topic)
                
                if content:
                    st.success(f"✅ Article taiyar hai! (Powered by {used_model})")
                    
                    # Layout columns
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader("Article Preview")
                        st.text_area("", value=content, height=500)
                    
                    with col2:
                        st.subheader("Export Options")
                        # Word File Generation
                        doc = Document()
                        doc.add_heading(topic, 0)
                        doc.add_paragraph(content)
                        bio = BytesIO()
                        doc.save(bio)
                        
                        st.download_button(
                            label="📥 Download Word (.docx)",
                            data=bio.getvalue(),
                            file_name=f"{topic.replace(' ', '_')}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                        st.info("Tip: Is content ko copy karke direct WordPress ya Google Docs mein paste kar sakte hain.")
                else:
                    st.error("Maaf kijiyeki, saare models ke free quota khatam ho gaye hain. Kuch der baad try karein.")
            
            except Exception as e:
                st.error(f"Technical Error: {e}")
                st.info("Solution: Agar 'API Key Invalid' aa raha hai, toh Google AI Studio se nayi key generate karein.")
