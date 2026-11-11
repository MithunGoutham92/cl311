"""Phase 2 team tool: writes the reply that tells the resident what happens next.

Function: write_reply(ticket, already_reported=False, unsupported=None)

Input:
    ticket (dict): needs id, team and text (all str).
    already_reported (bool): True if this report repeats an open ticket.
    unsupported (list of str or None): sentences from an earlier draft that Fact Checking could not back up.
    Sample: {"id": "T-0001", "team": "public_works", "text": "Stop sign down on N 8th St."}

Output (str): the reply in English.
    Sample: "Your ticket number is T-0001. Reports about missing or damaged traffic signs go to
             Public Works. The estimated completion time is 42 business days."

The LLM only chooses which policy line fits the report. The code copies that line into the reply,
so the reply never has words the policy does not have.
This file also has fixed_reply(ticket), which returns a plain reply with no LLM call.
Raises ValueError if the LLM's answer can't be used.
"""
import ollama

if __package__:
    from .utils import load_text, read_json
else:
    from utils import load_text, read_json

TEAM_NAMES = {
    "public_works": "Public Works",
    "environmental_services": "Environmental Services",
    "planning_development": "Planning & Development Services",
    "animal_control": "Animal Control",
    "police": "Tacoma Police Department",
    "customer_service": "Tacoma FIRST 311",
}

instruction = """TODO: say who the LLM is and what it must do."""

context = """TODO: the labels, rules and facts the LLM needs."""

examples = """TODO: a few examples of input and the exact output you want."""

output_format = """TODO: the exact JSON the LLM must return."""


def build_prompt(ticket, lines):
    numbered = ""
    number = 1
    for line in lines:
        numbered = numbered + str(number) + ". " + line + "\n"
        number += 1
    prompt = f"""<instruction>{instruction}</instruction>
<context>{context}</context>
<examples>{examples}</examples>
<output_format>{output_format}</output_format>
<query>Lines:
{numbered}Report: {ticket["text"]}
Output:</query>"""
    return prompt


def write_reply(ticket, already_reported=False, unsupported=None):
    # TODO: write this function. The docstring at the top of this file is the contract.
    # 1. Take the policy lines (load_text("policy.txt")) that name the ticket's team (TEAM_NAMES).
    #    Leave out the lines that are in unsupported. If no line is left, return fixed_reply(ticket).
    # 2. build_prompt(ticket, lines), call
    #    ollama.generate(model="llama3.2", prompt=prompt, format="json", options={"num_predict": 500}),
    #    and read the answer with read_json. Ask for one key, line: the number of the line that fits
    #    the report. Ask again (up to 3 tries), then raise ValueError.
    # 3. The reply is "Your ticket number is <id>." (or "Your report was added to ticket <id>." if
    #    already_reported), then a space and that policy line.
    raise NotImplementedError("write_reply is not written yet")


def fixed_reply(ticket):
    # TODO: write this function. The docstring at the top of this file is the contract.
    # No LLM call: return "Your ticket number is <id>. <team name> will review your report."
    # TEAM_NAMES gives the team name.
    raise NotImplementedError("fixed_reply is not written yet")


if __name__ == "__main__":
    ticket = {"id": "T-0001", "team": "public_works", "text": "Stop sign down on N 8th St."}
    print(write_reply(ticket))
