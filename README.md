# Prompt Challenge Generator

Generate **injection-resistant prompt engineering challenges** — complete with
[promptfoo](https://www.promptfoo.dev/) evaluation assets and test cases — from a
single command. A two-agent pipeline (challenge generator + test-case generator)
runs on **OpenRouter** LLMs, writes ready-to-run eval suites, and scales to many
challenges in parallel. Used to some extent by the
[LunaPrompts](https://lunaprompts.com/challenges) Prompt Engineering Challenge
website.

**Topics:** prompt-engineering · prompt-injection · llm-security · promptfoo ·
llm-evaluation · openrouter · openai · ai-agents · test-generation · python · uv

### Prerequisites
- [uv](https://github.com/astral-sh/uv) with Python 3.13 installed
- Node.js (needed later to run `promptfoo`)
- `OPENROUTER_API_KEY` exported in your environment or stored in `.env` at the project root:
  ```
  OPENROUTER_API_KEY="sk-or-v1-yourkeyhere"
  ```

### Quick Start
```bash
uv run main.py \
  --theme "the user will provide you cities he wants to travel to, provide IATA codes for each of them" \
  --tcCount=10 \
  --alias "IATA codes" \
  --n 10 \
  --max_concurrent 5
```
- `--theme` (required) supplies the creative direction for the challenge. The value is stripped of whitespace and must not be empty.
- `--tcCount` (optional, default `50`) controls how many test cases the generator requests from the test-case agent. Pass integers only.
- `--alias` (optional) overrides the folder prefix used inside `generated_challenges/`. Provide a short name such as `--alias Theme`; it will be slugified to `theme` and versioned as `theme-001`, `theme-002`, and so on.
- `--n` (optional, default `1`) repeats the full generation pipeline so you can capture multiple challenge variants per run.
- `--max_concurrent` (optional, default `1`) limits how many of those runs execute in parallel to avoid API rate limits.

All arguments are parsed by `src/Args.py`, which raises a `ValueError` if `--theme` resolves to an empty string, `--alias` lacks non-whitespace characters, or either batching flag is set below `1`.

### Configuration and Clients
- `src/ClientConfig.py` loads `.env`, verifies `OPENROUTER_API_KEY`, and instantiates an `openai.OpenAI` client pinned to `https://openrouter.ai/api/v1`.
- `src/AgentConfig.py` builds two `src.Agent.Agent` instances with the `openai/gpt-5-nano` model:
  - **Challenge Generator** uses `prompts/problem_statement_system_prompt.md` to draft the problem statement, examples, and parameter declaration.
  - **Test Case Generator** uses `prompts/test_case_system_prompt.md` to create the JSON test suite.

### Generation Workflow
1. **Challenge Drafting** – The challenge agent receives the theme and returns fenced sections inside triple backticks.  
   `src/section_splitter.save_section` extracts the `problem_statement`, `examples`, and `parameter` blocks, writes them into a fresh directory under `generated_challenges/<slug-nnn>/` (or `<alias-nnn>/` when `--alias` is set), and returns the persisted problem statement text for downstream use. The entire step repeats `--n` times, with up to `--max_concurrent` runs executing simultaneously.
2. **Test Case Production** – The test-case agent is prompted with the saved problem statement and the requested count. Its fenced `test_cases` JSON array is stored in the same directory.
3. **Promptfoo Assets** – `src/test_cast_writer.generate_promptfoo_test_cases` validates the JSON, creates `EDIT_THIS_PROMPT_TO_BEAT_THE_CHALLENGE.md`, and writes `eval_test.yaml` configured for the `openrouter:openai/gpt-4.1` provider. The rubric embedded in `prompts/evaluation_prompt.md` is referenced through the YAML variables.

`src/file_manager.create_theme_directory` guarantees unique challenge directories by slugifying the alias when provided (otherwise the theme) and incrementing a three-digit suffix, guarding the process with a lock so concurrent runs never collide.

### Output Layout
Every successful run populates `generated_challenges/<slug-nnn>/` with:
- `problem_statement`, `examples`, `parameter` – plain-text files mirroring the agent’s fenced sections.
- `test_cases` – JSON array with the generated scenarios, including ≥20 % expectations of `invalid_question`.
- `evaluation_prompt` – copied rubric consumed by promptfoo.
- `EDIT_THIS_PROMPT_TO_BEAT_THE_CHALLENGE.md` – placeholder instructions for human-crafted prompts.
- `eval_test.yaml` – promptfoo configuration that binds the `user_prompt`, test inputs, and expected outputs.

### Running Evaluations
From the generated challenge directory:
```bash
npx promptfoo@latest eval -c eval_test.yaml --max-concurrency 5 --repeat 1
```
Edit `EDIT_THIS_PROMPT_TO_BEAT_THE_CHALLENGE.md` between runs to iterate on your prompt. The evaluator feeds each JSON scenario to the model and checks the response against `expected_output`.

### Module Overview
- `main.py` – Entry point that wires together `ClientConfig`, `AgentConfig`, argument parsing, challenge generation, batching (`--n`), and concurrency throttling (`--max_concurrent`).
- `src/Agent.py` – Lightweight wrapper around the OpenRouter Chat Completions API. Logs parameters, loads system prompts from `prompts/`, and returns the first completion message.
- `src/section_splitter.py` – Parses ```section``` fences, writes files, and emits warnings when sections are missing.
- `src/test_cast_writer.py` – Validates test case structure, writes the prompt-edit placeholder, and renders `eval_test.yaml`.
- `src/file_manager.py` – Handles directory naming, slugification, and index management.
- `src/Args.py` – CLI argument parser and validation logic.
- `src/ClientConfig.py` / `src/AgentConfig.py` – Client bootstrap and agent wiring described above.

### Prompts
- `prompts/problem_statement_system_prompt.md` – Defines the challenge specification contract, enforces the `invalid_question` fallback, and documents the `{{user_prompt}}` parameter.
- `prompts/test_case_system_prompt.md` – Demands a fixed-count JSON array with unique values and at least 20 % `invalid_question` expectations.
- `prompts/evaluation_prompt.md` – Promptfoo rubric that passes only exact matches to `{{expected_output}}`, tolerating minor punctuation drift.

### Dependencies
The project targets Python 3.13 and relies primarily on:
- `openai>=2.6.1` for OpenRouter API access
- `python-dotenv>=1.0.1` for `.env` loading
Transitive requirements (captured in `uv.lock`) include `httpx`, `pydantic`, `tqdm`, and supporting packages.

# Disclaimer

This software is provided under the MIT License on an **“as is”** basis, without warranties of any kind. To the maximum extent permitted by applicable law, the authors and copyright holders shall not be liable for any claims, damages, losses, or other liability arising from the use of this software.

You are solely responsible for determining whether this software is suitable, safe, lawful, and appropriate for your intended use. Unless explicitly stated otherwise, this project is general-purpose software and is not designed, tested, certified, or approved for safety-critical, medical, automotive, aviation, industrial-control, life-support, cybersecurity-critical, financial-critical, or other high-risk use cases.

The authors and copyright holders make no guarantees regarding security, reliability, availability, correctness, compliance, non-infringement, or fitness for any particular purpose.

This notice is intended to clarify the nature of the project and does not impose additional restrictions beyond the MIT License.
