---
angle: behind-the-scenes
post_number: 5
blog_post: 2026-02-23 - Why learn linux before containerisation
generated: 2026-05-26T14:21:55.400422
---

I'm starting to document every significant bug I hit.
Not for others. For future me.

After spending 3 days debugging a devcontainer issue that turned out to be a memory constraint in a Linux VM — not a script error — I realized I had no systematic way to work through it.

I went straight to the code. The problem was in the infrastructure.

So I'm building a personal issue template. When I hit something significant:

→ Context (what I was doing, what changed recently)
→ Environment (tools, versions, OS, resource limits)
→ Symptoms (exactly what failed, exact error)
→ Root cause (what was actually wrong)
→ Resolution (what fixed it)
→ Lessons learned (what I'll do differently)

This isn't about being thorough for the sake of it.
It's about building a debugging mindset over time.

The goal isn't to remember every fix. It's to get faster at identifying the right layer to investigate.

In platform engineering, understanding the system matters more than writing the code.

The knowledge base is the engineering.

#devops #platformengineering #linux #learning #homelab
