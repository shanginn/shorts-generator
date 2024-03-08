from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional

from .function import FunctionCall


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class BaseMessage:
    content: str
    role: Role
    meta: Optional[dict] = None

    def as_dict(self):
        ret_dict = {**asdict(self), "role": self.role.value}
        return {k: v for k, v in ret_dict.items() if k != 'meta'}

    def print(self):
        print(f'{self.role.value}: {self.content}')


@dataclass
class SystemMessage(BaseMessage):
    role: Role = Role.SYSTEM


@dataclass
class UserMessage(BaseMessage):
    role: Role = Role.USER


@dataclass
class AssistantMessage(BaseMessage):
    role: Role = Role.ASSISTANT
    function_call: Optional[FunctionCall] = None

    def as_dict(self):
        return {
            'role': self.role.value,
            'content': self.content,
            **({"function_call": self.function_call.as_dict()} if self.function_call is not None else {})
        }

    def print(self):
        if not self.content and not self.function_call:
            print('assistant response is empty...')

        if self.content:
            print(f'assistant: {self.content}')

        if self.function_call:
            print(f'  Function call: {self.function_call}')

            if self.function_call.arguments:
                if self.function_call.parsed_arguments:
                    print(f'  Function call parsed arguments: {self.function_call.parsed_arguments}')
                else:
                    print(f'  Function call plain arguments: {self.function_call.arguments}')
