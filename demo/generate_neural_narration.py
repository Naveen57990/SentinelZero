"""
Generate Human Explanatory Narration using Indian English Neural Voice (Prabhat)
Includes conversational pacing, natural pauses, and sentence-level timestamps.
"""
import asyncio
import edge_tts
import os
import subprocess

VOICE = "en-IN-PrabhatNeural"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECTIONS = [
    (
        "part_1_human",
        "Hey everyone! As developers, we are rapidly building autonomous AI agents and cloud APIs. "
        "But here's the dangerous part: we're silently introducing critical vulnerabilities. "
        "Things like hardcoded production keys, missing enterprise SSO gates, and MCP tools with unrestricted shell execution."
    ),
    (
        "part_2_human",
        "That's why we built SentinelZero. It is an autonomous, developer-first zero-trust security auditor. "
        "We engineered it from scratch with deterministic AST parsing, Shannon entropy mathematics, and specialized boundary inspection for Model Context Protocol agents."
    ),
    (
        "part_3_human",
        "In a single command, SentinelZero audits your entire codebase in under two milliseconds! "
        "Take a look right here. It immediately flags critical exposures: a leaked OpenAI key, an insecure JWT bypass, and a dangerous terminal tool hazard... "
        "computing an urgent Posture Score of Grade F."
    ),
    (
        "part_4_human",
        "Now, let's look at our live production dashboard in action. "
        "As we run the zero-trust audit, SentinelZero evaluates the live code in real time. "
        "It visualizes our security posture ring, flags unconfined MCP tools, and verifies compliance once remediated, bringing our score right back to Grade A."
    ),
    (
        "part_5_human",
        "We built SentinelZero specifically for the TLN Cybersecurity Challenge 2026. "
        "It is completely open-source, verified with a 100% passing test suite, and deployed live on Vercel. "
        "Try it out today at web-theta-tawny-78.vercel.app. Thank you!"
    )
]

async def generate_narration():
    section_files = []
    vtt_files = []
    
    for sec_id, text in SECTIONS:
        mp3_path = os.path.join(BASE_DIR, f"{sec_id}.mp3")
        vtt_path = os.path.join(BASE_DIR, f"{sec_id}.vtt")
        # -4% rate creates a calm, clear, confident explanatory tone with breathing room
        comm = edge_tts.Communicate(text, VOICE, rate="-4%", pitch="+0Hz")
        await comm.save(mp3_path)
        
        # Also generate subtitles for this section
        comm_sub = edge_tts.Communicate(text, VOICE, rate="-4%", pitch="+0Hz")
        with open(vtt_path, "w", encoding="utf-8") as f:
            async for chunk in comm_sub.stream():
                if chunk["type"] == "subtitles":
                    f.write(chunk["data"])

        section_files.append(mp3_path)
        vtt_files.append(vtt_path)
        print(f"Generated {sec_id}.mp3 and {sec_id}.vtt")

    return section_files, vtt_files

if __name__ == "__main__":
    asyncio.run(generate_narration())
