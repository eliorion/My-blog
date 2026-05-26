"""Unit tests for pure functions in generate.py."""

import json
from pathlib import Path
from unittest.mock import MagicMock

import linkedin.generate as gen


def test_post_slug_replaces_spaces():
    assert gen.post_slug(Path("2026-05-24 - mve-itguard")) == "2026-05-24---mve-itguard"


def test_post_slug_lowercases():
    assert gen.post_slug(Path("2026-05-24 - MyPost")) == "2026-05-24---mypost"


def test_has_draft_false_no_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(gen, "DRAFTS_DIR", tmp_path / "drafts")
    assert gen.has_draft(tmp_path / "2026-01-01 - Test") is False


def test_has_draft_false_empty_dir(tmp_path, monkeypatch):
    post = tmp_path / "2026-01-01 - Test"
    draft_dir = tmp_path / "drafts" / gen.post_slug(post)
    draft_dir.mkdir(parents=True)
    monkeypatch.setattr(gen, "DRAFTS_DIR", tmp_path / "drafts")
    assert gen.has_draft(post) is False


def test_has_draft_true_with_post_file(tmp_path, monkeypatch):
    post = tmp_path / "2026-01-01 - Test"
    draft_dir = tmp_path / "drafts" / gen.post_slug(post)
    draft_dir.mkdir(parents=True)
    (draft_dir / "post_1.md").write_text("content")
    monkeypatch.setattr(gen, "DRAFTS_DIR", tmp_path / "drafts")
    assert gen.has_draft(post) is True


def test_read_post_returns_content(tmp_path):
    post = tmp_path / "2026-01-01 - Test"
    post.mkdir()
    (post / "index.md").write_text("# Hello world")
    content, cover = gen.read_post(post)
    assert content == "# Hello world"
    assert cover is None


def test_read_post_returns_cover_path(tmp_path):
    post = tmp_path / "2026-01-01 - Test"
    post.mkdir()
    (post / "index.md").write_text("content")
    (post / "cover.svg").write_text("<svg/>")
    _, cover = gen.read_post(post)
    assert cover == str(post / "cover.svg")


def test_read_post_no_index_returns_empty(tmp_path):
    post = tmp_path / "2026-01-01 - Test"
    post.mkdir()
    content, cover = gen.read_post(post)
    assert content == ""
    assert cover is None


def test_write_drafts_creates_numbered_files(tmp_path, monkeypatch):
    monkeypatch.setattr(gen, "DRAFTS_DIR", tmp_path / "drafts")
    post = tmp_path / "2026-01-01 - Test"
    posts = [
        {"angle": "story", "hook": "Hook", "body": "Body", "hashtags": ["test"]},
        {"angle": "lesson", "hook": "Hook2", "body": "Body2", "hashtags": ["devops"]},
    ]
    gen.write_drafts(post, posts, None)
    draft_dir = tmp_path / "drafts" / gen.post_slug(post)
    assert (draft_dir / "post_1.md").exists()
    assert (draft_dir / "post_2.md").exists()
    assert not (draft_dir / "post_3.md").exists()


def test_write_drafts_hashtags_prefixed(tmp_path, monkeypatch):
    monkeypatch.setattr(gen, "DRAFTS_DIR", tmp_path / "drafts")
    post = tmp_path / "2026-01-01 - Test"
    gen.write_drafts(post, [{"angle": "a", "hook": "h", "body": "b", "hashtags": ["homelab", "devops"]}], None)
    content = (tmp_path / "drafts" / gen.post_slug(post) / "post_1.md").read_text()
    assert "#homelab" in content
    assert "#devops" in content


def test_write_drafts_copies_cover(tmp_path, monkeypatch):
    monkeypatch.setattr(gen, "DRAFTS_DIR", tmp_path / "drafts")
    post = tmp_path / "2026-01-01 - Test"
    cover = tmp_path / "cover.svg"
    cover.write_text("<svg/>")
    gen.write_drafts(post, [{"angle": "a", "hook": "h", "body": "b", "hashtags": []}], str(cover))
    assert (tmp_path / "drafts" / gen.post_slug(post) / "cover.svg").read_text() == "<svg/>"


def test_write_drafts_does_not_overwrite_existing_cover(tmp_path, monkeypatch):
    monkeypatch.setattr(gen, "DRAFTS_DIR", tmp_path / "drafts")
    post = tmp_path / "2026-01-01 - Test"
    draft_dir = tmp_path / "drafts" / gen.post_slug(post)
    draft_dir.mkdir(parents=True)
    (draft_dir / "cover.svg").write_text("<svg>original</svg>")
    cover = tmp_path / "cover.svg"
    cover.write_text("<svg>new</svg>")
    gen.write_drafts(post, [{"angle": "a", "hook": "h", "body": "b", "hashtags": []}], str(cover))
    assert (draft_dir / "cover.svg").read_text() == "<svg>original</svg>"


def _mock_client(response_text: str) -> MagicMock:
    mock_content = MagicMock()
    mock_content.text = response_text
    mock_response = MagicMock()
    mock_response.content = [mock_content]
    client = MagicMock()
    client.messages.create.return_value = mock_response
    return client


def test_generate_posts_parses_clean_json():
    payload = {"posts": [{"angle": "story", "hook": "H", "body": "B", "hashtags": ["homelab"]}]}
    result = gen.generate_posts("content", _mock_client(json.dumps(payload)), "claude-sonnet-4-6")
    assert len(result) == 1
    assert result[0]["angle"] == "story"


def test_generate_posts_strips_markdown_fence():
    payload = {"posts": [{"angle": "a", "hook": "h", "body": "b", "hashtags": []}]}
    wrapped = f"```json\n{json.dumps(payload)}\n```"
    result = gen.generate_posts("content", _mock_client(wrapped), "claude-sonnet-4-6")
    assert result[0]["angle"] == "a"


def test_generate_posts_strips_plain_fence():
    payload = {"posts": [{"angle": "a", "hook": "h", "body": "b", "hashtags": []}]}
    wrapped = f"```\n{json.dumps(payload)}\n```"
    result = gen.generate_posts("content", _mock_client(wrapped), "claude-sonnet-4-6")
    assert len(result) == 1
