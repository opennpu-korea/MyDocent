from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from .furiosa import FuriosaLLMClient
from .llm_clients import NvidiaGpuLLMClient


@dataclass
class AppConfig:
    provider: str = "furiosa_npu"
    endpoint: str = "http://localhost:8000"
    model: str = "furiosa-llm"
    api_key: Optional[str] = None
    llm_endpoint: Optional[str] = None


def default_config_path() -> Path:
    return Path("config.json")


def save_config(config: AppConfig, path: Optional[Union[str, Path]] = None) -> Path:
    target = Path(path or default_config_path())
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "provider": config.provider,
                "endpoint": config.endpoint,
                "model": config.model,
                "api_key": config.api_key,
                "llm_endpoint": config.llm_endpoint,
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )
    return target


def load_config(path: Optional[Union[str, Path]] = None) -> AppConfig:
    target = Path(path or default_config_path())
    if not target.exists():
        return AppConfig()
    with target.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return AppConfig(
        provider=data.get("provider", "furiosa_npu"),
        endpoint=data.get("endpoint", "http://localhost:8000"),
        model=data.get("model", "furiosa-llm"),
        api_key=data.get("api_key"),
        llm_endpoint=data.get("llm_endpoint"),
    )


def resolve_llm_client(config: AppConfig):
    if config.provider == "nvidia_gpu":
        return NvidiaGpuLLMClient(endpoint=config.llm_endpoint or config.endpoint, api_key=config.api_key, model=config.model)
    return FuriosaLLMClient(endpoint=config.llm_endpoint or config.endpoint, api_key=config.api_key, model=config.model)
