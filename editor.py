import json
import logging
import os
import random
import uuid
from decimal import Decimal

from tenacity import retry, stop_after_attempt, wait_fixed, wait_incrementing

import moviepy.editor as mp
from moviepy.audio.fx.volumex import volumex
from moviepy.video.VideoClip import TextClip, ColorClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
import requests
from typing import List

from moviepy.video.fx.crop import crop
from termcolor import colored

from Openai import SystemMessage, OpenAIChat, ModelConfig, AssistantMessage
from dataobjects import Scenario, TextLine, TranscriptionWord, ScenarioTextBlock


class Editor:
    used_videos = {}
    files_folder = 'stock_videos'

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
    def download_video(self, url, video_path):
        response = requests.get(url)
        if response.status_code == 200:
            with open(video_path, "wb") as file:
                file.write(response.content)
        else:
            raise Exception(f"Failed to download video from {url}")

    def download_and_trim_video(self, stock_video: dict, duration: float, target_dimensions: tuple[int, int]) -> str:
        url = stock_video['url']
        video_id = stock_video['id']

        video_extension = url.split('.')[-1].split('?')[0]
        video_filename = f'{video_id}.{video_extension}'
        video_path = f'{self.files_folder}/{video_filename}'

        trimmed_path = f'{self.files_folder}/trimmed_{duration}_{video_filename}'

        if os.path.exists(trimmed_path):
            return trimmed_path

        if not os.path.exists(video_path):
            self.download_video(url, video_path)

        # Load the video
        video_clip = mp.VideoFileClip(video_path)

        # Adjust start_time and end_time to be within the video's duration
        video_duration = video_clip.duration
        start_time = 0
        end_time = min(duration, video_duration)

        trimmed_filename = f'trimmed_{end_time}_{video_filename}'
        trimmed_path = f'{self.files_folder}/{trimmed_filename}'

        if os.path.exists(trimmed_path):
            return trimmed_path

        # Load and trim the video
        video_clip = (
            mp.VideoFileClip(video_path)
            .subclip(start_time, end_time)
            .resize(newsize=target_dimensions)
        )

        # Resize and crop the video to the target dimensions
        video_clip = crop(video_clip, width=target_dimensions[0], height=target_dimensions[1],
                          x_center=video_clip.w / 2, y_center=video_clip.h / 2)

        # Save the trimmed video
        video_clip.write_videofile(trimmed_path, codec="libx264")

        return trimmed_path

    def select_stock_video(self, block: ScenarioTextBlock) -> dict:
        shuffled_ids = list(block.stock_video_urls.keys())
        random.shuffle(shuffled_ids)

        for video_id in shuffled_ids:
            if video_id not in self.used_videos:
                self.used_videos[video_id] = True

                return {'id': video_id, 'url': block.stock_video_urls[video_id]}

        # if no new video is available, select a random video
        random_id = random.choice(shuffled_ids)
        return {'id': random_id, 'url': block.stock_video_urls[random_id]}

    def get_subtitles_clips(self, scenario: Scenario) -> List[TextClip]:
        frame_size = (1080, 1920)
        captions = []

        for i, line in enumerate(scenario.lines):
            captions.extend(self.create_caption(line, frame_size))

        return captions

    def get_stock_video_clips(self, scenario: Scenario) -> List[mp.VideoClip]:
        stock_clips = []

        start_time = 0
        for i, block in enumerate(scenario.text_blocks):
            stock_video = self.select_stock_video(block)
            next_block_start_time = None
            if i + 1 < len(scenario.text_blocks):
                next_block_start_time = scenario.text_blocks[i + 1].start()

            if next_block_start_time is None:
                next_block_start_time = scenario.text_blocks[i].end()

            if next_block_start_time is None:
                next_block_start_time = start_time + 5


            duration = float(Decimal(next_block_start_time - start_time).quantize(Decimal('0.00')))

            if duration <= 0:
                raise Exception(f"Duration is less than 0: {duration}. {next_block_start_time, start_time}")

            trimmed_video_path = self.download_and_trim_video(
                stock_video,
                duration,
                (1080, 1920)
            )

            video_clip = (
                mp.VideoFileClip(trimmed_video_path)
                .set_start(start_time)
                .set_duration(duration)
            )

            stock_clips.append(video_clip)

            start_time = next_block_start_time

        return stock_clips

    def get_background_music(self) -> mp.AudioClip:
        # Select a random song from the 'songs' folder
        songs_folder = os.path.join(os.path.dirname(__file__), 'songs')
        song_files = [f for f in os.listdir(songs_folder) if f.endswith('.m4a') or f.endswith('.mp3')]
        random_song_path = os.path.join(songs_folder, random.choice(song_files))

        return mp.AudioFileClip(random_song_path)

    def compose_video(
        self,
        subtitles_clips: List[TextClip],
        stock_video_clips: List[mp.VideoClip],
        background_music: mp.AudioClip,
        narration_path: str,
        output_path: str
    ):
        frame_size = (1080, 1920)

        # Load the input audio (voiceover)
        input_audio = mp.AudioFileClip(narration_path)

        # Load the background music and set its volume lower than the voiceover
        background_music = volumex(background_music, 0.08)
        background_music = background_music.subclip(0, min(input_audio.duration, background_music.duration))

        # Combine the voiceover and background music
        combined_audio = mp.CompositeAudioClip([input_audio, background_music])

        # Create a black background clip with the given frame size and duration
        background_clip = ColorClip(size=frame_size, color=(0, 0, 0)).set_duration(input_audio.duration)

        # Combine the background clip and subtitles
        final_video = CompositeVideoClip([background_clip] + stock_video_clips + subtitles_clips)

        # Set the audio of the final video to be the combined audio
        final_video = final_video.set_audio(combined_audio)

        # Save the final video
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")


    @staticmethod
    def _text_line_from_words(words: List[TranscriptionWord]) -> TextLine:
        return TextLine(
            text=" ".join(item.word for item in words),
            start=words[0].start,
            end=words[-1].end,
            words=words
        )

    @staticmethod
    def split_words_into_lines(scenario: Scenario) -> Scenario:
        max_chars = 60
        max_duration = 1.5
        max_gap = 1.5

        lines = []
        line_words = []
        line_duration = 0

        for idx, word_data in enumerate(scenario.subtitles):
            start = word_data.start
            end = word_data.end

            line_words.append(word_data)
            line_duration += end - start

            temp = " ".join(item.word for item in line_words)
            new_line_chars = len(temp)

            duration_exceeded = line_duration > max_duration
            chars_exceeded = new_line_chars > max_chars
            maxgap_exceeded = (idx > 0) and (start - scenario.subtitles[idx - 1].end > max_gap)

            if duration_exceeded or chars_exceeded or maxgap_exceeded:
                if line_words:
                    lines.append(Editor._text_line_from_words(line_words))
                    line_words = []
                    line_duration = 0

        if line_words:
            lines.append(Editor._text_line_from_words(line_words))

        scenario.lines = lines

        return scenario

    def create_caption(
        self,
        text_json: TextLine,
        frame_size,
        font="Helvetica-Bold",
        fontsize=70,
        color='white',
        bgcolor='blue'
    ) -> List[TextClip]:
        full_duration = text_json.end - text_json.start

        word_clips = []
        xy_textclips_positions = []

        frame_width, frame_height = frame_size
        x_buffer = frame_width / 10
        y_buffer = frame_height / 5

        x_pos = 0
        y_pos = 600

        for index, word_json in enumerate(text_json.words):
            duration = word_json.end - word_json.start
            word_clip = TextClip(
                word_json.word + ' ',
                font=font,
                fontsize=fontsize,
                bg_color='black',
                color=color,
            ).set_start(text_json.start).set_duration(full_duration)
            word_width, word_height = word_clip.size

            if x_pos + word_width > frame_width - 2 * x_buffer:
                x_pos = 0
                y_pos += word_height + 20

            xy_textclips_positions.append({
                "x_pos": x_pos + x_buffer,
                "y_pos": y_pos + y_buffer,
                "width": word_width,
                "height": word_height,
                "word": word_json.word,
                "start": word_json.start,
                "end": word_json.end,
                "duration": duration
            })

            word_clip = word_clip.set_position((x_pos + x_buffer, y_pos + y_buffer))
            x_pos += word_width

            word_clips.append(word_clip)

        for highlight_word in xy_textclips_positions:
            word_clip_highlight = TextClip(
                highlight_word['word'],
                font=font,
                fontsize=fontsize,
                color=color,
                bg_color=bgcolor,
            ).set_start(highlight_word['start']).set_duration(highlight_word['duration'])

            word_clip_highlight = word_clip_highlight.set_position((highlight_word['x_pos'], highlight_word['y_pos']))
            word_clips.append(word_clip_highlight)

        return word_clips


class StockFinder:
    def __init__(self, pexels_api_key: str, openai_api_key: str):
        self.pexels_api_key = pexels_api_key

        self.openai = OpenAIChat(
            openai_api_key,
            model='gpt-3.5-turbo-0125',
            config=ModelConfig(temperature=0.3),
        )

    async def get_keywords(self, paragraph: str) -> str:
        system_message = SystemMessage(
            'You are a talented ENGLISH keywords maker. ' 
            'Given the input phrase in any language, you will generate SINGLE NOUN '
            'that will be used to find a stock footage video. '
            'No intro, no outro, just the words IN ENGLISH.'
        )

        messages = [
            system_message,
            AssistantMessage(paragraph)
        ]

        result = await self.openai.completion(
            messages,
        )

        if result.is_err():
            raise Exception(result.err())

        return result.ok().content

    @retry(stop=stop_after_attempt(5), wait=wait_incrementing(10, 10, 60))
    def search_pexels(self, query: str, per_page: int) -> dict:
        headers = {
            "Authorization": self.pexels_api_key
        }

        query_params = {
            'query': query,
            'per_page': per_page,
            'orientation': 'portrait'
        }

        response = requests.get(
            "https://api.pexels.com/videos/search",
            params=query_params,
            headers=headers,
        )

        if response.status_code != 200:
            logging.error(f"Request failed: {response.json()}")
            raise Exception(f"Request failed: {response.json()}")

        return response.json()

    async def add_stock_video_candidates(
        self,
        scenario: Scenario
    ):
        per_page = 50
        found_video_urls = {}

        for block_idx, block in enumerate(scenario.text_blocks):
            print(colored(f"Searching for videos related to: {block.keywords}. for '{block.text}'", "cyan"))
            video_urls = {}

            for keyword in block.keywords:
                response = self.search_pexels(keyword, per_page)

                if 'videos' not in response:
                    print(response)
                    print(colored(f"[-] Response error", "red"))
                    continue

                if len(response["videos"]) == 0 and len(keyword.split()) > 1:
                    print(colored(f"No videos found for '{keyword}' trying search each word", "red"))
                    for single_keyword in keyword.split():
                        print(colored(f"Searching for: {single_keyword}", "cyan"))

                        response = self.search_pexels(single_keyword, per_page)

                        if len(response["videos"]) != 0:
                            break

                if len(response["videos"]) == 0:
                    print(colored(f'\t=> "{keyword}"  no videos found. moving on', "yellow"))
                    continue

                video_res = 0
                try:
                    # loop through each video in the result
                    for video_data in response["videos"]:
                        # check if video has desired minimum duration
                        if video_data["duration"] < ((block.duration() or 5) + 0.5):
                            continue

                        raw_urls = video_data["video_files"]
                        temp_video_url = ""

                        # loop through each url to determine the best quality
                        for video in raw_urls:
                            # Check if video has a valid download link
                            if ".mp4" in video["link"]:
                                # Only save the URL with the largest resolution
                                if (video["width"] * video["height"]) > video_res:
                                    temp_video_url = video["link"]
                                    video_res = video["width"] * video["height"]

                        # add the url to the return list if it's not empty
                        if temp_video_url != "":
                            video_urls[video_data['id']] = temp_video_url
                except Exception as e:
                    print(colored(f"[-] No Videos found: {e}", "red"))

                    continue

                if len(video_urls) == 0 and block_idx - 1 in found_video_urls:
                    video_urls = found_video_urls[block_idx - 1]

                print(colored(f"\t=> \"{keyword}\" found {len(video_urls)} Videos", "cyan"))

                found_video_urls[block_idx] = video_urls
                block.stock_video_urls = video_urls
