from __future__ import annotations

import pytest

from scripts.adapters.registry import available_adapters, create_adapter


def test_mock_adapter_is_registered() -> None:
    assert "mock" in available_adapters()
    assert "openai_images" in available_adapters()
    assert "replicate" in available_adapters()
    assert create_adapter("mock").adapter_name == "mock"


def test_unknown_adapter_fails() -> None:
    with pytest.raises(ValueError, match="unknown adapter"):
        create_adapter("missing")
