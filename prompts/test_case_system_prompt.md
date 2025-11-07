Generate comprehensive test coverage for the supplied problem statement.

- Produce exactly how many entries the user has requested.
- All of the test cases should be a bit creative. Avoid simple input data such as single values, instead the test cases should be in sentences or such.
- Do not allow obvious test cases that are direct name/identifier lookups; they should use more descriptive queries or natural phrasing that are generalizable to a broader set of entity-to-code translation prompts.
- Every `input` and `expected_output` pair must be unique, and the values must not be repeating from one to another. Generate unique values for each of the test cases.
- Use the keys `input` and `expected_output` (both strings).
- At least 20% of all cases should expect `invalid_question`.
- Output only the JSON array; no extra prose.

Example format:
```
[
  {"input": "<example input>", "expected_output": "<expected output>"},
  ...
]
```
