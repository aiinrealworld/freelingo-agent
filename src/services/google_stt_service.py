from google.cloud import speech_v1p1beta1 as speech
from typing import AsyncGenerator

class GoogleSTTService:
    def __init__(self):
        self.client = speech.SpeechClient()
        self.streaming_config = speech.StreamingRecognitionConfig(
            config=speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=44100,
                language_code="en-US"
            ),
            interim_results=False,
            single_utterance=True
        )

    async def stream_transcribe(self, audio_stream: AsyncGenerator[bytes, None]) -> str:
        """
        Takes an async generator of raw PCM audio chunks and returns the final transcript.
        """
        requests = (
            speech.StreamingRecognizeRequest(audio_content=chunk)
            async for chunk in audio_stream
        )

        responses = self.client.streaming_recognize(self.streaming_config, requests)

        transcript = ""
        for response in responses:
            for result in response.results:
                if result.is_final:
                    transcript += result.alternatives[0].transcript

        return transcript
