from pathlib import Path

from src.seogeo_reporter.prompt_inputs import load_prompt_set


def test_load_prompt_set_from_inline_only() -> None:
    payload = load_prompt_set(None, ["first question", "second question"])
    assert [p["prompt_id"] for p in payload] == ["P001", "P002"]
    assert payload[0]["prompt_text"] == "first question"


def test_load_prompt_set_from_csv(tmp_path: Path) -> None:
    csv_file = tmp_path / "prompts.csv"
    csv_file.write_text("prompt_text\nalpha\nbeta\n", encoding="utf-8")
    payload = load_prompt_set(str(csv_file), [])
    assert len(payload) == 2
    assert payload[1]["prompt_text"] == "beta"
