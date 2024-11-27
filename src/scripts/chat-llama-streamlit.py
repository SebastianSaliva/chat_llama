import enum
import json

import requests
import streamlit as st


class Models(enum.Enum):
    LLAMA3_2 = "llama3.2"
    LLAMA3_1_8B = "llama3.1:8b"

    @classmethod
    def default(cls):
        return cls.LLAMA3_2


def send_request(model, prompt):
    base_url = "http://localhost:11434/api/generate"
    data = {"model": model, "prompt": prompt}
    response_text = ""
    try:
        response = requests.post(base_url, json=data, stream=True)
        response.raise_for_status()

        # Display a spinner while processing
        with st.spinner("Sending request..."):
            # Placeholder for response
            response_placeholder = st.empty()
            # Process streaming response
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    chunk = json_response.get("response", "")
                    response_text += chunk
                    # Update the response text area
                    response_placeholder.text_area(
                        "Response:", value=response_text, height=300
                    )
        st.success("Request completed successfully")

    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {str(e)}")


def main():
    st.title("Ollama Chat Interface")

    # Model selection
    model = st.selectbox("Model:", options=[model.value for model in Models], index=0)

    # Input text area
    prompt = st.text_area("Prompt:", height=150)

    # Send button
    if st.button("Send"):
        if prompt.strip() == "":
            st.warning("Please enter a prompt.")
        else:
            send_request(model, prompt)


if __name__ == "__main__":
    main()
