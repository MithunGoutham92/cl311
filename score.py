"""Scores one tool on the 10 given cases in data/cases.json and on your own cases. Do not change this file.

Run from the project folder:
    python3 score.py sorter            the 10 given cases, then yours
    python3 score.py sorter given      the 10 given cases only
    python3 score.py sorter mine       your cases only
    python3 score.py sorter 3          given case 3 only
    python3 score.py sorter mine 3     your case 3 only
Tools: sorter, privacy, fact_check, details, language
Your cases are in data/my_cases/<tool>.json, such as data/my_cases/sorter.json. Write 30 of them.
"""
import json
import sys

from llm.utils import load_data, split_sentences

GOAL = 30         # write 30 of your own, for 40 in all


def check_sorter(case):
    from llm.sorter import sort_report
    answer = sort_report(case["report"])
    expected = case["expected"]["team"]
    return answer["team"] == expected, f"team {answer['team']!r}, expected {expected!r}"


def check_privacy(case):
    from llm.privacy import redact
    keep = case["privacy"]["must_keep"]
    # Test 1: the report alone has nothing to hide, so the place words must stay.
    plain = redact(case["report"])["redacted_text"]
    # Test 2: the report with a made-up contact line: hide the name, number and email, keep the place words.
    text = redact(case["privacy"]["text"])["redacted_text"]
    shown = []
    for item in case["privacy"]["must_hide"]:
        if item in text:
            shown.append(item)
    kept_plain = 0
    kept = 0
    for word in keep:
        if word.lower() in plain.lower():
            kept_plain += 1
        if word.lower() in text.lower():
            kept += 1
    ok = not shown and kept_plain * 2 >= len(keep) and kept * 2 >= len(keep)
    return ok, (f"still shown: {shown}; place words kept {kept_plain} and {kept} of {len(keep)} "
                f"-> {plain!r} | {text!r}")


def check_fact_check(case):
    from llm.fact_check import check_reply
    test = case["fact_check"]
    answer = check_reply(test["reply"], test["ticket"])
    got = []
    for claim in answer["claims"]:
        got.append(claim["source"])
    expected = test["expected_sources"]
    supported = None not in expected
    ok = got == expected and answer["supported"] == supported
    return ok, f"sources {got}, expected {expected}; supported {answer['supported']}, expected {supported}"


def check_details(case):
    from llm.details import extract_details
    answer = extract_details(case["report"])
    words = case["expected"]["street_words"]
    location = answer["location"] or ""
    if not words:
        return True, f"no street name in this report (location {answer['location']!r})"
    found = False
    for word in words:
        if word.lower() in location.lower():
            found = True
    return found, f"location {answer['location']!r} should contain one of {words}"


def check_language(case):
    from llm.language import translate_inbound, translate_reply
    inbound = translate_inbound(case["report"])
    english_ok = inbound["language"].lower().startswith("en") and inbound["back_translation"] is None
    ticket_id = case["fact_check"]["ticket"]["id"]
    reply = translate_reply(case["fact_check"]["reply"], "Spanish")["translated_reply"]
    reply_ok = ticket_id in reply and reply != case["fact_check"]["reply"]
    note = (f"language {inbound['language']!r}, back_translation {inbound['back_translation']!r}; "
            f"Spanish reply keeps {ticket_id}: {ticket_id in reply}")
    return english_ok and reply_ok, note


CHECKS = {"sorter": check_sorter, "privacy": check_privacy, "fact_check": check_fact_check,
          "details": check_details, "language": check_language}


# ---------------------------------------------------------------------------
# Your own cases: data/my_cases/<tool>.json, a list of cases with these fields.
# "text" is text in quote marks, and a list of words means the value must be one of them.
# Any other field, such as "note" or "source", is allowed and not used.

TEAMS = ["public_works", "environmental_services", "planning_development", "animal_control", "police",
         "customer_service"]
FIELDS = {
    "sorter": {"report": "text", "team": TEAMS},
    "privacy": {"text": "text", "must_hide": "list of text", "must_keep": "list of text"},
    "fact_check": {"reply": "text", "ticket_id": "text", "team": TEAMS, "sources": "list"},
    "details": {"report": "text", "location_words": "list of text"},
    "language": {"message": "text", "language": "text", "keep": "list of text"},
}


def extra_problems(tool, case):
    """Checks that need more than one field."""
    problems = []
    if tool == "fact_check":
        for source in case["sources"]:
            if source not in ["ticket", "policy", None]:
                problems.append(f'"sources" can only hold "ticket", "policy" or null, not {json.dumps(source)}')
        sentences = len(split_sentences(case["reply"]))
        if len(case["sources"]) != sentences:
            problems.append(f'the reply has {sentences} sentences, so "sources" needs {sentences} values')
    return problems


def mine_sorter(case):
    return check_sorter({"report": case["report"], "expected": {"team": case["team"]}})


def mine_privacy(case):
    from llm.privacy import redact
    text = redact(case["text"])["redacted_text"]
    shown = [item for item in case["must_hide"] if item in text]
    kept = [word for word in case["must_keep"] if word.lower() in text.lower()]
    ok = not shown and len(kept) * 2 >= len(case["must_keep"])
    return ok, f"still shown: {shown}; place words kept {len(kept)} of {len(case['must_keep'])} -> {text!r}"


def mine_fact_check(case):
    ticket = {"id": case["ticket_id"], "team": case["team"]}
    return check_fact_check({"fact_check": {"reply": case["reply"], "ticket": ticket,
                                            "expected_sources": case["sources"]}})


def mine_details(case):
    if case["location_words"]:
        return check_details({"report": case["report"], "expected": {"street_words": case["location_words"]}})
    from llm.details import extract_details
    answer = extract_details(case["report"])
    return not answer["location"], f"this report names no place, so location must be None: {answer['location']!r}"


def mine_language(case):
    from llm.language import translate_inbound, translate_reply
    inbound = translate_inbound(case["message"])
    english = case["language"].lower().startswith("en")
    found_english = inbound["language"].lower().startswith("en")
    if english:
        language_ok = found_english and inbound["back_translation"] is None
    else:
        language_ok = not found_english and bool(inbound["back_translation"])
    lost = [word for word in case["keep"] if word.lower() not in inbound["english"].lower()]
    reply = "Your ticket number is T-0001."
    translated = translate_reply(reply, inbound["language"])["translated_reply"]
    reply_ok = "T-0001" in translated and (translated.strip() == reply) == english
    note = (f"language {inbound['language']!r}, expected {case['language']!r}; words lost {lost}; "
            f"back_translation {inbound['back_translation']!r}; reply {translated!r}")
    return language_ok and not lost and reply_ok, note


MINE = {"sorter": mine_sorter, "privacy": mine_privacy, "fact_check": mine_fact_check,
        "details": mine_details, "language": mine_language}


# ---------------------------------------------------------------------------
# Reading and checking your own cases

def field_problem(value, kind):
    """Returns what is wrong with one field of your case, or "" if nothing is wrong."""
    if isinstance(kind, list):
        if value not in kind:
            return "must be one of: " + ", ".join(json.dumps(choice) for choice in kind)
    elif kind == "text":
        if not isinstance(value, str) or not value.strip():
            return "must be text in double quotes, and not empty"
    elif kind == "list of text":
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            return 'must be a list of text, such as ["a", "b"], or [] for none'
    elif kind == "true or false":
        if not isinstance(value, bool):
            return "must be true or false, with no quote marks"
    elif kind == "list":
        if not isinstance(value, list):
            return "must be a list, in [ ]"
    return ""


def case_problems(tool, number, case):
    """Returns a list of the mistakes in one of your cases."""
    if not isinstance(case, dict):
        return [f"your case {number}: must be {{ ... }}, like the sample case"]
    problems = []
    for name, kind in FIELDS[tool].items():
        if name not in case:
            problems.append(f'your case {number}: has no "{name}"')
        elif field_problem(case[name], kind):
            problems.append(f'your case {number}: "{name}" {field_problem(case[name], kind)}')
    if not problems:
        for problem in extra_problems(tool, case):
            problems.append(f"your case {number}: {problem}")
    return problems


def load_my_cases(tool):
    """Reads your cases from data/my_cases/<tool>.json and numbers them 1, 2, 3, ...
    If the file has a mistake, it prints what is wrong and returns None."""
    name = f"my_cases/{tool}.json"
    try:
        cases = load_data(name)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        print(f"data/{name} is not valid JSON: {error.msg}, on line {error.lineno}.")
        print("Look for a missing comma, quote mark or bracket on that line or the line before it.")
        return None
    if not isinstance(cases, list):
        print(f"data/{name} must be a list of cases: it starts with [ and ends with ].")
        return None
    problems = []
    for number, case in enumerate(cases, start=1):
        problems += case_problems(tool, number, case)
    if problems:
        print(f"data/{name} has mistakes:")
        for problem in problems:
            print("  " + problem)
        return None
    for number, case in enumerate(cases, start=1):
        case["id"] = number
    return cases


def run(check, cases, label):
    """Runs one check on each case and prints PASS or FAIL.
    Returns how many passed, or None if the tool is not written yet."""
    passed = 0
    for case in cases:
        try:
            ok, note = check(case)
        except NotImplementedError as error:
            print(error)
            return None
        except Exception as error:
            ok, note = False, f"error: {error}"
        if ok:
            passed += 1
            print(f"{label} {case['id']}: PASS  {note}")
        else:
            print(f"{label} {case['id']}: FAIL  {note}")
    return passed


def main():
    args = sys.argv[1:]
    if not args or args[0] not in CHECKS:
        print("Usage: python3 score.py TOOL [given | mine] [NUMBER]   TOOL is one of:", ", ".join(CHECKS))
        return
    tool = args[0]
    which = "all"
    if len(args) > 1 and args[1] in ("given", "mine"):
        which = args[1]
        args = args[:1] + args[2:]
    number = None
    if len(args) > 1:
        number = args[1]
        if which == "all":
            which = "given"

    given = []
    mine = []
    if which in ("all", "given"):
        given = load_data("cases.json")["cases"]
    if which in ("all", "mine"):
        mine = load_my_cases(tool)
        if mine is None:
            return
    count_mine = len(mine)
    if number is not None:
        given = [case for case in given if str(case["id"]) == number]
        mine = [case for case in mine if str(case["id"]) == number]
        if not given and not mine:
            if which == "given":
                print(f"There is no given case {number}.")
            else:
                print(f"There is no case {number} in data/my_cases/{tool}.json.")
            return
    if which == "mine" and not mine:
        print(f"data/my_cases/{tool}.json has no cases yet.")
        return

    passed_given = 0
    passed_mine = 0
    if given:
        passed_given = run(CHECKS[tool], given, "Case")
        if passed_given is None:
            return
    if mine:
        if given:
            print(f"Given cases: {passed_given} of {len(given)}")
        passed_mine = run(MINE[tool], mine, "Your case")
        if passed_mine is None:
            return
        if given:
            print(f"Your cases: {passed_mine} of {len(mine)}")
    print(f"Score: {passed_given + passed_mine} of {len(given) + len(mine)}")
    if which != "given" and number is None and count_mine < GOAL:
        print(f"You have {count_mine} of your {GOAL} cases in data/my_cases/{tool}.json.")


if __name__ == "__main__":
    main()
