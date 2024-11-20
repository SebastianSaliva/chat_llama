import enum, ollama

your_prompt = """test"""

usr_model_choice = None

PRINT_PROMPT = 0

base_url = "http://localhost:11434/api/generate"


class Models(enum.Enum):
    DEF_MoI: int = 0
    LLAMA3_2 = "llama3.2"
    LLAMA3_1_8B = "llama3.1:8b"
    LLAMA3_1_70B = "llama3.1:70b"
    LLAMA3_1_405B = "llama3.1:405b"
    l32 = LLAMA3_2
    l318 = LLAMA3_1_8B
    l3170 = LLAMA3_1_70B
    l31405 = LLAMA3_1_405B
    llamas = (l32, l318, l3170, l31405)
    default = llamas[DEF_MoI]


llama_models = Models.llamas.value

m_to_use = None
try:
    if usr_model_choice in (None, ""):
        m_to_use = (
            usr_model_choice
            if usr_model_choice in llama_models
            else Models.default.value
        )
    else:
        usr_model_choice = llama_models[int(usr_model_choice)]
        m_to_use = usr_model_choice
except:
    print("Invalid model, setting as default.")
    m_to_use = usr_model_choice = Models.default.value


usrpc = your_prompt if your_prompt not in (None, "") else "What is the meaning of life?"

print(f"Using model: {m_to_use}")

if PRINT_PROMPT:
    print(f"Prompt: {usrpc}")

print("waiting...\n")

response = ollama.chat(
    model=m_to_use,
    messages=[
        {
            "role": "user",
            "content": usrpc,
        },
    ],
)
print(response["message"]["content"])
