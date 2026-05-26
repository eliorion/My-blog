#!/usr/bin/env python3
"""LinkedIn post generator — transforms blog posts into LinkedIn drafts."""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

import anthropic

BLOG_POSTS_DIR = Path("blog/content/11 - Posts")
DRAFTS_DIR = Path("linkedin/drafts")

SYSTEM_PROMPT = """You are a LinkedIn content strategist who transforms technical blog posts into engaging LinkedIn posts.

Rules:
- Each post must open with a strong hook (first 2 lines visible before "see more")
- Max 1500 characters per post body (not counting hashtags)
- Use line breaks generously for readability
- 3-5 relevant hashtags per post, no # prefix in the hashtags array
- Pick a different angle for each post: personal story, technical deep-dive, key lesson, hot take, tool spotlight, behind-the-scenes
- No corporate buzzwords. Write like a human sharing real experience.
- Return valid JSON only, no markdown code block wrapper.

Output format (strict):
{
  "posts": [
    {
      "angle": "string",
      "hook": "string (first 2 lines, the visible preview before 'see more')",
      "body": "string (full post text including the hook, with \\n for line breaks)",
      "hashtags": ["tag1", "tag2", "tag3"]
    }
  ]
}"""


def find_posts() -> list[Path]:
    if not BLOG_POSTS_DIR.exists():
        print(f"Error: {BLOG_POSTS_DIR} not found. Run from repo root.", file=sys.stderr)
        sys.exit(1)
    return sorted(p for p in BLOG_POSTS_DIR.iterdir() if p.is_dir())


def post_slug(post_dir: Path) -> str:
    return post_dir.name.lower().replace(" ", "-")


def has_draft(post_dir: Path) -> bool:
    draft_dir = DRAFTS_DIR / post_slug(post_dir)
    return draft_dir.exists() and any(draft_dir.glob("post_*.md"))


def read_post(post_dir: Path) -> tuple[str, str | None]:
    index = post_dir / "index.md"
    if not index.exists():
        return "", None
    content = index.read_text(encoding="utf-8")
    cover = post_dir / "cover.svg"
    return content, str(cover) if cover.exists() else None


def generate_posts(content: str, client: anthropic.Anthropic, model: str) -> list[dict]:
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"Transform this blog post into multiple LinkedIn posts:\n\n{content}",
            }
        ],
    )
    raw = response.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw.strip())
    data = json.loads(raw)
    return data["posts"]


def write_drafts(post_dir: Path, posts: list[dict], cover_path: str | None):
    draft_dir = DRAFTS_DIR / post_slug(post_dir)
    draft_dir.mkdir(parents=True, exist_ok=True)

    for i, post in enumerate(posts, 1):
        hashtags = " ".join(f"#{tag.lstrip('#')}" for tag in post["hashtags"])
        full_text = f"{post['body']}\n\n{hashtags}"
        md = (
            f"---\nangle: {post['angle']}\n"
            f"post_number: {i}\n"
            f"blog_post: {post_dir.name}\n"
            f"generated: {datetime.now().isoformat()}\n"
            f"---\n\n{full_text}\n"
        )
        (draft_dir / f"post_{i}.md").write_text(md, encoding="utf-8")

    if cover_path:
        dest = draft_dir / "cover.svg"
        if not dest.exists():
            shutil.copy(cover_path, dest)

    print(f"  -> {len(posts)} posts written to {draft_dir}")


def cmd_generate(args, client: anthropic.Anthropic):
    posts = find_posts()

    if args.post:
        posts = [p for p in posts if args.post.lower() in p.name.lower()]
        if not posts:
            print(f"No post matching '{args.post}'")
            sys.exit(1)

    for post_dir in posts:
        if has_draft(post_dir) and not args.force:
            print(f"Skip {post_dir.name}  (draft exists, use --force to regenerate)")
            continue

        content, cover = read_post(post_dir)
        if not content:
            continue

        print(f"Processing: {post_dir.name}")
        try:
            linkedin_posts = generate_posts(content, client, args.model)
            write_drafts(post_dir, linkedin_posts, cover)
        except Exception as e:
            print(f"  Error: {e}", file=sys.stderr)


def cmd_status():
    posts = find_posts()
    print(f"\n{'STATUS':<12} {'POST'}")
    print("-" * 70)
    for post_dir in posts:
        label = "done" if has_draft(post_dir) else "pending"
        print(f"{label:<12} {post_dir.name}")
    pending = sum(1 for p in posts if not has_draft(p))
    done = len(posts) - pending
    print(f"\n{done} done, {pending} pending\n")


def main():
    parser = argparse.ArgumentParser(description="LinkedIn post generator from Hugo blog posts")
    sub = parser.add_subparsers(dest="cmd")

    gen = sub.add_parser("generate", aliases=["g"], help="Generate LinkedIn posts")
    gen.add_argument("--post", "-p", help="Filter by post name/date (partial match)")
    gen.add_argument("--force", "-f", action="store_true", help="Regenerate even if draft exists")
    gen.add_argument(
        "--model",
        "-m",
        default="claude-sonnet-4-6",
        help="Claude model to use (default: claude-sonnet-4-6)",
    )

    sub.add_parser("status", aliases=["s"], help="Show processing status")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    if args.cmd in ("status", "s"):
        cmd_status()
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    cmd_generate(args, client)


if __name__ == "__main__":
    main()
