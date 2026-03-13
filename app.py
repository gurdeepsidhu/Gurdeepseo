import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
import time

# ============================================================
# PAGE SETUP - Browser tab ka title aur icon set karta hai
# ============================================================
st.set_page_config(
    page_title="AgencyWriter Pro",
    page_icon="🖋️",
    layout="wide"
)

# ============================================================
# APP HEADER
# ============================================================
st.title("🖋️ Professional Agency Content Engine")
st.markdown("**Powered by Google Gemini 2.0 Flash**")
st.markdown("---")

# ============================================================
# API KEY MANAGEMENT
# Pehle Streamlit Secrets se key lene ki koshish karta hai
# Agar nahi mili, toh sidebar mein manually daalne deta hai
# ============================================================
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    st.sidebar.success("✅ API Key loaded from secrets!")
else:
    api_key = st.sidebar.text_input(
        "🔑 Enter Gemini API Key:",
        type="password",
        help="Google AI Studio se apni free API key lein: https://aistudio.google.com/app/apikey"
    )

# Agar API key nahi hai toh app yahan ruk jaayegi
if not api_key:
    st.info("👋 Shuru karne ke liye sidebar mein apni **Google Gemini API Key** daalein.")
    st.markdown("🔗 **Key kahan se lein?** [Google AI Studio](https://aistudio.google.com/app/apikey) — Bilkul FREE hai!")
    st.stop()

# ============================================================
# GEMINI API CONFIGURE
# ============================================================
genai.configure(api_key=api_key)

# ============================================================
# ARTICLE GENERATION FUNCTION
#
# IMPORTANT FIX: gemini-1.5-flash aur gemini-1.5-pro
# April 2025 mein RETIRED ho gaye hain.
#
# Ab hum ye models use karein ge (latest & free):
#   1. gemini-2.0-flash     ← sabse best free model (FAST)
#   2. gemini-2.0-flash-lite ← backup (lightest)
# ============================================================
def generate_article(topic, word_count, tone, language):
    """
    Yeh function Google Gemini API ko call karke article generate karta hai.
    - topic: User ka diya hua topic
    - word_count: Kitne words ka article chahiye
    - tone: Formal ya Casual
    - language: Hindi ya English
    """

    # Updated model list - ONLY working models (2025 mein)
    models_to_try = [
        'gemini-2.0-flash',       # Best free model - fastest
        'gemini-2.0-flash-lite',  # Backup option - lightest
    ]

    # Prompt banate hain
    prompt = f"""
    Write a high-quality, SEO-optimized article on the topic: '{topic}'.

    Requirements:
    - Word Count: Approximately {word_count} words
    - Tone: {tone}
    - Language: {language}
    - Style: Human-written, no AI clichés, engaging and informative
    
    Structure (use proper Markdown formatting):
    1. # Main Title (H1)
    2. ## Introduction (hook the reader)
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

    # Ek ek model try karo
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text, model_name  # Kaam kar gaya!

        except Exception as e:
            error_str = str(e)

            # Rate limit error (429) - thoda wait karo aur next model try karo
            if "429" in error_str:
                st.warning(f"⚠️ **{model_name}** ki rate limit ho gayi. Next model try kar raha hoon...")
                time.sleep(3)
                continue

            # Model not found (404) - next try karo
            elif "404" in error_str:
                st.warning(f"⚠️ **{model_name}** available nahi. Next model try kar raha hoon...")
                continue

            # Invalid API Key
            elif "API_KEY" in error_str or "invalid" in error_str.lower():
                st.error("❌ **API Key galat hai!** Google AI Studio se nayi key lein.")
                return None, None

            # Koi aur error
            else:
                st.error(f"❌ Error in {model_name}: {error_str}")
                continue

    # Sab models fail ho gaye
    return None, None


# ============================================================
# SIDEBAR - Settings / Options
# ============================================================
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Article Settings")

word_count = st.sidebar.select_slider(
    "📝 Word Count:",
    options=[500, 800, 1000, 1500, 2000],
    value=1000
)

tone = st.sidebar.radio(
    "🎨 Writing Tone:",
    options=["Professional & Formal", "Casual & Friendly", "Academic & Research"],
    index=0
)

language = st.sidebar.radio(
    "🌐 Language:",
    options=["English", "Hinglish (Hindi + English Mix)"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("**🤖 Active Model:** `gemini-2.0-flash`")
st.sidebar.markdown("**✅ Status:** Free Tier Available")
st.sidebar.markdown("**📊 Free Limit:** 15 requests/minute")


# ============================================================
# MAIN USER INTERFACE
# ============================================================
st.subheader("📌 Enter Your Topic")

topic = st.text_input(
    "Topic likhiye:",
    placeholder="e.g., Digital Marketing Trends 2026, AI in Healthcare, Content Writing Tips...",
    help="Jitna specific topic hoga, utna better article banega!"
)

# Optional: Additional context
extra_context = st.text_area(
    "📋 Additional Context (Optional):",
    placeholder="Koi specific points jo include karne hain? Target audience? Special requirements?",
    height=80
)

# Generate button
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    generate_btn = st.button("🚀 Generate Article", use_container_width=True, type="primary")


# ============================================================
# GENERATION LOGIC
# ============================================================
if generate_btn:
    if not topic.strip():
        st.error("❌ Topic khali hai! Kuch toh likhiye.")
    else:
        # Final prompt mein extra context bhi add kar do agar diya ho
        full_topic = topic
        if extra_context.strip():
            full_topic = f"{topic}\n\nAdditional context: {extra_context}"

        with st.spinner(f"🔍 Research aur writing jari hai... (~{word_count} words, 1-2 minutes lagte hain)"):
            content, used_model = generate_article(full_topic, word_count, tone, language)

        # ---- SUCCESS ----
        if content:
            st.success(f"✅ Article taiyar! | Model: `{used_model}` | Words: ~{len(content.split())}")
            st.markdown("---")

            # Two column layout
            col1, col2 = st.columns([3, 1])

            with col1:
                st.subheader("📄 Article Preview")
                # Markdown render karke dikhao (formatted)
                with st.expander("👁️ Formatted Preview (Recommended)", expanded=True):
                    st.markdown(content)

                # Plain text bhi dikhao (copy ke liye)
                with st.expander("📋 Plain Text (Copy/Paste ke liye)"):
                    st.text_area("", value=content, height=400, label_visibility="collapsed")

            with col2:
                st.subheader("📥 Export Options")

                # --- Word Document Download ---
                doc = Document()

                # Title add karo
                doc.add_heading(topic, level=0)

                # Content add karo - line by line
                for line in content.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    # Headings detect karo
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

                # File memory mein save karo
                bio = BytesIO()
                doc.save(bio)
                bio.seek(0)

                # Download button
                st.download_button(
                    label="📥 Download Word (.docx)",
                    data=bio.getvalue(),
                    file_name=f"{topic[:30].replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

                # Text download bhi dete hain
                st.download_button(
                    label="📄 Download Text (.txt)",
                    data=content.encode('utf-8'),
                    file_name=f"{topic[:30].replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

                st.markdown("---")
                st.info("""
                **💡 Tips:**
                - Word file directly WordPress mein import ho jaati hai
                - Text file ko Google Docs mein paste kar sakte hain
                - Headings automatically formatted hain
                """)

                # Article stats
                words = len(content.split())
                chars = len(content)
                st.metric("📊 Word Count", words)
                st.metric("📊 Characters", chars)

        # ---- FAILURE ----
        else:
            st.error("❌ Article generate nahi hua. Kuch gadbad hai.")
            st.markdown("""
            **Possible Solutions:**
            1. ✅ API key check karein — Google AI Studio se nayi banayein
            2. ✅ Internet connection check karein
            3. ✅ Kuch minutes baad dobara try karein (rate limit)
            4. ✅ Topic simple rakhein pehle test ke liye
            """)


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray;'>AgencyWriter Pro | Powered by Google Gemini 2.0 Flash | Free Tier Compatible</p>",
    unsafe_allow_html=True
)
