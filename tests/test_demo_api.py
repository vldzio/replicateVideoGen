"""StoryForge demo API tests (LLM stubbed at the llm.chat_json seam)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from demo_api import app as app_module, guard, llm  # noqa: E402

STORY = {
    "characters": [{"characterId": "char1", "name": "Ada", "characterPrompt": "A botanist in a patched coat"}],
    "scenes": [
        {"sceneNumber": 1, "sceneDescription": "She enters the ruins.", "characterIds": ["char1"], "settingPrompt": "Overgrown neon alley", "durationSeconds": 5},
        {"sceneNumber": 2, "sceneDescription": "The garden glows.", "characterIds": ["char1"], "settingPrompt": "Bioluminescent atrium", "durationSeconds": 8},
    ],
}


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(guard, "UPSTASH_URL", "")
    guard._mem.clear()
    return TestClient(app_module.app)


def test_story_includes_theme_and_returns_pipeline_shape(client, monkeypatch):
    seen = {}

    def fake(system, user, **kw):
        seen["user"] = user
        return STORY

    monkeypatch.setattr(llm, "chat_json", fake)
    r = client.post("/story", json={"theme": 'a "singing" lighthouse'})
    assert r.status_code == 200 and r.json()["success"] is True and r.json()["story"]["scenes"][1]["sceneNumber"] == 2
    assert "singing" in seen["user"] and '"singing"' not in seen["user"]  # quotes neutralised in the prompt


def test_default_theme_when_empty(client, monkeypatch):
    seen = {}
    monkeypatch.setattr(llm, "chat_json", lambda s, u, **k: seen.setdefault("u", u) and STORY)
    client.post("/story", json={})
    assert "botanist" in seen["u"]


def test_schema_accepts_pipeline_story_and_rejects_empty():
    import jsonschema

    jsonschema.validate(STORY, app_module.STORY_SCHEMA)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"characters": [], "scenes": []}, app_module.STORY_SCHEMA)


def test_llm_outage_is_503_and_limits_apply(client, monkeypatch):
    def boom(*a, **k):
        raise llm.LLMUnavailable("pool busy")

    monkeypatch.setattr(llm, "chat_json", boom)
    assert client.post("/story", json={}).status_code == 503
    monkeypatch.setattr(guard, "PER_IP_DAILY", 2)
    guard._mem.clear()
    monkeypatch.setattr(llm, "chat_json", lambda *a, **k: STORY)
    assert client.post("/story", json={}).status_code == 200
    assert client.post("/story", json={}).status_code == 429
