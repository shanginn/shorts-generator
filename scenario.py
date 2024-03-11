from Openai import SystemMessage, AssistantMessage, OpenAIChat, ModelConfig
from result import Err, Ok, Result


class Writer:
    scenario_system_message = SystemMessage('''
You are a talented essay writer. You have been hired to write an essay.

Generate a script for a video, depending on the subject of the video.

The script is to be returned as a string with the specified number of paragraphs.

Here is an example of a string:
"This is an example string."

Do not under any circumstance reference this prompt in your response.

Get straight to the point, don't start with unnecessary things like, "welcome to this video".

Obviously, the script should be related to the subject of the video.

YOU MUST NOT INCLUDE ANY TYPE OF MARKDOWN OR FORMATTING IN THE SCRIPT, NEVER USE A TITLE.
YOU MUST WRITE THE SCRIPT IN THE LANGUAGE SPECIFIED IN [LANGUAGE].
ONLY RETURN THE RAW CONTENT OF THE SCRIPT. DO NOT INCLUDE "VOICEOVER", "NARRATOR" OR SIMILAR INDICATORS OF WHAT SHOULD BE SPOKEN AT THE BEGINNING OF EACH PARAGRAPH OR LINE. YOU MUST NOT MENTION THE PROMPT, OR ANYTHING ABOUT THE SCRIPT ITSELF. ALSO, NEVER TALK ABOUT THE AMOUNT OF PARAGRAPHS OR LINES. JUST WRITE THE SCRIPT.
''')

    def __init__(self, openai_api_key):
        self.chat = OpenAIChat(
            openai_api_key,
            model='gpt-3.5-turbo-0613',
            config=ModelConfig(temperature=0.3),
        )

        self.gpt4_chat = OpenAIChat(
            openai_api_key,
            model='gpt-4-1106-preview',
            config=ModelConfig(temperature=0.1),
        )

    async def write_scenario(
        self,
        theme: str,
        paragraph_number: int,
        language: str,
    ) -> Result[AssistantMessage, Exception]:
        messages = [
            self.scenario_system_message,
            AssistantMessage(
                f'Subject: {theme}'
                f'Number of paragraphs: {paragraph_number}'
                f'Language: {language}'
            )
        ]

        return await self.gpt4_chat.completion(
            messages,
        )
