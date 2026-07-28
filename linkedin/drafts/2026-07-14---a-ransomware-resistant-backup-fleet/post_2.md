---
angle: technical deep-dive
post_number: 2
blog_post: 2026-07-14 - A ransomware-resistant backup fleet
generated: 2026-07-27T21:29:46.142854
---

S3 credentials leaked? The attacker can delete every object in the bucket.
Unless there's a moat.

Separating my backup fleet from production protects against a compromised cluster. But leaked S3 credentials are a different attacker: a valid key can issue deletes, and the object store will obediently execute them.

My answer: ZFS snapshots as a moat.

Every storage node runs sanoid, taking scheduled read-only ZFS snapshots of the Garage datasets. S3 operations happen inside the castle. Snapshots live outside its walls.

No S3 credential, no API call, nothing short of root on the node itself can touch a snapshot. Ransomware encrypts or deletes my objects? One `zfs rollback` and they're back.

My favorite detail: the moat configures itself. Each node declares a role, and the snapshot module gates on it:

config = lib.mkIf (config.fleet.role == "storage") { ... }

A storage node cannot forget its snapshots. The gateway cannot accidentally grow them. The configuration follows the role, not my memory.

Bonus: scheduled scrubs catch silent corruption early — instead of on the day I need the data back, which is the worst possible time to find out.

Defense in depth isn't a stack of tools. It's knowing exactly which attacker each layer stops.

#zfs #nixos #ransomware #sanoid #selfhosted
