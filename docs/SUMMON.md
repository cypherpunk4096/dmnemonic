# Summon

The ceremony for creating a key you will put real value behind. Each step exists because skipping it
has cost someone funds. For practice and testnet you can skip straight to [step 4](#4-summon).

## What you need

- A computer you can take offline. A laptop booted from a live USB (Tails, or an Ubuntu live
  session) is ideal, because it leaves nothing behind.
- This repository on a USB stick, or just `dmnemonic.html` and `dmnemonic.py`.
- Paper and a pen. For a coven, one sheet per keeper. Metal plates are better for long-term storage.
- For a post-quantum account: the built `tools/pqaddr` helper, or a machine with `algokey`.

## 1. Verify what you are about to run

On a connected machine, fetch the repository and record the hashes:

```sh
git clone https://github.com/cypherpunk4096/dmnemonic && cd dmnemonic
sha256sum dmnemonic.html dist/demonic-creator.html
cat dist/SHA256SUMS                 # the build's own record; the two must agree
```

Read `dmnemonic.py` and the `<script>` blocks in `dmnemonic.html` if you can. They are short and
have no dependencies. Then copy the files to the USB stick.

## 2. Go dark

Disconnect the network: unplug the cable, switch off Wi-Fi in hardware if you can, and close the
other programs. The page's status bar shows **network: offline** when the browser agrees. The
standalone file's Content-Security-Policy already blocks every network request, so being offline is
a second wall, not the first.

## 3. Let the tool test itself

```sh
./dmnemonic.py selftest
```

Or open `dmnemonic.html` and look for **self-test passed**. The test checks the arithmetic against
published vectors: RFC 8032 Ed25519, algosdk's mnemonic and address, go-algorand's post-quantum
vector, the grimoire and the coven. If anything fails, the tool refuses to create keys. Stop there:
the copy you have is damaged or modified.

## 4. Summon

Choose the reading **before** you summon, because it decides how the phrase may ever be used:

| you want | page | CLI |
|---|---|---|
| an ordinary Algorand account (Pera, Defly, goal) | Summon · Account | `./dmnemonic.py summon --gloss` |
| a post-quantum Falcon-1024 account | Summon · Quantum | `./dmnemonic.py summon --quantum --gloss` |

An **incantation** is optional. Any text you type is hashed into the system randomness. It can add
entropy but never replace it, so a memorable phrase is safe to add and useless on its own.

The page shows the words blurred. When nobody can see your screen, press and hold **Hold to reveal** for about a second. The words stay visible for the time you chose (15, 30 or 60 seconds), then blur again. To copy one word at a time, press and hold just that word: it shows only while your finger or mouse button is down. Switching to another app or tab blurs everything at once.

## 5. Write

Write the phrase by hand in the tongue you will keep. Number every word.

- **dmnemonic** is what wallets read.
- **demonic** is easier to remember and means nothing to a casual finder, but you will need this
  tool (or a printed copy of the grimoire, `./dmnemonic.py lexicon --gloss`) to turn it back into
  dmnemonic.

The last word is the checksum. Copy it like any other word.

For a post-quantum phrase, write **`PQ · Falcon-1024 · f1`** at the top of the sheet. It must never
go into an ordinary wallet ([QUANTUM.md §1.4](QUANTUM.md#14-the-one-rule-never-cross-the-readings)).

## 6. Seal

On the page, hide the words and complete the **Seal** step: it asks for three randomly chosen words,
which you type from your paper copy. With the CLI, run `reveal` on your written copy:

```sh
./dmnemonic.py reveal <your written words…>        # add --pq for a post-quantum phrase
```

The address it prints must match the one shown at summoning. If it does not, your paper is wrong.
Fix it now, while the original is still on screen.

## 7. Form a coven (optional, recommended for large sums)

A single sheet of paper is a single point of failure: fire, flood, theft, or one careless heir. A
coven of *n* keepers, any *k* of whom can restore the key, removes it.

```sh
./dmnemonic.py split -k 3 -n 5 --tongue demonic <phrase…>     # add --pq for a post-quantum phrase
```

- Check that the address printed above the shards matches your account.
- Give each shard to a different keeper, kept in a different place.
- 3-of-5 survives the loss of two shards and the betrayal of any two keepers.
- Shards say nothing about the key until *k* of them meet. A keeper can safely hold one.
- Destroy the original full phrase only after you have **tested a bind** (step 9).

## 8. Banish

Choose **Banish all** on the page. It zeroes the key bytes in memory and clears every field, and it
runs on its own after 5 idle minutes. Close the browser. If you booted a live system, shut it down:
that clears RAM completely.

Never photograph the phrase, type it into a connected device, or store it in a password manager
that syncs.

## 9. Test the recovery

Before the account holds anything you cannot afford to lose:

1. Gather *k* shards, or the full phrase, on the offline machine.
2. Bind or reveal them and confirm the address:
   ```sh
   ./dmnemonic.py bind "<shard 1>" "<shard 4>" "<shard 5>"     # --pq for post-quantum
   ```
3. Send a small amount to the address, then confirm you can move it out again.

## 10. Use the account

- **Ordinary account.** Translate to dmnemonic if you kept demonic, then import it into a wallet:
  ```sh
  ./dmnemonic.py translate --to dmnemonic --oneline <demonic words…>
  ```
- **Post-quantum account.** Use only PQ tooling. Get the address with `./dmnemonic.py reveal --pq`
  (with `tools/pqaddr` built) or `algokey pq import -m "<dmnemonic words>"`. Sign with `algokey pq sign`.

Whatever you do, the phrase and the shards are the key. Anyone holding the phrase, or *k* shards,
holds the account.
