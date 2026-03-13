import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
import time

# ============================================================
# GURJEET BHAI — SIRF YAHAN APNI KEYS DAALO
#
# IMPORTANT: Teen ALAG Google accounts se keys banao!
# Ek hi account ki 3 keys = same quota = fayda nahi
#
# Keys kahan banayein:
#   https://aistudio.google.com/app/apikey
#
# Account 1: apna main Gmail
# Account 2: dusra Gmail (ya family ka)
# Account 3: teesra Gmail (ya koi bhi)
# ============================================================

KEY_FROM_ACCOUNT_1 = "AIzaSyDnRQESmfZGMDlFaeMUaep7BaBaVwc1zOk"   # <- Pehle Gmail ki key
KEY_FROM_ACCOUNT_2 = "AIzaSyCACN-AMO_reLWkXD90wbhygiMOxYQuBg0"   # <- Doosre Gmail ki key
KEY_FROM_ACCOUNT_3 = "AIzaSyBfHrkK5f7wraDWcJ4rOsx0AXuef7eXHI8"   # <- Teesre Gmail ki key

# ============================================================
# PAGE SETUP
# ============================================================
st.set_page_config(page_title="AgencyWriter Pro", page_icon="✍️", layout="wide")
st.title("✍️ AgencyWriter Pro")
st.markdown("**AI Content Engine — 3 Account Rotation System**")
st.markdown("---")

# ============================================================
# MODEL SETUP
# Best free models (March 2026):
#   gemini-2.5-flash-lite  -> 1000 requests/day (SABSE ZYADA!)
#   gemini-2.5-flash       -> 250 requests/day
#   gemini-2.0-flash       -> limited but stable
# ============================================================
ALL_COMBOS = [
    (KEY_FROM_ACCOUNT_1, "gemini-2.5-flash-lite"),   # Account 1, best model
    (KEY_FROM_ACCOUNT_2, "gemini-2.5-flash-lite"),   # Account 2, best model
    (KEY_FROM_ACCOUNT_3, "gemini-2.5-flash-lite"),   # Account 3, best model
    (KEY_FROM_ACCOUNT_1, "gemini-2.5-flash"),        # Account 1, backup
    (KEY_FROM_ACCOUNT_2, "gemini-2.5-flash"),        # Account 2, backup
    (KEY_FROM_ACCOUNT_3, "gemini-2.5-flash"),        # Account 3, backup
]

# ============================================================
# ARTICLE GENERATION FUNCTION
# ============================================================
def generate_article(topic, word_count, tone, language):
    prompt = f"""
    Write a high-quality, SEO-optimized article on the topic: '{topic}'.

    Requirements:
    - Word Count: Approximately {word_count} words
    - Tone: {tone}
    - Language: {language}
    - Style: Human-written, engaging, no robotic language

    Structure (use Markdown):
    1. # Catchy Main Title
    2. ## Introduction  
    3. ## Background & Overview
    4. ## Key Points & Details
    5. ## Benefits & Importance
    6. ## Practical Tips (step by step)
    7. ## Common Mistakes to Avoid
    8. ## Future Trends
    9. ## Conclusion
    10. ## FAQ (5 questions with detailed answers)

    Use bullet points, bold important words, and clear headings.
    Make it feel human-written, not AI-generated.
    """

    progress_bar = st.progress(0)
    status_text = st.empty()
    total = len(ALL_COMBOS)

    for i, (api_key, model_name) in enumerate(ALL_COMBOS):
        progress_bar.progress((i) / total)
        account_num = (i % 3) + 1
        status_text.info(f"🔄 Account {account_num} + {model_name} try kar raha hoon... ({i+1}/{total})")

        # Key check — agar placeholder hai toh skip
        if "YAHAN" in api_key or len(api_key) < 20:
            status_text.warning(f"⚠️ Account {account_num} ki key nahi daali. Skip...")
            time.sleep(0.5)
            continue

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            progress_bar.progress(1.0)
            status_text.success(f"✅ Kaam kar gaya! Account {account_num} + {model_name}")
            return response.text, model_name, account_num

        except Exception as e:
            error_str = str(e)
            if "429" in error_str:
                status_text.warning(f"⚠️ Account {account_num} rate limit. Next try...")
                time.sleep(2)
            elif "404" in error_str:
                status_text.warning(f"⚠️ {model_name} available nahi. Next...")
            elif "API_KEY" in error_str or "invalid" in error_str.lower() or "400" in error_str:
                status_text.error(f"❌ Account {account_num} ki key galat hai!")
                time.sleep(1)
            else:
                status_text.warning(f"⚠️ Error: {str(e)[:60]}...")
                time.sleep(1)
            continue

    progress_bar.progress(1.0)
    return None, None, None


# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.header("⚙️ Settings")
word_count = st.sidebar.select_slider(
    "📝 Word Count",
    options=[500, 800, 1000, 1500, 2000],
    value=1000
)
tone = st.sidebar.radio(
    "🎨 Tone",
    ["Professional & Formal", "Casual & Friendly", "Academic"]
)
language = st.sidebar.radio(
    "🌐 Language",
    ["English", "Hindi", "Hinglish (Hindi+English)"]
)
st.sidebar.markdown("---")
st.sidebar.markdown("**ℹ️ Free Limits (per account):**")
st.sidebar.markdown("• gemini-2.5-flash-lite: 1000/day")
st.sidebar.markdown("• gemini-2.5-flash: 250/day")
st.sidebar.markdown("• 3 accounts = 3x quota!")


# ============================================================
# MAIN UI
# ============================================================
st.subheader("📌 Article Topic")
topic = st.text_input(
    "Topic likhiye:",
    placeholder="e.g., Digital Marketing Trends 2026, Benefits of Yoga, AI Tools for Business..."
)
extra = st.text_area(
    "📋 Extra Details (Optional):",
    placeholder="Koi specific angle, audience, ya points include karne hain?",
    height=80
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    go = st.button("🚀 Generate Article", use_container_width=True, type="primary")

# ============================================================
# RUN
# ============================================================
if go:
    if not topic.strip():
        st.error("❌ Topic daalna zaroori hai!")
    else:
        full_topic = topic
        if extra.strip():
            full_topic = f"{topic}\n\nExtra details: {extra}"

        st.markdown("---")
        content, used_model, used_account = generate_article(
            full_topic, word_count, tone, language
        )

        if content:
            st.markdown("---")
            left, right = st.columns([3, 1])

            with left:
                st.subheader("📄 Article Preview")
                with st.expander("👁️ Formatted (Recommended)", expanded=True):
                    st.markdown(content)
                with st.expander("📋 Plain Text (Copy ke liye)"):
                    st.text_area("", value=content, height=400, label_visibility="collapsed")

            with right:
                st.subheader("💾 Download")

                # Word file banana
                doc = Document()
                doc.add_heading(topic, level=0)
                for line in content.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('# ') and not line.startswith('##'):
                        doc.add_heading(line[2:], level=1)
                    elif line.startswith('## '):
                        doc.add_heading(line[3:], level=2)
                    elif line.startswith('### '):
                        doc.add_heading(line[4:], level=3)
                    elif line.startswith(('- ', '* ', '• ')):
                        doc.add_paragraph(line[2:], style='List Bullet')
                    else:
                        doc.add_paragraph(line)

                bio = BytesIO()
                doc.save(bio)
                bio.seek(0)

                st.download_button(
                    "📥 Word File (.docx)",
                    data=bio.getvalue(),
                    file_name=f"{topic[:25].replace(' ','_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
                st.download_button(
                    "📄 Text File (.txt)",
                    data=content.encode('utf-8'),
                    file_name=f"{topic[:25].replace(' ','_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                st.markdown("---")
                st.metric("Words", len(content.split()))
                st.metric("Characters", len(content))
                st.caption(f"Model: {used_model}")
                st.caption(f"Account: #{used_account}")

        else:
            st.markdown("---")
            st.error("❌ Koi bhi attempt kaam nahi ki.")
            st.markdown("""
            ### 🔧 Kya karein:

            **Sabse pehle check karein:**
            - Kya teeno keys **ALAG Gmail accounts** se bani hain?
            - Ek hi Gmail account ki 3 keys = same quota = same error!

            **Steps:**
            1. [aistudio.google.com](https://aistudio.google.com/app/apikey) kholo
            2. **Doosre Gmail se login** karo (ya nayi Gmail banao — free hai)
            3. Nayi key banao, `app.py` mein `KEY_FROM_ACCOUNT_2` mein daalo
            4. Dobara try karo

            **Ya 15-20 minute wait karein** — rate limit automatically reset hoti hai
            """)

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption("AgencyWriter Pro | gemini-2.5-flash-lite | 3 Account Rotation | Free Tier")
