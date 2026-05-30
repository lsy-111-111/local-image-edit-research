from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


STATUSES = {"success", "failed", "filtered", "timeout", "rate_limited", "invalid_input"}


@dataclass(frozen=True)
class ImageEditRequest:
    source_image: str
    mask: str
    prompt: str
    seed: int | None
    config: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ImageEditResult:
    output_path: str
    raw_response_path: str
    status: str
    runtime_seconds: float
    cost_usd: float
    seed_effective: int | None
    error: str = ""


class ImageEditAdapter(Protocol):
    adapter_name: str

    def generate(self, request: ImageEditRequest) -> ImageEditResult:
        """Generate or dry-run one image editing request."""
