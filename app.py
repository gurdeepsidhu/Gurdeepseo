import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO

# --- PAGE SETUP ---
st.set_page_config(page_title="Agency Content Writer AI", page_icon="✍️")
st.title("✍️ Agency Content Writer AI")

# --- API KEY SETUP ---
# Pehle check karega ki Secrets mein key hai ya nahi
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Paste your Google Gemini API Key here:", type="password")

if not api_key:
    st.info("💡 Please sidebar mein API Key daalein ya Streamlit Secrets set karein.")
    st.stop()

# AI Setup with the correct model name
try:
    genai.configure(api_key=api_key)
    # Humne model ka naam 'gemini-1.5-flash' kar diya hai jo ki stable hai
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Setup Error: {e}")

# --- INTERFACE ---
topic = st.text_input("📝 Article ka Topic ya Keyword daaliye:")

if st.button("Generate Article 🚀"):
    if not topic:
        st.warning("⚠️ Please koi topic enter kariye.")
    else:
        # Secret prompt for 1500 words & SEO
        prompt = f"""
        Write a professional, SEO-optimized article on the topic: '{topic}'.
        Requirements:
        1. Length: Approximately 1500 words.
        2. Format: Use H1 for title, H2 and H3 for subheadings. Use bullet points.
        3. Tone: Human-like, engaging, and conversational. Avoid AI clichés.
        4. Content: Deep-dive information, introduction, and a strong conclusion.
        """
        
        with st.spinner("✨ AI dimaag laga raha hai... 1500 words likhne mein thoda waqt lagta hai..."):
            try:
                response = model.generate_content(prompt)
                article_text = response.text
                
                st.success("🎉 Article taiyar hai!")
                
                # Display text
                st.text_area("Copy your article:", value=article_text, height=400)
                
                # Word File Download
                doc = Document()
                doc.add_heading(topic, 0)
                doc.add_paragraph(article_text)
                bio = BytesIO()
                doc.save(bio)
                
                st.download_button(
                    label="📄 Download as Word (.docx)",
                    data=bio.getvalue(),
                    file_name=f"{topic.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as e:
                st.error(f"Opps! Ek error aayi hai: {e}")
