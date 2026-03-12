import re
from typing import Any, Protocol, TypedDict
from src.llm_sdk.llm_sdk import Small_LLM_Model

from src.predict import JSONPredict
from src.validator import FunctionsDefinitionValidator, ParametersValidator


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
        if not (len(allowed_logits)):
            return model.decode([data["logits"].index(max(data["logits"]))])
        best_token = max(
            allowed_logits, key=lambda token: data["logits"][token]
        )
        return model.decode([best_token])


class NameAndDescriptionStage:
    def process(
        self,
        prompt: str,
        model: Small_LLM_Model,
        functions: list[FunctionsDefinitionValidator],
    ) -> str:
        from src.generation import generate_response

        functions_help = ""
        for func in functions:
            functions_help += (
                f"- Name: {func.function_name}\n  "
                "Description: {func.description}\n"
            )

        sys_prompt = (
            "You are a function classifier. "
            "Your task is to select the ONLY correct function "
            "from the list below that matches the user's intent.\n\n"
            "### AVAILABLE FUNCTIONS:\n"
            f"{functions_help}\n"
            "--- RULES ---\n"
            "1. Analyze the user prompt carefully.\n"
            "2. Compare it with the 'Description' of each function.\n"
            "3. Return ONLY the JSON with the exact function name.\n"
            "4. If multiple functions seem similar, "
            "pick the most specific one for regex/substitution."
        )
        predict = JSONPredict(
            [
                "name",
            ],
            [func.function_name for func in functions],
            model,
        )
        res = generate_response(sys_prompt, prompt, predict, model)
        return res


class ParameterStage:
    def process(
        self,
        prompt: str,
        model: Small_LLM_Model,
        function_name: str,
        description: str,
        parameters: list[ParametersValidator],
    ) -> str:
        from src.generation import generate_response

        parameters_dict = {
            parameter.name: parameter.type for parameter in parameters
        }
        sys_prompt = (
            f"You are a strict text extraction engine. "
            f"Function: {function_name}. Parameters: {parameters_dict}. \n"
            "--- MANDATORY RULES ---\n"
            "1. COPY PASTE ONLY: Extract values EXACTLY as "
            "they appear. If lowercase, keep lowercase.\n"
            "2. NO FORMATTING: Never use double asterisks (**)."
            " Use only '*' if needed.\n"
            "3. NO CORRECTIONS: Do not fix spelling or capitalization.\n\n"
            "--- EXAMPLES ---\n"
            "Prompt: 'replace the word cat'\n"
            'JSON: {"regex": "\\\\bcat\\\\b"}\n'
            "Prompt: 'invite alex to the party'\n"
            'JSON: {"name": "alex"}\n'
            "Prompt: 'use an asterisk here'\n"
            'JSON: {"symbol": "*"}\n'
            "--- END OF EXAMPLES ---\n"
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
        predict = JSONPredict(list(parameters_dict.keys()), [], model, True)

        res = generate_response(sys_prompt, prompt + "\n", predict, model)
        return res


# class StepsManager
