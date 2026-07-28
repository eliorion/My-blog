"""E2E tests — full pipeline with mocked claude CLI."""

import argparse
from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest

import linkedin.generate as gen

SAMPLE_POSTS = [
    {"angle": "story", "hook": "I did a thing", "body": "Full body\nLine 2", "hashtags": ["homelab"]},
    {"angle": "lesson", "hook": "What I learned", "body": "Lesson body", "hashtags": ["devops", "learning"]},
]


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {"post": None, "force": False, "days": None}
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
def cli_mock(monkeypatch):
    mock = MagicMock(return_value=SAMPLE_POSTS)
    monkeypatch.setattr(gen, "generate_posts_via_cli", mock)
    return mock


@pytest.fixture()
def patched(tmp_path, monkeypatch, blog_post):
    drafts = tmp_path / "drafts"
    monkeypatch.setattr(gen, "BLOG_POSTS_DIR", blog_post.parent)
    monkeypatch.setattr(gen, "DRAFTS_DIR", drafts)
    return drafts


# --- generate ---


def test_generate_creates_all_draft_files(patched, blog_post, cli_mock):
    gen.cmd_generate(make_args())
    draft_dir = patched / gen.post_slug(blog_post)
    assert (draft_dir / "post_1.md").exists()
    assert (draft_dir / "post_2.md").exists()


def test_generate_copies_cover_svg(patched, blog_post, cli_mock):
    gen.cmd_generate(make_args())
    assert (patched / gen.post_slug(blog_post) / "cover.svg").exists()


def test_generate_draft_contains_body_and_hashtags(patched, blog_post, cli_mock):
    gen.cmd_generate(make_args())
    content = (patched / gen.post_slug(blog_post) / "post_1.md").read_text()
    assert "Full body" in content
    assert "#homelab" in content


def test_generate_draft_frontmatter_has_angle(patched, blog_post, cli_mock):
    gen.cmd_generate(make_args())
    content = (patched / gen.post_slug(blog_post) / "post_1.md").read_text()
    assert "angle: story" in content


def test_generate_skips_post_with_existing_draft(patched, blog_post, cli_mock):
    draft_dir = patched / gen.post_slug(blog_post)
    draft_dir.mkdir(parents=True)
    (draft_dir / "post_1.md").write_text("existing")
    gen.cmd_generate(make_args())
    cli_mock.assert_not_called()


def test_generate_force_regenerates_existing_draft(patched, blog_post, cli_mock):
    draft_dir = patched / gen.post_slug(blog_post)
    draft_dir.mkdir(parents=True)
    (draft_dir / "post_1.md").write_text("existing")
    gen.cmd_generate(make_args(force=True))
    cli_mock.assert_called_once()


def test_generate_filter_matches_partial_name(patched, blog_post, cli_mock):
    gen.cmd_generate(make_args(post="test"))
    cli_mock.assert_called_once()


def test_generate_filter_no_match_exits(patched, cli_mock):
    with pytest.raises(SystemExit):
        gen.cmd_generate(make_args(post="nonexistent"))


def test_generate_skips_dir_without_index_md(tmp_path, monkeypatch, cli_mock):
    post = tmp_path / "posts" / "2026-01-01 - Empty Post"
    post.mkdir(parents=True)
    monkeypatch.setattr(gen, "BLOG_POSTS_DIR", post.parent)
    monkeypatch.setattr(gen, "DRAFTS_DIR", tmp_path / "drafts")
    gen.cmd_generate(make_args())
    cli_mock.assert_not_called()


def test_generate_cli_error_is_caught_and_printed(patched, blog_post, monkeypatch, capsys):
    monkeypatch.setattr(gen, "generate_posts_via_cli", MagicMock(side_effect=RuntimeError("claude failed")))
    gen.cmd_generate(make_args())
    assert "claude failed" in capsys.readouterr().err


# --- --days filter ---


def test_days_filter_skips_old_post(tmp_path, monkeypatch, cli_mock):
    old_date = (date.today() - timedelta(days=30)).isoformat()
    post = tmp_path / "posts" / f"{old_date} - Old Post"
    post.mkdir(parents=True)
    (post / "index.md").write_text("content")
    monkeypatch.setattr(gen, "BLOG_POSTS_DIR", post.parent)
    monkeypatch.setattr(gen, "DRAFTS_DIR", tmp_path / "drafts")
    gen.cmd_generate(make_args(days=14))
    cli_mock.assert_not_called()


def test_days_filter_includes_recent_post(tmp_path, monkeypatch, cli_mock):
    recent_date = (date.today() - timedelta(days=3)).isoformat()
    post = tmp_path / "posts" / f"{recent_date} - Recent Post"
    post.mkdir(parents=True)
    (post / "index.md").write_text("content")
    monkeypatch.setattr(gen, "BLOG_POSTS_DIR", post.parent)
    monkeypatch.setattr(gen, "DRAFTS_DIR", tmp_path / "drafts")
    gen.cmd_generate(make_args(days=14))
    cli_mock.assert_called_once()


def test_days_none_includes_all_posts(patched, blog_post, cli_mock):
    gen.cmd_generate(make_args(days=None))
    cli_mock.assert_called_once()


# --- status ---


def test_status_shows_pending_for_new_post(patched, blog_post, capsys):
    gen.cmd_status()
    assert "pending" in capsys.readouterr().out


def test_status_shows_done_after_generate(patched, blog_post, cli_mock, capsys):
    gen.cmd_generate(make_args())
    capsys.readouterr()  # clear generate output
    gen.cmd_status()
    assert "done" in capsys.readouterr().out


def test_status_pending_count(patched, blog_post, capsys):
    gen.cmd_status()
    out = capsys.readouterr().out
    assert "0 done, 1 pending" in out


def test_status_done_count_after_generate(patched, blog_post, cli_mock, capsys):
    gen.cmd_generate(make_args())
    capsys.readouterr()
    gen.cmd_status()
    assert "1 done, 0 pending" in capsys.readouterr().out
