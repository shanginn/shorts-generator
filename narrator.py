from os import PathLike
from pathlib import Path
from typing import List

from openai.types.audio import Transcription

from Openai.speech_to_text import SpeechToText
from Openai.text_to_speech import TextToSpeech, Voice


class Narrator:
    def __init__(self, openai_api_key):
        self.text_to_speech = TextToSpeech(
            api_key=openai_api_key,
            voice=Voice.shimmer,
            model='tts-1',
        )

        self.speech_to_text = SpeechToText(
            api_key=openai_api_key,
            timestamp_granularities=['word'],
            response_format='verbose_json',
        )

    async def narrate(self, text: str) -> bytes:
        return await self.text_to_speech.text_to_speech(text, speed=1.1)

    async def get_subtitles(self, file_path: str) -> List[dict]:
        transcription = await self.speech_to_text.speech_to_text(
            file=Path(file_path),
            language='ru',
        )

        return transcription.words
