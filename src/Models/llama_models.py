import enum


class Models(enum.Enum):
    LLAMA3_1_8B = "llama3.1:8b"
    LLAMA3_1_70B = "llama3.1:70b"
    LLAMA3_1_405B = "llama3.1:405b"
    LLAMA3_2 = "llama3.2"

    l318 = LLAMA3_1_8B
    l3170 = LLAMA3_1_70B
    l31405 = LLAMA3_1_405B
    l32 = LLAMA3_2

    llamas = (l32, l318, l3170, l31405)

    use = llamas[0]
