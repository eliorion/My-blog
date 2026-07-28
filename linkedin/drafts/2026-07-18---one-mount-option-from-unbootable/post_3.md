---
angle: key lesson
post_number: 3
blog_post: 2026-07-18 - One mount option from unbootable
generated: 2026-07-27T21:32:21.523848
---

The documentation tells you what an option means.
Only the source tells you what it does.

Last week a well-known mount option — noauto, something every sysadmin has typed a hundred times — nearly took down my backup fleet.

The man page definition was correct: don't mount this filesystem automatically. But on NixOS, mount options aren't just read at mount time. They feed a module that generates systemd units, and eight lines in nixpkgs' zfs.nix decided that a pool where everything is noauto doesn't need importing at boot.

Result: healthy disks, an existing import service, and a pool that never appeared. On two of my three nodes — the offsite ones — that would have meant a bricked machine with nobody nearby.

I spent a while debugging with hypotheses. Was the key wrong? Was the install script broken? Did I mistype the dataset name?

The turning point wasn't a clever hypothesis. It was opening zfs.nix and reading the eight lines that wire pool imports. Once lib.optional (!noauto) was on the screen, every symptom collapsed into one obvious mechanism: the missing import, the impossible error message, why one node survived.

Twenty minutes of reading source explained what hours of guessing couldn't.

When a well-known option behaves strangely, stop reasoning about what it should do. Go read the code that consumes it. On NixOS the source is right there — and twenty minutes of reading are cheaper than one bricked offsite node.

#debugging #nixos #opensource #softwareengineering
