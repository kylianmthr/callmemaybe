import re
from src.llm_sdk import llm_sdk
from src.predict import JSONPredict, Status
from src.stages import DecodeStage, EncodingStage, LogitsStage


def generate_response(
    sys_prompt: str,
    prompt: str,
    predict: JSONPredict,
    model: llm_sdk.Small_LLM_Model,
) -> str:
    initial_prompt = sys_prompt + prompt
    sentence = initial_prompt
    while True:
        if not (len(predict.stack)):
            break
        allowed_logits = []
        logits = LogitsStage().process(EncodingStage().process(sentence, model), model)
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
