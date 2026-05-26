---
angle: tool spotlight
post_number: 2
blog_post: 2026-03-24 - Containerise Python application
generated: 2026-05-26T14:25:07.681526
---

I almost pushed a container with dozens of known vulnerabilities.
Trivy caught them before I could.

When I containerized my Python app, my first instinct was: build → run → ship.

The DevSecOps way adds one step: build → scan → fix → run → ship.

Trivy is a container security scanner. One command:

trivy image --format table --severity CRITICAL,HIGH backend:00

It shows every CRITICAL and HIGH CVE in your image, where it came from, and whether a fix exists.

What I found: most vulnerabilities weren't in my code. They were in the base image — python:latest built on Debian, with dozens of tools my app never needed.

The fix was switching base images:
→ python:latest (440MB, lots of CVEs)
→ python:3.13-slim (smaller, fewer CVEs)
→ python:3.13-alpine (minimal, attack surface nearly gone)

Security isn't something you bolt on after shipping. It's a step in the build pipeline.

Add Trivy to your workflow. Free, fast, and it will find things you didn't know were there.

#devsecops #docker #trivy #containersecurity #devops
