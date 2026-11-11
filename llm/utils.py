"""Functions that every tool in this project can use. Do not change this file.

load_data(name)       reads data/<name> (a JSON file) and returns a list or a dict
save_data(name, data) writes data to data/<name> as JSON
load_text(name)       reads data/<name> (a text file) and returns a str
split_sentences(text) returns the sentences of text as a list of str
read_json(text)       like json.loads, but returns {} if the text is not complete JSON
same_place(a, b)      True if two place descriptions share a street or place word
"""
import json
import re
from pathlib import Path

DATA_FOLDER = Path(__file__).parent.parent / "data"

# A sentence never ends after one of these, even if a space comes next.
ABBREVIATIONS = ("St.", "Ave.", "Dr.", "Mr.", "Mrs.", "Ms.", "No.", "Rd.", "Blvd.",
                 "e.g.", "i.e.", "U.S.", "a.m.", "p.m.")


def load_data(name):
    path = DATA_FOLDER / name
    text = path.read_text(encoding="utf-8")
    return json.loads(text)


def save_data(name, data):
    path = DATA_FOLDER / name
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8")


def load_text(name):
    path = DATA_FOLDER / name
    return path.read_text(encoding="utf-8")


def read_json(text):
    """Turns the LLM's JSON answer into a dict. Returns {} if the answer was cut off or is not JSON,
    so the tool's while loop simply asks again."""
    try:
        answer = json.loads(text)
    except json.JSONDecodeError:
        answer = {}
    if not isinstance(answer, dict):
        answer = {}
    return answer


def split_sentences(text):
    # Cut after . ! or ? when a space comes next.
    pieces = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = []
    for piece in pieces:
        piece = piece.strip()
        if not piece:
            continue
        # Join the piece back on if the last sentence ended with an abbreviation like "St."
        if sentences and sentences[-1].endswith(ABBREVIATIONS):
            sentences[-1] = sentences[-1] + " " + piece
        else:
            sentences.append(piece)
    return sentences


# Words that do not name a place on their own.
NOT_PLACE_WORDS = ("st", "sts", "street", "ave", "avenue", "rd", "road", "dr", "drive", "way", "blvd",
                   "n", "s", "e", "w", "ne", "nw", "se", "sw", "north", "south", "east", "west",
                   "the", "and", "of", "on", "at", "in", "by", "near", "from", "to", "corner", "side")


def place_words(text):
    words = []
    for word in re.findall(r"[a-z0-9]+", text.lower()):
        if word not in NOT_PLACE_WORDS and not (word.isdigit() and len(word) > 3):
            words.append(word)
    return words


def same_place(a, b):
    if not a or not b:
        return False
    words_b = place_words(b)
    for word in place_words(a):
        if word in words_b:
            return True
    return False


if __name__ == "__main__":
    print(split_sentences("The light on N 8th St. is out. Please fix it!"))
    print(same_place("64th from Pacific", "East 64th Street"), same_place("Pearl St", "N 8th St"))
