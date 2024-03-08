from enum import Enum
from typing import Literal

from openai import AsyncOpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt


class Voice(Enum):
    alloy = 'alloy'
    echo = 'echo'
    fable = 'fable'
    onyx = 'onyx'
    nova = 'nova'
    shimmer = 'shimmer'


class TextToSpeech:
    def __init__(
        self,
        api_key: str,
        model: str = 'tts-1',
        voice: Voice = Voice.alloy,
        response_format: Literal["mp3", "opus", "aac", "flac", "pcm", "wav"] = 'mp3',
    ):
        if not api_key:
            raise ValueError('Open AI api key cannot be empty')

        self.client = AsyncOpenAI(
            api_key=api_key,
            max_retries=3,
        )
        self.model = model
        self.voice = voice
        self.response_format = response_format

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    async def text_to_speech(self, text: str, speed: float = 1.0) -> bytes:
        response = await self.client.audio.speech.create(
            model=self.model,
            voice=self.voice.value,
            input=text,
            speed=speed,
            response_format=self.response_format,
        )

        return response.content
