# ✅ Updated media_gen.py with file logging + UI debug toggle
import os
import re
import logging
import streamlit as st
import requests
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from dotenv import load_dotenv
from moviepy.editor import ImageClip, AudioFileClip
from elevenlabs import generate, save, set_api_key
from googletrans import Translator
from PIL import ImageEnhance, Image
import tempfile

# Load env vars
load_dotenv()

# Logging setup
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Constants
OUTPUT_DIR = "outputs"
DEFAULT_IMAGE = "assets/fallback.jpg"
WATERMARK_PATH = "assets/logo_watermark.png"
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

os.makedirs("outputs/audio", exist_ok=True)
os.makedirs("outputs/images", exist_ok=True)
os.makedirs("outputs/videos", exist_ok=True)

def translate_text(text, target_lang):
    return Translator().translate(text, dest=target_lang).text

def sanitize_filename(text):
    return re.sub(r'\W+', '_', text).lower()[:50]

def apply_watermark(image_path, watermark_path=WATERMARK_PATH):
    try:
        base = Image.open(image_path).convert("RGBA")
        watermark = Image.open(watermark_path).convert("RGBA").resize((100, 100))
        base.paste(watermark, (base.width - 110, base.height - 110), watermark)
        base.convert("RGB").save(image_path)
    except Exception as e:
        logging.error(f"Watermarking failed: {e}")
        st.write(f"❌ Watermarking failed: {e}")

def use_fallback_image(prompt, add_watermark=False):
    try:
        fallback_path = DEFAULT_IMAGE
        output_path = f"outputs/images/{sanitize_filename(prompt)}.jpg"
        with Image.open(fallback_path) as img:
            img.save(output_path)
        if add_watermark:
            apply_watermark(output_path)
        return output_path
    except UnidentifiedImageError:
        logging.error("Could not open fallback image.")
        st.write("❌ Could not open fallback image.")
        return None

def generate_gtts_fallback(prompt, output_path, debug_mode=False):
    try:
        from gtts import gTTS
        tts = gTTS(text=prompt, lang="en")
        tts.save(output_path)
        logging.info(f"gTTS fallback audio saved to {output_path}")
        if debug_mode:
            st.write(f"✅ Fallback audio (gTTS) saved to {output_path}")
        return output_path
    except Exception as e:
        logging.error(f"gTTS fallback failed: {e}")
        st.write(f"❌ gTTS fallback failed: {str(e)}")
        return None

def generate_image(prompt, file_tag, add_watermark=False, dark_mode=False, debug_mode=False):
    try:
        # Enhance prompt if dark mode is enabled
        if dark_mode:
            prompt += " at night, dark theme, low light, moody lighting"

        url = f"https://api.unsplash.com/photos/random?query={requests.utils.quote(prompt)}&client_id={UNSPLASH_ACCESS_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        image_url = response.json()["urls"]["regular"]
        image_response = requests.get(image_url, timeout=10)
        image_response.raise_for_status()

        output_path = f"outputs/images/{sanitize_filename(prompt)}.jpg"
        img = Image.open(BytesIO(image_response.content))
        img.convert("RGB").save(output_path)

        if add_watermark:
            apply_watermark(output_path)

        return output_path

    except Exception as e:
        logging.error(f"Image generation failed: {e}")
        st.write("🔁 Unsplash failed. Using fallback.")
        st.write(f"❌ Image generation failed: {e}")
        return use_fallback_image(prompt, add_watermark=add_watermark)


# ✅ Updated generate_audio with proper language handling

def generate_audio(prompt, output_path, debug_mode=False, lang="en"):
    try:
        api_key = os.getenv("ELEVEN_API_KEY") or st.secrets.get("ELEVEN_API_KEY", None)

        # Use gTTS for non-English languages
        if lang != "en":
            if debug_mode:
                st.write(f"🌐 Non-English language selected: {lang}. Using gTTS.")
            return generate_gtts_fallback(prompt, output_path, debug_mode, lang=lang)

        if api_key:
            if debug_mode:
                st.write(f"✅ ELEVEN_API_KEY loaded: {api_key[:4]}...****")

            set_api_key(api_key)
            if debug_mode:
                st.write(f"🎧 Generating audio for prompt: {prompt}")

            try:
                audio = generate(text=prompt, voice="Aria", model="eleven_monolingual_v1")
                save(audio, output_path)
                logging.info(f"Audio saved successfully to {output_path}")

                if debug_mode:
                    st.write(f"🔍 File exists after save? {os.path.exists(output_path)}")
                    st.write(f"✅ Audio saved successfully to {output_path}")
                return output_path

            except Exception as e:
                logging.warning(f"ElevenLabs failed: {e}")
                if debug_mode:
                    st.write(f"⚠️ ElevenLabs failed: {str(e)}")
                    st.write("🔁 Falling back to gTTS...")
                return generate_gtts_fallback(prompt, output_path, debug_mode)

        else:
            logging.warning("ELEVEN_API_KEY not found")
            if debug_mode:
                st.write("❌ ELEVEN_API_KEY not found. Falling back to gTTS.")
            return generate_gtts_fallback(prompt, output_path, debug_mode)

    except Exception as e:
        logging.error(f"Exception during audio generation setup: {e}")
        if debug_mode:
            st.write(f"❌ Exception during audio generation setup: {str(e)}")
            st.write("🔁 Falling back to gTTS...")
        return generate_gtts_fallback(prompt, output_path, debug_mode)
  

def generate_video(prompt, image_path, audio_path, output_path, add_watermark=False, dark_mode=False):
    try:
        # If dark_mode, darken the image temporarily
        if dark_mode:
            with Image.open(image_path) as img:
                enhancer = ImageEnhance.Brightness(img)
                darker_img = enhancer.enhance(0.5)  # Reduce brightness to 50%
                
                # Save to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    temp_image_path = tmp.name
                    darker_img.save(temp_image_path)
                    image_path = temp_image_path

        audio_clip = AudioFileClip(audio_path)
        image_clip = ImageClip(image_path).set_duration(audio_clip.duration).resize(height=720)
        video = image_clip.set_audio(audio_clip)

        output_path = f"outputs/videos/{sanitize_filename(prompt)}.mp4"
        video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        return output_path

    except Exception as e:
        logging.error(f"Video generation failed: {e}")
        st.write(f"❌ Video generation failed: {e}")
        return None

