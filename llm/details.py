"""CL311.D Details: pulls out the details a crew needs from a report.

Function: extract_details(report)

Input:
    report (str): the report in English, with personal details hidden.
    Sample: "Street light out at the corner of Pine and N 3rd since Monday."

Output (dict):
    location (str or None): the street, address, crossing or landmark, copied from the report.
    when (str or None): a time or date copied from the report.
    crew_needs (str): a short phrase that says what work the crew must do.
    Sample: {"location": "corner of Pine and N 3rd", "when": "since Monday", "crew_needs": "street light repair"}

Raises ValueError if the LLM's answer can't be used.
Test it: python3 llm/details.py      Score it: python3 score.py details
"""
import ollama

# This lets the file work both as "python3 llm/details.py" and as "from llm.details import ...".
if __package__:
    from .utils import read_json
else:
    from utils import read_json

instruction = """TODO: say who the LLM is and what it must do."""

context = """TODO: the labels, rules and facts the LLM needs."""

examples = """TODO: a few examples of input and the exact output you want."""

output_format = """TODO: the exact JSON the LLM must return."""


def build_prompt(report):
    prompt = f"""<instruction>{instruction}</instruction>
<context>{context}</context>
<examples>{examples}</examples>
<output_format>{output_format}</output_format>
<query>Report: {report}
Output:</query>"""
    return prompt


def extract_details(report):
    # TODO: write this function. The docstring at the top of this file is the contract.
    # 1. build_prompt(...), call
    #    ollama.generate(model="llama3.2", prompt=prompt, format="json", options={"num_predict": 500}),
    #    and read the answer with read_json.
    # 2. Check it: the keys location and when are there, and crew_needs is a str. A location or time of "", "null" or "None" becomes None.
    #    Ask again (up to 3 tries) if it fails, then raise ValueError.
    # 3. Return {"location": ..., "when": ..., "crew_needs": ...}.
    raise NotImplementedError("extract_details is not written yet")


if __name__ == "__main__":
    report = input("Report: ")
    result = extract_details(report)
    print(result)
