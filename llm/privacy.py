"""CL311.B Privacy: hides names, phone numbers and email addresses before the report is saved.

Function: redact(text)

Input:
    text (str): a report from a resident.
    Sample: "Pothole on N 8th St. Call me, Sam Lee, at 253-555-0199."

Output (dict):
    redacted_text (str): the text with each item replaced by [NAME], [PHONE] or [EMAIL].
                         Street names and places stay, because the crew needs them.
    items_hidden (int): how many items were hidden.
    Sample: {"redacted_text": "Pothole on N 8th St. Call me, [NAME], at [PHONE].", "items_hidden": 2}

Raises ValueError if the LLM's answer can't be used.
Test it: python3 llm/privacy.py      Score it: python3 score.py privacy
"""
import ollama

# This lets the file work both as "python3 llm/privacy.py" and as "from llm.privacy import ...".
if __package__:
    from .utils import read_json
else:
    from utils import read_json

PLACEHOLDERS = {"names": "[NAME]", "phones": "[PHONE]", "emails": "[EMAIL]"}
# The LLM sometimes lists these words as names. They are never names, so never hide them.
NOT_NAMES = ["someone", "somebody", "anyone", "everyone", "nobody", "neighbor", "neighbors",
             "owner", "resident", "residents", "we", "they", "i", "me", "my"]


instruction = """TODO: say who the LLM is and what it must do."""

context = """TODO: the labels, rules and facts the LLM needs."""

examples = """TODO: a few examples of input and the exact output you want."""

output_format = """TODO: the exact JSON the LLM must return."""


def build_prompt(text):
    prompt = f"""<instruction>{instruction}</instruction>
<context>{context}</context>
<examples>{examples}</examples>
<output_format>{output_format}</output_format>
<query>Report: {text}
Output:</query>"""
    return prompt


def redact(text):
    # TODO: write this function. The docstring at the top of this file is the contract.
    # A plan that works well:
    # 1. Ask the LLM to list what it finds, not to rewrite the text. Ask for JSON with one list for each
    #    key of PLACEHOLDERS, plus a list of places (streets, addresses and landmarks). Call
    #    ollama.generate(model="llama3.2", prompt=prompt, format="json", options={"num_predict": 500}),
    #    and read output.response with read_json. If a list is missing, ask again (up to 3 tries),
    #    then raise ValueError.
    # 2. Your code, not the LLM, replaces each listed item in the text with its PLACEHOLDERS value
    #    and counts the items it hides. Skip an item that is not a personal detail: a word in NOT_NAMES,
    #    a name that starts with a small letter, an email without an @, one letter, or a part of one of
    #    the places (or a long phrase that has one in it).
    #    A helper function such as should_hide(item, key, text, places) keeps this short.
    # 3. Return {"redacted_text": ..., "items_hidden": ...}.
    raise NotImplementedError("redact is not written yet")


if __name__ == "__main__":
    text = input("Text: ")
    result = redact(text)
    print(result)
