Your task is to design prompt-engineering challenges.

The output that the LLM produces should be something pre-defined that is mentioned in the problem statement. This should have multiple available words that the LLM can produce. 
Make sure to always include one word that defines the protection against prompt-injection attacks, such as "NA". Mention the meaning of this label to the user and make examples out of it.

Craft:
- The problem statement.
- Examples to pass the test cases with input / expected output.
- {{input}} Parameter that is related to the challenge. Only provide the parameter with a simple description.

Return each of these inside triple backticks in the following format:
```problem_statement
the problem statement here
```

```examples
examples here
```

```parameter
{{input}} & the description of the parameter
```