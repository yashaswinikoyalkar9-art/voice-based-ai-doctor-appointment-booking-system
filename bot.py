"""Pipecat voice agent scaffold.

The Pipecat pipeline below shows the required audio flow. The dashboard's REST
API implements the three appointment tools. Connect the tool callbacks to the
same API methods before demoing end-to-end voice tool execution.

Pipecat's WebRTC signaling/client SDK versions evolve; follow the official
Pipecat Small WebRTC quickstart matching your installed Pipecat version.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask, PipelineParams
from pipecat.pipeline.runner import PipelineRunner
from pipecat.transports.base_transport import TransportParams
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport
from pipecat.services.elevenlabs.stt import ElevenLabsSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.google.llm import GoogleLLMService
from pipecat.processors.aggregators.llm_context import LLMContext, LLMContextAggregatorPair
from pipecat.audio.vad.silero import SileroVADAnalyzer

SYSTEM_PROMPT = """You are CareCall, a friendly doctor appointment assistant.
Ask which doctor/specialty and date the caller wants. Ask the caller to say their
phone number. Read the full number back and obtain explicit confirmation before
booking or cancelling. Never assume the number from caller ID or login.
Only claim an appointment is booked/cancelled after the booking tool succeeds.
Keep spoken responses brief and natural. This is a demo, not medical advice."""

async def run_bot(transport: SmallWebRTCTransport):
    stt = ElevenLabsSTTService(api_key=os.environ["ELEVENLABS_API_KEY"])
    tts = ElevenLabsTTSService(
        api_key=os.environ["ELEVENLABS_API_KEY"],
        voice_id=os.getenv("ELEVENLABS_VOICE_ID", ""),
    )
    llm = GoogleLLMService(
        api_key=os.environ["GOOGLE_API_KEY"],
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    )

    # Add tool definitions and callbacks using the function-calling API supported
    # by your installed Pipecat version. Suggested functions:
    # check_doctor_availability(doctor_id, date)
    # book_appointment(phone, doctor_id, date, time)
    # cancel_appointment(phone)
    # Call the backend endpoints in main.py and return their JSON results.

    context = LLMContext()
    user_ctx, assistant_ctx = LLMContextAggregatorPair(context)
    pipeline = Pipeline([
        transport.input(),
        stt,
        user_ctx,
        llm,
        tts,
        transport.output(),
        assistant_ctx,
    ])
    task = PipelineTask(pipeline, params=PipelineParams(enable_metrics=True))
    await PipelineRunner().run(task)

# For browser WebRTC signaling, use Pipecat's SmallWebRTC request handler /
# development runner from the official quickstart for the matching version.
# This keeps signaling and transport setup separate from appointment logic.
