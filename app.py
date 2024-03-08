import json
import os
from os import PathLike
from dotenv import load_dotenv
import uuid
from pathlib import Path

from editor import Editor
from narrator import Narrator
from scenario import Writer
import logging
import asyncio

load_dotenv()
logging.basicConfig(
    format="(%(asctime)s) %(name)s:%(lineno)d [%(levelname)s] | %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def main(openai_api_key: str):
    # id = uuid.uuid4()
    id = 'f50144e7-9f15-4f90-ae15-5d42c1236529'
    # writer = Writer(openai_api_key)
    #
    # scenario = await writer.write(
    #     theme='Биткоин',
    #     paragraph_number=1,
    #     language='ru',
    # )
    #
    # print(scenario)
    #
    # if scenario.is_err():
    #     logger.error(scenario)
    #
    #     exit(1)
    #
    # scenario = scenario.ok().content

    scenario = 'Биткоин - это цифровая валюта, которая была создана в 2009 году неизвестным лицом или группой лиц под псевдонимом Сатоши Накамото. Биткоин использует технологию блокчейн, которая обеспечивает безопасность и прозрачность транзакций. Он отличается от традиционных валют, таких как доллары или евро, тем, что не имеет центрального банка или правительства, контролирующего его. Биткоин можно использовать для покупки товаров и услуг, а также для инвестирования и торговли на криптовалютных биржах. Он также стал объектом интереса для инвесторов, и его цена может значительно колебаться. В целом, биткоин представляет собой новую форму децентрализованной и цифровой валюты, которая имеет потенциал изменить финансовую систему.'
    narrator = Narrator(openai_api_key)
    #
    # mp3_bytes = await narrator.narrate(scenario)
    mp3_filename = f'narrate_{id}.mp3'
    #
    # with open(mp3_filename, 'wb') as f:
    #     f.write(mp3_bytes)

    # subtitles = await narrator.get_subtitles(mp3_filename)

    subtitles_path = f'subtitles_{id}.json'

    # with open(subtitles_path, 'w') as f:
    #     f.write(json.dumps(subtitles))

    editor = Editor()

    editor.burn_subtitles(
        audio_path=mp3_filename,
        subtitles_path=subtitles_path,
        output_path=f'narrate_{id}.mp4',
    )

    print('Done')



if __name__ == "__main__":
    asyncio.run(main(openai_api_key=os.getenv('OPENAI_API_KEY')))
