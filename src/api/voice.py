from fastapi import APIRouter, WebSocket
from services.google_stt_service import GoogleSTTService
from starlette.websockets import WebSocketDisconnect
import asyncio

router = APIRouter()
stt_service = GoogleSTTService()

@router.websocket("/ws")
async def voice_websocket(websocket: WebSocket):
    await websocket.accept()
    print("🔌 WebSocket connected")

    queue = asyncio.Queue()

    async def receive_audio():
        try:
            while True:
                data = await websocket.receive_bytes()
                await queue.put(data)
        except WebSocketDisconnect:
            print("❌ WebSocket disconnected")
            await queue.put(None)  # Sentinel to end STT stream

    async def audio_stream():
        while True:
            chunk = await queue.get()
            if chunk is None:
                break
            yield chunk

    # Run receiver in background
    receiver_task = asyncio.create_task(receive_audio())

    try:
        transcript = await stt_service.stream_transcribe(audio_stream())
        print(f"🗣️ Final transcript: {transcript}")
    except Exception as e:
        print("🚨 STT error:", e)
    finally:
        receiver_task.cancel()
        await websocket.close()