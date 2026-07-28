---
angle: behind-the-scenes
post_number: 5
blog_post: 2026-07-18 - One mount option from unbootable
generated: 2026-07-27T21:32:21.524763
---

One debugging session. Two bugs.
The one I was hunting, and the one hiding behind it.

Behind the scenes of last week's "server won't import its ZFS pool" incident, here's what the work actually looked like:

1. Install the node. The finalize step runs zfs load-key. It returns "dataset does not exist" — for a dataset I created minutes ago.

2. Stare in disbelief. Re-check the dataset name three times.

3. Realize the pool never imported. The dataset doesn't exist... to a system that never imported the pool. The error was honest. I was asking the wrong question.

4. Trace why the import never ran. Read nixpkgs' zfs.nix. Find that noauto on all of a pool's filesystems removes its import service from the boot target.

5. Fix: drop noauto, keep nofail. Verify in the built configs — every pool's import service back in zfs-import.target — before touching a single machine.

6. Bonus: the same session flushed out a race in my install script. It SSH'd into a freshly rebooted node at full speed and hit "Connection refused". Now it polls until the box actually answers, and clears the stale known_hosts entry while it's there.

Two-line fix. One less flaky install.

Nobody's homelab posts show step 2.

It's always there.

#homelab #debugging #nixos #automation #linux
