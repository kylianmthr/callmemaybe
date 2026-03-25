import enum
import re
from typing import Any

from src.llm_sdk.llm_sdk import Small_LLM_Model


class Status(enum.Enum):
    """
    An enumeration representing the various states in a parsing or prediction
    process.

    Attributes:
        START (list): Indicates the start of a structure, represented by "{".
        INSERT_KEY (list): Represents the state where a key (e.g., "name") is
            to be inserted.
        INSERT_STRING (list): Represents the state where a string delimiter
            ('"') is to be inserted.
        INSERT_SEMI_COLUMN (list): Represents the state where a colon (":") is
            to be inserted.
        INSERT_VALUE (list): Represents the state where a value
            (function name) is to be inserted.
        INSERT_NL (list): Represents the state where a newline or comma (",")
            is to be inserted.
        INSERT_ONLY_NL (list): Represents the state where only a newline or
            comma (",") is to be inserted.
        END (list): Indicates the end of a structure, represented by "}".
        FREE_TEXT (None): Represents a state where free text is allowed.
    """
    START = ["{"]
    INSERT_KEY = [
        "name",
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
    """
    JSONPredict is a state machine for generating or parsing JSON-like
    structures in a controlled, stepwise manner.

    Attributes:
        keys (list[str]): List of possible keys to insert into the JSON
            object.
        value (list[str]): List of possible values to insert for a key.
        model (Small_LLM_Model): The language model used for prediction or
            generation.
        always_free_mode (bool): If True, allows free text entry for all keys.
        stack (list[Status]): Stack representing the current state of the JSON
            generation process.
        actual_buffer (str): Buffer holding the current string being
            processed.
        last_key (str): The last key that was inserted or processed.
    """
    def __init__(
        self,
        keys: list[str],
        value: list[str],
        model: Small_LLM_Model,
        always_free_mode: bool = False,
    ) -> None:
        self.stack: list[Status] = [Status.START]
        self.actual_buffer = ""
        self.last_key = ""
        self.keys = keys
        self.value = value
        self.always_free_mode = always_free_mode

    def append(self, status: Status) -> None:
        """
        Appends a Status object to the stack.

        Args:
            status (Status): The status object to be added to the stack.
        """
        self.stack.append(status)

    def pop(self) -> Status:
        """
        Removes and returns the top element from the stack.

        Returns:
            Status: The top element that was removed from the stack.

        Raises:
            IndexError: If the stack is empty.
        """
        return self.stack.pop()

    def get_state(self) -> Status:
        """
        Returns the current state from the top of the stack.

        Returns:
            Status: The most recent status object from the stack.
        """
        return self.stack[-1]

    def get_possible_characters(self) -> list[str] | Any:
        """
        Returns a list of possible characters based on the current state.

        Depending on the current state of the object, this method returns:
        - The list of keys if the state is `Status.INSERT_KEY`.
        - The value if the state is `Status.INSERT_VALUE`.
        - Otherwise, returns the value associated with the current state.

        Returns:
            list[str] | Any: The possible characters or values based on the
                current state.
        """
        if self.get_state() == Status.INSERT_KEY:
            return self.keys
        if self.get_state() == Status.INSERT_VALUE:
            return self.value
        else:
            return self.get_state().value

    def manage_state(self, last_token: str) -> bool:
        """
        Manages and updates the internal state machine based on the latest
        input token.

        This method processes the `last_token` character, updates the
        `actual_buffer`, and transitions between different states defined by
        the `Status` enum. It uses regular expressions to match specific
        patterns in the buffer and determines the next state accordingly.
        The method also manages the list of keys and values, and handles
        transitions for inserting keys, strings, values, newlines, and ending
        the process.

        Args:
            last_token (str): The latest character or token to process.

        Returns:
            bool: True if a state transition occurred, False otherwise.
        """
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
            self.keys.remove(self.last_key)
            if self.last_key == "description" or self.always_free_mode:
                # and self.last_key != "regex":
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
            self.pop()
            self.append(Status.INSERT_KEY)
            return True
        if self.get_state() == Status.END:
            self.pop()
            return True
        return False
