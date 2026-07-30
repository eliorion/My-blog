#!/usr/bin/env python3
"""Publish LinkedIn drafts to a member profile via the LinkedIn Posts API.

Commands:
  auth              One-time OAuth flow, saves .linkedin_token.json (60-day token)
  next              Publish the oldest unpublished draft post
  publish <file>    Publish a specific post_N.md
  status            Show publish queue state
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

_HERE = Path(__file__).parent
DRAFTS_DIR = _HERE / "drafts"
TOKEN_FILE = _HERE / ".linkedin_token.json"
ENV_FILE = _HERE / ".env"

API_VERSION = "202606"
REDIRECT_PORT = 8917
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}/callback"
AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
POSTS_URL = "https://api.linkedin.com/rest/posts"
IMAGES_INIT_URL = "https://api.linkedin.com/rest/images?action=initializeUpload"
SCOPES = "openid profile w_member_social"

# LinkedIn "little text format" reserved characters that must be escaped in commentary.
# '#' is left alone so hashtags keep working.
_ESCAPE_CHARS = "\\|{}@[]()<>"


def _load_env() -> dict:
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    env.update({k: v for k, v in os.environ.items() if k.startswith("LINKEDIN_")})
    return env


_USER_AGENT = "linkedin-drip/1.0 (blog publishing; +https://eliorion.github.io/My-blog)"


def _http_json(url: str, data: bytes | None = None, headers: dict | None = None, method: str | None = None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": _USER_AGENT, **(headers or {})}, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, dict(resp.headers), resp.read().decode()


# ---------------------------------------------------------------- auth


def _grab_code_via_server() -> str:
    code_holder = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            code_holder["code"] = qs.get("code", [""])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h2>Token received - back to the terminal.</h2>")

        def log_message(self, *a):
            pass

    with HTTPServer(("localhost", REDIRECT_PORT), Handler) as srv:
        srv.handle_request()
    return code_holder.get("code", "")


def cmd_auth(args):
    env = _load_env()
    client_id = env.get("LINKEDIN_CLIENT_ID")
    client_secret = env.get("LINKEDIN_CLIENT_SECRET")
    if not client_id or not client_secret:
        print(f"Set LINKEDIN_CLIENT_ID / LINKEDIN_CLIENT_SECRET (env or {ENV_FILE})", file=sys.stderr)
        sys.exit(1)

    if args.code:
        code = args.code
    else:
        params = urllib.parse.urlencode(
            {
                "response_type": "code",
                "client_id": client_id,
                "redirect_uri": REDIRECT_URI,
                "scope": SCOPES,
            }
        )
        print("Open this URL in your browser and authorize:\n")
        print(f"  {AUTH_URL}?{params}\n")
        print(f"Waiting for the redirect on {REDIRECT_URI} ...")
        print("(If the redirect can't reach this machine, rerun with: publish.py auth --code <code from URL>)")
        code = _grab_code_via_server()
        if not code:
            print("No code received.", file=sys.stderr)
            sys.exit(1)

    body = urllib.parse.urlencode(
        {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": REDIRECT_URI,
        }
    ).encode()
    _, _, raw = _http_json(TOKEN_URL, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
    tok = json.loads(raw)
    access_token = tok["access_token"]
    expires_at = (datetime.now() + timedelta(seconds=tok.get("expires_in", 0))).isoformat()

    _, _, raw = _http_json(USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"})
    person_urn = f"urn:li:person:{json.loads(raw)['sub']}"

    TOKEN_FILE.write_text(
        json.dumps(
            {
                "access_token": access_token,
                "expires_at": expires_at,
                "person_urn": person_urn,
            },
            indent=2,
        )
    )
    print(f"Token saved to {TOKEN_FILE}")
    print(f"Person URN: {person_urn}")
    print(f"Expires: {expires_at}  (re-run auth before then)")
    print("\nFor GitHub Actions, set repo secrets:")
    print("  LINKEDIN_ACCESS_TOKEN  = <the access_token value>")
    print(f"  LINKEDIN_PERSON_URN    = {person_urn}")


def _load_token() -> tuple[str, str]:
    env = _load_env()
    if env.get("LINKEDIN_ACCESS_TOKEN") and env.get("LINKEDIN_PERSON_URN"):
        return env["LINKEDIN_ACCESS_TOKEN"], env["LINKEDIN_PERSON_URN"]
    if not TOKEN_FILE.exists():
        print("No token. Run: publish.py auth", file=sys.stderr)
        sys.exit(1)
    tok = json.loads(TOKEN_FILE.read_text())
    if datetime.fromisoformat(tok["expires_at"]) < datetime.now():
        print("Token expired. Run: publish.py auth", file=sys.stderr)
        sys.exit(1)
    return tok["access_token"], tok["person_urn"]


# ---------------------------------------------------------------- drafts


def _split_frontmatter(text: str) -> tuple[str, str]:
    m = re.match(r"^---\n(.*?)\n---\n\n?(.*)$", text, re.DOTALL)
    if not m:
        raise ValueError("no frontmatter")
    return m.group(1), m.group(2)


def _escape_commentary(text: str) -> str:
    return "".join(f"\\{c}" if c in _ESCAPE_CHARS else c for c in text)


def _draft_posts() -> list[Path]:
    posts = []
    for d in sorted(p for p in DRAFTS_DIR.iterdir() if p.is_dir()):
        posts.extend(sorted(d.glob("post_*.md")))
    return posts


def _is_published(path: Path) -> bool:
    fm, _ = _split_frontmatter(path.read_text(encoding="utf-8"))
    return "published:" in fm


def _rest_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": API_VERSION,
        "Content-Type": "application/json",
    }


def _upload_image(token: str, person_urn: str, png: Path) -> str:
    init = json.dumps({"initializeUploadRequest": {"owner": person_urn}}).encode()
    _, _, raw = _http_json(IMAGES_INIT_URL, data=init, headers=_rest_headers(token))
    value = json.loads(raw)["value"]
    req = urllib.request.Request(
        value["uploadUrl"],
        data=png.read_bytes(),
        method="PUT",
        headers={"Authorization": f"Bearer {token}", "User-Agent": _USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=60):
        pass
    return value["image"]


def publish_file(path: Path):
    token, person_urn = _load_token()
    text = path.read_text(encoding="utf-8")
    fm, body = _split_frontmatter(text)
    if "published:" in fm:
        print(f"Already published: {path}", file=sys.stderr)
        sys.exit(1)

    post: dict = {
        "author": person_urn,
        "commentary": _escape_commentary(body.strip()),
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    png = path.with_suffix(".png")
    if png.exists():
        angle = re.search(r"^angle:\s*(.+)$", fm, re.MULTILINE)
        alt = angle.group(1).strip() if angle else "cover"
        try:
            post["content"] = {"media": {"id": _upload_image(token, person_urn, png), "altText": alt}}
        except urllib.error.HTTPError as e:
            print(f"Image upload failed ({e.code}): {e.read().decode()[:300]} - posting text-only", file=sys.stderr)

    payload = json.dumps(post).encode()

    try:
        status, headers, _ = _http_json(POSTS_URL, data=payload, headers=_rest_headers(token))
    except urllib.error.HTTPError as e:
        print(f"LinkedIn API error {e.code}: {e.read().decode()[:500]}", file=sys.stderr)
        sys.exit(1)

    post_urn = headers.get("x-restli-id", "")
    new_fm = f"{fm}\npublished: {datetime.now().isoformat()}\npost_urn: {post_urn}"
    path.write_text(f"---\n{new_fm}\n---\n\n{body}", encoding="utf-8")
    print(f"Published {path.relative_to(_HERE)} -> {post_urn}")


def _published_today(posts: list[Path]) -> bool:
    today = datetime.now().date().isoformat()
    for post in posts:
        fm, _ = _split_frontmatter(post.read_text(encoding="utf-8"))
        m = re.search(r"^published:\s*(\d{4}-\d{2}-\d{2})", fm, re.MULTILINE)
        if m and m.group(1) == today:
            return True
    return False


def cmd_next():
    posts = _draft_posts()
    if _published_today(posts):
        print("Already published today - nothing to do.")
        return
    for post in posts:
        if not _is_published(post):
            publish_file(post)
            return
    print("Queue empty - nothing to publish.")


def cmd_status():
    posts = _draft_posts()
    done = sum(1 for p in posts if _is_published(p))
    print(f"{done}/{len(posts)} published, {len(posts) - done} queued")
    for post in posts:
        if not _is_published(post):
            print(f"next -> {post.relative_to(_HERE)}")
            break


def main():
    parser = argparse.ArgumentParser(description="Publish LinkedIn drafts via the Posts API")
    sub = parser.add_subparsers(dest="cmd")

    auth = sub.add_parser("auth", help="OAuth flow, save token")
    auth.add_argument("--code", help="Authorization code (manual fallback)")

    sub.add_parser("next", help="Publish oldest unpublished draft")

    pub = sub.add_parser("publish", help="Publish a specific draft file")
    pub.add_argument("file", type=Path)

    sub.add_parser("status", help="Show queue state")

    args = parser.parse_args()
    if args.cmd == "auth":
        cmd_auth(args)
    elif args.cmd == "next":
        cmd_next()
    elif args.cmd == "publish":
        publish_file(args.file)
    elif args.cmd == "status":
        cmd_status()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
