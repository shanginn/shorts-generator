import json
import moviepy.editor as mp
from moviepy.video.VideoClip import TextClip, ColorClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

class Editor:
    def burn_subtitles(self, audio_path: str, subtitles_path: str, output_path: str):
        # Load the subtitles from the JSON file
        with open(subtitles_path, 'r') as f:
            subtitles = json.load(f)

        # Split the text into lines
        subtitles = self.split_text_into_lines(subtitles)

        # Create the video with subtitles
        frame_size = (1080, 1920)
        all_line_level_splits = []

        for line in subtitles:
            out = self.create_caption(line, frame_size)
            all_line_level_splits.extend(out)

        # Load the input audio
        input_audio = mp.AudioFileClip(audio_path)

        # Get the duration of the input audio
        input_audio_duration = input_audio.duration

        # Create a black background clip with the given frame size and duration
        background_clip = ColorClip(size=frame_size, color=(0, 0, 0)).set_duration(input_audio_duration)

        # Combine the background clip and subtitles
        final_video = CompositeVideoClip([background_clip] + all_line_level_splits)

        # Set the audio of the final video to be the same as the input audio
        final_video = final_video.set_audio(input_audio)

        # Save the final video
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

    def split_text_into_lines(self, data):
        max_chars = 80
        max_duration = 3.0
        max_gap = 1.5

        subtitles = []
        line = []
        line_duration = 0

        for idx, word_data in enumerate(data):
            word = word_data["word"]
            start = word_data["start"]
            end = word_data["end"]

            line.append(word_data)
            line_duration += end - start

            temp = " ".join(item["word"] for item in line)
            new_line_chars = len(temp)

            duration_exceeded = line_duration > max_duration
            chars_exceeded = new_line_chars > max_chars
            maxgap_exceeded = (idx > 0) and (start - data[idx - 1]['end'] > max_gap)

            if duration_exceeded or chars_exceeded or maxgap_exceeded:
                if line:
                    subtitle_line = {
                        "line": " ".join(item["word"] for item in line),
                        "start": line[0]["start"],
                        "end": line[-1]["end"],
                        "words": line
                    }
                    subtitles.append(subtitle_line)
                    line = []
                    line_duration = 0

        if line:
            subtitle_line = {
                "line": " ".join(item["word"] for item in line),
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
            word_clip = (
                TextClip(word_json['word'] + ' ', font=font, fontsize=fontsize, color=color)
                     .set_start(text_json['start'])
                     .set_duration(full_duration)
             )
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
            word_clip_highlight = (
                TextClip(highlight_word['word'], font=font, fontsize=fontsize, color=color, bg_color=bgcolor)
                   .set_start(highlight_word['start'])
                   .set_duration(highlight_word['duration'])
            )
            word_clip_highlight = word_clip_highlight.set_position((highlight_word['x_pos'], highlight_word['y_pos']))
            word_clips.append(word_clip_highlight)

        return word_clips
