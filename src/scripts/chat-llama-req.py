import enum
import json

import requests

base_url = "http://localhost:11434/api/generate"
your_prompt = """test"""


class Models(enum.Enum):
    LLAMA3_2 = "llama3.2"
    LLAMA3_1_8B = "llama3.1:8b"

    @classmethod
    def default(cls):
        return cls.LLAMA3_2


def send_request():
    global res
    prompt = your_prompt
    model = Models.default().value
    url = base_url
    data = {"model": model, "prompt": prompt}

    try:
        response = requests.post(url, json=data, stream=True)
        response.raise_for_status()

        # Ollama streams responses, so we need to process them accordingly
        full_response = ""
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                full_response += json_response.get("response", "")

        return full_response

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


res = send_request()
if res:
    print(res)
