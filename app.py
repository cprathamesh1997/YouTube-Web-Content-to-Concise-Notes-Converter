import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from bs4 import BeautifulSoup
load_dotenv()

#Configure Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
if not os.getenv("GOOGLE_API_KEY"):
    st.error("GOOGLE_API_KEY not found in .env. Please configure it and restart the app.")
    st.stop()

#Defining prompts
youtube_prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video, providing the important points in a summary
within 250 words. Please format the summary as a bulleted list. Please provide the summary of the text given here: """

url_prompt = """You are a web content summarizer. You will be taking the text from a webpage
and summarizing the main points in a concise summary within 250 words. Please format the summary as a bulleted list. Please provide the summary of the text given here: """

#Getting transcript from YouTube video
def extract_transcript_details(youtube_video_url):
    try:
        if "youtube.com" in youtube_video_url:
            video_id = youtube_video_url.split("=")[1]
        elif "youtu.be" in youtube_video_url:
            video_id = youtube_video_url.split("/")[-1]
        else:
            raise ValueError("Unsupported YouTube URL format.")
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join(i["text"] for i in transcript_text)
        return transcript
    except IndexError:
        st.error("Invalid YouTube URL format. Please use a link like https://www.youtube.com/watch?v=video_id or https://youtu.be/video_id.")
        return None
    except Exception as e:
        st.error(f"Failed to extract transcript: {str(e)}. Check if the video has captions or the URL is valid.")
        return None

#Extracting text from webpage
def extract_webpage_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs)
        return text if text else "No significant content found on the webpage."
    except Exception as e:
        st.error(f"Failed to fetch webpage content: {str(e)}. Ensure the URL is valid and accessible.")
        return None

#Generate summary using Google Gemini model
def generate_gemini_content(text, prompt):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt + text)
        return response.text
    except Exception as e:
        st.error(f"Failed to generate content: {str(e)}. Check API key or model availability.")
        return None

#Streamlit Interface
st.title("YouTube & Web Content to Detailed Notes Converter")
st.markdown("Enter a YouTube video link or any webpage URL to generate detailed notes.")

url_input = st.text_input("Enter YouTube Video Link or Web URL:", key="url_input")

if url_input:
    if "youtube.com" in url_input or "youtu.be" in url_input:
        if "youtube.com" in url_input:
            video_id = url_input.split("=")[1]
        elif "youtu.be" in url_input:
            video_id = url_input.split("/")[-1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True, caption="Video Thumbnail")
    else:
        st.write("Processing webpage content...")

if st.button("Get Detailed Notes"):
    if not url_input:
        st.error("Please provide a URL to get started.")
    else:
        text = None
        if "youtube.com" in url_input or "youtu.be" in url_input:
            text = extract_transcript_details(url_input)
            prompt = youtube_prompt
        else:
            text = extract_webpage_text(url_input)
            prompt = url_prompt
        if text:
            summary = generate_gemini_content(text, prompt)
            if summary:
                st.markdown("## Detailed Notes:")
                st.markdown(summary)

# Add a footer
st.markdown("---")
st.markdown("Powered by Streamlit and Google Generative AI")