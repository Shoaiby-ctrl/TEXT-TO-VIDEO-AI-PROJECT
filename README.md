# 🎬 AI Movie Maker Pro

**AI Movie Maker Pro** is a fully automated "Text-to-Video" pipeline built with Python. It takes a simple user prompt and generates a complete short video with a scripted voiceover, high-quality cinematic visuals, and synchronized audio.

## 🚀 Features
* **Automated Storytelling:** Uses **Google Gemini 2.5 Flash** to write a coherent 3-sentence story and matching image prompts.
* **Cinematic Visuals:** Generates 16:9 photorealistic images using the **Flux** model (via Pollinations.ai).
* **Neural Voiceover:** Generates professional-grade speech using **EdgeTTS**.
* **Video Rendering:** Uses **MoviePy** to stitch images and audio into a downloadable `.mp4` file.

## 🛠️ Tech Stack
* **Backend:** Python (Flask)
* **AI Logic:** Google Generative AI (Gemini)
* **Image Gen:** Flux Model API
* **Audio:** EdgeTTS (Microsoft Azure Neural Voices)
* **Video Processing:** MoviePy

## 📦 How to Run
1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You must have ImageMagick installed on your system for MoviePy)*
3.  Set your API Key:
    ```bash
    export GEMINI_API_KEY=your_key_here
    ```
4.  Run the app:
    ```bash
    python app.py
    ```
5.  Open `http://127.0.0.1:5000`

## 📸 Screenshots
*(Add a screenshot of the dark mode UI here)*