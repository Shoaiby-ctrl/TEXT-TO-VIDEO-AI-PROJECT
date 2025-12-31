import os
import asyncio
import edge_tts
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import requests
import json
import random
import uuid
import shutil

app = Flask(__name__)

# --- CONFIGURATION ---
api_key = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
genai.configure(api_key=api_key)

# --- ENSURE FOLDERS EXIST ---
os.makedirs('static/audio', exist_ok=True)
os.makedirs('static/images', exist_ok=True)
os.makedirs('static/videos', exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate_video", methods=["POST"])
def generate_video():
    user_prompt = request.form.get("prompt")
    run_id = str(uuid.uuid4())[0:8]
    
    try:
        # STEP 1: Generate Story & Prompts
        model = genai.GenerativeModel("gemini-2.5-flash") 
        
        # We tell Gemini to keep prompts simple because FLUX handles the rest
        system_prompt = f"""
        You are a Movie Director.
        Topic: "{user_prompt}" 
        
        Task:
        1. Write a 3-sentence story.
        2. Write 3 image prompts (one for each sentence).
        
        CRITICAL FOR IMAGES: Describe the subject and action clearly. Do not add too many "quality" words, I will add those.
        
        OUTPUT JSON:
        {{
            "script": "Sentence 1. Sentence 2. Sentence 3.",
            "image_prompts": ["Scene 1 description...", "Scene 2...", "Scene 3..."]
        }}
        """
        
        response = model.generate_content(
            system_prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        data = json.loads(response.text)
        script = data['script']
        prompts = data['image_prompts']

        # STEP 2: Generate Audio
        output_audio_path = f"static/audio/{run_id}.mp3"
        voice = "en-US-GuyNeural"
        
        async def gen_audio():
            communicate = edge_tts.Communicate(script, voice)
            await communicate.save(output_audio_path)
            
        asyncio.run(gen_audio())

        # STEP 3: Generate Images using FLUX (The Quality Fix) 🌟
        image_files = []
        for i, prompt in enumerate(prompts):
            seed = random.randint(1, 999999)
            
            # 1. We add "Flux Realism" keywords manually
            enhanced_prompt = f"{prompt}, photorealistic, 8k, highly detailed, cinematic lighting, shot on 35mm lens"
            encoded_prompt = enhanced_prompt.replace(' ', '%20')
            
            # 2. We Switch to 16:9 Aspect Ratio (1280x720)
            # 3. We Force the 'Flux' Model (&model=flux)
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&seed={seed}&model=flux"
            
            print(f"Downloading image {i} from Flux...")
            img_data = requests.get(image_url).content
            
            filename = f"static/images/{run_id}_{i}.jpg"
            with open(filename, "wb") as f:
                f.write(img_data)
            image_files.append(filename)

        # STEP 4: Stitch Video
        audio_clip = AudioFileClip(output_audio_path)
        total_duration = audio_clip.duration
        clip_duration = total_duration / len(image_files)

        clips = []
        for img_file in image_files:
            # We resize to ensure it fits 720p perfectly
            clip = ImageClip(img_file).set_duration(clip_duration).crossfadein(0.5)
            clips.append(clip)

        final_video = concatenate_videoclips(clips, method="compose", padding=-0.5)
        final_video = final_video.set_audio(audio_clip)
        
        output_video_path = f"static/videos/video_{run_id}.mp4"
        final_video.write_videofile(output_video_path, fps=10, codec="libx264", audio_codec="aac")

        # Cleanup
        audio_clip.close()
        os.remove(output_audio_path)
        for img_file in image_files:
             os.remove(img_file)

        return jsonify({
            "success": True, 
            "video_url": output_video_path, 
            "script": script
        })

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)