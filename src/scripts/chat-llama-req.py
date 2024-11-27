import enum
import json
import sys

import requests


your_prompt = """test"""


class Models(enum.Enum):
    LLAMA3_2 = "llama3.2"
    LLAMA3_1_8B = "llama3.1:8b"
    LLAMAS = (LLAMA3_2, LLAMA3_1_8B)

    @classmethod
    def default(cls):
        return cls.LLAMA3_2.value


def get_llama(i):
    if i in range(0, 2):
        return Models.LLAMAS.value[i]
    else:
        return Models.default()


def make_request(prompt, model):
    global res
    url = "http://localhost:11434/api/generate"
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


def main(args=None):
    prompt = None

    if len(args) == 2 and args[1] in ("0", "1"):
        model = get_llama(int(args[1]))
        print(f"using {model}")
        prompt = input(">>> ")

    if len(args) == 1:
        prompt = input(">>> ")
        if len(prompt) == 1 and prompt in ("0", "1"):
            model = get_llama(int(prompt))
            print(f"using {model}")
            prompt = input(">>> ")
        if len(prompt) < 3:
            print("quiting.")
            return

    prompt = args[1] if prompt is None else prompt
    model = get_llama(int(args[2])) if len(args) == 3 else Models.default()

    res = make_request(prompt, model)
    if res:
        print(res)


if __name__ == "__main__":
    main(sys.argv)
