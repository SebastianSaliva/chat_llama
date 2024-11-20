import enum
import json
import tkinter as tk
from threading import Thread
from tkinter import scrolledtext, ttk

import requests


class Models(enum.Enum):
    LLAMA3_2 = "llama3.2"
    LLAMA3_1_8B = "llama3.1:8b"

    @classmethod
    def default(cls):
        return cls.LLAMA3_2


class OllamaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ollama Chat Interface")
        self.root.geometry("800x600")

        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Model selection
        ttk.Label(main_frame, text="Model:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5
        )
        self.model_var = tk.StringVar(value=Models.default().value)
        model_combo = ttk.Combobox(
            main_frame, textvariable=self.model_var, state="readonly"
        )
        model_combo["values"] = [model.value for model in Models]
        model_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

        # Input text area
        ttk.Label(main_frame, text="Prompt:").grid(
            row=1, column=0, sticky=(tk.N, tk.W), padx=5, pady=5
        )
        self.input_text = scrolledtext.ScrolledText(main_frame, height=10, wrap=tk.WORD)
        self.input_text.grid(
            row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5
        )

        # Send button
        self.send_button = ttk.Button(
            main_frame, text="Send", command=self.send_request
        )
        self.send_button.grid(row=2, column=1, sticky=tk.E, padx=5, pady=5)

        # Response text area
        ttk.Label(main_frame, text="Response:").grid(
            row=3, column=0, sticky=(tk.N, tk.W), padx=5, pady=5
        )
        self.response_text = scrolledtext.ScrolledText(
            main_frame, height=15, wrap=tk.WORD
        )
        self.response_text.grid(
            row=3, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5
        )

        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_bar.grid(
            row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5
        )

    def send_request(self):
        # Disable send button and update status
        self.send_button.state(["disabled"])
        self.status_var.set("Sending request...")
        self.response_text.delete(1.0, tk.END)

        # Create and start thread for API request
        Thread(target=self._process_request, daemon=True).start()

    def _process_request(self):
        base_url = "http://localhost:11434/api/generate"
        prompt = self.input_text.get(1.0, tk.END).strip()
        model = self.model_var.get()
        data = {"model": model, "prompt": prompt}

        try:
            response = requests.post(base_url, json=data, stream=True)
            response.raise_for_status()

            # Process streaming response
            full_response = ""
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    chunk = json_response.get("response", "")
                    full_response += chunk
                    # Update response text in main thread
                    self.root.after(0, self._update_response_text, chunk)

            self.root.after(
                0, self._request_completed, "Request completed successfully"
            )

        except requests.exceptions.RequestException as e:
            error_message = f"Request failed: {str(e)}"
            self.root.after(0, self._request_completed, error_message)

    def _update_response_text(self, text):
        self.response_text.insert(tk.END, text)
        self.response_text.see(tk.END)

    def _request_completed(self, status_message):
        self.send_button.state(["!disabled"])
        self.status_var.set(status_message)


if __name__ == "__main__":
    root = tk.Tk()
    app = OllamaGUI(root)
    root.mainloop()
