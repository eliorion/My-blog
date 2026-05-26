---
angle: technical deep-dive
post_number: 4
blog_post: 2026-05-24 - mve-itguard
generated: 2026-05-26T14:28:03.162882
---

5 open-source tools. 1 Debian server. 0 ports exposed to the internet.
This is what a self-hosted home security platform looks like.

The stack:

Frigate — connects to IP cameras via RTSP, runs AI object detection on every frame. Person, car, animal — detected locally, in real time.

Mosquitto — MQTT broker. Frigate publishes detection events. Home Assistant subscribes. They never talk directly — the broker decouples them cleanly.

Home Assistant — central hub. Receives events, triggers automations, sends notifications, provides the mobile UI.

Zigbee2MQTT — bridges Zigbee sensors and devices into the MQTT network. One vendor-neutral bridge instead of a dozen proprietary hubs.

Cloudflare Tunnel — outbound connection from the server to Cloudflare's edge. No port forwarding. No exposed IP. Only Home Assistant is reachable remotely; everything else stays internal.

The network split matters:
Cameras live on an isolated segment.
The server bridges them to the automation layer.
A compromised camera cannot reach the rest of the home network.

All containers. All config in Git. All deployed automatically on push.

This is what it looks like to own your infrastructure instead of renting it.

Full series starting now — each post covers one layer of the system.
Link in comments.

#selfhosted #homeautomation #docker #homelab #frigate
