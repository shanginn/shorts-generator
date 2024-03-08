import json
import os
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
    # id = uuid.uuid4()
    id = 'f50144e7-9f15-4f90-ae15-5d42c1236529'
    #
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

    # # Load the subtitles from the JSON file
    # with open(subtitles_path, 'r') as f:
    #     subtitles_json = json.load(f)
    #
    # # Split the text into lines
    # subtitles_lines = editor.split_words_into_lines(subtitles_json)
    #
    # for line in subtitles_lines:
    #     line['stock_candidates'] = await stock.search_for_stock_videos(line['text'], 5)

    subtitles_lines = [{'text': 'Биткоин – это цифровая валюта которая была создана в 2009', 'start': 0.0, 'end': 4.099999904632568, 'words': [{'word': 'Биткоин', 'start': 0.0, 'end': 0.6200000047683716}, {'word': '–', 'start': 0.6200000047683716, 'end': 0.8399999737739563}, {'word': 'это', 'start': 0.8399999737739563, 'end': 1.0199999809265137}, {'word': 'цифровая', 'start': 1.0199999809265137, 'end': 1.440000057220459}, {'word': 'валюта', 'start': 1.440000057220459, 'end': 1.9199999570846558}, {'word': 'которая', 'start': 2.5399999618530273, 'end': 2.619999885559082}, {'word': 'была', 'start': 2.619999885559082, 'end': 2.9000000953674316}, {'word': 'создана', 'start': 2.9000000953674316, 'end': 3.2200000286102295}, {'word': 'в', 'start': 3.2200000286102295, 'end': 3.3399999141693115}, {'word': '2009', 'start': 3.3399999141693115, 'end': 4.099999904632568}], 'stock_candidates': ['https://player.vimeo.com/external/539033394.hd.mp4?s=4a924ed8ab86e02f62f2458f134d2374ee6b6907&profile_id=172&oauth2_token_id=57447761']}, {'text': 'году неизвестным лицом или группой лиц под', 'start': 4.099999904632568, 'end': 7.300000190734863, 'words': [{'word': 'году', 'start': 4.099999904632568, 'end': 4.679999828338623}, {'word': 'неизвестным', 'start': 4.679999828338623, 'end': 5.300000190734863}, {'word': 'лицом', 'start': 5.300000190734863, 'end': 5.760000228881836}, {'word': 'или', 'start': 5.760000228881836, 'end': 6.28000020980835}, {'word': 'группой', 'start': 6.28000020980835, 'end': 6.659999847412109}, {'word': 'лиц', 'start': 6.659999847412109, 'end': 6.980000019073486}, {'word': 'под', 'start': 6.980000019073486, 'end': 7.300000190734863}], 'stock_candidates': ['https://player.vimeo.com/external/530783417.hd.mp4?s=308f4717af71f6f3f4e2349b872d3bcb3cb2b233&profile_id=172&oauth2_token_id=57447761']}, {'text': 'псевдонимом Сатоши Накамото Биткоин использует технологию блокчейн', 'start': 7.300000190734863, 'end': 11.920000076293945, 'words': [{'word': 'псевдонимом', 'start': 7.300000190734863, 'end': 7.920000076293945}, {'word': 'Сатоши', 'start': 7.920000076293945, 'end': 8.34000015258789}, {'word': 'Накамото', 'start': 8.34000015258789, 'end': 8.779999732971191}, {'word': 'Биткоин', 'start': 9.579999923706055, 'end': 10.0}, {'word': 'использует', 'start': 10.0, 'end': 10.520000457763672}, {'word': 'технологию', 'start': 10.520000457763672, 'end': 11.079999923706055}, {'word': 'блокчейн', 'start': 11.079999923706055, 'end': 11.920000076293945}], 'stock_candidates': ['https://player.vimeo.com/external/539013037.hd.mp4?s=68eefdd3bbf8cabeddc43062f2d043752cb0c226&profile_id=172&oauth2_token_id=57447761']}, {'text': 'которая обеспечивает безопасность и прозрачность транзакций Он отличается', 'start': 12.199999809265137, 'end': 16.520000457763672, 'words': [{'word': 'которая', 'start': 12.199999809265137, 'end': 12.319999694824219}, {'word': 'обеспечивает', 'start': 12.319999694824219, 'end': 12.960000038146973}, {'word': 'безопасность', 'start': 12.960000038146973, 'end': 13.65999984741211}, {'word': 'и', 'start': 13.65999984741211, 'end': 13.859999656677246}, {'word': 'прозрачность', 'start': 13.859999656677246, 'end': 14.34000015258789}, {'word': 'транзакций', 'start': 14.34000015258789, 'end': 15.0}, {'word': 'Он', 'start': 15.920000076293945, 'end': 15.960000038146973}, {'word': 'отличается', 'start': 15.960000038146973, 'end': 16.520000457763672}], 'stock_candidates': ['https://player.vimeo.com/external/390172691.hd.mp4?s=a8bb245082608fdc64be0fa3f509a2a132e3b400&profile_id=173&oauth2_token_id=57447761']}, {'text': 'от традиционных валют таких как доллары или евро тем что не имеет центрального', 'start': 16.520000457763672, 'end': 21.1200008392334, 'words': [{'word': 'от', 'start': 16.520000457763672, 'end': 16.68000030517578}, {'word': 'традиционных', 'start': 16.68000030517578, 'end': 17.260000228881836}, {'word': 'валют', 'start': 17.260000228881836, 'end': 17.579999923706055}, {'word': 'таких', 'start': 18.059999465942383, 'end': 18.059999465942383}, {'word': 'как', 'start': 18.059999465942383, 'end': 18.260000228881836}, {'word': 'доллары', 'start': 18.260000228881836, 'end': 18.780000686645508}, {'word': 'или', 'start': 18.780000686645508, 'end': 18.860000610351562}, {'word': 'евро', 'start': 18.860000610351562, 'end': 19.239999771118164}, {'word': 'тем', 'start': 19.920000076293945, 'end': 20.0}, {'word': 'что', 'start': 20.139999389648438, 'end': 20.219999313354492}, {'word': 'не', 'start': 20.219999313354492, 'end': 20.360000610351562}, {'word': 'имеет', 'start': 20.360000610351562, 'end': 20.559999465942383}, {'word': 'центрального', 'start': 20.559999465942383, 'end': 21.1200008392334}], 'stock_candidates': ['https://player.vimeo.com/external/494469638.hd.mp4?s=51746034598cdf1a6ea7849b6f08404de61fdbbc&profile_id=175&oauth2_token_id=57447761', 'https://player.vimeo.com/external/507877197.hd.mp4?s=e6047c0fde051a074dc4cf1a9c99ec1a6c9080e1&profile_id=172&oauth2_token_id=57447761', 'https://player.vimeo.com/external/539033394.hd.mp4?s=4a924ed8ab86e02f62f2458f134d2374ee6b6907&profile_id=172&oauth2_token_id=57447761']}, {'text': 'банка или правительства контролирующего его Биткоин можно использовать', 'start': 21.1200008392334, 'end': 25.34000015258789, 'words': [{'word': 'банка', 'start': 21.1200008392334, 'end': 21.520000457763672}, {'word': 'или', 'start': 21.520000457763672, 'end': 21.760000228881836}, {'word': 'правительства', 'start': 21.760000228881836, 'end': 22.3799991607666}, {'word': 'контролирующего', 'start': 22.520000457763672, 'end': 23.15999984741211}, {'word': 'его', 'start': 23.15999984741211, 'end': 23.459999084472656}, {'word': 'Биткоин', 'start': 24.079999923706055, 'end': 24.5}, {'word': 'можно', 'start': 24.5, 'end': 24.780000686645508}, {'word': 'использовать', 'start': 24.780000686645508, 'end': 25.34000015258789}], 'stock_candidates': ['https://player.vimeo.com/external/539033394.hd.mp4?s=4a924ed8ab86e02f62f2458f134d2374ee6b6907&profile_id=172&oauth2_token_id=57447761']}, {'text': 'для покупки товаров и услуг а также для инвестирования', 'start': 25.34000015258789, 'end': 28.760000228881836, 'words': [{'word': 'для', 'start': 25.34000015258789, 'end': 25.540000915527344}, {'word': 'покупки', 'start': 25.540000915527344, 'end': 26.0}, {'word': 'товаров', 'start': 26.0, 'end': 26.360000610351562}, {'word': 'и', 'start': 26.360000610351562, 'end': 26.559999465942383}, {'word': 'услуг', 'start': 26.559999465942383, 'end': 26.899999618530273}, {'word': 'а', 'start': 26.899999618530273, 'end': 27.440000534057617}, {'word': 'также', 'start': 27.440000534057617, 'end': 27.719999313354492}, {'word': 'для', 'start': 27.719999313354492, 'end': 28.0}, {'word': 'инвестирования', 'start': 28.0, 'end': 28.760000228881836}], 'stock_candidates': ['https://player.vimeo.com/external/437865346.hd.mp4?s=e5fb763e9a751b8d8cc8922fa06c60df40933242&profile_id=172&oauth2_token_id=57447761']}, {'text': 'и торговли на криптовалютных биржах Он также стал объектом', 'start': 28.760000228881836, 'end': 32.63999938964844, 'words': [{'word': 'и', 'start': 28.760000228881836, 'end': 29.020000457763672}, {'word': 'торговли', 'start': 29.020000457763672, 'end': 29.5}, {'word': 'на', 'start': 29.5, 'end': 29.780000686645508}, {'word': 'криптовалютных', 'start': 29.780000686645508, 'end': 30.440000534057617}, {'word': 'биржах', 'start': 30.440000534057617, 'end': 30.780000686645508}, {'word': 'Он', 'start': 31.639999389648438, 'end': 31.639999389648438}, {'word': 'также', 'start': 31.639999389648438, 'end': 31.979999542236328}, {'word': 'стал', 'start': 31.979999542236328, 'end': 32.13999938964844}, {'word': 'объектом', 'start': 32.13999938964844, 'end': 32.63999938964844}], 'stock_candidates': ['https://player.vimeo.com/external/488253991.hd.mp4?s=aa71c302ee0a166ac0eb78ab31baecabcff738da&profile_id=175&oauth2_token_id=57447761', 'https://player.vimeo.com/external/539033394.hd.mp4?s=4a924ed8ab86e02f62f2458f134d2374ee6b6907&profile_id=172&oauth2_token_id=57447761']}, {'text': 'интереса для инвесторов и его цена может значительно колебаться', 'start': 32.63999938964844, 'end': 36.279998779296875, 'words': [{'word': 'интереса', 'start': 32.63999938964844, 'end': 33.099998474121094}, {'word': 'для', 'start': 33.099998474121094, 'end': 33.279998779296875}, {'word': 'инвесторов', 'start': 33.279998779296875, 'end': 33.7400016784668}, {'word': 'и', 'start': 34.2599983215332, 'end': 34.41999816894531}, {'word': 'его', 'start': 34.41999816894531, 'end': 34.560001373291016}, {'word': 'цена', 'start': 34.560001373291016, 'end': 34.79999923706055}, {'word': 'может', 'start': 34.79999923706055, 'end': 35.13999938964844}, {'word': 'значительно', 'start': 35.13999938964844, 'end': 35.68000030517578}, {'word': 'колебаться', 'start': 35.68000030517578, 'end': 36.279998779296875}], 'stock_candidates': ['https://player.vimeo.com/external/438101362.hd.mp4?s=306221fbde6efcc163c3510ce1b746c50298b17c&profile_id=172&oauth2_token_id=57447761']}, {'text': 'В целом биткоин представляет собой новую форму децентрализованной', 'start': 37.02000045776367, 'end': 40.560001373291016, 'words': [{'word': 'В', 'start': 37.02000045776367, 'end': 37.060001373291016}, {'word': 'целом', 'start': 37.060001373291016, 'end': 37.380001068115234}, {'word': 'биткоин', 'start': 37.560001373291016, 'end': 37.79999923706055}, {'word': 'представляет', 'start': 37.79999923706055, 'end': 38.36000061035156}, {'word': 'собой', 'start': 38.36000061035156, 'end': 38.63999938964844}, {'word': 'новую', 'start': 38.63999938964844, 'end': 39.13999938964844}, {'word': 'форму', 'start': 39.13999938964844, 'end': 39.560001373291016}, {'word': 'децентрализованной', 'start': 39.560001373291016, 'end': 40.560001373291016}], 'stock_candidates': ['https://player.vimeo.com/external/539033394.hd.mp4?s=4a924ed8ab86e02f62f2458f134d2374ee6b6907&profile_id=172&oauth2_token_id=57447761']}, {'text': 'и цифровой валюты которая имеет потенциал изменить финансовую', 'start': 40.560001373291016, 'end': 44.41999816894531, 'words': [{'word': 'и', 'start': 40.560001373291016, 'end': 40.7400016784668}, {'word': 'цифровой', 'start': 40.7400016784668, 'end': 41.13999938964844}, {'word': 'валюты', 'start': 41.13999938964844, 'end': 41.619998931884766}, {'word': 'которая', 'start': 42.040000915527344, 'end': 42.31999969482422}, {'word': 'имеет', 'start': 42.31999969482422, 'end': 42.63999938964844}, {'word': 'потенциал', 'start': 42.63999938964844, 'end': 43.29999923706055}, {'word': 'изменить', 'start': 43.29999923706055, 'end': 43.779998779296875}, {'word': 'финансовую', 'start': 43.779998779296875, 'end': 44.41999816894531}], 'stock_candidates': ['https://player.vimeo.com/external/539033394.hd.mp4?s=4a924ed8ab86e02f62f2458f134d2374ee6b6907&profile_id=172&oauth2_token_id=57447761']}, {'text': 'систему', 'start': 44.41999816894531, 'end': 44.79999923706055, 'words': [{'word': 'систему', 'start': 44.41999816894531, 'end': 44.79999923706055}], 'stock_candidates': ['https://player.vimeo.com/external/538256299.hd.mp4?s=ecb416a05baf4819268621b4c2252334a2fc3486&profile_id=172&oauth2_token_id=57447761']}]

    editor.burn_subtitles(
        audio_path=mp3_filename,
        subtitles_lines=subtitles_lines,
        output_path=f'narrate_{id}.mp4',
    )

    print('Done')



if __name__ == "__main__":
    asyncio.run(main())
