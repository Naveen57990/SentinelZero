"""
Burn Subtitles & Composite Final Demo Video
Combines Indian English voiceover (Rishi), live Playwright dashboard screen recording,
presentation slides, and burned-in anti-aliased subtitles into sentinelzero_demo.mp4.
"""
import os
import re
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRT_PATH = os.path.join(BASE_DIR, "subtitles.srt")
AUDIO_PATH = os.path.join(BASE_DIR, "voiceover_in.wav")
OUTPUT_PATH = os.path.join(BASE_DIR, "sentinelzero_demo.mp4")
TEMP_VIDEO = os.path.join(BASE_DIR, "temp_concat.mp4")

WIDTH, HEIGHT = 1920, 1080
FPS = 30

def parse_time(t_str):
    # 00:01:05,000
    h, m, rest = t_str.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0

def parse_srt(srt_file):
    with open(srt_file, "r", encoding="utf-8") as f:
        content = f.read().strip()
    
    blocks = content.split("\n\n")
    subs = []
    for b in blocks:
        lines = b.strip().split("\n")
        if len(lines) >= 3:
            time_match = re.match(r"(\d+:\d+:\d+,\d+)\s*-->\s*(\d+:\d+:\d+,\d+)", lines[1])
            if time_match:
                start = parse_time(time_match.group(1))
                end = parse_time(time_match.group(2))
                text = " ".join(lines[2:])
                subs.append((start, end, text))
    return subs

def prepare_concatenated_video():
    print("Preparing padded segment 4...")
    padded_rec = os.path.join(BASE_DIR, "scene_4_padded.mp4")
    # Screen recording is ~18.44s. Part 4 audio is 18.77s. Pad 0.5s freeze-frame.
    cmd_pad = [
        "ffmpeg", "-y",
        "-i", os.path.join(BASE_DIR, "recordings", "page@4d5b1f9b43baf5d8ad147643750ea97a.webm"),
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,tpad=stop_mode=clone:stop_duration=0.5",
        "-t", "18.8",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        padded_rec
    ]
    subprocess.run(cmd_pad, check=True)

    # Re-render slide segments with precise durations matching Rishi narration
    durations = [
        ("seg1.mp4", "frames/slide_1.png", 17.5),
        ("seg2.mp4", "frames/slide_2.png", 14.0),
        ("seg3.mp4", "frames/slide_3.png", 21.2),
        ("seg5.mp4", "frames/slide_5.png", 15.0)
    ]
    for seg_name, slide_rel, dur in durations:
        seg_path = os.path.join(BASE_DIR, seg_name)
        slide_path = os.path.join(BASE_DIR, slide_rel)
        cmd_slide = [
            "ffmpeg", "-y", "-loop", "1",
            "-i", slide_path,
            "-t", str(dur),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
            seg_path
        ]
        subprocess.run(cmd_slide, check=True)

    # Create concat list
    concat_list = os.path.join(BASE_DIR, "concat_final.txt")
    with open(concat_list, "w") as f:
        f.write(f"file '{os.path.join(BASE_DIR, 'seg1.mp4')}'\n")
        f.write(f"file '{os.path.join(BASE_DIR, 'seg2.mp4')}'\n")
        f.write(f"file '{os.path.join(BASE_DIR, 'seg3.mp4')}'\n")
        f.write(f"file '{padded_rec}'\n")
        f.write(f"file '{os.path.join(BASE_DIR, 'seg5.mp4')}'\n")

    print("Concatenating segments into raw video...")
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        TEMP_VIDEO
    ]
    subprocess.run(cmd_concat, check=True)
    print("Concatenation complete.")

def wrap_text(text, max_chars=65):
    words = text.split()
    lines = []
    cur = []
    for w in words:
        if sum(len(x) for x in cur) + len(cur) + len(w) > max_chars:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))
    return lines

def main():
    prepare_concatenated_video()
    subs = parse_srt(SRT_PATH)
    print(f"Loaded {len(subs)} subtitle blocks.")

    # Try font
    font_path = "/System/Library/Fonts/Helvetica.ttc"
    if not os.path.exists(font_path):
        font_path = "/Library/Fonts/Arial.ttf"
    font = ImageFont.truetype(font_path, 34)

    # Launch FFmpeg input pipe (decode RGB24)
    cmd_in = [
        "ffmpeg", "-i", TEMP_VIDEO,
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
    ]
    p_in = subprocess.Popen(cmd_in, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    # Launch FFmpeg output pipe (encode H.264 + AAC + Subtitles)
    cmd_out = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS),
        "-i", "-",
        "-i", AUDIO_PATH,
        "-i", SRT_PATH,
        "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-c:s", "mov_text",
        "-shortest",
        OUTPUT_PATH
    ]
    p_out = subprocess.Popen(cmd_out, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    frame_bytes = WIDTH * HEIGHT * 3
    frame_idx = 0

    print("Burning subtitles onto video stream...")
    while True:
        raw_frame = p_in.stdout.read(frame_bytes)
        if not raw_frame or len(raw_frame) < frame_bytes:
            break
        
        t = frame_idx / float(FPS)
        
        # Check active subtitle
        active_text = None
        for s_start, s_end, s_txt in subs:
            if s_start <= t <= s_end:
                active_text = s_txt
                break

        if active_text:
            img = Image.frombytes("RGB", (WIDTH, HEIGHT), raw_frame)
            draw = ImageDraw.Draw(img, "RGBA")
            lines = wrap_text(active_text, max_chars=60)
            
            line_height = 42
            total_text_h = len(lines) * line_height
            badge_h = total_text_h + 26
            badge_y1 = HEIGHT - 85 - badge_h
            badge_y2 = HEIGHT - 85

            # Calculate max width of lines
            max_w = 0
            for l in lines:
                bbox = draw.textbbox((0, 0), l, font=font)
                w = bbox[2] - bbox[0]
                if w > max_w:
                    max_w = w
            
            badge_w = max(max_w + 50, 400)
            badge_x1 = (WIDTH - badge_w) // 2
            badge_x2 = badge_x1 + badge_w

            # Draw sleek translucent rounded badge
            draw.rounded_rectangle(
                [badge_x1, badge_y1, badge_x2, badge_y2],
                radius=14,
                fill=(10, 15, 26, 230),
                outline=(59, 130, 246, 180),
                width=2
            )

            # Draw text
            cur_y = badge_y1 + 13
            for l in lines:
                draw.text(
                    (WIDTH // 2, cur_y + line_height // 2),
                    l,
                    fill=(255, 255, 255),
                    font=font,
                    anchor="mm"
                )
                cur_y += line_height

            p_out.stdin.write(img.tobytes())
        else:
            p_out.stdin.write(raw_frame)

        frame_idx += 1
        if frame_idx % 300 == 0:
            print(f"Processed {frame_idx} frames ({frame_idx/FPS:.1f}s)...")

    p_in.stdout.close()
    p_in.wait()
    p_out.stdin.close()
    p_out.wait()

    # Clean up temp
    if os.path.exists(TEMP_VIDEO):
        os.remove(TEMP_VIDEO)

    print(f"Successfully generated final demo video with burned-in subtitles at: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
