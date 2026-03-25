import re
from llm_sdk import llm_sdk
from src.predict import JSONPredict, Status
from src.stages import DecodeStage, EncodingStage, LogitsStage


def generate_response(
    sys_prompt: str,
    prompt: str,
    predict: JSONPredict,
    model: llm_sdk.Small_LLM_Model,
) -> str:
    """
    Generates a response string by iteratively predicting and appending tokens
    using a language model and prediction state.

    Args:
        sys_prompt (str): The system prompt to prepend to the user prompt.
        prompt (str): The user prompt to generate a response for.
        predict (JSONPredict): An object managing the prediction state and
            possible next characters.
        model (llm_sdk.Small_LLM_Model): The language model used for
            encoding and decoding tokens.

    Returns:
        str: The generated response string, excluding the initial prompt.

    Notes:
        - The function continues generating tokens until the prediction
            stack is empty.
        - Only allowed tokens, as determined by the prediction state, are
            considered at each step.
        - Special handling is applied when the prediction state is
            Status.FREE_TEXT and a specific pattern is matched in the buffer.
    """
    initial_prompt = sys_prompt + prompt
    sentence = initial_prompt
    while True:
        if not (len(predict.stack)):
            break
        allowed_logits = []
        logits = LogitsStage().process(
            EncodingStage().process(sentence, model), model
        )
        possible_char = predict.get_possible_characters()
        if len(predict.stack):
            if possible_char:
                for token in possible_char:
                    allowed_logits += model.encode(token).tolist()[0]
        word = DecodeStage().process(logits, model, allowed_logits)
        if predict.get_state() == Status.FREE_TEXT and (
            re.search(
                r'([^" \t]+)"',
                predict.actual_buffer.split(":")[-1] + word,
            )
        ):
            word = word[: word.find('"') + 1]
        sentence += word
        predict.manage_state(word)
    return sentence.replace(initial_prompt, "")
