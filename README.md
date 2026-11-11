# CityLink311

CityLink311 helps the Tacoma FIRST 311 service line. A resident sends a report in any language. The assistant hides personal details, chooses the city team, pulls out the location, saves a ticket, and writes a reply that is checked against the city policy and translated back.

## What the assistant does

`python3 main.py` sends each report through the tools in this order:

1. **Language** (`translate_inbound`): finds the language and makes an English copy. If the report is not in
   English, the resident sees it translated back and types `y` if it is right.
2. **Privacy** (`redact`): hides names, phone numbers and email addresses.
3. **Sorter** (`sort_report`): chooses the city team and the urgency.
4. **Details** (`extract_details`): pulls out the location, the time and the work the crew must do.
5. **Duplicates** (`find_duplicate`, team file): checks if an open ticket already has this problem.
   If one does, the report is added to that ticket. If not, a new ticket is made.
6. **Reply** (`write_reply`, team file) writes the reply, and **Fact Checking** (`check_reply`) checks each
   sentence against the ticket and the city policy. If a sentence has no source, the reply is written again
   without it. If it still fails, `fixed_reply` gives a plain reply.
7. **Language** (`translate_reply`): translates the reply into the resident's language.
8. The ticket is saved in `data/tickets.json`, and the reply is shown.

Each tool is one function in one file in `llm/`. When every tool works, the whole assistant works.
`main.py` stops at the first tool that is not written yet and says "Not ready yet", so in Phase 1 you test
your own tool on its own (see "Test and score your tool").

## Get the code

1. On this project's GitHub page, click the green **Code** button, then **Download ZIP**.
2. Unzip the file. You get a folder whose name ends in `-main`, such as `CityLink311-main`.
   On Windows, "Extract All" can put it inside a second folder with the same name: use the folder that has `main.py` in it.
3. In VS Code, choose **File > Open Folder...** and pick that folder. The VS Code Terminal then starts in it.
   Run every command from this folder.

## Set up

1. Install Ollama from https://ollama.com and open it. It must be running whenever you use the project.
2. In the Terminal, run `ollama pull llama3.2`. This downloads the model (about 2 GB), once.
3. Install the Python package: `python3 -m pip install -r requirements.txt`.
4. Check it: run `python3 main.py`. It starts and waits for you to type. Until the tools are written, it says
   "Not ready yet" for anything you type. Type `quit` to stop.

On Windows, type `py` where this README says `python3`. For example: `py -m pip install -r requirements.txt`.

## Your work, step by step

Use your own file and tool name where this list says `llm/sorter.py` and `sorter`.

1. Do "Get the code" and "Set up" above.
2. Find your role in "Find your file". Open your tool file and read its docstring.
3. Read your role in "Your role" below. It says what score.py checks and gives tips.
4. In your tool file, write the four prompt parts (`instruction`, `context`, `examples`, `output_format`).
   They start as TODO.
5. Follow the TODO comments in your function. Write the code, then delete the `raise NotImplementedError` line.
6. Run `python3 llm/sorter.py` and try your function on one input.
7. Run `python3 score.py sorter given`. Change your prompt and code until most of the 10 given
   cases pass.
8. Write your 30 test cases in your cases file (see the section "Write 30 test cases of your own"), then run
   `python3 score.py sorter` for the score out of 40.
9. Save your tool file and your cases file. Phase 2 then joins every tool in `main.py`.

## Find your file

Find your role in the table. You change two files: you write your function in your tool file, and you write
30 test cases in your cases file. **Do not change any other file.**

| Role | Your tool file | Write this function | Your cases file | Score it |
|---|---|---|---|---|
| CL311.A Sorter | `llm/sorter.py` | `sort_report` | `data/my_cases/sorter.json` | `python3 score.py sorter` |
| CL311.B Privacy | `llm/privacy.py` | `redact` | `data/my_cases/privacy.json` | `python3 score.py privacy` |
| CL311.C Fact Checking | `llm/fact_check.py` | `check_reply` | `data/my_cases/fact_check.json` | `python3 score.py fact_check` |
| CL311.D Details | `llm/details.py` | `extract_details` | `data/my_cases/details.json` | `python3 score.py details` |
| CL311.E Language | `llm/language.py` | `translate_inbound`, `translate_reply` | `data/my_cases/language.json` | `python3 score.py language` |

## What is in your file

Open your file. From top to bottom it has:

1. **The docstring**, the text between the `"""` marks at the top: the inputs, the
   output and a sample of each. Do not change the function name, its inputs or the keys of its output,
   because `main.py` and `score.py` use them.
2. **The import lines.** The `if __package__:` lines let the file run on its own and from `main.py`.
   Leave them as they are. To use one more function from `utils.py`, add its name to both import lines.
3. **Four prompt parts**: `instruction`, `context`, `examples` and `output_format`. Each one says TODO. Write them.
4. **`build_prompt`**: already written. It puts the four parts and the input into one prompt. Do not change it.
5. **Your function.** It has TODO comments with the steps, and `raise NotImplementedError(...)`.
   Write the function, then delete the `raise NotImplementedError` line.
6. **A small test** at the bottom, under `if __name__ == "__main__":`. Some tests ask you to type an input.

You may add your own helper functions to your file, and you may import more from `utils.py`.

## How every tool works

Every tool follows the same steps:

1. Make the prompt: `prompt = build_prompt(...)`, with your function's inputs.
2. Call the LLM:
   `output = ollama.generate(model="llama3.2", prompt=prompt, format="json", options={"num_predict": 500})`.
   `format="json"` makes the LLM answer in JSON. `num_predict` stops an answer that runs on too long.
3. Turn the answer into a dict: `answer = read_json(output.response)`. If the answer is not complete JSON,
   you get `{}`.
4. Check the answer: are all the keys there, and are the values allowed (for example, a word from your list)?
   If not, ask again. Use a `while` loop that stops after 3 tries.
5. If the 3rd answer is still not usable, `raise ValueError("...")` with a short message. `main.py` then says
   "Sorry, we couldn't process this" and saves nothing.

Some tools need more than one LLM call, or code that does part of the work. The TODO comments in your
function and the tips for your role below say how.

## Your role

### CL311.A Sorter: `llm/sorter.py`

Write `sort_report(report)`. It gets the English report, with personal details hidden, and returns `{"team": ..., "urgency": ...}`.

- **score.py passes a given case when** `team` is the team in the source data. `urgency` is not scored, but `main.py` saves it in the ticket.
- **Your cases** (`data/my_cases/sorter.json`): `report`: a report, as a resident would write it. `team`: the team that should get it, one of the words in `TEAMS`.
- **Tip:** `TEAMS` and `URGENCIES` at the top of your file list the allowed words. Say in `context` what each team handles.
- **Tip:** Check that both answers are words from those lists. If not, ask again.

### CL311.B Privacy: `llm/privacy.py`

Write `redact(text)`. It gets the English report and returns `{"redacted_text": ..., "items_hidden": ...}`.

- **score.py passes a given case when** both tests work. Test 1 is the report alone: at least half of its place words must still be there. Test 2 adds a made-up contact line (Jordan Example, a phone number and an email): the name, the phone number and the email must be gone, and at least half of the place words must still be there.
- **Your cases** (`data/my_cases/privacy.json`): `text`: a report with made-up personal details in it (or none). `must_hide`: every name, phone number and email in the text, copied exactly. `must_keep`: the place words that must stay, such as "Fawcett". score.py runs `redact` once on `text`: nothing in `must_hide` may be left, and at least half of `must_keep` must stay.
- **Tip:** Do not ask the LLM to rewrite the text, because it changes other words too. Ask it to list the items it finds, one list for each key of `PLACEHOLDERS`, plus a list of places (streets, addresses, landmarks). Your code then replaces each item in the text with its `PLACEHOLDERS` value.
- **Tip:** The LLM often lists things that are not personal details, such as "Someone" or a street name. Your code should skip them. `NOT_NAMES` at the top of your file is a start, and the TODO comments in your function list more cases.

### CL311.C Fact Checking: `llm/fact_check.py`

Write `check_reply(reply, ticket)`. It gets a draft reply and its ticket, and returns `{"supported": ..., "claims": [...]}`, with one claim for each sentence.

- **score.py passes a given case when** the source of every sentence (`ticket`, `policy` or None) is the one in the answer key, and `supported` is right. score.py gives your tool replies with known answers, so you can work before the Reply team file is written.
- **Your cases** (`data/my_cases/fact_check.json`): `reply`: a draft reply. `ticket_id` and `team`: the ticket it answers. `sources`: one value for each sentence of the reply, `"ticket"`, `"policy"` or `null` (nothing backs it up).
- **Tip:** Check one sentence at a time: `split_sentences` in `utils.py` splits the reply. One small question for each sentence is easier for the LLM than one big question.
- **Tip:** `SOURCES` lists the three answers the LLM may give. Read the policy with `load_text("policy.txt")`. A sentence with the ticket number comes from the ticket.

### CL311.D Details: `llm/details.py`

Write `extract_details(report)`. It gets the English report, with personal details hidden, and returns `{"location": ..., "when": ..., "crew_needs": ...}`.

- **score.py passes a given case when** `location` has the street name from the report in it. A report with no street name always passes.
- **Your cases** (`data/my_cases/details.json`): `report`: a report. `location_words`: words that must be in `location`, such as `["26th", "Proctor"]`. Use `[]` for a report that names no place: then `location` must be None.
- **Tip:** Ask the LLM to copy the location and the time word for word from the report, and to give `null` when the report has none. `read_json` turns `null` into None.
- **Tip:** Check that all three keys are there. If not, ask again.

### CL311.E Language: `llm/language.py`

Write two functions. `translate_inbound(message)` gets the resident's message and returns `{"language": ..., "english": ..., "back_translation": ...}`. `translate_reply(reply, language)` gets the English reply and returns `{"translated_reply": ...}`.

- **score.py passes a given case when** an English report stays English (`language` starts with "en" and `back_translation` is None), and a reply translated into Spanish still has the ticket number and is not the same as the English reply.
- **Your cases** (`data/my_cases/language.json`): `message`: a message in any language. `language`: its language, such as "English" or "Spanish". `keep`: words that must stay the same in the English text, such as a street name. score.py checks that your tool tells English from other languages, keeps those words, gives a back-translation for a message that is not in English, and translates a reply into that language with its ticket number kept.
- **Tip:** `build_prompt(task, message)` takes a task, such as "Find the language and translate to English." or "Translate to Spanish.", so one prompt serves both functions.
- **Tip:** If the message is in English, return it exactly as the resident wrote it. A reworded copy makes Privacy and Details work less well.
- **Tip:** The 10 test reports are all in English. Try other languages with `python3 llm/language.py`.

## Write 30 test cases of your own

The 10 given cases in `data/cases.json` are only a start. Write 30 more for your tool, so that it is
tested on 40 cases.

1. Open your cases file, such as `data/my_cases/sorter.json`. It starts with one sample case.
   Change the sample, or replace it with your own.
2. Add your cases after it. Each case is `{ ... }` with the fields that "Your role" lists for your
   tool. Put a comma between two cases. The file looks like this:

```json
[
  {
    "report": "There is a deep pothole in the right lane of S 19th St near Union Ave.",
    "team": "public_works",
    "note": "Sample case: change it or replace it with your own."
  },
  {
    "report": "...",
    "team": "..."
  }
]
```

3. Run `python3 score.py sorter mine` (with your tool's name). score.py first checks your file. If a
   case has a missing field or a wrong value, it tells you which one and scores nothing until you fix it.

Rules for good test cases:

- Decide the right answer for each case before you run your tool. Never change an answer to match
  what your tool says.
- Cover every team, and make at least a quarter of your cases hard: cases where a careless
  tool would go wrong.
- Do not copy your test cases, or the 10 given cases, into the `examples` of your prompt.
  A test shows something only if the tool has not seen the answer.
- Personal details must be made up. Use phone numbers from 555-0100 to 555-0199 and email addresses that end in @example.com: they are kept for examples.
- score.py does not use the fields `source` and `note`. Use `note` to say why a case is hard.

## Team files (Phase 2)

In Phase 2 the whole team writes these files together. Do not change them in Phase 1.
They have TODO steps, like the role files.

- `llm/duplicates.py`: `find_duplicate(report, team, location, tickets)` returns `{"duplicate_of": ...}`: the id of an open ticket with the same problem, or None.
- `llm/reply.py`: `write_reply(ticket, already_reported, unsupported)` returns the reply (a str). `fixed_reply(ticket)` returns a plain reply with no LLM call.

## Test and score your tool

Use your own tool's name in these commands.

- `python3 llm/sorter.py`: runs the small test at the bottom of your tool file.
- `python3 score.py sorter`: runs your tool on the 10 given cases, then on your own cases.
  Each case prints PASS or FAIL and what your tool returned. At the end you see the score on the given
  cases, the score on yours, and the total, such as `Score: 34 of 40`.
- `python3 score.py sorter given` or `python3 score.py sorter mine`: only the given cases,
  or only yours.
- `python3 score.py sorter 3` runs given case 3, and `python3 score.py sorter mine 3` runs
  your case 3. One case is quicker while you change your prompt.
- An LLM does not give the same answer every time. Run score.py two or three times before you decide that a
  change made your prompt better.

What the messages mean:

- `data/my_cases/... is not valid JSON ... on line 5`: look for a missing comma, quote mark or bracket on that
  line or the line before it. JSON needs double quotes, and `true`, `false` and `null` in small letters.
- `data/my_cases/... has mistakes`: the list under it says which of your cases has a missing field or a
  wrong value.
- `... is not written yet`: your function still has `raise NotImplementedError`.
- `FAIL  error: ...`: your function stopped with an error on that case. If it is your ValueError, the LLM gave
  3 answers your code could not use: make `output_format` and `examples` clearer.
- `Failed to connect to Ollama`: open the Ollama app, then try again.
- `model "llama3.2" not found`: run `ollama pull llama3.2`.
- `No module named 'ollama'`: do step 3 of "Set up".

To try another local model, download it with `ollama pull <name>` (the names are on https://ollama.com/search)
and change `model="llama3.2"` in your file. Score both models and compare.

## Files you do not change

- `llm/utils.py` (utils is short for utilities): functions that every tool can use. `load_data(name)` and `load_text(name)` read a file in `data/`, `save_data(name, data)` writes one, `split_sentences(text)` gives a list of sentences, and `read_json(text)` turns the LLM's answer into a dict (`{}` if the answer is not complete JSON). `same_place(a, b)` is True if two place descriptions share a street or place word.
- `llm/__init__.py`: makes `llm/` a package, so `main.py` can import your tool.
- `score.py`: checks your tool on the given cases and on yours.
- `main.py`: joins all the tools.
- `data/`: the given cases and the data that `main.py` saves. In `data/my_cases/`, change only your own cases file.

## Run the whole assistant

`python3 main.py`. Type a report, `demo` to send the 10 test reports, or `quit`.

## Data

- `data/cases.json`: 10 labelled test reports, used by score.py
- `data/policy.txt`: the city policy that Fact Checking and the reply use
- `data/tickets.json`: the saved tickets (main.py writes it; it starts as [])
- `data/my_cases/`: one cases file for each tool, such as `data/my_cases/sorter.json`. Each starts with one sample; students add their own.

## Licence and sources

The 10 reports come from SeeClickFix (seeclickfix.com), Tacoma, WA, under CC BY-NC-SA 3.0 US (https://creativecommons.org/licenses/by-nc-sa/3.0/us/). Use them for non-commercial teaching only, keep this notice, and share changed copies under the same licence. policy.txt is a summary in our own words of https://tacoma.gov/services/tacoma-first-311-services/ (checked 2026-11-09).

## Notes

- The 10 reports are all in English, so the Language score only checks that English stays English and that a Spanish reply keeps the ticket number. Try other languages by hand with `python3 main.py`.
- Each Privacy test adds a made-up contact line (Jordan Example, 206-555-01xx, jordan@example.com), because the public reports have no personal details. Privacy is also tested on the report alone: street names must not be hidden.
- This project uses the local model llama3.2. Every call has `options={"num_predict": 500}`, so an answer that
  runs on too long stops instead of hanging your program.
