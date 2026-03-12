SRC=src
FUNCTION_DEF_FILE=${SRC}/data/input/functions_definition.json
#INPUT_FILE=${SRC}/data/input/temp.json
INPUT_FILE=${SRC}/data/input/function_calling_tests.json
OUTPUT_FILE=output.json

all: ${NAME}

install:
	uv sync

run: ${NAME}
	uv run python -m ${SRC} ${FUNCTION_DEF_FILE} ${INPUT_FILE} ${OUTPUT_FILE}

debug: ${NAME}
	python3 -m pdb -m ${SRC} ${FUNCTION_DEF_FILE} ${INPUT_FILE} ${OUTPUT_FILE}

clean:
	find . -iname "__pycache__" -type d -exec rm -rf "{}" +
	find . -iname ".mypy_cache" -type d -exec rm -rf "{}" +

lint:
	uv run flake8 . --exclude .venv
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude .venv

lint-strict:
	uv run flake8 ${SRC}
	uv run mypy ${SRC} --exclude "src/llm_sdk/" --follow-imports=silent

#TODO: A SUPPRIMER
test:
	uv run pytest -vv

.PHONY: install run debug clean lint lint-strict test
