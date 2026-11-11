"""CL311.C Fact Checking: checks that each sentence of a reply is backed up by the ticket or the city policy.

Function: check_reply(reply, ticket)

Input:
    reply (str): the draft reply in English.
    ticket (dict): needs id (str) and team (str).
    Sample: "Your ticket number is T-0001. A crew will come tomorrow.",
            {"id": "T-0001", "team": "public_works"}

Output (dict):
    supported (bool): True if every sentence has a source.
    claims (list of dict): one for each sentence, with:
        claim (str): the sentence.
        source (str or None): "ticket", "policy", or None if nothing backs it up.
    Sample: {"supported": False,
             "claims": [{"claim": "Your ticket number is T-0001.", "source": "ticket"},
                        {"claim": "A crew will come tomorrow.", "source": None}]}

The city policy is in data/policy.txt.
Raises ValueError if the LLM's answer can't be used.
Test it: python3 llm/fact_check.py      Score it: python3 score.py fact_check
"""
import ollama

# This lets the file work both as "python3 llm/fact_check.py" and as "from llm.fact_check import ...".
if __package__:
    from .utils import load_text, split_sentences, read_json
else:
    from utils import load_text, split_sentences, read_json

SOURCES = ["ticket", "policy", "none"]

instruction = """TODO: say who the LLM is and what it must do."""

context = """TODO: the labels, rules and facts the LLM needs."""

examples = """TODO: a few examples of input and the exact output you want."""

output_format = """TODO: the exact JSON the LLM must return."""


def build_prompt(sentence, ticket, policy):
    prompt = f"""<instruction>{instruction}</instruction>
<context>{context}</context>
<examples>{examples}</examples>
<output_format>{output_format}</output_format>
<query>Ticket: id {ticket["id"]}, team {ticket["team"]}
City policy:
{policy}
Sentence: {sentence}
Output:</query>"""
    return prompt


def check_reply(reply, ticket):
    # TODO: write this function. The docstring at the top of this file is the contract.
    # 1. Read the policy with load_text("policy.txt"). Split the reply with split_sentences.
    # 2. For each sentence: build_prompt(sentence, ticket, policy), call
    #    ollama.generate(model="llama3.2", prompt=prompt, format="json", options={"num_predict": 500}),
    #    and read the answer with read_json. Ask for one key, source, with a word from SOURCES.
    #    Ask again (up to 3 tries) if the answer is not in SOURCES, then raise ValueError.
    # 3. Add {"claim": sentence, "source": ...} to the list of claims. "none" becomes None.
    # 4. supported is True only if no source is None. Return {"supported": ..., "claims": ...}.
    # A helper function such as check_sentence(sentence, ticket, policy) keeps check_reply short.
    raise NotImplementedError("check_reply is not written yet")


if __name__ == "__main__":
    reply = input("Reply: ")
    ticket = {"id": "T-0001", "team": "public_works"}
    result = check_reply(reply, ticket)
    print(result)
