*This project has been created as part of the 42 curriculum by kmathuri.* 
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Code Style](https://img.shields.io/badge/code%20style-flake8-green)](https://flake8.pycqa.org/)
[![Type Checking](https://img.shields.io/badge/type%20checking-mypy-lightgrey)](http://mypy-lang.org/)
[![Validated with](https://img.shields.io/badge/validation-pydantic-red)](https://docs.pydantic.dev/)
[![Testing](https://img.shields.io/badge/tests-pytest-yellow)](https://docs.pytest.org/)

# 📝 Description

**Call Me Maybe** is a function-calling tool that translates natural language prompts into structured machine-executable function calls. While Large Language Models (LLMs) are naturally prone to generating unstructured text, this project bridges the gap by using **constrained decoding** to guarantee 100% valid JSON output. This ensures near-perfect reliability even when using a small 500 million parameter model like **Qwen3-0.6B**. 

# ⚙️ Instructions

## Installation

The project uses `uv` for dependency management. To set up the environment and install dependencies (including `numpy` and `pydantic`): 

```bash
make install

```

## Execution

To run the program using the default paths (`data/input/` and `data/output/`): 

```bash
make run

```

Alternatively, you can specify custom paths: 

```bash
uv run python -m src --functions_definition <file> --input <file> --output <file>

```

## Code Quality

To ensure the code adheres to the required standards (`flake8` and `mypy`): 

```bash
make lint

```

# 🧠 Algorithm Explanation

My implementation uses a **State Machine-based JSON Predictor** combined with **Logit Masking** to enforce structure: 

1. 
**JSON Predictor:** This component "pre-shots" which character or token type is allowed based on the preceding character (e.g., after a key, a colon is expected; after a bracket, a key or closing bracket is expected). 


2. 
**Logit Masking:** At each generation step, the model produces logits for all tokens. My algorithm masks these logits, setting the probability of invalid tokens to negative infinity. 


3. 
**Token Filtering:** I restrict the model to specific lists of authorized tokens for keys and function names. 


4. 
**Free Mode:** For string values (parameters), the system enters a "free mode" where it accepts the most probable tokens until the JSON Predictor signals that the string must be closed to maintain valid structure. 



# 🛠️ Design Decisions

* **Pydantic Integration:** All input files and internal structures are mapped using Pydantic classes to ensure immediate validation and type safety. 


* **Modular Pipeline:** The generation follows a clear path: `Tokenization` -> `Logit Generation` -> `JSON Predictor Filtering` -> `Decoding`. 


* **Error Handling:** The system uses `try-except` blocks and context managers to handle malformed JSON inputs or missing files without crashing. 



# 📊 Performance Analysis

* **Accuracy:** The system achieves over **90% accuracy** in function selection and argument extraction. 


* **Reliability:** Due to constrained decoding, the output is **100% valid JSON** every time. 


* **Speed:** The implementation processes all test prompts in approximately **3 minutes**, well within the 5-minute requirement. 



# 🚧 Challenges Faced

The primary challenge was handling the **tokenizer specifics**, such as leading spaces represented by the `Ġ` symbol. Mapping these specific subword units to the character-based rules of the JSON Predictor required careful manipulation of the vocabulary JSON file. Additionally, ensuring that the model correctly identified function names from a dynamic list without relying on "magic" or heuristics was a significant part of the logic. 

# 🧪 Testing Strategy

I validated the implementation using the following strategies: 

* **Pytest Suite:** Created unit tests to verify the JSON Predictor's state transitions and the logit masking logic. 


* **Edge Case Testing:** Tested with empty strings, large numbers, and special characters to ensure robust argument extraction. 


* **Schema Validation:** Ensured all outputs strictly match the types (number, string, boolean) defined in `function_definitions.json`. 



# 💻 Example Usage

To process a request like *"What is the sum of 2 and 3?"*: 

**Input:**

`{"prompt": "What is the sum of 2 and 3?"}` 

**Output in `function_calling_results.json`:** 

```json
{
  "prompt": "What is the sum of 2 and 3?",
  "name": "fn_add_numbers",
  "parameters": {"a": 2.0, "b": 3.0}
}

```

# 📚 Resources

* **Python Typing & PEP 257:** For code standards. 


* **JSON Schema:** For understanding constrained structure. 


* **AI Usage:** AI was used to assist in understanding `pytest` configurations, setting up the `Makefile` rules, and generating configuration files like `.flake8` and `pyproject.toml`. 
