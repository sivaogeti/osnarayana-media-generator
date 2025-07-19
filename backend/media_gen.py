# media_gen.py

import os
import streamlit as st
import re
import requests
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from dotenv import load_dotenv
from elevenlabs import generate, save, Voice, VoiceSettings, set_api_key
from moviepy.editor import ImageClip, AudioFileClip
from googletrans import Translator

# Load environment variables
load_dotenv()

# Config
OUTPUT_DIR = "outputs"
DEFAULT_IMAGE = "assets/fallback.jpg"
WATERMARK_PATH = "assets/logo_watermark.png"
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

# Set ElevenLabs API key
if not ELEVEN_API_KEY:
    raise ValueError("ELEVEN_API_KEY is not set. Please check your .env file.")
set_api_key(ELEVEN_API_KEY)

# Ensure output folders exist
os.makedirs("outputs/audio", exist_ok=True)
os.makedirs("outputs/images", exist_ok=True)
os.makedirs("outputs/videos", exist_ok=True)

def translate_text(text, target_lang):
    translator = Translator()
    translated = translator.translate(text, dest=target_lang)
    return translated.text

def sanitize_filename(text):
    return re.sub(r'\W+', '_', text).lower()[:50]

def apply_watermark(image_path, watermark_path=WATERMARK_PATH):
    try:
        base = Image.open(image_path).convert("RGBA")
        watermark = Image.open(watermark_path).convert("RGBA").resize((100, 100))
        base.paste(watermark, (base.width - 110, base.height - 110), watermark)
        base.convert("RGB").save(image_path)
    except Exception as e:
        st.write("❌ Watermarking failed: {e}")

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
        st.write("❌ Could not open fallback image.")
        return None

def generate_image(prompt, file_tag, add_watermark=False):
    try:
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
        st.write("🔁 Unsplash failed. Using fallback.")
        st.write("❌ Image generation failed: {e}")
        return use_fallback_image(prompt, add_watermark=add_watermark)

def generate_audio(prompt, output_path):
    try:
        import streamlit as st
        api_key = os.getenv("ELEVEN_API_KEY") or st.secrets.get("ELEVEN_API_KEY", None)
        if api_key:
            st.write(f"✅ ELEVEN_API_KEY loaded: {api_key[:4]}...****")
        else:
            st.write("❌ ELEVEN_API_KEY not found.")
            return None

        set_api_key(api_key)

        st.write(f"🎧 Generating audio for prompt: {prompt}")
        audio = generate(
            text=prompt,
            voice=Voice(
                voice_id="21m00Tcm4TlvDq8ikWAM",  # Aria's official voice ID
                settings=VoiceSettings(stability=0.5, similarity_boost=0.75)
            )
        )
        save(audio, output_path)
        st.write(f"🔍 File exists after save? {os.path.exists(output_path)}")
        st.write(f"✅ Audio saved successfully to {output_path}")
        return output_path

    except Exception as e:
        st.write(f"❌ Exception during audio generation: {str(e)}")
        return None

def generate_video(prompt, image_path, audio_path):
    try:
        audio_clip = AudioFileClip(audio_path)
        image_clip = ImageClip(image_path).set_duration(audio_clip.duration).resize(height=720)
        video = image_clip.set_audio(audio_clip)
        output_path = f"outputs/videos/{sanitize_filename(prompt)}.mp4"
        video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        return output_path
    except Exception as e:
        st.write("❌ Video generation failed: {e}")
        return None
