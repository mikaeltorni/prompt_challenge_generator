Generate comprehensive test coverage for the supplied problem statement.

Return the cases inside triple backticks in this exact format:
```test_cases
[
  {"input": "<example input>", "expected_output": "<expected output>"},
  ...
]
```

Constraints:
- Produce exactly 10 entries.
- Every `input` and `expected_output` pair must be unique, and the values must not be repeating from one to another. Generate unique values for each of the test cases.
- Use the keys `input` and `expected_output` (both strings).
- At least 20% of all cases should expect `invalid_question`.
- Output only the JSON array—no extra prose.
