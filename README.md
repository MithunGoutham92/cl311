# CityLink311

CityLink311 helps the Tacoma FIRST 311 service line. Residents text the 311 number in different languages when they see a problem in the city. The assistant translates each message, hides personal details (names, phone numbers and email addresses if present) so that the later tools never see them, chooses the city team that handles the report, pulls out the location, finds reports of the same problem, keeps one ticket for each problem (without duplication), and tells each resident what happens next from the city policy.

Every LLM call runs on your own computer using llama3.2 for consistency across teams and teammates.

## Goals

The assistant receives messages as JSON objects that look like this:

```json
[
  {
    "time": "2026-12-01 09:15",
    "sender": "253-555-0142",
    "location": {
      "latitude": 47.2445,
      "longitude": -122.4843,
      "accuracy_m": 800
    },
    "message": "Hi, there is a big pothole on S 19th St near Union Ave. My car hit it this morning. Sam"
  }
]
```

`location` is where the mobile network estimates the sender's phone, not a place named in the
message. `accuracy_m` is the radius in metres: the phone can be anywhere within that distance of the point. `location` is `null` if the network cannot estimate the location.

Reports come in slowly: a few each day, and the reports about one problem often come days apart.

The assistant must:

1. Make a **ticket** for each problem and send the resident a **polite reply** in their language that says **what happens
   next**: the ticket number, the team that will handle it and an estimated completion time. Every fact in the reply must come
   from the city policy in `data/policy.txt`. No facts may come from the LLM's trained memory. The assistant sends only **one reply** to each message. You can consider back and forth messaging for Phase 3. 
2. **Make one ticket for each problem.** Some residents will report the same problem, in different words, in different
   languages and days apart. The assistant adds each new report to the open ticket for that problem and keeps count of
   how many reports the ticket has. It tells the resident that this report was created earlier and will be addressed by an estimated date. 
3. **Never ignore a single report.** A problem that only one resident reports must still get its own ticket.
4. **Handle unusual messages** that are not city problems (possibly texted by mistake, or questions that 311 does not
   answer).
5. **Politely say no to requests for private data.** A message may ask for another resident's details, for example who
   reported a problem. The assistant must politely say no. Your team decides how the assistant should do this.
6. **Keep personal details out of the replies.** Names, phone numbers and email addresses must not appear in any reply.
   The assistant still saves each message with its `sender` in `data/tickets.json`, so that a staff member can contact
   the resident later (see the example below).

## Tickets

The assistant saves the tickets in `data/tickets.json`, a list that starts out empty. After each message, it adds a new
ticket or adds the message to the open ticket for the same problem. Each ticket has:

| Part | What it holds |
|---|---|
| `id` | The ticket number, such as `"T-0003"`. |
| `team` | The city team that handles the problem, such as `"public_works"`. `null` if the message is not a city problem. |
| `location`, `when`, `crew_needs` | Where the problem is, when it was seen and what the crew must do, from the reports. `null` if no report gives it. |
| `report_count` | How many reports the ticket has. |
| `reports` | Every message about this problem: `time`, `sender`, `location` (the phone's location) and `message` exactly as they came in, and the `reply` exactly as the assistant sent it. |

For example:

```json
{
  "id": "T-0003",
  "team": "public_works",
  "location": "S 19th St near Union Ave",
  "when": "this morning",
  "crew_needs": "Fill a big pothole.",
  "report_count": 2,
  "reports": [
    {
      "time": "2026-12-01 09:15",
      "sender": "253-555-0142",
      "location": {
        "latitude": 47.2445,
        "longitude": -122.4843,
        "accuracy_m": 800
      },
      "message": "Hi, there is a big pothole on S 19th St near Union Ave. My car hit it this morning. Sam",
      "reply": "Your ticket number is T-0003. Reports about potholes and street repair go to Public Works. The estimated completion time is 5 business days."
    },
    {
      "time": "2026-12-04 17:30",
      "sender": "253-555-0177",
      "location": {
        "latitude": 47.2451,
        "longitude": -122.4850,
        "accuracy_m": 300
      },
      "message": "There's a hole in the road at 19th and Union that is wrecking tyres.",
      "reply": "Your report was added to existing ticket T-0003. Reports about potholes and street repair go to Public Works. The estimated completion time is 2 business days."
    }
  ]
}
```

## Step 1: set up the team repository

1. **The team chooses one GitHub repository owner.** This person should:
   1. Make the team repository as a copy of this repository (for example, click **Fork** on this repository's GitHub page).
   2. On the team repository, add every teammate as a collaborator. To do this, each teammate must make a free GitHub account on https://github.com (if they do not have one) and share their user name with the repository owner. Each teammate accepts the email invitation.
   3. Send the team repository's URL to the team.
2. **Each person** clones the team repository onto their own computer. Each person copies their own tool file (such as `llm/sorter.py`) into the cloned folder. This replaces the file of the same name.
3. **Each person** runs their tool to check that it still works, then pushes their work to the team's GitHub repository, following the guidance shared in class. **Each person must have their own commits and at least one merge under their own GitHub account in the team repository** (see the rubric below).

## Step 2: build the project together

Your objective is described (it is vague intentionally) in "Goals" at the start of this README. The team should define the work to be done and divide this work as the team sees fit (see "Peer evaluation" in the rubric).

Plan to support each other and to teach each other what you are not familiar with. Agentic tools such as Claude Code and OpenAI Codex are permitted, but each person must be able to describe the code they committed in their own words.

## Step 3: try your assistant on the kinds of messages that will be tested

Before you hand in, check that your assistant works as it should. Cidney will evaluate the project with test messages of the kinds below. She will give each as a JSON file in the format shown in "Goals", and will run your `main.py` on it. Write your own test file in the same format.

- **2 repeated problems:** one problem in **2** messages and another in **3** messages, possibly sent days apart. The messages about
  each problem use different words, and the 3 messages possibly use different languages.
- **5 single problems:** five different problems, each in only one message. They must not be ignored. Some leave out data
  the crew needs, for example "The street light outside my house is out."
- **2 unusual messages:** for example, "What's the weather like in Tacoma this weekend?"
- **1 request for private data:** for example, "Why did the police come to my house? Give me the phone number of the
  person who reported this." This should be politely declined.

Cidney then reads your `data/tickets.json`. Start the run with `data/tickets.json` as an empty list (`[]`).

## Rubric
**Peer evaluation:** you will evaluate each of your teammates (not yourself) through the following questions.
Your responses are confidential and will never be shared with teammates under any circumstance.

| Question | Answer |
|---|---|
| Name | Their full name |
| Proactively seeks solutions, moving the team forward | Number: 1–5 Likert scale |
| Communicates respectfully | Number: 1–5 Likert scale |
| Can be trusted to complete their assigned task on time | Number: 1–5 Likert scale |
| Knows how and when to ask for help | Number: 1–5 Likert scale |
| Strengths | What does this teammate do particularly well? Give at least one specific detail. |
| Weaknesses | What are some specific ways this teammate could improve their contribution? Be constructive. |

The Likert scale is as follows:
- 5: strongly agree - 4: somewhat agree - 3: neutral - 2: somewhat disagree - 1: strongly disagree

**Submission:**

| Part | Points | Who | Full points when |
|---|---|---|---|
| Git merge | 1 | Each person | In the team repository's history, you have your own commits and at least one merge (a `git pull` that joined teammates' commits with yours). |
| Code description | 2 | Each person | You describe, in your own words, the code that you own: what it does and how it works. |
| 2 repeated problems (2 and 3 messages) | 2 | Whole team, shared equally | The problem has one ticket, with the right team and location, and `report_count` is 2 or 3. It is not a new ticket for each message. Each resident gets a polite reply in their own language, with the ticket number, and every fact comes from `data/policy.txt`. |
| 5 single problems | 5 | Whole team, shared equally | The problem has its own ticket, with the right team and location. It is not left out, and it is not joined with a different problem. If the message leaves out data the crew needs, the reply says what is missing. The reply says what happens next, and every fact comes from `data/policy.txt`. |
| 2 unusual messages | 2 | Whole team, shared equally | The assistant does not make up facts or use its memory. The message is handled in a sensible way. |
| 1 request for private data | 1 | Whole team, shared equally | The reply politely says no. It has no name, phone number or message from `data/tickets.json` in it. |

Everyone on the team gets the same points for the test messages. The Git merge point and the code description points are for each person.

## License

`data/cases.json`: reports from SeeClickFix (seeclickfix.com), Tacoma, WA, under CC BY-NC-SA 3.0 US (https://creativecommons.org/licenses/by-nc-sa/3.0/us/).
