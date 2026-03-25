from typing import TypedDict
from llm_sdk.llm_sdk import Small_LLM_Model
from src.predict import JSONPredict
from src.validator import FunctionsDefinitionValidator, ParametersValidator


# class TokenizationStage:
#    def process(self, data: str) -> dict[str, list[str]]:
#        tokenized_dict: dict[str, list[str]] = {}
#        splited_data = re.split(r"(?=[_])", data)
#        tokenized_dict["tokenized_prompt"] = splited_data
#        return tokenized_dict


class EncodingDict(TypedDict):
    """
    A TypedDict representing the encoding result of a prompt.

    Attributes:
        encoded_prompt (list[int]): The prompt after being encoded as a list
            of integers.
    """

    encoded_prompt: list[int]


class LogitsDict(TypedDict):
    """
    A TypedDict representing a dictionary with a single key 'logits' that maps
    to a list of floats.

    Attributes:
        logits (list[float]): The list of floating-point values representing
            logits.
    """

    logits: list[float]


class EncodingStage:
    """
    EncodingStage is responsible for encoding input data using a provided
    language model.

    Methods:
        process(data: str, model: Small_LLM_Model) -> EncodingDict:
            Encodes the input string using the specified language model and
            returns the encoded result.

    Args:
        data (str): The input string to be encoded.
        model (Small_LLM_Model): The language model used for encoding.

    Returns:
        EncodingDict: A dictionary containing the encoded prompt as a list of
        token IDs.
    """

    def process(self, data: str, model: Small_LLM_Model) -> EncodingDict:
        encoded_dict: EncodingDict = {
            "encoded_prompt": model.encode(data).tolist()[0]
        }
        return encoded_dict


class LogitsStage:
    """
    Stage that computes logits from encoded input prompts using a
    language model.

    Methods:
        process(data: EncodingDict, model: Small_LLM_Model) -> LogitsDict:
            Computes the logits for the given encoded prompt using the
            provided model.

    Args:
        data (EncodingDict): A dictionary containing the encoded prompt under
            the key "encoded_prompt".
        model (Small_LLM_Model): The language model used to compute logits.

    Returns:
        LogitsDict: A dictionary containing the computed logits under the
            key "logits".
    """

    def process(
        self, data: EncodingDict, model: Small_LLM_Model
    ) -> LogitsDict:
        logits_dict: LogitsDict = {
            "logits": model.get_logits_from_input_ids(data["encoded_prompt"])
        }
        return logits_dict


class DecodeStage:
    """
    DecodeStage is responsible for selecting and decoding the most probable
    token from a set of logits, optionally constrained by a list of allowed
    token indices.
    """

    def process(
        self,
        data: LogitsDict,
        model: Small_LLM_Model,
        allowed_logits: list[int],
    ) -> str:
        """
        Processes the given logits data to select and decode the best token.

        Args:
            data (LogitsDict): A dictionary containing logits, typically with
                a "logits" key mapping to a list of scores.
            model (Small_LLM_Model): The language model used to decode token
                indices into strings.
            allowed_logits (list[int]): A list of token indices that are
                allowed for selection.

        Returns:
            str: The decoded string corresponding to the selected token.

        Notes:
            - If allowed_logits is empty, selects the token with the maximum
                logit from all available logits.
            - Otherwise, selects the token with the highest logit among the
                allowed_logits.
        """
        if not (len(allowed_logits)):
            return model.decode([data["logits"].index(max(data["logits"]))])
        best_token = max(
            allowed_logits, key=lambda token: data["logits"][token]
        )
        return model.decode([best_token])


class NameAndDescriptionStage:
    """
    NameAndDescriptionStage is responsible for selecting the most appropriate
    function from a list of available functions based on a user's prompt.
    It analyzes the user's intent, compares it with the descriptions of each
    function, and returns the name of the function that best matches the
    intent. This class is typically used in scenarios where automated function
    selection is required, such as in conversational AI or function routing
    systems.
    """

    def process(
        self,
        prompt: str,
        model: Small_LLM_Model,
        functions: list[FunctionsDefinitionValidator],
    ) -> str:
        """
        Classifies a user prompt by selecting the most appropriate function
        from a provided list based on their descriptions.

        Args:
            prompt (str): The user's input prompt describing the intended
                action.
            model (Small_LLM_Model): The language model used for generating
                the classification response.
            functions (list[FunctionsDefinitionValidator]): A list of function
                definitions, each containing a name and description.

        Returns:
            str: A JSON string containing the name of the selected function
            that best matches the user's intent.

        Raises:
            Any exceptions raised by the underlying `generate_response`
            or model prediction logic.

        Notes:
            - The function constructs a system prompt to guide the model in
                selecting the correct function.
            - Only the function name in JSON format is expected as output.
            - If multiple functions are similar, the most specific one
                (especially for regex/substitution) is chosen.
        """
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
    """
    ParameterStage is responsible for extracting and validating
    parameter values from a given prompt using a language model.
    It enforces strict extraction rules to ensure values are
    copied exactly as they appear in the input, without formatting
    or corrections.
    """

    def process(
        self,
        prompt: str,
        model: Small_LLM_Model,
        function_name: str,
        description: str,
        parameters: list[ParametersValidator],
    ) -> str:
        """
        Processes a prompt to extract parameter values using a strict
        text extraction engine.

        Args:
            prompt (str): The user input or instruction to process.
            model (Small_LLM_Model): The language model used for
                response generation.
            function_name (str): The name of the function for which parameters
                are being extracted.
            description (str): A description of the function or task.
            parameters (list[ParametersValidator]): A list of parameter
                validators specifying expected parameters and their types.

        Returns:
            str: The extracted parameter values in JSON format as generated
                by the model.

        Notes:
            - The extraction follows strict rules: no formatting, no
                corrections, and values are copied exactly as they appear.
            - For the function "fn_substitute_string_with_regex", additional
                regex options are provided in the system prompt.
        """
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
