"""CityLink 311: joins the five tools into one assistant.

Run from the project folder:  python3 main.py
Type a report, "demo" to send the 10 reports in data/cases.json, or "quit" to stop.
Tickets are saved in data/tickets.json.
"""
from llm.details import extract_details
from llm.duplicates import find_duplicate
from llm.fact_check import check_reply
from llm.language import translate_inbound, translate_reply
from llm.privacy import redact
from llm.reply import fixed_reply, write_reply
from llm.sorter import sort_report
from llm.utils import load_data, save_data


def find_ticket(tickets, ticket_id):
    found = None
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            found = ticket
    return found


def new_ticket(tickets, text, language, sorted_report, details):
    ticket_number = len(tickets) + 1
    ticket = {
        "id": "T-" + str(ticket_number).zfill(4),
        "status": "open",
        "text": text,
        "language": language,
        "team": sorted_report["team"],
        "urgency": sorted_report["urgency"],
        "location": details["location"],
        "when": details["when"],
        "crew_needs": details["crew_needs"],
        "report_count": 1,
        "related_reports": [],
    }
    return ticket


def checked_reply(ticket, already_reported):
    """Writes a reply and fact checks it. Tries once more, then uses the fixed reply."""
    reply = write_reply(ticket, already_reported)
    result = check_reply(reply, ticket)
    if not result["supported"]:
        unsupported = []
        for claim in result["claims"]:
            if claim["source"] is None:
                unsupported.append(claim["claim"])
        reply = write_reply(ticket, already_reported, unsupported)
        result = check_reply(reply, ticket)
        if not result["supported"]:
            reply = fixed_reply(ticket)
    return reply


def resident_confirms(inbound):
    """Shows the resident their message in their own language and asks if it is right. English skips this."""
    confirmed = True
    if inbound["back_translation"] is not None:
        print('Is this your message? "' + inbound["back_translation"] + '" (y/n)')
        answer = input("> ").strip().lower()
        confirmed = answer in ("y", "yes")
    return confirmed


def handle_report(inbound):
    """Runs one report through every tool. The ticket is saved only if every step works."""
    # Step 1: understand the report
    redacted = redact(inbound["english"])
    text = redacted["redacted_text"]
    sorted_report = sort_report(text)
    details = extract_details(text)

    # Step 2: make a new ticket, or add the report to an open ticket
    tickets = load_data("tickets.json")
    duplicate = find_duplicate(text, sorted_report["team"], details["location"], tickets)
    duplicate_of = duplicate["duplicate_of"]
    if duplicate_of:
        ticket = find_ticket(tickets, duplicate_of)
        ticket["report_count"] += 1
        ticket["related_reports"].append(text)
    else:
        ticket = new_ticket(tickets, text, inbound["language"], sorted_report, details)
        tickets.append(ticket)

    # Step 3: write the reply in the resident's language
    reply = checked_reply(ticket, duplicate_of is not None)
    translated = translate_reply(reply, inbound["language"])

    # Step 4: save, now that every step has worked
    save_data("tickets.json", tickets)
    print(f"[{ticket['id']} | {ticket['team']} | {ticket['urgency']} | {ticket['location']}]")
    return translated["translated_reply"]


def run(message):
    try:
        inbound = translate_inbound(message)
        if resident_confirms(inbound):
            print(handle_report(inbound))
        else:
            print("Please type your message again.")
    except NotImplementedError as error:
        print("Not ready yet:", error)
    except (ValueError, ConnectionError) as error:
        print("Sorry, we couldn't process this. Please try again.", error)


def main():
    print("CityLink 311. Type a report, demo, or quit.")
    while True:
        message = input("\n> ").strip()
        if message.lower() in ("quit", "exit"):
            break
        if not message:
            continue
        if message.lower() == "demo":
            for case in load_data("cases.json")["cases"]:
                print("\n> " + case["report"])
                run(case["report"])
            continue
        run(message)


if __name__ == "__main__":
    main()
