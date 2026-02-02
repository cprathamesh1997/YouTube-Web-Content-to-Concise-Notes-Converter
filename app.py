import streamlit as st
from dotenv import load_dotenv
import os
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from bs4 import BeautifulSoup
import re

# ===============================
# Environment & App Configuration
# ===============================

load_dotenv()

st.set_page_config(
    page_title="Youtube Content Summarizer",
    page_icon="📝",
    layout="centered"
)

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("❌ GOOGLE_API_KEY not found in environment variables.")
    st.stop()

# ✅ NEW Gemini SDK client
client = genai.Client(api_key=api_key)

# ===============================
# Prompt Templates
# ===============================

youtube_prompt = """
You are a YouTube video summarizer.
Summarize the transcript below into the most important points.
Limit the response to ~250 words.
Format the output as a bulleted list.

Transcript:
"""

url_prompt = """
You are a web content summarizer.
Summarize the webpage content below into the most important points.
Limit the response to ~250 words.
Format the output as a bulleted list.

Webpage Content:
"""

# ===============================
# Helper Functions
# ===============================

def extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID using regex."""
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None


def extract_transcript_details(youtube_url: str) -> str | None:
    try:
        video_id = extract_video_id(youtube_url)
        if not video_id:
            st.error("❌ Invalid YouTube URL.")
            return None

        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(item["text"] for item in transcript_list)

    except Exception as e:
        st.error(f"❌ Failed to fetch transcript: {e}")
        st.info("ℹ️ The video may not have captions enabled.")
        return None


def extract_webpage_text(url: str) -> str | None:
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/116.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ")
        text = re.sub(r"\s+", " ", text).strip()

        return text if len(text) > 100 else None

    except Exception as e:
        st.error(f"❌ Failed to fetch webpage: {e}")
        return None


def generate_gemini_content(text: str, prompt: str) -> str | None:
    """
    Gemini Free Tier (2026)
    Primary: gemini-2.5-flash
    Fallback: gemini-2.5-pro
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt + text
        )
        return response.text

    except Exception:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt + text
            )
            return response.text
        except Exception as e:
            st.error(f"❌ Gemini API Error: {e}")
            return None

# ===============================
# Streamlit UI
# ===============================

st.title("📝 Universal Content Summarizer")
st.markdown(
    "Generate **concise, structured notes** from "
    "**YouTube videos** using Google Gemini."
)

url_input = st.text_input(
    "Paste YouTube Video URL:",
    placeholder="https://www.youtube.com/watch?v=..."
)

# Thumbnail Preview
if url_input and ("youtube.com" in url_input or "youtu.be" in url_input):
    video_id = extract_video_id(url_input)
    if video_id:
        st.image(
            f"https://img.youtube.com/vi/{video_id}/0.jpg",
            use_container_width=True
        )
    else:
        st.warning("⚠️ Invalid YouTube URL format.")

# Generate Button
if st.button("🚀 Generate Notes"):
    if not url_input:
        st.warning("Please enter a URL first.")
    else:
        with st.spinner("Processing content..."):
            if "youtube.com" in url_input or "youtu.be" in url_input:
                extracted_text = extract_transcript_details(url_input)
                prompt = youtube_prompt
            else:
                extracted_text = extract_webpage_text(url_input)
                prompt = url_prompt

            if extracted_text:
                summary = generate_gemini_content(extracted_text, prompt)
                if summary:
                    st.markdown("## 📌 Detailed Summary")
                    st.markdown(summary)
            else:
                st.error(
                    "❌ Unable to extract content. "
                    "The video may lack captions or the website blocked scraping."
                )

st.markdown("---")
st.markdown("Powered by **Google Gemini (2.5 Free Tier)**")

