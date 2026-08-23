---
title: "Automated AGE Key Rotation in CI"
date: 2026-05-30T09:00:00+02:00
draft: false
aliases: ["/11---posts/2026-05-30---mve-itguard-key-rotation/"]
topics:
  - DevOps
  - Security
  - Homelab
tags:
  - sops
  - age
  - key-rotation
  - github-actions
  - security
  - ci-cd
  - homelab
projects:
  - mve-itguard
categories:
  - IT
  - Security
weight: 2
cover:
  image: cover.svg
  alt: Automated AGE key rotation
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---

## The Key Rotation Problem

Encryption key rotation is one of those security practices that everyone agrees is important and almost nobody does consistently. The reason is not laziness. It is friction. Rotating a key that is used to encrypt many files means re-encrypting all of them. One missed file means that the new key cannot decrypt it. One mismatch between the key on the server and the key in CI means the next deployment fails.

With mve-itguard, the AGE private key encrypts nine files spread across four directories. A manual rotation requires: generating a new key, updating four `.sops.yaml` files, running `sops updatekeys` on each encrypted file individually, updating the key on the production server, and updating the GitHub Actions secret. Miss any step, do them in the wrong order, and you have a system that cannot deploy until you diagnose which key is out of sync with which file.

The solution is to automate the detection and execution of rotation inside the CI pipeline itself, so that a rotation becomes a two-step operation for the developer, and the pipeline handles everything else.

---

## The Mechanism: Hash Comparison

Every push to `main` triggers the deploy pipeline. Before the deploy job runs, a dedicated `rotate` job executes on `runner-rotate`. That runner is the only container in the system with two properties simultaneously: access to `/etc/sops/age/keys.txt` on the host (via a read-write volume mount) and the `SOPS_AGE_KEY` GitHub Actions secret injected as an environment variable.

The rotation script compares the key material from both sources:

```bash
SERVER_SECRET=$(grep "^AGE-SECRET-KEY-" /etc/sops/age/keys.txt)
GH_SECRET=$(printf '%s\n' "$SOPS_AGE_KEY" | grep "^AGE-SECRET-KEY-")

if [ "$SERVER_SECRET" = "$GH_SECRET" ]; then
    log "Keys match — no rotation needed."
    exit 0
fi
```

The comparison extracts only the `AGE-SECRET-KEY-1...` line, ignoring the comment lines at the top of the key file (creation date, public key comment). This makes the comparison robust to formatting differences, two key files with identical key material but different timestamps will still match.

On every normal push, this exits 0 in milliseconds. No rotation, no cost. The `deploy` job proceeds immediately.

---

## When Keys Differ: Full Rotation

A mismatch means one thing: the developer has intentionally updated the `SOPS_AGE_KEY` GitHub Actions secret with a new key, and the server's key has not been updated yet, or both have been updated and the pipeline has not run since.

When the script detects a mismatch, it performs the full rotation:

### Step 1, Write keys to temporary files

```bash
OLD_KEY_FILE=$(mktemp)
NEW_KEY_FILE=$(mktemp)
trap 'rm -f "$OLD_KEY_FILE" "$NEW_KEY_FILE"' EXIT

cp /etc/sops/age/keys.txt "$OLD_KEY_FILE"
printf '%s' "$SOPS_AGE_KEY" > "$NEW_KEY_FILE"
chmod 600 "$OLD_KEY_FILE" "$NEW_KEY_FILE"

OLD_PUBKEY=$(grep "^# public key:" "$OLD_KEY_FILE" | awk '{print $4}')
NEW_PUBKEY=$(grep "^# public key:" "$NEW_KEY_FILE" | awk '{print $4}')
```

The `trap` guarantees cleanup regardless of how the script exits: error, signal, or normal completion. Both keys exist as temporary files for the duration of the rotation and are removed when it finishes.

### Step 2, Update all `.sops.yaml` files

```bash
find "$REPO_ROOT" -name ".sops.yaml" -not -path "*/.git/*" | while IFS= read -r config; do
    sed -i "s|$OLD_PUBKEY|$NEW_PUBKEY|g" "$config"
done
```

Each `.sops.yaml` contains the AGE public key that SOPS uses to encrypt new values. The old public key is replaced with the new one in-place. SOPS uses the nearest `.sops.yaml` when encrypting: after this step, any new encryption targets the new key automatically.

### Step 3, Re-encrypt all `.enc` files

```bash
export SOPS_AGE_KEY_FILE="$OLD_KEY_FILE"

find "$REPO_ROOT" -name "*.enc" -not -path "*/.git/*" | while IFS= read -r file; do
    [ "$file" = "$KEYS_ENC" ] && continue   # handled separately
    (cd "$(dirname "$file")" && sops updatekeys --yes --input-type "$input_type" "$(basename "$file")")
done
```

`SOPS_AGE_KEY_FILE` is set to the **old** key. This is required: `sops updatekeys` needs to decrypt the file first, which requires the old key. The `.sops.yaml` already contains the new public key (updated in Step 2), so SOPS re-encrypts each value to the new key automatically.

The script detects the format of each file by extension (`*.env.enc` → dotenv, `*.yaml.enc` → yaml, etc.) and passes the correct `--input-type` flag. Running `sops updatekeys` from the file's own directory ensures SOPS finds the nearest `.sops.yaml` correctly.

### Step 4, Re-encrypt `keys.txt.enc` specially

```bash
sops --encrypt --age "$NEW_PUBKEY" "$NEW_KEY_FILE" > "$KEYS_ENC"
```

`infrastructure/ansible/files/keys.txt.enc` is special: its **content** is the private key itself, encrypted with the public key. A regular `sops updatekeys` would only change which key it is encrypted *to*. It would not change what it contains.

This file is skipped in Step 3 and handled here instead: the new private key is encrypted with the new public key and written to `keys.txt.enc`. After this step, the self-referential backup is up to date.

### Step 5, Update the server key

```bash
cp "$NEW_KEY_FILE" /etc/sops/age/keys.txt
chmod 600 /etc/sops/age/keys.txt
```

`runner-rotate` has `/etc/sops/age` mounted read-write from the host and runs as root. Writing to this path updates the actual key on the production server: the same key that will be used by the next backup run, the next `sops` command executed interactively, and by future rotation comparisons.

---

## The Pipeline Commits and Continues

After rotation completes, the pipeline commits all the re-encrypted files back to `main`:

```yaml
- name: Commit re-encrypted files if rotation occurred
  run: |
    git config user.name  "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    if ! git diff --quiet; then
      git add -A
      git commit -m "fix(security): rotate AGE encryption key [skip ci]"
      git push
    fi
```

The `[skip ci]` tag in the commit message is critical. Without it, committing back to `main` would trigger a new CI run, which would trigger a new deploy run, which would try to commit again: an infinite loop. GitHub Actions recognises `[skip ci]` and does not trigger new workflow runs for that commit.

The `deploy` job runs after `rotate` regardless of whether rotation occurred. If files were re-encrypted and committed, the `deploy` job checks out the updated branch head and deploys the freshly rotated state.

---

## Developer Steps to Rotate

From the developer's perspective, rotation is a two-step operation:

**Step 1, Generate a new key and update the server:**

```bash
# Generate new key
age-keygen -o ~/.config/sops/age/keys.txt

# Copy to server (or generate on server directly)
scp ~/.config/sops/age/keys.txt sysadmin@<server>:/tmp/new-keys.txt
ssh sysadmin@<server> "sudo install -m 600 -o root -g root /tmp/new-keys.txt /etc/sops/age/keys.txt && rm /tmp/new-keys.txt"
```

**Step 2, Update the GitHub Actions secret:**

GitHub → Repository → Settings → Secrets and variables → Actions → `SOPS_AGE_KEY` → Update with the new key content.

**Step 3, Push any commit to `main`:**

The pipeline detects the hash mismatch and handles everything: re-encrypts all files, commits back, deploys.

> **Warning:** Steps 1 and 2 must happen together, before the next pipeline run. If only the GitHub secret is updated (new key in CI, old key on server), the rotation script will attempt to decrypt files with the old key (which still works at that point) and re-encrypt with the new key, then update the server. This is the intended flow. If only the server key is updated (new key on server, old key in CI), the comparison detects a mismatch, but the old key in `SOPS_AGE_KEY` will not match the `.enc` files after the attempt, causing decryption failures. Always update both together.

---

## What Makes This Safe

A few details in the rotation script are worth noting explicitly.

**The old key is only in memory.** It is written to a `mktemp` file with mode 600 and deleted by `trap`. The new key from `SOPS_AGE_KEY` is also written to a temp file. Neither persists beyond the script's lifetime.

**`sops updatekeys` decrypts and re-encrypts atomically.** SOPS does not write partial files. If `updatekeys` fails mid-way through a file (corrupt data, wrong key, network issue), the original `.enc` file is unchanged. The pipeline will fail, the rotation commit will not happen, and the next push will retry.

**The comparison is on key material, not on file hashes.** The key file header contains a creation timestamp. If the key was regenerated with the same cryptographic material (impossible in practice but worth noting), or if the file was reformatted, comparing whole-file hashes would produce false positives. Extracting the `AGE-SECRET-KEY-1...` line directly avoids that.

**No secrets are logged.** The script logs the public keys (which are safe to display) but never logs the private key, the `SOPS_AGE_KEY` value, or any decrypted secret content.

---

## The Result

Key rotation went from a multi-step manual process with several opportunities for error to a two-step developer operation: update the secret, update the server key, push. The pipeline detects the change, re-encrypts everything correctly, commits the result, and continues to deploy.

The property this gives is that rotation actually happens. When rotation is friction-free, it can be scheduled regularly. When it is painful and error-prone, it gets deferred indefinitely.

---

*Next in this series: [Multi-Node Backup with Restic]({{< relref "2026-05-31 - mve-itguard-backup/index.md" >}}): append-only backups across redundant nodes over Cloudflare Tunnel, with automatic daily scheduling and container-pause consistency.*
