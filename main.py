import os
import asyncio

from livekit.agents import JobContext, WorkerOptions, cli, JobProcess
from livekit.agents.llm import (
    ChatContext,
    ChatMessage,
)
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import deepgram, silero, cartesia, openai

from dotenv import load_dotenv

load_dotenv()

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    initial_ctx = ChatContext(
        messages=[
            ChatMessage(
                role="system",
                content=(
                    "You are Amara, the voice assistant for Lumen Ads. Your job is to handle incoming calls from potential clients by creating a friendly, human-like, and comfortable conversation. Once the client feels at ease, ask about their Amazon business, challenges, and goals—one question at a time—while keeping your responses short and clear. If appropriate, suggest scheduling a meeting for a later date (not the same day) to dive deeper into how Lumen Ads can help. Before scheduling, always ask for their phone number. If you don’t know the answer to a question, let the client know you’re still in development and continuously learning. Avoid repeating sentences unnecessarily, and feel free to use sarcasm or humor when needed to keep the conversation engaging. However, ensure the call doesn’t last longer than 10 minutes."
                ),
            )
        ]
    )

    assistant = VoiceAssistant(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(),
        llm=openai.LLM(
            base_url="https://api.cerebras.ai/v1",
            api_key=os.environ.get("CEREBRAS_API_KEY"),
            model="llama3.1-8b",
        ),
        tts=cartesia.TTS(voice="694f9389-aac1-45b6-b726-9d9369183238"),
        chat_ctx=initial_ctx,
    )

    await ctx.connect()
    assistant.start(ctx.room)
    await asyncio.sleep(1)
    await assistant.say("Hello, I’m Amara, your assistant from Lumen Ads. How’s everything going?", allow_interruptions=True)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
