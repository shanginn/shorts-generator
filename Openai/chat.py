from dataclasses import dataclass

import json5
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from result import Result, Ok, Err
from typing import Dict, List, Optional, Callable, Any, Tuple

from termcolor import colored
from .messages import BaseMessage, AssistantMessage, Role
from .function import Function, Functions, FunctionCall
import logging
from tenacity import retry, wait_random_exponential, stop_after_attempt

@dataclass
class ModelConfig:
    temperature: float = 0.9


class OpenAIChat:
    def __init__(self, api_key: str, model: str = 'gpt-3.5-turbo', config: ModelConfig = ModelConfig()):
        if not api_key:
            raise ValueError('Open AI api key cannot be empty')

        self.client = AsyncOpenAI(
            api_key=api_key,
            max_retries=3,
        )
        self.model = model
        self.config = config
        self.logger = logging.getLogger(__name__)

    async def completion(
        self,
        messages: List[BaseMessage],
        functions: Optional[Functions] = None,
        function_call: Optional[str] = None
    ) -> Result[BaseMessage, Exception]:
        try:
            completion = await self.completion_request(
                [message.as_dict() for message in messages],
                functions.as_list() if functions is not None else None,
                {'name': function_call} if function_call is not None else None
            )
        except Exception as e:
            self.logger.error(f'Error requesting completion: {e}')
            return Err(e)

        try:
            message: ChatCompletionMessage = completion.choices[0].message
        except Exception as e:
            self.logger.error(f'Error fetching message: {e}')
            return Err(e)

        if message.role == "assistant":
            function_call = None
            function_call_data = message.function_call

            if function_call_data is not None:
                arguments = function_call_data.arguments
                parsed_arguments = None

                if arguments is not None:
                    try:
                        parsed_arguments = json5.loads(arguments)
                    except ValueError as json_error:
                        self.logger.error(json_error)

                function_call = FunctionCall(
                    function_call_data.name,
                    arguments,
                    parsed_arguments
                )
            return Ok(AssistantMessage(
                message.content,
                function_call=function_call,
            ))
        else:
            return Ok(BaseMessage(
                message.content,
                role=Role(message.role),
            ))

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    async def completion_request(self, messages, functions=None, function_call=None) -> ChatCompletion:
        return await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.config.temperature,
            functions=functions if functions else None,
            function_call=function_call if function_call else None,
        )

    @staticmethod
    def pretty_print_conversation(messages):
        role_to_color = {
            "system": "red",
            "user": "green",
            "assistant": "blue",
            "function": "magenta",
        }

        formatted_messages = []

        for message in messages:
            if message["role"] == "system":
                formatted_messages.append(f"system: {message['content']}\n")
            elif message["role"] == "user":
                formatted_messages.append(f"user: {message['content']}\n")
            elif message["role"] == "assistant" and message.get("function_call"):
                formatted_messages.append(f"assistant: {message['function_call']}\n")
            elif message["role"] == "assistant" and not message.get("function_call"):
                formatted_messages.append(f"assistant: {message['content']}\n")
            elif message["role"] == "function":
                formatted_messages.append(f"function ({message['name']}): {message['content']}\n")
        for formatted_message in formatted_messages:
            print(
                colored(
                    formatted_message,
                    role_to_color[messages[formatted_messages.index(formatted_message)]["role"]],
                )
            )


@dataclass
class FunctionCaller:
    function: Function
    chat: OpenAIChat
    messages: List[BaseMessage]

    async def call(self) -> Result[Tuple[bool, Any], Exception]:
        response = await self.chat.completion(
            self.messages,
            Functions({self.function.name: self.function}),
            self.function.name
        )

        if isinstance(response, Err):
            return response

        response = response.ok()

        if not isinstance(response, AssistantMessage):
            return Ok((False, response))

        needed_function_call = response.function_call and response.function_call.name == self.function.name

        if not needed_function_call or not self.function.handler:
            return Ok((False, response))

        try:
            handler_response = self.function.handler(
                **response.function_call.parsed_arguments
            )

            return Ok((True, handler_response))
        except Exception as e:
            return Err(e)
