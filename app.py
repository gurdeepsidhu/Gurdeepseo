import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
import time

# ============================================================
# ⚠️ APNI 3 NAYI API KEYS YAHAN DAALO
# Har key ke saamne quotes ke andar apni key likhein
# ============================================================
API_KEYS = [
    "AIzaSyDfyNzUJPVm5wIah8e2OLMFxjmZxbjcsKU",   # ← Key 1 yahan
    "AIzaSyAFuh2kWBvAdqfYhvYxqeB2Bt3JocoCALk",   # ← Key 2 yahan
    "AIzaSyArpeE6WpdCkW2LBm8UdaAhN8AXo-KYdSY",   # ← Key 3 yahan
]

# ============================================================
# PAGE SETUP
# ============================================================
st.set_page_config(
    page_title="AgencyWriter Pro",
    page_icon="🖋️",
    layout="wide"
)

st.title("🖋️ Professional Agency Content Engine")
st.markdown("**Powered by Google Gemini 2.0 Flash — 3 Keys Auto Rotation**")
st.markdown("---")

# ============================================================
# ARTICLE GENERATION — 3 KEYS + 2 MODELS = 6 ATTEMPTS
# Ek bhi fail hogi toh dusri automatically try hogi
# ============================================================
def generate_article(topic, word_count, tone, language):
    models_to_try = ['gemini-2.0-flash', 'gemini-2.0-flash-lite']

    prompt = f"""
    Write a high-quality, SEO-optimized article on the topic: '{topic}'.

    Requirements:
    - Word Count: Approximately {word_count} words
    - Tone: {tone}
    - Language: {language}
    - Style: Human-written, no AI cliches, engaging and informative

    Structure (use proper Markdown formatting):
    1. # Main Title (H1)
    2. ## Introduction
    3. ## Section 1 - Background / Overview
    4. ## Section 2 - Key Points / Details
    5. ## Section 3 - Benefits / Importance
    6. ## Section 4 - Practical Tips / How-to
    7. ## Section 5 - Common Mistakes to Avoid
    8. ## Section 6 - Future Outlook / Trends
    9. ## Conclusion
    10. ## FAQ (5 questions with answers)

    Important: Use bullet points, bold text, and clear headings throughout.
    """

    attempt = 0
    total = len(API_KEYS) * len(models_to_try)

    for key_index, api_key in enumerate(API_KEYS):
        for model_name in models_to_try:
            attempt += 1
            try:
                st.info(f"Trying... Key {key_index+1} + {model_name} (Attempt {attempt}/{total})")
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text, model_name, key_index + 1

            except Exception as e:
                error_str = str(e)
                if "429" in error_str:
                    st.warning(f"Key {key_index+1} + {model_name} rate limit. Next try...")
                    time.sleep(2)
                    continue
                elif "404" in error_str:
                    st.warning(f"{model_name} not available. Next try...")
                    continue
                elif "API_KEY" in error_str or "invalid" in error_str.lower():
                    st.error(f"Key {key_index+1} invalid hai! Sahi key daalo.")
                    continue
                else:
                    st.warning(f"Error: {error_str[:80]}... Next try...")
                    continue

    return None, None, None

# ============================================================
# SIDEBAR SETTINGS
# ============================================================
st.sidebar.header("Article Settings")

word_count = st.sidebar.select_slider(
    "Word Count:",
    options=[500, 800, 1000, 1500, 2000],
    value=1000
)

tone = st.sidebar.radio(
    "Writing Tone:",
    options=["Professional & Formal", "Casual & Friendly", "Academic & Research"],
    index=0
)

language = st.sidebar.radio(
    "Language:",
    options=["English", "Hinglish (Hindi + English Mix)"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Keys Loaded:** 3 Active")
st.sidebar.markdown("**Models:** gemini-2.0-flash + lite")
st.sidebar.markdown("**Total Attempts:** 6 per request")

# ============================================================
# MAIN UI
# ============================================================
st.subheader("Enter Your Topic")

topic = st.text_input(
    "Topic likhiye:",
    placeholder="e.g., Digital Marketing Trends 2026, AI in Healthcare..."
)

extra_context = st.text_area(
    "Additional Context (Optional):",
    placeholder="Koi specific points jo include karne hain?",
    height=80
)

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    generate_btn = st.button("Generate Article", use_container_width=True, type="primary")

# ============================================================
# GENERATION LOGIC
# ============================================================
if generate_btn:
    if not topic.strip():
        st.error("Topic khali hai! Kuch toh likhiye.")
    else:
        full_topic = topic
        if extra_context.strip():
            full_topic = f"{topic}\n\nAdditional context: {extra_context}"

        with st.spinner(f"Writing jari hai... (~{word_count} words)"):
            content, used_model, used_key = generate_article(full_topic, word_count, tone, language)

        if content:
            st.success(f"Article taiyar! | Model: {used_model} | Key #{used_key} use hui")
            st.markdown("---")

            col1, col2 = st.columns([3, 1])

            with col1:
                st.subheader("Article Preview")
                with st.expander("Formatted Preview", expanded=True):
                    st.markdown(content)
                with st.expander("Plain Text (Copy/Paste ke liye)"):
                    st.text_area("", value=content, height=400, label_visibility="collapsed")

            with col2:
                st.subheader("Export")

                # Word Document
                doc = Document()
                doc.add_heading(topic, level=0)
                for line in content.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('# ') and not line.startswith('## '):
                        doc.add_heading(line.replace('# ', ''), level=1)
                    elif line.startswith('## '):
                        doc.add_heading(line.replace('## ', ''), level=2)
                    elif line.startswith('### '):
                        doc.add_heading(line.replace('### ', ''), level=3)
                    elif line.startswith('- ') or line.startswith('* '):
                        doc.add_paragraph(line.replace('- ', '').replace('* ', ''), style='List Bullet')
                    else:
                        doc.add_paragraph(line)

                bio = BytesIO()
                doc.save(bio)
                bio.seek(0)

                st.download_button(
                    label="Download Word (.docx)",
                    data=bio.getvalue(),
                    file_name=f"{topic[:30].replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

                st.download_button(
                    label="Download Text (.txt)",
                    data=content.encode('utf-8'),
                    file_name=f"{topic[:30].replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

                st.markdown("---")
                st.metric("Words", len(content.split()))
                st.metric("Characters", len(content))

        else:
            st.error("Saari 6 attempts fail ho gayi.")
            st.markdown("""
            **Kya karein:**
            - 15-20 minute baad try karein (rate limit reset hoti hai)
            - API keys check karein — Google AI Studio se nayi banao
            - Internet connection check karein
            """)

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray;'>AgencyWriter Pro | 3-Key Rotation System | Free Tier</p>",
    unsafe_allow_html=True
)
