import streamlit as st
import os
from datetime import datetime
from backend.media_gen import generate_audio, generate_image, generate_video
from googletrans import Translator

# --- Helper Functions ---

def translate_prompt(prompt, lang):
    if lang == "English":
        return prompt
    try:
        translator = Translator()
        translated = translator.translate(prompt, dest=lang.lower()).text
        return translated
    except Exception:
        return prompt  # fallback to original

def sanitize_filename(prompt):
    return "".join(c if c.isalnum() else "_" for c in prompt.strip())[:50].lower()

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

#def reset_state():
#    st.session_state.clear()
#    st.experimental_rerun()

# --- Page Configuration ---
st.set_page_config(page_title="OSN Media Generator", layout="wide")

# --- Top Splash Header ---
st.caption("Built by O.S.Narayana ❤️ using Streamlit + ElevenLabs + Unsplash")
st.title("🎮 Welcome to OSN Media Generator")

# --- Collapsed Settings ---
with st.expander("⚙️ Settings", expanded=False):
    language_options = ['English', 'Telugu', 'Hindi']
    prompt_lang = st.selectbox("Select Prompt Language", options=language_options, index=0)
    target_lang = st.selectbox("Translate to Language", options=language_options, index=0)

    # Optional manual toggle fallback (not auto, just UI helper)
    dark_mode = st.toggle("🌗 Force Dark Mode", value=False)

    # Reset Button
    #if st.button("♻️ Reset"):
    #    reset_state()

    st.markdown("---")

# --- Auto Dark Mode Styling (based on browser/device) ---
st.markdown("""
<style>
    /* Auto light/dark theme support */
    body {
        background-color: var(--background-color);
        color: var(--text-color);
    }

    /* Vertical tabs for mobile */
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

# --- Prompt Section ---
st.caption("Enter your media prompt")

prompt = st.text_input("📝 Prompt", placeholder="e.g., A farmer working in the field", label_visibility="collapsed")

# Inline Toggles
debug_mode = st.toggle("🪛 Show Debug Logs", value=False)
add_watermark = st.checkbox("🌊 Add watermark/logo (optional)", value=False)
lang = st.selectbox("🌐 Language", ["English", "Telugu", "Hindi", "Tamil"], index=0)

# ---------- Tabs for Media ----------
tab1, tab2, tab3 = st.tabs(["🖼️ Image", "🔊 Audio", "🎞️ Video"])

if prompt:
    translated_prompt = translate_prompt(prompt, lang)
    safe_prompt = sanitize_filename(prompt)

    with tab1:
        if st.button("Generate Image"):
            image_path = f"outputs/images/{safe_prompt}.png"
            ensure_dir("outputs/images")
            path = generate_image(translated_prompt, image_path, add_watermark, dark_mode,debug_mode)
            if path and os.path.exists(path):
                st.image(path, caption="Generated Image", use_container_width=True)
                st.download_button("📥 Download Image", data=open(path, "rb"), file_name=os.path.basename(path), mime="image/png")

    with tab2:
        if st.button("Generate Audio"):
            audio_path = f"outputs/audio/{safe_prompt}.mp3"
            ensure_dir("outputs/audio")
            path = generate_audio(translated_prompt, audio_path, debug_mode)
            if path and os.path.exists(path):
                st.audio(path)
                st.download_button("📥 Download Audio", data=open(path, "rb"), file_name=os.path.basename(path), mime="audio/mpeg")

    with tab3:
        if st.button("Generate Video"):
            video_path = f"outputs/videos/{safe_prompt}.mp4"
            image_path = f"outputs/images/{safe_prompt}.jpg"
            audio_path = f"outputs/audio/{safe_prompt}.mp3"
    
            ensure_dir("outputs/videos")
    
            # Ensure audio and image exist before generating video
            if not os.path.exists(image_path):
                if debug_mode:
                    st.info("🎨 Generating image as it doesn't exist...")
                image_path = generate_image(translated_prompt, image_path, add_watermark, dark_mode, debug_mode)
    
            if not os.path.exists(audio_path):
                if debug_mode:
                    st.info("🎤 Generating audio as it doesn't exist...")
                audio_path = generate_audio(translated_prompt, audio_path, debug_mode)
    
            # Proceed only if both files exist
            if os.path.exists(image_path) and os.path.exists(audio_path):
                path = generate_video(translated_prompt, image_path, audio_path, video_path, add_watermark, dark_mode)
                if path and os.path.exists(path):
                    st.video(path)
                    st.download_button("📥 Download Video", data=open(path, "rb"), file_name=os.path.basename(path), mime="video/mp4")
            else:
                st.error("❌ Could not generate image/audio required for video.")




# --- Privacy Policy ---

#with st.expander("📜 Privacy Policy", expanded=False):
#    st.markdown(
#        "We value your privacy. View our [Privacy Policy](https://github.com/sivaogeti/osnarayana-media-generator/blob/main/PRIVACY_POLICY.md)",
#        unsafe_allow_html=True
#    )


st.markdown("[📜 View Privacy Policy](https://sivaogeti.github.io/osnarayana-media-generator/privacy.html)", unsafe_allow_html=True)
