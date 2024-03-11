import json
import os
from datetime import datetime
from os import PathLike
from dotenv import load_dotenv
import uuid
from pathlib import Path

from editor import Editor, StockFinder
from narrator import Narrator
from scenario import Writer

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

    Path(today_output_directory).mkdir(parents=True, exist_ok=True)

    themes = [
        'Влияние социальных сетей на подростков.',
        'Как музыка влияет на настроение.',
        'Эволюция моды в XX веке.',
        'Значение снов в нашей жизни.',
        'Почему кофе так популярен во всем мире.',
        'Вегетарианство: плюсы и минусы.',
        'Как чтение книг влияет на развитие мозга.',
        'Важность воды для человеческого организма.',
        'Психология цвета: как цвета влияют на нас.',
    ]

    for theme in themes:
        video_id = uuid.uuid5(uuid.NAMESPACE_DNS, theme)

        scenario_filename = f'{today_output_directory}/scenario_{video_id}.txt'
        if not os.path.exists(scenario_filename):
            scenario = await writer.write_scenario(
                theme=theme,
                paragraph_number=1,
                language='ru',
            )

            if scenario.is_err():
                logger.error(scenario)

                exit(1)

            scenario = scenario.ok().content

            with open(scenario_filename, 'w') as f:
                f.write(scenario)

        with open(scenario_filename, 'r') as f:
            scenario = f.read()

        print(scenario)

        mp3_filename = f'{today_output_directory}/narrate_{video_id}.mp3'

        if not os.path.exists(mp3_filename):
            mp3_bytes = await narrator.narrate(scenario)

            with open(mp3_filename, 'wb') as f:
                f.write(mp3_bytes)

        subtitles_path = f'{today_output_directory}/subtitles_{video_id}.json'

        if not os.path.exists(subtitles_path):
            subtitles = await narrator.get_subtitles(mp3_filename)

            with open(subtitles_path, 'w') as f:
                f.write(json.dumps(subtitles))

        # Load the subtitles from the JSON file
        with open(subtitles_path, 'r') as f:
            subtitles_json = json.load(f)

        # Split the text into lines
        subtitles_lines = editor.split_words_into_lines(subtitles_json)

        for line in subtitles_lines:
            line['stock_candidates'] = await stock.search_for_stock_videos(line['text'], 5)

        editor.burn_subtitles(
            audio_path=mp3_filename,
            subtitles_lines=subtitles_lines,
            output_path=f'{today_output_directory}/{theme}_{video_id}.mp4',
        )

        print('Done ' + theme)


if __name__ == "__main__":
    asyncio.run(main())
