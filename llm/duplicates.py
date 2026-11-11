"""Phase 2 team tool: checks whether a new report repeats an open ticket.

Function: find_duplicate(report, team, location, tickets)

Input:
    report (str): the new report, with personal details hidden.
    team (str): the new report's team, from the Sorter.
    location (str or None): the new report's location, from Details.
    tickets (list of dict): saved tickets, each with id, status, team, location and text.
    Sample: "Street lights out on 64th near Pacific.", "public_works", "64th near Pacific",
            [{"id": "T-0002", "status": "open", "team": "public_works",
              "location": "64th from Pacific to McKinley", "text": "Street lights on 64th are out"}]

Output (dict):
    duplicate_of (str or None): the matching ticket's id, or None if there is no match.
    Sample: {"duplicate_of": "T-0002"}

The code keeps only open tickets for the same team on the same street (same_place in utils.py).
The LLM then chooses which of those tickets, if any, is the same problem.
Raises ValueError if the LLM's answer can't be used.
"""
import ollama

if __package__:
    from .utils import same_place, read_json
else:
    from utils import same_place, read_json

instruction = """TODO: say who the LLM is and what it must do."""

context = """TODO: the labels, rules and facts the LLM needs."""

examples = """TODO: a few examples of input and the exact output you want."""

output_format = """TODO: the exact JSON the LLM must return."""


def build_prompt(report, location, candidates):
    numbered = ""
    number = 1
    for ticket in candidates:
        numbered = numbered + f"{number}. {ticket['text']} (Location: {ticket['location']})\n"
        number += 1
    prompt = f"""<instruction>{instruction}</instruction>
<context>{context}</context>
<examples>{examples}</examples>
<output_format>{output_format}</output_format>
<query>Tickets:
{numbered}New report: {report} (Location: {location})
Output:</query>"""
    return prompt


def find_duplicate(report, team, location, tickets):
    # TODO: write this function. The docstring at the top of this file is the contract.
    # 1. The candidates are the open tickets of the same team at the same place (same_place from utils).
    #    If there are none, return {"duplicate_of": None}.
    # 2. build_prompt(report, location, candidates), call
    #    ollama.generate(model="llama3.2", prompt=prompt, format="json", options={"num_predict": 500}),
    #    and read the answer with read_json. Ask for one key, ticket: 0 if no candidate is the same
    #    problem, 1 for the first candidate, and so on. Ask again (up to 3 tries), then raise ValueError.
    # 3. Return {"duplicate_of": the id of that candidate, or None}.
    raise NotImplementedError("find_duplicate is not written yet")


if __name__ == "__main__":
    tickets = [{"id": "T-0002", "status": "open", "team": "public_works",
                "location": "64th from Pacific to McKinley", "text": "Street lights on 64th are out"}]
    print(find_duplicate("Street lights out on 64th near Pacific.", "public_works", "64th near Pacific", tickets))
    print(find_duplicate("Pothole on Pearl St.", "public_works", "Pearl St", tickets))
