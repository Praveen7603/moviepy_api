from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import uuid
import os

app = FastAPI()

# ------------------------
# Test API
# ------------------------
@app.get("/")
def home():
    return {"message": "API working"}

# ------------------------
# Cut Video API
# ------------------------
@app.post("/cut-video")
async def cut_video(file: UploadFile = File(...), start: float = Form(0), end: float = Form(10)):
    input_name = f"input_{uuid.uuid4()}.mp4"
    output_name = f"cut_{uuid.uuid4()}.mp4"

    with open(input_name, "wb") as f:
        f.write(await file.read())

    clip = VideoFileClip(input_name)
    cut_clip = clip.subclipped(start, min(end, clip.duration))
    cut_clip.write_videofile(output_name, fps=24)

    clip.close()
    cut_clip.close()
    os.remove(input_name)

    return FileResponse(output_name, media_type="video/mp4", filename="result.mp4")

# ------------------------
# Add Text API
# ------------------------
@app.post("/add-text")
async def add_text(file: UploadFile = File(...), text: str = Form("Hello World")):
    input_name = f"input_{uuid.uuid4()}.mp4"
    output_name = f"text_{uuid.uuid4()}.mp4"

    with open(input_name, "wb") as f:
        f.write(await file.read())

    clip = VideoFileClip(input_name)
    txt_clip = TextClip(text, fontsize=50, color='white', font='Arial')\
               .set_position('center').set_duration(clip.duration)
    final_clip = CompositeVideoClip([clip, txt_clip])
    final_clip.write_videofile(output_name, fps=24)

    clip.close()
    final_clip.close()
    os.remove(input_name)

    return FileResponse(output_name, media_type="video/mp4", filename="result_with_text.mp4")
