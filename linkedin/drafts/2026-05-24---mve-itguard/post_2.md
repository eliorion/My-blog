---
angle: personal story
post_number: 2
blog_post: 2026-05-24 - mve-itguard
generated: 2026-05-26T14:28:03.160225
---

Someone needed a security camera system with no cloud dependency and no monthly bill.
I spent a few weeks building exactly that.

The project is called mve-itguard.
The hardware was already there. The question was: what runs on it?

Requirements:
→ Live camera feeds via RTSP
→ Real-time object detection (person, car, animal)
→ Home automation that reacts to detections
→ Secure remote access — without opening a single port

The stack that solved this:
- Frigate for video + AI detection
- Home Assistant as the automation hub
- Mosquitto as the MQTT message broker
- Zigbee2MQTT for wireless sensors
- Cloudflare Tunnel for remote access

Everything runs as Docker containers on one Debian server.
Config lives in Git. Deployments are automated.
No manual SSH. No commands run by hand on the machine.

The part I'm most proud of: cameras sit on an isolated network segment.
A compromised camera cannot reach the rest of the home network.
Blast radius — limited by design.

Now writing the full technical series.
Each post covers one decision and the reasoning behind it.

Post 1 is live — link in comments.

#selfhosted #homelab #devops #security #homeassistant
