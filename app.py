import json
import os
from datetime import datetime
from os import PathLike
from typing import List

import json5
from dotenv import load_dotenv
import uuid
from pathlib import Path

from editor import Editor, StockFinder
from narrator import Narrator
from scenario import Writer

from dataobjects import Scenario

import logging
import asyncio

load_dotenv()
logging.basicConfig(
    format="(%(asctime)s) %(name)s:%(lineno)d [%(levelname)s] | %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

openai_api_key = os.getenv('OPENAI_API_KEY')
pexels_api_key = os.getenv('PEXELS_API_KEY')

writer = Writer(openai_api_key)
narrator = Narrator(openai_api_key)
editor = Editor()
stock = StockFinder(pexels_api_key, openai_api_key)


async def main():
    base_output_directory = 'output'
    today_output_directory = f'{base_output_directory}/{datetime.now().strftime("%Y-%m-%d")}'
    today_video_output_directory = f'{today_output_directory}/videos'

    Path(today_output_directory).mkdir(parents=True, exist_ok=True)
    Path(today_video_output_directory).mkdir(parents=True, exist_ok=True)

    themes = [
        # "Пять утренних привычек для энергии на весь день",
        # "Топ-7 продуктов для повышения настроения",
        # "Улучшаем сон: практические советы",
        # "Медитация для начинающих: первые шаги к спокойствию",
        # "Как избавиться от стресса: эффективные методы",
        # "Секреты правильного питания для здоровья и счастья",
        "Простые упражнения для улучшения самочувствия",
        "Полезные привычки для укрепления иммунитета",
        "Техники релаксации: как найти внутренний покой",
        "Борьба с усталостью: советы для поддержания энергии",
    ]

    for theme in themes:
        video_id = uuid.uuid5(uuid.NAMESPACE_DNS, theme)

        scenario_filename = f'{today_output_directory}/scenario_{video_id}.json'
        if not os.path.exists(scenario_filename):
            scenario_result = await writer.write_scenario(
                subject=theme,
            )

            if scenario_result.is_err():
                logger.error(scenario_result)

                exit(1)

            scenario: Scenario = scenario_result.ok()

            with open(scenario_filename, 'w') as f:
                json5.dump(scenario.to_json(), f, ensure_ascii=False, indent=4)

        with open(scenario_filename, 'r') as f:
            scenario = Scenario.from_dict(json5.load(f))

        narration_filename = f'{today_output_directory}/narrate_{video_id}.mp3'

        if not os.path.exists(narration_filename):
            mp3_bytes = await narrator.narrate(scenario)

            with open(narration_filename, 'wb') as f:
                f.write(mp3_bytes)

        scenario.narration_path = narration_filename

        subtitles_path = f'{today_output_directory}/subtitles_{video_id}.json'

        if not os.path.exists(subtitles_path):
            subtitles = await narrator.get_subtitles(narration_filename)

            with open(subtitles_path, 'w') as f:
                json5.dump(subtitles, f, ensure_ascii=False, indent=4)

        # Load the subtitles from the JSON file
        with open(subtitles_path, 'r') as f:
            subtitles_json = json5.load(f)

        narrator.add_transcription_words_and_subtitles(scenario, subtitles_json)
        editor.split_words_into_lines(scenario)
        subtitles_clips = editor.get_subtitles_clips(scenario)

        try:
            await stock.add_stock_video_candidates(scenario)

            stock_video_clips = editor.get_stock_video_clips(scenario)
        except Exception as e:
            logger.error(e)
            logger.info(scenario)

            raise e

        background_music = editor.get_background_music()

        output_path = f'{today_video_output_directory}/{theme}.mp4'

        try:
            editor.compose_video(
                subtitles_clips,
                stock_video_clips,
                background_music,
                narration_filename,
                output_path
            )
        except Exception as e:
            logger.error(e)
            logger.info(scenario)

            raise e

        print('Done ' + theme)


if __name__ == "__main__":
    asyncio.run(main())
