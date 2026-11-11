"""CL311.A Sorter: decides which city team gets each report, and how urgent it is.

Function: sort_report(report)

Input:
    report (str): the report in English, with personal details hidden.
    Sample: "Stop sign down at N 8th St and Pine."

Output (dict):
    team (str): public_works, environmental_services, planning_development,
                animal_control, police or customer_service.
    urgency (str): emergency, high, normal or low.
    Sample: {"team": "public_works", "urgency": "high"}

Raises ValueError if the LLM's answer can't be used.
Test it: python3 llm/sorter.py      Score it: python3 score.py sorter
"""
import ollama

# This lets the file work both as "python3 llm/sorter.py" and as "from llm.sorter import ...".
if __package__:
    from .utils import read_json
else:
    from utils import read_json

TEAMS = ["public_works", "environmental_services", "planning_development",
         "animal_control", "police", "customer_service"]
URGENCIES = ["emergency", "high", "normal", "low"]

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


def sort_report(report):
    # TODO: write this function. The docstring at the top of this file is the contract.
    # Steps: build the prompt, call ollama.generate(model="llama3.2", prompt=prompt,
    # format="json", options={"num_predict": 500}), turn output.response into a dict
    # with read_json, check it, and ask again (up to 3 tries) if you can't use it.
    # Then return the dict the contract describes.
    raise NotImplementedError("sort_report is not written yet")


if __name__ == "__main__":
    report = input("Report: ")
    result = sort_report(report)
    print(result)
