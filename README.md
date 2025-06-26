# YouTube-Web-Content-to-Detailed-Notes-Converter
A Streamlit app that takes a YouTube video URL or a webpage link and generates structured, bulleted summaries using the Google Gemini generative model. It pulls transcripts from YouTube or extracts visible text from a webpage, processes the content, and returns concise notes.

<img width="413" alt="YT TO NOTES" src="https://github.com/user-attachments/assets/d5058a97-fda7-4d17-a729-2428ce78720d" />


# Techniques Used

* __Transcript Extraction__ via YouTube Transcript Api automatically extracts and concatenates subtitle text, enabling summarization of video content without audio processing.

* __Google Generative AI__ via Gemini API Uses the google generative ai client to access the Gemini model for summarization.

* __Web Scraping__ with Beautiful Soup Retrieves text from webpage tags,enabling general-purpose web article summarization.

* __Streamlit UI__ Integration utilizes st.image() for displaying YouTube thumbnails and st.markdown() for formatted summary output.

* __Environment Variable Handling__ via dotenv loads sensitive API keys using python-dotenv, promoting secure configuration.
