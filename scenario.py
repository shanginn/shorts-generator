import dataclasses
import logging

from Openai import SystemMessage, AssistantMessage, OpenAIChat, ModelConfig, UserMessage
from result import Err, Ok, Result
import json5

from dataobjects import Scenario

logging.basicConfig(
    format="(%(asctime)s) %(name)s:%(lineno)d [%(levelname)s] | %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class Writer:
    scenario_system_message = '''
Prompt:
You will be generating an essay scenario in Russian (with keywords in english) 
about a given subject for a 1-minute long video.
The output should be in JSON format, with the essay split into logical text blocks. Each text block
should have a corresponding list of keywords to search for relevant stock footage.

The subject of the essay is:
<subject>
{SUBJECT}
</subject>

Here are the steps to follow:
1. Write the full scenario  IN RUSSIAN in the `full_scenario` field, in Russian. This should be the complete essay. 
Aim for a total essay length of approximately 150-200 words.

2. Chop the `full_scenario` into logical text blocks. Each text block should be as plain text without any markup.
Around 5-10 words each.

3. For each text block, generate a list of 3-5 keywords or phrases IN ENGLISH that capture the main ideas and
could be used to search for relevant stock footage. Include these keyword lists under .keywords json key
right near the text block. English only

4. Combine all the text blocks and their keyword lists into a single JSON object, with the following
structure:
<json_structure>
{
"full_scenario": "Полный сценарий на русском языке...",
"text_blocks": [
{
"text": "Кусок текста на русском языке. ",
"keywords": ["english keyword1", "second keyword", "keyword3"]
},
{
"text": "Второй кусок текста. Может быть другой длинны. ",
"keywords": ["keyword4", "keyword5", "keyword6"]
},
...
]
}
</json_structure>

Please generate the complete essay scenario in Russian, following the specified format and
instructions. Ensure the output is well-structured, concise, and appropriate for a 1-minute video on
the given subject.
'''

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
        subject: str,
    ) -> Result[Scenario, Exception]:
        messages = [
            SystemMessage(self.scenario_system_message.replace('{SUBJECT}', subject)),
        ]

        scenario_result = await self.gpt4_chat.completion(
            messages,
            json_mode=True
        )

        if scenario_result.is_err():
            return scenario_result

        scenario_json = scenario_result.ok().content

        try:
            scenario = json5.loads(scenario_json)
        except Exception as e:
            logging.error(f'Error parsing scenario JSON ({scenario_json}): {e}')

            return Err(e)

        try:
            return Ok(Scenario.from_dict(scenario))
        except Exception as e:
            logging.error(f'Error hydrating Scenario object ({scenario}): {e}')

            return Err(e)
