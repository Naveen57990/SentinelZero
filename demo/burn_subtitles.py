"""
Burn Subtitles & Composite Final Demo Video
Combines natural conversational Indian English neural voice (Prabhat),
live Playwright screen recording, presentation slides, and burned-in subtitles.
"""
import glob
import os
import re
import subprocess
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRT_PATH = os.path.join(BASE_DIR, "subtitles.srt")
AUDIO_COMBINED = os.path.join(BASE_DIR, "voiceover_human_combined.wav")
OUTPUT_PATH = os.path.join(BASE_DIR, "sentinelzero_demo.mp4")
TEMP_VIDEO = os.path.join(BASE_DIR, "temp_concat.mp4")

WIDTH, HEIGHT = 1920, 1080
FPS = 30

DURATIONS = {
    "seg1": 25.40,
    "seg2": 21.40,
    "seg3": 23.64,
    "scene_4": 25.10,
    "seg5": 24.70
}

SRT_CONTENT = """1
00:00:00,500 --> 00:00:07,000
Hey everyone! As developers, we are rapidly building autonomous AI agents and cloud APIs.

2
00:00:07,200 --> 00:00:15,000
But here's the dangerous part: we're silently introducing critical security vulnerabilities.

3
00:00:15,200 --> 00:00:25,200
Things like hardcoded production keys, missing enterprise SSO gates, and MCP tools with unrestricted shell execution.

4
00:00:25,800 --> 00:00:32,000
That's why we built SentinelZero: an autonomous, developer-first zero-trust security auditor.

5
00:00:32,200 --> 00:00:46,600
We engineered it from scratch with deterministic AST parsing, Shannon entropy mathematics, and specialized boundary inspection for Model Context Protocol agents.

6
00:00:47,000 --> 00:00:54,500
In a single command, SentinelZero audits your entire codebase in under two milliseconds!

7
00:00:54,700 --> 00:01:03,500
Take a look right here. It immediately flags critical exposures: a leaked OpenAI key, an insecure JWT bypass,

8
00:01:03,700 --> 00:01:10,200
and a dangerous terminal tool hazard, computing an urgent Posture Score of Grade F.

9
00:01:10,800 --> 00:01:17,500
Now, let's look at our live production dashboard in action.

10
00:01:17,700 --> 00:01:25,500
As we run the zero-trust audit, SentinelZero evaluates the live code in real time.

11
00:01:25,700 --> 00:01:35,300
It visualizes our security posture ring, flags unconfined MCP tools, and verifies compliance once remediated, bringing our score right back to Grade A.

12
00:01:35,800 --> 00:01:43,000
We built SentinelZero specifically for the TLN Cybersecurity Challenge 2026.

13
00:01:43,200 --> 00:01:52,500
It is completely open-source, verified with a 100% passing test suite, and deployed live on Vercel.

14
00:01:52,700 --> 00:02:00,000
Try it out today at web-theta-tawny-78.vercel.app. Thank you!
"""

def prepare_audio():
    print("Combining neural narration tracks...")
    p1 = os.path.join(BASE_DIR, "part_1_human.mp3")
    p2 = os.path.join(BASE_DIR, "part_2_human.mp3")
    p3 = os.path.join(BASE_DIR, "part_3_human.mp3")
    p4 = os.path.join(BASE_DIR, "part_4_human.mp3")
    p5 = os.path.join(BASE_DIR, "part_5_human.mp3")

    cmd = [
        "ffmpeg", "-y",
        "-i", p1, "-i", p2, "-i", p3, "-i", p4, "-i", p5,
        "-filter_complex", "[0:a][1:a][2:a][3:a][4:a]concat=n=5:v=0:a=1[aout]",
        "-map", "[aout]",
        "-c:a", "pcm_s16le",
        AUDIO_COMBINED
    ]
    subprocess.run(cmd, check=True)
    print(f"Combined audio saved to {AUDIO_COMBINED}")

def parse_time(t_str):
    h, m, rest = t_str.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0

def parse_srt(content):
    blocks = content.strip().split("\n\n")
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

def prepare_video_segments():
    print("Rendering video segments with synced durations...")
    # Find latest webm recording
    rec_files = sorted(glob.glob(os.path.join(BASE_DIR, "recordings", "*.webm")), key=os.path.getmtime)
    if not rec_files:
        raise RuntimeError("No screen recording webm found!")
    latest_webm = rec_files[-1]
    print(f"Using screen recording: {latest_webm}")

    padded_rec = os.path.join(BASE_DIR, "scene_4_padded.mp4")
    dur_s4 = DURATIONS["scene_4"]
    # Retime & pad screen recording to exact duration
    cmd_pad = [
        "ffmpeg", "-y",
        "-i", latest_webm,
        "-vf", f"setpts=1.064*PTS,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,tpad=stop_mode=clone:stop_duration=2.0",
        "-t", str(dur_s4),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        padded_rec
    ]
    subprocess.run(cmd_pad, check=True)

    # Slide segments
    slide_configs = [
        ("seg1.mp4", "frames/slide_1.png", DURATIONS["seg1"]),
        ("seg2.mp4", "frames/slide_2.png", DURATIONS["seg2"]),
        ("seg3.mp4", "frames/slide_3.png", DURATIONS["seg3"]),
        ("seg5.mp4", "frames/slide_5.png", DURATIONS["seg5"])
    ]
    for seg_name, slide_rel, dur in slide_configs:
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

    # Concat list
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

def wrap_text(text, max_chars=60):
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
    with open(SRT_PATH, "w", encoding="utf-8") as f:
        f.write(SRT_CONTENT.strip() + "\n")

    prepare_audio()
    prepare_video_segments()
    subs = parse_srt(SRT_CONTENT)
    print(f"Loaded {len(subs)} subtitle blocks.")

    font_path = "/System/Library/Fonts/Helvetica.ttc"
    if not os.path.exists(font_path):
        font_path = "/Library/Fonts/Arial.ttf"
    font = ImageFont.truetype(font_path, 34)

    cmd_in = [
        "ffmpeg", "-i", TEMP_VIDEO,
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
    ]
    p_in = subprocess.Popen(cmd_in, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    cmd_out = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS),
        "-i", "-",
        "-i", AUDIO_COMBINED,
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

            max_w = 0
            for l in lines:
                bbox = draw.textbbox((0, 0), l, font=font)
                w = bbox[2] - bbox[0]
                if w > max_w:
                    max_w = w
            
            badge_w = max(max_w + 50, 400)
            badge_x1 = (WIDTH - badge_w) // 2
            badge_x2 = badge_x1 + badge_w

            draw.rounded_rectangle(
                [badge_x1, badge_y1, badge_x2, badge_y2],
                radius=14,
                fill=(10, 15, 26, 230),
                outline=(59, 130, 246, 180),
                width=2
            )

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

    if os.path.exists(TEMP_VIDEO):
        os.remove(TEMP_VIDEO)

    print(f"Successfully generated final demo video with burned-in subtitles at: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
