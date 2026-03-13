import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO

# --- PAGE SETUP ---
st.set_page_config(page_title="Agency Content Writer AI", page_icon="✍️")
st.title("✍️ Agency Content Writer AI")
st.write("Apna topic daaliye aur 1500 words ka SEO-friendly, human-written article paiye.")

# --- SIDEBAR: API KEY INPUT ---
api_key = st.sidebar.text_input("Paste your Google Gemini API Key here:", type="password")
st.sidebar.info("Ye key save nahi hoti, safe hai.")

# --- MAIN INTERFACE ---
topic = st.text_input("📝 Article ka Topic ya Keyword daaliye:")

if st.button("Generate Article 🚀"):
    if not api_key:
        st.error("⚠️ Please sidebar mein apni API Key daaliye.")
    elif not topic:
        st.warning("⚠️ Please koi topic enter kariye.")
    else:
        # AI Setup
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        # Ye hamara secret command hai jo background mein jayega
        prompt = f"""
        You are an expert SEO content writer. Write a high-quality article on the topic: '{topic}'.
        Strict Guidelines:
        1. Length should be around 1500 words.
        2. The article must be highly SEO-friendly.
        3. The tone must be 100% human-written, conversational yet professional. Avoid typical AI jargon or robotic phrasing.
        4. Use proper headings (H1, H2, H3), subheadings, and bullet points where necessary.
        5. Write in English.
        """
        
        with st.spinner("Aapka article likha ja raha hai... (Isme 1-2 minute lag sakte hain) ⏳"):
            try:
                # Content Generate karna
                response = model.generate_content(prompt)
                article_text = response.text
                
                st.success("🎉 Aapka Article Ready Hai!")
                
                # Copy karne ke liye Text Box
                st.text_area("Generated Article (Yahan se Copy kar sakte hain):", value=article_text, height=400)
                
                # Word Document banane ka code
                doc = Document()
                doc.add_heading(topic, 0)
                doc.add_paragraph(article_text)
                
                bio = BytesIO()
                doc.save(bio)
                
                # Word File Download Button
                st.download_button(
                    label="📄 Download as Word File (.docx)",
                    data=bio.getvalue(),
                    file_name=f"{topic.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
            except Exception as e:
                st.error(f"Koi error aayi hai: {e}")
