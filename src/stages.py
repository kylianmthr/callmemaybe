import re
from typing import Any, Protocol, TypedDict
from src.llm_sdk.llm_sdk import Small_LLM_Model

from src.predict import JSONPredict
from src.validator import ParametersValidator


class Stage(Protocol):
    def process(self, data: Any, model: Small_LLM_Model) -> Any: ...


class TokenizationStage:
    def process(self, data: str) -> dict[str, list[str]]:
        tokenized_dict: dict[str, list[str]] = {}
        splited_data = re.split(r"(?=[_])", data)
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
        logits_dict: LogitsDict = {
            "logits": model.get_logits_from_input_ids(data["encoded_prompt"])
        }
        return logits_dict


class DecodeStage:
    def process(
        self,
        data: LogitsDict,
        model: Small_LLM_Model,
        allowed_logits: list[int],
    ) -> str:
        data_with_allowed_logits = []
        for token in allowed_logits:
            data_with_allowed_logits.append(data["logits"][token])
        if not (len(allowed_logits)):
            return model.decode([data["logits"].index(max(data["logits"]))])
        return model.decode(
            [data["logits"].index(max(data_with_allowed_logits))]
        )


class NameAndDescriptionStage:
    def process(
        self, prompt: str, model: Small_LLM_Model, functions_name: list[str]
    ) -> str:
        from src.generation import generate_response

        sys_prompt = (
            "You must generate a JSON response with this format:"
            "{"
            '"name": "function name",'
            "}"
            "So you have this keys:"
            '"name" (function name, You can choose from these functions:'
            f"{functions_name}"
        )
        predict = JSONPredict(
            [
                "name",
            ],
            functions_name,
        )
        res = generate_response(sys_prompt, prompt, predict, model)
        return res


class ParameterStage:
    def process(
        self,
        prompt: str,
        model: Small_LLM_Model,
        function_name: str,
        parameters: list[ParametersValidator],
    ) -> str:
        from src.generation import generate_response

        parameters_dict = {
            parameter.name: parameter.type for parameter in parameters
        }
        sys_prompt = (
            f"You must generate a JSON response with this format: "
            f'{{"parameter name": "what can match this parameter in the '
            'sentence", ...}. '
            f"Function: {function_name}. "
            f"Parameters to type: {parameters_dict}. "
            "CRITICAL: A Regex is a TEXTUAL pattern. Its data type is ALWAYS a"
            " 'string'. "
            "If you see the word NUMBERS, it doesn't mean that you have to "
            "replace it with real number. NUMBERS is simply the word NUMBERS "
            "(in the regex context)"
            "If you see the word asterisks, it mean '*'. "
        )
        # allowed_regex = []
        if function_name == "fn_substitute_string_with_regex":
            # allowed_regex = [r"\\d+", r"[aeiouAEIOU]", r"\\bcat\\b"]
            sys_prompt += (
                "You can choose between this regex: "
                r"- \\d+ to replace numbers "
                r"- [aeiouAEIOU] to replace vowels "
                "- \\\\bcat\\\\b to replace the word cat.\n"
            )
        predict = JSONPredict(list(parameters_dict.keys()), [], True)

        res = generate_response(sys_prompt, prompt + ".\n", predict, model)
        return res


# class StepsManager
