## Prompt Challenge Generator

This project generates prompt challenges and the artifacts needed to evaluate them with promptfoo.

### Prerequisites
- UV with Python 3.13
- `OPENROUTER_API_KEY` environment variable configured for the OpenRouter API (use .env file at the root of the project):
```
OPENROUTER_API_KEY="sk-or-v1-yourkeyhere"
```
- Node.js (for running `npx promptfoo`).

### Generate a challenge
```bash
    uv run main.py --theme "LLM redteaming challenge"
```

The generator creates a new directory under `generated_challenges/`. Each challenge directory contains:
- `problem_statement`, `examples`, `parameter`, `test_cases`, and `evaluation_prompt`.
- `test_cases` is a JSON array with exactly 10 objects using `{"input": "...", "expected_output": "..."}`.
- `parameter` declares the placeholder `{{user_prompt}}` and describes the instructions you will craft. No scenario inputs are appended automatically—the grader supplies them independently.
- `EDIT_THIS_PROMPT_TO_BEAT_THE_CHALLENGE.md` where you write the user prompt that will be sent verbatim to the model.
- `eval_test.yaml` configured to run against `openrouter:openai/gpt-4.1`, containing one test entry per JSON case. Each test passes `user_prompt` to the model and evaluates the response via the rubric.

### Run the promptfoo evaluation
From inside the generated challenge directory:
```bash
    npx promptfoo@latest eval -c generated_challenges/llm-redteaming-challenge-001/eval_test.yaml --max-concurrency 5 --repeat 1
```
if you generate many challenges, edit the 001 in the command to try them out

Edit `EDIT_THIS_PROMPT_TO_BEAT_THE_CHALLENGE.md` between runs to iterate on your user prompt. Only your instructions are sent to the model; the evaluator separately checks each `input`/`expected_output` pair against the model's reply. The `test_cases` file offers a consistent, machine-readable list of checks, and the evaluation rubric is referenced directly from `evaluation_prompt`.
