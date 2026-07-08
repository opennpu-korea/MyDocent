from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from .config import AppConfig, load_config, save_config


class SettingsWindow(tk.Tk):
    def __init__(self, config_path: str | Path | None = None) -> None:
        super().__init__()
        self.title("MyDocent Settings")
        self.geometry("480x320")
        self.config_path = Path(config_path or "config.json")
        self.config = load_config(self.config_path)

        self.provider_var = tk.StringVar(value=self.config.provider)
        self.endpoint_var = tk.StringVar(value=self.config.endpoint)
        self.model_var = tk.StringVar(value=self.config.model)
        self.api_key_var = tk.StringVar(value=self.config.api_key or "")
        self.llm_endpoint_var = tk.StringVar(value=self.config.llm_endpoint or self.config.endpoint)

        self._build_ui()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Hardware Provider").grid(row=0, column=0, sticky="w")
        provider_combo = ttk.Combobox(frame, textvariable=self.provider_var, state="readonly")
        provider_combo["values"] = ["furiosa_npu", "nvidia_gpu"]
        provider_combo.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)

        ttk.Label(frame, text="Endpoint").grid(row=1, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.endpoint_var).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=4)

        ttk.Label(frame, text="LLM Endpoint").grid(row=2, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.llm_endpoint_var).grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=4)

        ttk.Label(frame, text="Model").grid(row=3, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.model_var).grid(row=3, column=1, sticky="ew", padx=(8, 0), pady=4)

        ttk.Label(frame, text="API Key").grid(row=4, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.api_key_var).grid(row=4, column=1, sticky="ew", padx=(8, 0), pady=4)

        ttk.Button(frame, text="Save", command=self._save).grid(row=5, column=0, columnspan=2, pady=(12, 0))

        frame.columnconfigure(1, weight=1)

    def _save(self) -> None:
        config = AppConfig(
            provider=self.provider_var.get(),
            endpoint=self.endpoint_var.get(),
            model=self.model_var.get(),
            api_key=self.api_key_var.get() or None,
            llm_endpoint=self.llm_endpoint_var.get() or None,
        )
        save_config(config, self.config_path)
        self.config = config
        self.destroy()


if __name__ == "__main__":
    SettingsWindow().mainloop()
