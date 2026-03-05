import re
from typing import Any, Protocol, TypedDict
from src.llm_sdk.llm_sdk import Small_LLM_Model
import json


class Stage(Protocol):
    def process(self, data: Any, model: Small_LLM_Model) -> Any: ...


class TokenizationStage:
    def process(self, data: str) -> dict[str, list[str]]:
        tokenized_dict: dict[str, list[str]] = {}
        data = data.replace(" ", "Ġ")
        splited_data = re.split(r"(?=[Ġ])", data)
        tokenized_dict["tokenized_prompt"] = splited_data
        return tokenized_dict


class EncodingDict(TypedDict):
    encoded_prompt: list[int]


class LogitsDict(TypedDict):
    logits: list[float]


class EncodingStage:
    def process(self, data: str, model: Small_LLM_Model) -> EncodingDict:
        encoded_dict: EncodingDict = {
            "encoded_prompt": model.encode(data).tolist()[0]
        }
        return encoded_dict


class LogitsStage:
    def process(
        self, data: EncodingDict, model: Small_LLM_Model
    ) -> LogitsDict:
        print(data["encoded_prompt"])
        logits_dict: LogitsDict = {
            "logits": model.get_logits_from_input_ids(data["encoded_prompt"])
        }
        return logits_dict


class LogitsToWordStage:
    def process(self, data: LogitsDict, model: Small_LLM_Model) -> str:
        return model.decode(data["logits"].index(max(data["logits"])))


# class StepsManager
