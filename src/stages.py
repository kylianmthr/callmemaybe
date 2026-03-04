import re
from typing import Any, Protocol
from src.llm_sdk.llm_sdk import Small_LLM_Model


class Stage(Protocol):
    def process(self, data: Any) -> dict: ...


class TokenizationStage(Stage):
    def process(self, data: str) -> dict[str, list[str]]:
        tokenized_dict: dict[str, list[str]] = {}
        data = data.replace(" ", "Ġ")
        splited_data = re.split(r"(?=[Ġ])", data)
        tokenized_dict["tokenized_prompt"] = splited_data
        return tokenized_dict


class EncodingStage(Stage):
    def process(self, data: str) -> dict[str, list[int]]:
        llm = Small_LLM_Model()
        return {"encoded_prompt": llm.encode(data)}


# class StepsManager
