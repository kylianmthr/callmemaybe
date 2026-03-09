import enum
import re

from src.llm_sdk.llm_sdk import Small_LLM_Model


class Status(enum.Enum):
    START = ["{"]
    INSERT_KEY = [
        "name",
        "description",
    ]
    INSERT_STRING = ['"']
    INSERT_SEMI_COLUMN = [":"]
    INSERT_VALUE = [
        "fn_add_numbers",
        "fn_greet",
        "fn_reverse_string",
        "fn_get_square_root",
        "fn_substitute_string_with_regex",
    ]
    INSERT_NL = [","]
    INSERT_ONLY_NL = [","]
    END = ["}"]
    FREE_TEXT = None


class JSONPredict:
    def __init__(self, keys, value) -> None:
        self.stack: list[Status] = [Status.START]
        self.actual_buffer = ""
        self.last_key = ""
        self.model = Small_LLM_Model()
        self.keys = keys
        self.value = value

    def append(self, status: Status) -> None:
        self.stack.append(status)

    def pop(self) -> Status:
        return self.stack.pop()

    def get_state(self) -> Status:
        return self.stack[-1]

    def get_possible_characters(self) -> list[str] | None:
        if self.get_state() == Status.INSERT_KEY:
            return self.keys
        if self.get_state() == Status.INSERT_VALUE:
            return self.value
        else:
            return self.get_state().value

    def manage_state(self, last_token: str) -> bool:
        self.actual_buffer += last_token
        if self.get_state() == Status.START:
            self.pop()
            self.append(Status.INSERT_STRING)
            self.actual_buffer = ""
            return True
        if self.get_state() == Status.INSERT_KEY and re.search(
            r'"\w+$', self.actual_buffer
        ):
            for key in self.keys:
                if key in self.actual_buffer:
                    self.pop()
                    self.append(Status.INSERT_STRING)
                    self.last_key = key
                    return True
            return True
        if self.get_state() == Status.INSERT_STRING and re.search(
            r'"([^"]+)"\s*:\s*"([^"]+)"$', self.actual_buffer
        ):
            self.pop()
            if len(self.keys):
                self.append(Status.INSERT_NL)
            else:
                self.append(Status.END)
            return True
        if self.get_state() == Status.INSERT_STRING and re.search(
            r'"\w+"$', self.actual_buffer
        ):
            self.pop()
            self.append(Status.INSERT_SEMI_COLUMN)
            return True
        if self.get_state() == Status.INSERT_SEMI_COLUMN:
            self.pop()
            self.append(Status.INSERT_STRING)
            return True
        if self.get_state() == Status.INSERT_STRING and re.search(
            r'"([^"]+)"\s*:\s*"$', self.actual_buffer
        ):
            self.pop()
            print("==>", self.last_key)
            self.keys.remove(self.last_key)
            if self.last_key == "description":
                self.append(Status.FREE_TEXT)
                return True
            self.append(Status.INSERT_VALUE)
            return True
        if (self.get_state() == Status.FREE_TEXT) and re.search(
            r'"([^"]+)"\s*:\s*"([^"]+)"$', self.actual_buffer
        ):
            self.pop()
            if len(self.keys):
                self.append(Status.INSERT_NL)
            else:
                self.append(Status.END)
            return True
        if self.get_state() == Status.INSERT_VALUE:
            for possibility in self.value:
                if possibility in self.actual_buffer:
                    self.pop()
                    self.append(Status.INSERT_STRING)
        if self.get_state() == Status.INSERT_NL and re.search(
            r'"([^"]+)"\s*:\s*"([^"]+)"\n', self.actual_buffer
        ):
            self.pop()
            self.append(Status.INSERT_STRING)
            self.actual_buffer = ""
            return True
        if self.get_state() == Status.INSERT_NL and re.search(
            r'"([^"]+)"\s*:\s*"([^"]+)",', self.actual_buffer
        ):
            self.pop()
            self.append(Status.INSERT_STRING)
            self.actual_buffer = ""
            return True
        if self.get_state() == Status.INSERT_ONLY_NL:
            self.pop()
            self.append(Status.INSERT_STRING)
            self.actual_buffer = ""
            return True
        if self.get_state() == Status.INSERT_STRING and re.search(
            r'"$', self.actual_buffer
        ):
            # Check si y'a qu'un ". Ca doit etre mis a la fin pour que les autres check soient prio
            self.pop()
            self.append(Status.INSERT_KEY)
            return True
        if self.get_state() == Status.END:
            self.pop()
            return True
        return False
