import sys
import typing
from enum import Enum
from functools import wraps
from inspect import signature, Parameter
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from docstring_parser import parse


@dataclass
class FunctionProperty:
    description: str
    required: bool
    type: str

    def as_dict(self):
        return {
            "type": self.type,
            "description": self.description,
        }


@dataclass
class RequiredStringProperty(FunctionProperty):
    required = True
    type = 'string'


@dataclass
class EnumProperty(FunctionProperty):
    enum: List[str]

    def as_dict(self):
        return {
            "type": self.type,
            "description": self.description,
            "enum": self.enum
        }


@dataclass
class ArrayProperty(FunctionProperty):
    type = 'array'
    item_type: str

    def as_dict(self):
        return {
            "type": self.type,
            "description": self.description,
            "items": {
                "type": self.item_type
            }
        }


@dataclass
class ArrayEnumProperty(ArrayProperty):
    enum: List[str]

    def as_dict(self):
        return {
            "type": self.type,
            "description": self.description,
            "items": {
                "type": self.item_type,
                "enum": self.enum
            }
        }

@dataclass
class Function:
    name: str
    description: str
    parameters: Optional[Dict[str, FunctionProperty]] = field(default_factory=dict)
    handler: Optional[Callable] = None

    def as_dict(self):
        return {
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": ({k: v.as_dict() for k, v in self.parameters.items()} if self.parameters else {}),
                "required": ([k for k, v in self.parameters.items() if v.required] if self.parameters else [])
            }
        }


@dataclass
class FunctionCall:
    name: str
    arguments: Optional[str] = None
    parsed_arguments: Optional[Dict[str, str]] = None

    def as_dict(self):
        return {
            "name": self.name,
            **({"arguments": self.arguments} if self.arguments is not None else {})
        }


@dataclass
class Functions:
    functions: Dict[str, Function]

    def add_function(self, name: str, function: Function) -> 'Functions':
        self.functions[name] = function

        return self

    def get_function(self, name: str):
        return self.functions.get(name)

    def as_list(self):
        return [
            {**function.as_dict(), 'name': name}
            for name, function in self.functions.items()
        ]


def openai_function(name: Optional[str] = None):
    def to_json_type(python_type: Any) -> str:
        if python_type == int:
            return 'integer'
        elif python_type == float:
            return 'number'
        elif python_type == bool:
            return 'boolean'
        elif (
                python_type == list
                or python_type == typing.List
                or typing.get_origin(python_type) == list
                or typing.get_origin(python_type) == typing.List
        ):
            return 'array'
        else:
            return 'string'

    def get_actual_type(param_type):
        origin_type = typing.get_origin(param_type)

        if origin_type is typing.Union:
            actual_type = typing.get_args(param_type)[0]
            return actual_type
        elif origin_type is list or origin_type is typing.List:
            element_type = typing.get_args(param_type)[0]
            return element_type
        return param_type

    def is_param_required(func, param_name):
        sig = signature(func)
        param = sig.parameters.get(param_name)

        if param is None:
            raise ValueError(f"No such parameter: {param_name}")

        # Check if the parameter has a default value
        has_default = param.default != Parameter.empty

        # Check if the parameter is type-hinted as typing.Optional
        param_type = param.annotation
        is_optional_type = (
                typing.get_origin(param_type) is typing.Union and
                type(None) in typing.get_args(param_type)
        )

        # A parameter is considered required if it doesn't have a default value
        # and isn't type-hinted as typing.Optional
        return not (has_default or is_optional_type)

    def wrapper(func: Callable):
        sig = signature(func)
        param_names = set(sig.parameters)

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            def _filtered_call():
                filtered_kwargs = {k: v for k, v in kwargs.items() if k in param_names}
                return func(*args, **filtered_kwargs)

            return _filtered_call()

        doc = parse(func.__doc__)
        description = doc.short_description

        parameters = {}
        for param in doc.params:
            annotation = sig.parameters[param.arg_name].annotation
            param_type = get_actual_type(annotation)
            required = is_param_required(func, param.arg_name)
            json_type = to_json_type(annotation)

            if json_type == 'array':
                item_type = to_json_type(param_type)
                if issubclass(param_type, Enum):
                    parameters[param.arg_name] = ArrayEnumProperty(
                        description=param.description,
                        item_type=item_type,
                        required=required,
                        type=json_type,
                        enum=[e.value for e in param_type]
                    )
                else:
                    parameters[param.arg_name] = ArrayProperty(
                        description=param.description,
                        item_type=item_type,
                        required=required,
                        type=json_type
                    )
            elif issubclass(param_type, Enum):
                enum_values = [e.value for e in param_type]
                base_type = to_json_type(type(enum_values[0]).__name__)
                parameters[param.arg_name] = EnumProperty(
                    description=param.description,
                    type=base_type,
                    required=required,
                    enum=enum_values
                )
            else:
                parameters[param.arg_name] = FunctionProperty(
                    description=param.description,
                    type=to_json_type(param_type),
                    required=required,
                )

        wrapped_func._function = Function(
            name=name or func.__name__,
            description=description,
            parameters=parameters,
            handler=wrapped_func
        )

        def to_function():
            return wrapped_func._function

        wrapped_func.to_function = to_function
        return wrapped_func

    return wrapper
