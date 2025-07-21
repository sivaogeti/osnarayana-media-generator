# ✅ Enhanced app.py for better UI look and feel using Streamlit
# ⚠️ Core logic untouched. Purely layout & visual updates.

import streamlit as st
import os
from datetime import datetime
from backend.media_gen import generate_audio, generate_image, generate_video
from googletrans import Translator
from gtts.lang import tts_langs
import base64

# --- Helper Functions ---
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


# --- Helper Functions ---
INDIAN_LANG_CODES = ["en", "hi", "te", "ta", "kn", "ml", "mr", "gu", "pa", "ur", "bn"]
all_langs = tts_langs()
SUPPORTED_LANGUAGES = {
    f"{all_langs[code]} ({code})": code
    for code in INDIAN_LANG_CODES if code in all_langs
}

def translate_prompt(prompt, target_lang):
    if target_lang == "English":
        return prompt
    try:
        translator = Translator()
        dest_code = SUPPORTED_LANGUAGES.get(target_lang, "en")
        translated = translator.translate(prompt, dest=dest_code)
        return translated.text
    except Exception as e:
        print(f"[Translation Error]: {e}")
        return prompt

def sanitize_filename(prompt):
    return "".join(c if c.isalnum() else "_" for c in prompt.strip())[:50].lower()

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

# --- Page Configuration ---
st.set_page_config(page_title="OSN Media Generator", page_icon="🎮", layout="wide")

# --- Header Section ---
icon_base64 = get_base64_image("assets/app_icon.png")  # Path of icon file

st.markdown(
    f"""
    <div style="display: flex; align-items: center; gap: 12px;">
        <img src="data:image/png;base64,{icon_base64}" width="50" style="border-radius: 10px;" />
        <h1 style="margin: 0; font-size: 2em;">Welcome to OSN Media Generator</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Caption below
st.caption("Crafted with 💗 by [O.S.Narayana](https://www.linkedin.com/in/osnarayana/)")

st.markdown("---")
# --- Settings ---
with st.expander("⚙️ Settings", expanded=False):
    target_lang = st.selectbox("🌐 Output Language", list(SUPPORTED_LANGUAGES.keys()), index=0)
    dark_mode = st.toggle("🌗 Force Dark Mode", value=False)
    st.markdown("---")

# --- Mobile Styles & Dark Mode Theme ---
st.markdown("""
<style>
    @media only screen and (max-width: 768px) {
        section[data-testid="stTabs"] div[role="tablist"] {
            flex-direction: column;
            align-items: stretch;
        }
        section[data-testid="stTabs"] button[role="tab"] {
            width: 100%;
            text-align: left;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Prompt Input ---
st.caption("Enter your media prompt")
prompt = st.text_input("📝 Prompt", placeholder="e.g., A farmer working in the field", label_visibility="collapsed")
selected_display = target_lang
debug_mode = st.toggle("🪛 Show Debug Logs", value=False)
add_watermark = True

# --- Tabs for Media Generation ---
tab1, tab2, tab3 = st.tabs(["🖼️ Image", "🔊 Audio", "🎞️ Video"])

if prompt:
    translated_prompt = translate_prompt(prompt, target_lang)
    safe_prompt = sanitize_filename(prompt)

    with tab1:
        if st.button("Generate Image", key="gen_img_btn"):
            with st.spinner("🔄 Generating image..."):
                image_path = f"outputs/images/{safe_prompt}.png"
                ensure_dir("outputs/images")
                path = generate_image(translated_prompt, image_path, add_watermark, dark_mode, debug_mode)
                if path and os.path.exists(path):
                    st.image(path, caption="Generated Image", use_container_width=True)
                    st.download_button("📥 Download Image", data=open(path, "rb"), file_name=os.path.basename(path), mime="image/png")

    with tab2:
        if st.button("Generate Audio", key="gen_audio_btn"):
            with st.spinner("🔄 Generating Audio..."):
                audio_path = f"outputs/audio/{safe_prompt}.mp3"
                ensure_dir("outputs/audio")
                lang_code = SUPPORTED_LANGUAGES[selected_display]
                path = generate_audio(translated_prompt, audio_path, debug_mode, lang=lang_code)
                if path and os.path.exists(path):
                    st.audio(path)
                    st.download_button("📥 Download Audio", data=open(path, "rb"), file_name=os.path.basename(path), mime="audio/mpeg")

    with tab3:
        if st.button("Generate Video", key="gen_video_btn"):
            with st.spinner("🔄 Generating Video..."):
                video_path = f"outputs/videos/{safe_prompt}.mp4"
                image_path = f"outputs/images/{safe_prompt}.png"
                audio_path = f"outputs/audio/{safe_prompt}.mp3"
                ensure_dir("outputs/videos")

                if not os.path.exists(image_path):
                    if debug_mode:
                        st.info("🎨 Generating image as it doesn't exist...")
                    image_path = generate_image(translated_prompt, image_path, add_watermark, dark_mode, debug_mode)

                if not os.path.exists(audio_path):
                    if debug_mode:
                        st.info("🎤 Generating audio as it doesn't exist...")
                    lang_code = SUPPORTED_LANGUAGES[selected_display]
                    audio_path = generate_audio(translated_prompt, audio_path, debug_mode, lang=lang_code)

                if os.path.exists(image_path) and os.path.exists(audio_path):
                    path = generate_video(translated_prompt, image_path, audio_path, video_path, add_watermark, dark_mode)
                    if path and os.path.exists(path):
                        st.video(path)
                        st.download_button("📥 Download Video", data=open(path, "rb"), file_name=os.path.basename(path), mime="video/mp4")
                else:
                    st.error("❌ Could not generate image/audio required for video.")

# --- Footer ---
st.markdown("---")
st.markdown("[📜 View Privacy Policy](https://sivaogeti.github.io/osnarayana-media-generator/privacy.html)", unsafe_allow_html=True)
st.caption("© 2025 OSN Media | Built with Streamlit")
