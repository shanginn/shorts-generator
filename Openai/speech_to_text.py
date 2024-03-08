from enum import Enum
from typing import Literal, List

from openai import AsyncOpenAI
from openai._types import FileTypes, NotGiven, NOT_GIVEN
from openai.types.audio import Transcription
from tenacity import retry, wait_random_exponential, stop_after_attempt


class SpeechToText:
    def __init__(
        self,
        api_key: str,
        model: str = 'whisper-1',
        timestamp_granularities: List[Literal["word", "segment"]] = None,
        response_format: Literal["json", "text", "srt", "verbose_json", "vtt"] = 'json',
    ):
        if not api_key:
            raise ValueError('Open AI api key cannot be empty')

        if 'word' in (timestamp_granularities or []) and response_format != 'verbose_json':
            raise ValueError('If timestamp_granularity has `word`, response_format must be verbose_json')

        self.client = AsyncOpenAI(
            api_key=api_key,
            max_retries=3,
        )
        self.model = model
        self.timestamp_granularities = timestamp_granularities or ['segment']
        self.response_format = response_format

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    async def speech_to_text(
        self,
        file: FileTypes,
        language: str | NotGiven = NOT_GIVEN,
        prompt: str | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
    ) -> Transcription:
        return await self.client.audio.transcriptions.create(
            model=self.model,
            file=file,
            language=language,
            prompt=prompt,
            temperature=temperature,
            timestamp_granularities=self.timestamp_granularities,
            response_format=self.response_format,
        )
