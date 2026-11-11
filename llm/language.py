"""CL311.E Language: lets residents write in their own language, and answers them in it.

Function: translate_inbound(message)

Input:
    message (str): the resident's message, in any language.
    Sample: "Hay un bache enorme en la calle S 38th."

Output (dict):
    language (str): the language name in English, such as "English" or "Spanish".
    english (str): the message in English (the same text if it is already English).
    back_translation (str or None): the English text translated back into the resident's language,
                                    so the resident can confirm it. None if the message is in English.
    Sample: {"language": "Spanish", "english": "There is a huge pothole on S 38th Street.",
             "back_translation": "Hay un bache enorme en la calle S 38th."}

Function: translate_reply(reply, language)

Input:
    reply (str): the reply in English.
    language (str): the resident's language, from translate_inbound.
    Sample: "Your ticket number is T-0001.", "Spanish"

Output (dict):
    translated_reply (str): the reply in that language. Ticket numbers, street names and phone
                            numbers stay exactly the same. English replies are returned unchanged.
    Sample: {"translated_reply": "Su número de ticket es T-0001."}

Raises ValueError if the LLM's answer can't be used.
Test it: python3 llm/language.py      Score it: python3 score.py language
"""
import ollama

# This lets the file work both as "python3 llm/language.py" and as "from llm.language import ...".
if __package__:
    from .utils import read_json
else:
    from utils import read_json

instruction = """TODO: say who the LLM is and what it must do."""

context = """TODO: the labels, rules and facts the LLM needs."""

examples = """TODO: a few examples of input and the exact output you want."""

output_format = """TODO: the exact JSON the LLM must return."""


def build_prompt(task, message):
    prompt = f"""<instruction>{instruction}</instruction>
<context>{context}</context>
<examples>{examples}</examples>
<output_format>{output_format}</output_format>
<query>Task: {task} Message: {message}
Output:</query>"""
    return prompt


def translate_inbound(message):
    # TODO: write this function. The docstring at the top of this file is the contract.
    # 1. build_prompt(task, message) takes a task, such as "Find the language and translate to English."
    #    Call ollama.generate(model="llama3.2", prompt=prompt, format="json", options={"num_predict": 500})
    #    and read the answer with read_json. Ask for two keys, language and text. Ask again (up to 3
    #    tries) if a key is missing or empty, then raise ValueError.
    # 2. If the language is English, keep the message exactly as the resident wrote it.
    #    back_translation is None.
    # 3. Otherwise ask again with the task "Translate to <language>." and the English text.
    #    Its text is the back_translation.
    # 4. Return {"language": ..., "english": ..., "back_translation": ...}.
    # Both functions call the LLM in the same way, so a helper function such as ask(task, message) saves code.
    raise NotImplementedError("translate_inbound is not written yet")


def translate_reply(reply, language):
    # TODO: write this function. The docstring at the top of this file is the contract.
    # 1. If the language is English, the reply stays as it is.
    # 2. Otherwise build_prompt("Translate to <language>.", reply), call the LLM and read_json in the same
    #    way as translate_inbound.
    # 3. Return {"translated_reply": ...}.
    raise NotImplementedError("translate_reply is not written yet")


if __name__ == "__main__":
    message = input("Message: ")
    inbound = translate_inbound(message)
    print(inbound)
    print(translate_reply("Your ticket number is T-0001.", inbound["language"]))
