"""E2E tests — full pipeline with mocked Anthropic API."""

import argparse
import json
from unittest.mock import MagicMock

import pytest

import linkedin.generate as gen

SAMPLE_POSTS = [
    {"angle": "story", "hook": "I did a thing", "body": "Full body\nLine 2", "hashtags": ["homelab"]},
    {"angle": "lesson", "hook": "What I learned", "body": "Lesson body", "hashtags": ["devops", "learning"]},
]


def make_mock_client(posts: list = SAMPLE_POSTS) -> MagicMock:
    mock_content = MagicMock()
    mock_content.text = json.dumps({"posts": posts})
    mock_response = MagicMock()
    mock_response.content = [mock_content]
    client = MagicMock()
    client.messages.create.return_value = mock_response
    return client


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {"post": None, "force": False, "model": "claude-sonnet-4-6", "backend": "anthropic"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def blog_post(tmp_path):
    post = tmp_path / "posts" / "2026-01-01 - Test Post"
    post.mkdir(parents=True)
    (post / "index.md").write_text("---\ntitle: Test\n---\n\nContent here.")
    (post / "cover.svg").write_text("<svg/>")
    return post


@pytest.fixture()
def patched(tmp_path, monkeypatch, blog_post):
    drafts = tmp_path / "drafts"
    monkeypatch.setattr(gen, "BLOG_POSTS_DIR", blog_post.parent)
    monkeypatch.setattr(gen, "DRAFTS_DIR", drafts)
    return drafts


# --- generate ---


def test_generate_creates_all_draft_files(patched, blog_post):
    gen.cmd_generate(make_args(), make_mock_client())
    draft_dir = patched / gen.post_slug(blog_post)
    assert (draft_dir / "post_1.md").exists()
    assert (draft_dir / "post_2.md").exists()


def test_generate_copies_cover_svg(patched, blog_post):
    gen.cmd_generate(make_args(), make_mock_client())
    assert (patched / gen.post_slug(blog_post) / "cover.svg").exists()


def test_generate_draft_contains_body_and_hashtags(patched, blog_post):
    gen.cmd_generate(make_args(), make_mock_client())
    content = (patched / gen.post_slug(blog_post) / "post_1.md").read_text()
    assert "Full body" in content
    assert "#homelab" in content


def test_generate_draft_frontmatter_has_angle(patched, blog_post):
    gen.cmd_generate(make_args(), make_mock_client())
    content = (patched / gen.post_slug(blog_post) / "post_1.md").read_text()
    assert "angle: story" in content


def test_generate_skips_post_with_existing_draft(patched, blog_post):
    draft_dir = patched / gen.post_slug(blog_post)
    draft_dir.mkdir(parents=True)
    (draft_dir / "post_1.md").write_text("existing")
    client = make_mock_client()
    gen.cmd_generate(make_args(), client)
    client.messages.create.assert_not_called()


def test_generate_force_regenerates_existing_draft(patched, blog_post):
    draft_dir = patched / gen.post_slug(blog_post)
    draft_dir.mkdir(parents=True)
    (draft_dir / "post_1.md").write_text("existing")
    client = make_mock_client()
    gen.cmd_generate(make_args(force=True), client)
    client.messages.create.assert_called_once()


def test_generate_filter_matches_partial_name(patched, blog_post):
    client = make_mock_client()
    gen.cmd_generate(make_args(post="test"), client)
    client.messages.create.assert_called_once()


def test_generate_filter_no_match_exits(patched):
    with pytest.raises(SystemExit):
        gen.cmd_generate(make_args(post="nonexistent"), make_mock_client())


def test_generate_skips_dir_without_index_md(tmp_path, monkeypatch):
    post = tmp_path / "posts" / "2026-01-01 - Empty Post"
    post.mkdir(parents=True)
    monkeypatch.setattr(gen, "BLOG_POSTS_DIR", post.parent)
    monkeypatch.setattr(gen, "DRAFTS_DIR", tmp_path / "drafts")
    client = make_mock_client()
    gen.cmd_generate(make_args(), client)
    client.messages.create.assert_not_called()


def test_generate_claude_backend_uses_cli(patched, blog_post, monkeypatch):
    monkeypatch.setattr(gen, "generate_posts_via_cli", lambda c: SAMPLE_POSTS)
    gen.cmd_generate(make_args(backend="claude"), None)
    assert (patched / gen.post_slug(blog_post) / "post_1.md").exists()


def test_generate_api_error_is_caught_and_printed(patched, blog_post, capsys):
    client = MagicMock()
    client.messages.create.side_effect = Exception("API timeout")
    gen.cmd_generate(make_args(), client)
    assert "API timeout" in capsys.readouterr().err


# --- status ---


def test_status_shows_pending_for_new_post(patched, blog_post, capsys):
    gen.cmd_status()
    assert "pending" in capsys.readouterr().out


def test_status_shows_done_after_generate(patched, blog_post, capsys):
    gen.cmd_generate(make_args(), make_mock_client())
    capsys.readouterr()  # clear generate output
    gen.cmd_status()
    assert "done" in capsys.readouterr().out


def test_status_pending_count(patched, blog_post, capsys):
    gen.cmd_status()
    out = capsys.readouterr().out
    assert "0 done, 1 pending" in out


def test_status_done_count_after_generate(patched, blog_post, capsys):
    gen.cmd_generate(make_args(), make_mock_client())
    capsys.readouterr()
    gen.cmd_status()
    assert "1 done, 0 pending" in capsys.readouterr().out
