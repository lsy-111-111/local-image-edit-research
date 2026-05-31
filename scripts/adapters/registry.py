from __future__ import annotations

from scripts.adapters.base import ImageEditAdapter
from scripts.adapters.mock_adapter import MockImageEditAdapter
from scripts.adapters.openai_images_adapter import OpenAIImagesAdapter
from scripts.adapters.replicate_adapter import ReplicateAdapter


ADAPTERS = {
    "mock": MockImageEditAdapter,
    "openai_images": OpenAIImagesAdapter,
    "replicate": ReplicateAdapter,
}


def available_adapters() -> list[str]:
    return sorted(ADAPTERS)


def create_adapter(name: str) -> ImageEditAdapter:
    try:
        adapter_cls = ADAPTERS[name]
    except KeyError as exc:
        choices = ", ".join(available_adapters())
        raise ValueError(f"unknown adapter: {name}; available adapters: {choices}") from exc
    return adapter_cls()
