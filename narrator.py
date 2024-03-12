from os import PathLike
from pathlib import Path
from typing import List, Dict

from dataobjects import Scenario, TranscriptionWord

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

    async def narrate(self, scenario: Scenario) -> bytes:
        return await self.text_to_speech.text_to_speech(
            scenario.full_scenario,
            speed=1
        )

    async def get_subtitles(self, file_path: str, scenario: Scenario) -> List[Dict]:
        transcription = await self.speech_to_text.speech_to_text(
            file=Path(file_path),
            language='ru',
            prompt=scenario.full_scenario,
        )

        return transcription.words

    def add_transcription_words_and_subtitles(self, scenario: Scenario, subtitles_json: List[Dict]) -> Scenario:
        subtitles = {i: TranscriptionWord.from_dict(word) for i, word in enumerate(subtitles_json)}
        scenario.subtitles = list(subtitles.values())

        last_seen_subtitle_index = 0
        for block in scenario.text_blocks:
            block_words = [word.lower().strip('.,!? ') for word in block.text.split()]
            for word in block_words:
                for i in range(last_seen_subtitle_index, len(subtitles)):
                    if word == subtitles[i].word.lower():
                        block.words.append(subtitles[i])
                        last_seen_subtitle_index = i
                        break

        return scenario
