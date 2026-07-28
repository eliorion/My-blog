---
angle: tool spotlight
post_number: 5
blog_post: 2026-05-24 - mve-itguard
generated: 2026-05-26T14:28:03.163686
published: 2026-07-28T12:34:15.698191  # posted manually
---

Frigate does real-time AI object detection on your cameras — completely locally, no cloud, no API calls.
It might be the most underrated open-source project in home automation.

Here's what that means in practice:

You point it at an IP camera RTSP stream.
It processes every frame.
When it detects a person (or a car, or an animal), it publishes an event on MQTT.
Home Assistant picks that up and triggers whatever you've configured — notification, recording, light, alarm.

Nothing leaves your server.
No footage transmitted anywhere.

The tradeoff: it's computationally expensive.
Object detection isn't free. Before committing this setup for someone else's hardware, I ran a proof of concept specifically to validate the CPU could handle the load.

If it can't — you need a hardware accelerator (Coral TPU, GPU passthrough).
If it can — you have a private, real-time detection system that costs nothing per month.

Combined with Home Assistant and Mosquitto, Frigate becomes the sensor layer for a full automation stack:

Person detected → recording starts → notification sent → porch light on.
All locally. All in under a second.

Running it in production on mve-itguard.
Full breakdown in the series — link in comments.

#frigate #selfhosted #homeassistant #homelab #privacy
