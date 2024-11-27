import enum
import json
import tkinter as tk
from threading import Thread
from tkinter import scrolledtext, ttk

import requests


class SystemPrompts(enum.Enum):
    DEFAULT = "You are a helpful, respectful and honest assistant."
    ASSISTANT = "You are a helpful, respectful, and honest assistant."
    USRPRO1 = "You are a professional assistant helping a software engineering student."


class StaticSystemPrompts(enum.Enum):
    FIX = "Help me fix this."
    SUMMARIZE = "Summarize this in 100 words or less."
    EXPLAIN = "Explain this in simple terms."
    TRANSLATE = "Translate this into English."
    CODE = "Write code for this."
    TEST = "Write a test for this."
    DEBUG = "Debug this code."
    OPTIMIZE = "Optimize this code."
    REFACTOR = "Refactor this code."
    DOCUMENT = "Document this code."
    EXPAND = "Expand this into a full program."
    SIMPLIFY = "Simplify this code."
    EXPLORE = "Explore this topic."
    RESEARCH = "Research this topic."


class Models(enum.Enum):
    LLAMA3_2 = "llama3.2"
    LLAMA3_1_8B = "llama3.1:8b"

    @classmethod
    def default(cls):
        return cls.LLAMA3_1_8B


class OllamaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ollama Chat Interface")
        self.root.geometry("800x800")

        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=0)
        main_frame.columnconfigure(1, weight=1)
        for i in range(9):
            main_frame.rowconfigure(i, weight=1)

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

        # System Prompt Label
        ttk.Label(main_frame, text="System Prompt:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5
        )
        # System Prompt Combobox
        self.system_prompt_var = tk.StringVar()
        self.system_prompt_combobox = ttk.Combobox(
            main_frame, textvariable=self.system_prompt_var, state="readonly"
        )
        self.system_prompt_combobox["values"] = [
            prompt.name for prompt in SystemPrompts
        ]
        self.system_prompt_combobox.grid(
            row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        self.system_prompt_combobox.bind(
            "<<ComboboxSelected>>", self.on_system_prompt_selected
        )

        # System Prompt Text
        self.system_prompt_text = scrolledtext.ScrolledText(
            main_frame, height=5, wrap=tk.WORD
        )
        self.system_prompt_text.grid(
            row=1, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5
        )

        # Static Prompt Label
        ttk.Label(main_frame, text="Static Prompt:").grid(
            row=3, column=0, sticky=tk.W, padx=5, pady=5
        )
        # Static Prompt Combobox
        self.static_prompt_var = tk.StringVar()
        self.static_prompt_combobox = ttk.Combobox(
            main_frame, textvariable=self.static_prompt_var, state="readonly"
        )
        self.static_prompt_combobox["values"] = [
            prompt.name for prompt in StaticSystemPrompts
        ]
        self.static_prompt_combobox.grid(
            row=4, column=0, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        self.static_prompt_combobox.bind(
            "<<ComboboxSelected>>", self.on_static_prompt_selected
        )

        # Static Prompt Text
        self.static_prompt_text = scrolledtext.ScrolledText(
            main_frame, height=5, wrap=tk.WORD
        )
        self.static_prompt_text.grid(
            row=3, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5
        )

        # Input text area Label
        ttk.Label(main_frame, text="Prompt:").grid(
            row=5, column=0, sticky=tk.W, padx=5, pady=5
        )
        # Input text area
        self.input_text = scrolledtext.ScrolledText(main_frame, height=5, wrap=tk.WORD)
        self.input_text.grid(
            row=5, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5
        )

        # Send button
        self.send_button = ttk.Button(
            main_frame, text="Send", command=self.send_request
        )
        self.send_button.grid(row=6, column=1, sticky=tk.E, padx=5, pady=5)

        # Response text area Label
        ttk.Label(main_frame, text="Response:").grid(
            row=7, column=0, sticky=tk.W, padx=5, pady=5
        )
        # Response text area
        self.response_text = scrolledtext.ScrolledText(
            main_frame, height=15, wrap=tk.WORD
        )
        self.response_text.grid(
            row=7, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5
        )

        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_bar.grid(
            row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5
        )

    def on_system_prompt_selected(self, event):
        selected_prompt_name = self.system_prompt_var.get()
        selected_prompt = SystemPrompts[selected_prompt_name].value
        self.system_prompt_text.delete(1.0, tk.END)
        self.system_prompt_text.insert(tk.END, selected_prompt)

    def on_static_prompt_selected(self, event):
        selected_prompt_name = self.static_prompt_var.get()
        selected_prompt = StaticSystemPrompts[selected_prompt_name].value
        self.static_prompt_text.delete(1.0, tk.END)
        self.static_prompt_text.insert(tk.END, selected_prompt)

    def send_request(self):
        # Disable send button and update status
        self.send_button.state(["disabled"])
        self.status_var.set("Sending request...")
        self.response_text.delete(1.0, tk.END)

        # Create and start thread for API request
        Thread(target=self._process_request, daemon=True).start()

    def _process_request(self):
        base_url = "http://localhost:11434/api/generate"
        model = self.model_var.get()
        sys_p = self.system_prompt_text.get(1.0, tk.END).strip()
        usr_p_static = self.static_prompt_text.get(1.0, tk.END).strip()
        usr_p = self.input_text.get(1.0, tk.END).strip()

        sys_p_prefix = "Treat this as a system prompt:\n"
        usr_p_prefix = "Treat this as a user prompt:\n"

        a = 1 if sys_p else 0
        b = 1 if usr_p_static else 0
        c = 1 if usr_p else 0
        prompting_case = (a, b, c)

        match prompting_case:
            case (0, 0, 0):
                prompt = "No prompt provided"
            case (0, 0, 1):
                prompt = usr_p
            case (0, 1, 0):
                prompt = usr_p_static
            case (0, 1, 1):
                prompt = f"{usr_p_static}\n{usr_p}"
            case (1, 0, 0):
                prompt = sys_p
            case (1, 0, 1):
                prompt = f"{sys_p_prefix}{sys_p}\n{usr_p_prefix}{usr_p}"
            case (1, 1, 0):
                prompt = f"{sys_p_prefix}{sys_p}\n{usr_p_prefix}{usr_p_static}"
            case (1, 1, 1):
                prompt = (
                    f"{sys_p_prefix}{sys_p}\n{usr_p_prefix}{usr_p_static}\n\n{usr_p}"
                )

        data = {"model": model, "prompt": prompt}

        try:
            response = requests.post(base_url, json=data, stream=True)
            response.raise_for_status()

            # Process streaming response
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    chunk = json_response.get("response", "")
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
