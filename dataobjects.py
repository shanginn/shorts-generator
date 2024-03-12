import dataclasses
from typing import Optional, List
from decimal import Decimal

@dataclasses.dataclass
class TranscriptionWord:
    start: float
    end: float
    word: str

    def to_json(self):
        return {
            "start": self.start,
            "end": self.end,
            "word": self.word,
        }

    @staticmethod
    def from_dict(d: dict):
        start = float(Decimal(d['start']).quantize(Decimal('0.00')))
        end = float(Decimal(d['end']).quantize(Decimal('0.00')))
        return TranscriptionWord(
            start=start,
            end=end,
            word=d['word'],
        )

@dataclasses.dataclass
class TextLine:
    text: str
    start: float
    end: float
    words: List[TranscriptionWord]

    def to_json(self):
        return {
            "text": self.text,
            "start": self.start,
            "end": self.end,
            "words": [word.to_json() for word in self.words],
        }

    @staticmethod
    def from_dict(d: dict):
        return TextLine(
            text=d['text'],
            start=d['start'],
            end=d['end'],
            words=[TranscriptionWord.from_dict(word) for word in d['words']],
        )

@dataclasses.dataclass
class ScenarioTextBlock:
    text: str
    keywords: list[str]
    words: List[TranscriptionWord] = dataclasses.field(default_factory=list)
    stock_video_urls: Optional[dict] = None

    def to_json(self):
        return {
            "text": self.text,
            "keywords": self.keywords,
            "words": [word.to_json() for word in self.words],
        }

    @staticmethod
    def from_dict(d: dict):
        return ScenarioTextBlock(
            text=d['text'],
            keywords=d['keywords'],
            words=[TranscriptionWord.from_dict(word) for word in (d['words'] if 'words' in d else [])],
        )

    def duration(self) -> float:
        return self.end() - self.start()

    def start(self) -> float:
        return self.words[0].start

    def end(self) -> float:
        return self.words[-1].end


@dataclasses.dataclass
class Scenario:
    full_scenario: str
    text_blocks: list[ScenarioTextBlock]
    narration_path: Optional[str] = None
    subtitles: Optional[List[TranscriptionWord]] = None
    lines: Optional[List[TextLine]] = None

    def to_json(self):
        return {
            "full_scenario": self.full_scenario,
            "text_blocks": [block.to_json() for block in self.text_blocks],
        }

    @staticmethod
    def from_dict(d: dict):
        return Scenario(
            full_scenario=d['full_scenario'],
            text_blocks=[ScenarioTextBlock.from_dict(block) for block in d['text_blocks']],
        )
