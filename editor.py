import json
import os
import random

import moviepy.editor as mp
from moviepy.audio.fx.volumex import volumex
from moviepy.video.VideoClip import TextClip, ColorClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
import requests
from typing import List

from moviepy.video.fx.crop import crop
from termcolor import colored

from Openai import SystemMessage, OpenAIChat, ModelConfig, AssistantMessage


class Editor:
    used_videos = {}
    files_folder = 'stock_videos'

    def download_and_trim_video(self, url, duration, target_dimensions):
        video_filename = url.split('/')[-1]
        video_filename = video_filename.split('?')[0]
        video_path = f'{self.files_folder}/{video_filename}'
        trimmed_filename = f'trimmed_{video_filename}'
        trimmed_path = f'{self.files_folder}/{trimmed_filename}'

        if os.path.exists(trimmed_path):
            return trimmed_path

        if not os.path.exists(video_path):
            # Download the video
            response = requests.get(url)

            with open(video_path, "wb") as file:
                file.write(response.content)

        # Load the video
        video_clip = mp.VideoFileClip(video_path)

        # Adjust start_time and end_time to be within the video's duration
        video_duration = video_clip.duration

        start_time = 0
        end_time = min(duration, video_duration)

        # Load and trim the video
        video_clip = (
            mp
              .VideoFileClip(video_path)
              .subclip(start_time, end_time)
        )

        # Resize and crop the video to the target dimensions
        video_clip = video_clip.resize(newsize=target_dimensions)
        video_clip = crop(video_clip, width=target_dimensions[0], height=target_dimensions[1],
                          x_center=video_clip.w / 2, y_center=video_clip.h / 2)

        # Save the trimmed video
        video_clip.write_videofile(trimmed_path, codec="libx264")

        return trimmed_path

    def select_stock_video(self, start_time, end_time, stock_candidates):
        selected_video = None
        for url in stock_candidates:
            if url not in self.used_videos or self.used_videos[url] < start_time:
                selected_video = url
                break

        if not selected_video:
            # Extend the previous video segment if possible
            for url, used_end_time in self.used_videos.items():
                if used_end_time >= start_time:
                    selected_video = url
                    self.used_videos[url] = max(used_end_time, end_time)
                    break

        if not selected_video:
            # Reuse a non-unique video
            selected_video = stock_candidates[0]

        self.used_videos[selected_video] = end_time
        return selected_video

    def burn_subtitles(self, audio_path: str, subtitles_lines, output_path: str):
        # Create the video with subtitles
        frame_size = (1080, 1920)
        all_line_level_splits = []

        for line in subtitles_lines:
            stock_video_url = self.select_stock_video(line['start'], line['end'], line['stock_candidates'])
            trimmed_video_path = self.download_and_trim_video(stock_video_url, line['end'] - line['start'], frame_size)

            video_clip = (
                mp
                .VideoFileClip(trimmed_video_path)
                .set_start(line['start'])
                .set_duration(line['end'] - line['start'])
            )
            all_line_level_splits.append(video_clip)

            # Create captions
            captions = self.create_caption(line, frame_size)
            all_line_level_splits.extend(captions)

        # Load the input audio (voiceover)
        input_audio = mp.AudioFileClip(audio_path)

        # Select a random song from the 'songs' folder
        songs_folder = os.path.join(os.path.dirname(__file__), 'songs')
        song_files = [f for f in os.listdir(songs_folder) if f.endswith('.m4a') or f.endswith('.mp3')]
        random_song_path = os.path.join(songs_folder, random.choice(song_files))

        # Load the background music and set its volume lower than the voiceover
        background_music = volumex(mp.AudioFileClip(random_song_path), 0.1)
        background_music = background_music.subclip(0, min(input_audio.duration, background_music.duration))

        # Combine the voiceover and background music
        combined_audio = mp.CompositeAudioClip([input_audio, background_music])

        # Get the duration of the input audio
        input_audio_duration = input_audio.duration

        # Create a black background clip with the given frame size and duration
        background_clip = ColorClip(size=frame_size, color=(0, 0, 0)).set_duration(input_audio_duration)

        # Combine the background clip and subtitles
        final_video = CompositeVideoClip([background_clip] + all_line_level_splits)

        # Set the audio of the final video to be the combined audio
        final_video = final_video.set_audio(combined_audio)

        # Save the final video
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

    def split_words_into_lines(self, subtitles_json: list[dict]):
        max_chars = 80
        max_duration = 3.0
        max_gap = 1.5

        subtitles = []
        line = []
        line_duration = 0

        for idx, word_data in enumerate(subtitles_json):
            word = word_data["word"]
            start = word_data["start"]
            end = word_data["end"]

            line.append(word_data)
            line_duration += end - start

            temp = " ".join(item["word"] for item in line)
            new_line_chars = len(temp)

            duration_exceeded = line_duration > max_duration
            chars_exceeded = new_line_chars > max_chars
            maxgap_exceeded = (idx > 0) and (start - subtitles_json[idx - 1]['end'] > max_gap)

            if duration_exceeded or chars_exceeded or maxgap_exceeded:
                if line:
                    subtitle_line = {
                        "text": " ".join(item["word"] for item in line),
                        "start": line[0]["start"],
                        "end": line[-1]["end"],
                        "words": line
                    }
                    subtitles.append(subtitle_line)
                    line = []
                    line_duration = 0

        if line:
            subtitle_line = {
                "text": " ".join(item["word"] for item in line),
                "start": line[0]["start"],
                "end": line[-1]["end"],
                "words": line
            }
            subtitles.append(subtitle_line)

        return subtitles

    def create_caption(self, text_json, frame_size, font="Helvetica-Bold", fontsize=70, color='white', bgcolor='blue'):
        full_duration = text_json['end'] - text_json['start']

        word_clips = []
        xy_textclips_positions = []

        frame_width, frame_height = frame_size
        x_buffer = frame_width / 10
        y_buffer = frame_height / 5

        x_pos = 0
        y_pos = 600

        for index, word_json in enumerate(text_json['words']):
            duration = word_json['end'] - word_json['start']
            word_clip = TextClip(
                word_json['word'] + ' ',
                font=font,
                fontsize=fontsize,
                bg_color='black',
                color=color,
            ).set_start(text_json['start']).set_duration(full_duration)
            word_width, word_height = word_clip.size

            if x_pos + word_width > frame_width - 2 * x_buffer:
                x_pos = 0
                y_pos += word_height + 20

            xy_textclips_positions.append({
                "x_pos": x_pos + x_buffer,
                "y_pos": y_pos + y_buffer,
                "width": word_width,
                "height": word_height,
                "word": word_json['word'],
                "start": word_json['start'],
                "end": word_json['end'],
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
            'Given the input phrase in any language, you will generate very short (1 to 3 ENGLISH words) '
            'sentence that will be used to find a stock footage video. '
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

    def search_pexels(self, query: str, per_page: int) -> dict:
        headers = {
            "Authorization": self.pexels_api_key
        }

        query_params = {
            'query': query,
            'per_page': per_page,
            'orientation': 'portrait'
        }

        return requests.get(
            "https://api.pexels.com/videos/search",
            params=query_params,
            headers=headers
        ).json()

    async def search_for_stock_videos(
        self,
        paragraph: str,
        min_dur: int
    ) -> List[str]:
        per_page = 10

        keywords = await self.get_keywords(paragraph)

        print(colored(f"Searching for videos related to: {keywords}. for '{paragraph}'", "cyan"))

        response = self.search_pexels(keywords, per_page)

        raw_urls = []
        video_url = []
        video_res = 0
        try:
            # loop through each video in the result
            for i in range(per_page):
                # check if video has desired minimum duration
                if response["videos"][i]["duration"] < min_dur:
                    continue
                raw_urls = response["videos"][i]["video_files"]
                temp_video_url = ""

                # loop through each url to determine the best quality
                for video in raw_urls:
                    # Check if video has a valid download link
                    if ".com/external" in video["link"]:
                        # Only save the URL with the largest resolution
                        if (video["width"] * video["height"]) > video_res:
                            temp_video_url = video["link"]
                            video_res = video["width"] * video["height"]

                # add the url to the return list if it's not empty
                if temp_video_url != "":
                    video_url.append(temp_video_url)

        except Exception as e:
            print(colored("[-] No Videos found.", "red"))
            print(colored(e, "red"))

        # Let user know
        print(colored(f"\t=> \"{keywords}\" found {len(video_url)} Videos", "cyan"))

        # Return the video url
        return video_url
