import os
from dotenv import load_dotenv
import google.generativeai as palm

load_dotenv()
TOKEN = os.getenv("PALM_API_KEY")
palm.configure(api_key=TOKEN)


def is_valid_response(response: palm.types.Completion) -> bool:
    if response.result is None:
        filters = response.filters
        safety_feedback = response.safety_feedback

        if filters is not None and len(filters) > 0:
            print(filters)
        if safety_feedback is not None and len(safety_feedback) > 0:
            print(safety_feedback)
        return False
    return True


def reply(history: list) -> str:
    defaults = {
        "model": "models/text-bison-001",
        "temperature": 1.0,
        "candidate_count": 1,
        "top_k": 100,
        "top_p": 0.95,
        "max_output_tokens": 3072,
        "stop_sequences": [],
        "safety_settings": [
            {"category": "HARM_CATEGORY_DEROGATORY", "threshold": 3},
            {"category": "HARM_CATEGORY_TOXICITY", "threshold": 3},
            {"category": "HARM_CATEGORY_VIOLENCE", "threshold": 3},
            {"category": "HARM_CATEGORY_SEXUAL", "threshold": 3},
            {"category": "HARM_CATEGORY_MEDICAL", "threshold": 3},
            {"category": "HARM_CATEGORY_DANGEROUS", "threshold": 3},
        ],
    }

    message_history = "\n".join(history)

    prompt = f"""
    Given this list of Discord messages,
    reply to the last message with a message of your own.

    {message_history}

    Reply: """

    response = palm.generate_text(**defaults, prompt=prompt)

    # Check for errors
    if not is_valid_response(response):
        return "Uh oh, something went wrong, try again later!"

    return response.result
