from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
import uuid
import os


app = FastAPI()


# 🔥 CORS (VERY IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def cut_video(
    file: UploadFile = File(...),
    start: float = Form(0),
    end: float = Form(10),
):
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
async def add_text(
    file: UploadFile = File(...),
    text: str = Form("Hello World"),
):
    input_name = f"input_{uuid.uuid4()}.mp4"
    output_name = f"text_{uuid.uuid4()}.mp4"

    with open(input_name, "wb") as f:
        f.write(await file.read())

    clip = VideoFileClip(input_name)

    txt_clip = TextClip(
        text=text,
        font="C:/Windows/Fonts/arial.ttf",
        font_size=48,
        color="#FFFFFF",
    ).with_position(("center", "center")).with_duration(clip.duration)

    final_clip = CompositeVideoClip([clip, txt_clip])

    final_clip.write_videofile(
        output_name,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    clip.close()
    txt_clip.close()
    final_clip.close()

    os.remove(input_name)

    return FileResponse(output_name, media_type="video/mp4", filename="result_with_text.mp4")



# ------------------------
# Merge Videos API
# ------------------------

@app.post("/merge-videos")
async def merge_videos(files: list[UploadFile] = File(...)):

    temp_files = []
    clips = []

    try:
        # Save uploaded videos
        for file in files:
            name = f"input_{uuid.uuid4()}.mp4"
            with open(name, "wb") as f:
                f.write(await file.read())
            temp_files.append(name)

        # Load clips
        for path in temp_files:
            clips.append(VideoFileClip(path))

        # Merge
        final_clip = concatenate_videoclips(clips, method="compose")

        output_name = f"merged_{uuid.uuid4()}.mp4"

        final_clip.write_videofile(
            output_name,
            fps=24,
            codec="libx264",
            audio_codec="aac"
        )

        # Cleanup
        for c in clips:
            c.close()

        final_clip.close()

        for f in temp_files:
            os.remove(f)

        return FileResponse(output_name, media_type="video/mp4", filename="merged.mp4")

    except Exception as e:
        return {"error": str(e)}
