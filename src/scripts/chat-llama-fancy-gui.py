import enum
import json
import tkinter as tk
from dataclasses import dataclass
from threading import Thread
from tkinter import scrolledtext, ttk
from typing import Optional

import requests


@dataclass
class ThemeColors:
    """Theme color configuration"""

    background: str
    foreground: str
    accent: str
    button_bg: str
    button_fg: str
    input_bg: str
    input_fg: str
    status_success: str
    status_error: str


class Theme:
    """Theme presets for the application"""

    DARK = ThemeColors(
        background="#2E3440",
        foreground="#ECEFF4",
        accent="#88C0D0",
        button_bg="#5E81AC",
        button_fg="#ECEFF4",
        input_bg="#3B4252",
        input_fg="#ECEFF4",
        status_success="#A3BE8C",
        status_error="#BF616A",
    )

    LIGHT = ThemeColors(
        background="#FFFFFF",
        foreground="#2E3440",
        accent="#5E81AC",
        button_bg="#88C0D0",
        button_fg="#2E3440",
        input_bg="#ECEFF4",
        input_fg="#2E3440",
        status_success="#A3BE8C",
        status_error="#BF616A",
    )

    FOREST = ThemeColors(
        background="#2B3834",
        foreground="#D3E1DD",
        accent="#8FAF9F",
        button_bg="#4A6670",
        button_fg="#D3E1DD",
        input_bg="#344B44",
        input_fg="#D3E1DD",
        status_success="#7FAE7B",
        status_error="#C25450",
    )


class Models(enum.Enum):
    """Available Llama models"""

    LLAMA3_2 = "llama3.2"
    LLAMA3_1_8B = "llama3.1:8b"

    @classmethod
    def default(cls):
        return cls.LLAMA3_2


class StyledText(scrolledtext.ScrolledText):
    """Custom styled text widget with modern appearance"""

    def __init__(self, master, theme: ThemeColors, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            bg=theme.input_bg,
            fg=theme.input_fg,
            insertbackground=theme.accent,
            selectbackground=theme.accent,
            selectforeground=theme.input_bg,
            font=("Consolas", 10),
            relief=tk.FLAT,
            padx=10,
            pady=10,
        )


class ModernButton(ttk.Button):
    """Custom styled button with hover effects"""

    def __init__(self, master, theme: ThemeColors, **kwargs):
        super().__init__(master, **kwargs)

        style = ttk.Style()
        style.configure(
            "Modern.TButton",
            background=theme.button_bg,
            foreground=theme.button_fg,
            padding=(20, 10),
            font=("Segoe UI", 10),
        )

        self.configure(style="Modern.TButton")


class StatusBar(ttk.Label):
    """Enhanced status bar with color-coded messages"""

    def __init__(self, master, theme: ThemeColors, **kwargs):
        super().__init__(master, **kwargs)
        self.theme = theme
        self.configure(
            background=theme.background, foreground=theme.foreground, padding=(10, 5)
        )

    def set_success(self, message: str):
        self.configure(foreground=self.theme.status_success)
        self.configure(text=message)

    def set_error(self, message: str):
        self.configure(foreground=self.theme.status_error)
        self.configure(text=message)

    def set_info(self, message: str):
        self.configure(foreground=self.theme.foreground)
        self.configure(text=message)


class OllamaGUI:
    def __init__(self, root, theme: Optional[ThemeColors] = None):
        self.root = root
        self.theme = theme or Theme.DARK
        self.setup_window()
        self.create_widgets()
        self.apply_theme()

    def setup_window(self):
        """Configure the main window"""
        self.root.title("Ollama Chat Interface")
        self.root.geometry("900x700")
        self.root.configure(bg=self.theme.background)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def create_widgets(self):
        """Create and arrange all GUI widgets"""
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.rowconfigure(3, weight=2)

        # Model selection
        self.create_model_selector()

        # Input area
        self.create_input_area()

        # Send button
        self.create_send_button()

        # Response area
        self.create_response_area()

        # Status bar
        self.create_status_bar()

    def create_model_selector(self):
        """Create the model selection dropdown"""
        label = ttk.Label(
            self.main_frame,
            text="Model:",
            background=self.theme.background,
            foreground=self.theme.foreground,
        )
        label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.model_var = tk.StringVar(value=Models.default().value)
        self.model_combo = ttk.Combobox(
            self.main_frame,
            textvariable=self.model_var,
            state="readonly",
            values=[model.value for model in Models],
        )
        self.model_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

    def create_input_area(self):
        """Create the input text area"""
        label = ttk.Label(
            self.main_frame,
            text="Prompt:",
            background=self.theme.background,
            foreground=self.theme.foreground,
        )
        label.grid(row=1, column=0, sticky=(tk.N, tk.W), padx=5, pady=5)

        self.input_text = StyledText(
            self.main_frame, theme=self.theme, height=10, wrap=tk.WORD
        )
        self.input_text.grid(
            row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5
        )

    def create_send_button(self):
        """Create the send button"""
        self.send_button = ModernButton(
            self.main_frame, theme=self.theme, text="Send", command=self.send_request
        )
        self.send_button.grid(row=2, column=1, sticky=tk.E, padx=5, pady=10)

    def create_response_area(self):
        """Create the response text area"""
        label = ttk.Label(
            self.main_frame,
            text="Response:",
            background=self.theme.background,
            foreground=self.theme.foreground,
        )
        label.grid(row=3, column=0, sticky=(tk.N, tk.W), padx=5, pady=5)

        self.response_text = StyledText(
            self.main_frame, theme=self.theme, height=15, wrap=tk.WORD
        )
        self.response_text.grid(
            row=3, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5
        )

    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = StatusBar(self.main_frame, theme=self.theme)
        self.status_bar.grid(
            row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5
        )

    def apply_theme(self):
        """Apply the current theme to all widgets"""
        style = ttk.Style()
        style.configure("TFrame", background=self.theme.background)
        style.configure(
            "TLabel", background=self.theme.background, foreground=self.theme.foreground
        )
        style.configure(
            "TCombobox",
            fieldbackground=self.theme.input_bg,
            background=self.theme.button_bg,
            foreground=self.theme.input_fg,
        )

    def send_request(self):
        """Handle the send request action"""
        self.send_button.state(["disabled"])
        self.status_bar.set_info("Sending request...")
        self.response_text.delete(1.0, tk.END)
        Thread(target=self._process_request, daemon=True).start()

    def _process_request(self):
        """Process the API request in a separate thread"""
        base_url = "http://localhost:11434/api/generate"
        prompt = self.input_text.get(1.0, tk.END).strip()
        model = self.model_var.get()
        data = {"model": model, "prompt": prompt}

        try:
            response = requests.post(base_url, json=data, stream=True)
            response.raise_for_status()

            full_response = ""
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    chunk = json_response.get("response", "")
                    full_response += chunk
                    self.root.after(0, self._update_response_text, chunk)

            self.root.after(
                0, lambda: self.status_bar.set_success("Request completed successfully")
            )

        except requests.exceptions.RequestException as e:
            error_message = f"Request failed: {str(e)}"
            self.root.after(0, lambda: self.status_bar.set_error(error_message))

        finally:
            self.root.after(0, lambda: self.send_button.state(["!disabled"]))

    def _update_response_text(self, text):
        """Update the response text area"""
        self.response_text.insert(tk.END, text)
        self.response_text.see(tk.END)


def main():
    root = tk.Tk()
    # You can easily switch themes here
    app = OllamaGUI(root, theme=Theme.DARK)  # Try Theme.LIGHT or Theme.FOREST
    root.mainloop()


if __name__ == "__main__":
    main()
