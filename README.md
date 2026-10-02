# ⛧ dmnemonic

**Algorand keys spoken in two tongues.** dmnemonic creates Algorand accounts, ordinary ed25519 and
native post-quantum Falcon-1024, and writes each one as:

- a **dmnemonic**: the standard 25-word Algorand phrase that every wallet reads, which can be split
  into a k-of-n **coven** so no single keeper holds the key; and
- a **demonic** phrase: the same key in a 2,048-word grimoire built from Old Irish, Welsh and Gaulish
  roots fused with Enochian, Goetic, Kabbalistic and alchemical names.

```
dmnemonic   crisp          sheriff        solution       ten              remove      …
demonic     cernunloch     aetherfinn     thelemator     rubedovash       azothlir    …
            horned one ·   fifth element  will ·         the reddening ·  universal
            lake           · bright       tower          invocatory       solvent · sea
```

The two phrases are the same 25 numbers. Translate a demonic phrase back and Pera, Defly, `goal` and
algosdk import the same account. Nothing about the key changes, only the words used to remember it.
(The example is the RFC 8032 test key. Never put funds on a published key.)

Live page: **https://deltaverse.pythai.net/dmnemonic** (for learning and testnet; make real keys
from the local file, offline).

---

## Contents

- [Why](#why)
- [Quick start](#quick-start)
- [How a mnemonic is made](#how-a-mnemonic-is-made)
- [The two tongues](#the-two-tongues)
- [The coven](#the-coven)
- [Quantum](#quantum)
- [Safeguards](#safeguards)
- [Repository layout](#repository-layout)
- [Documentation](#documentation)
- [Verification status](#verification-status)
- [License](#license)

## Why

A seed phrase has three jobs: be copied correctly, be remembered or stored safely, and survive the
person who wrote it. Standard phrases do the first job well and leave the other two to the user.

- **Memory.** `cernunloch aetherfinn thelemator` is a sequence of images: the horned one at the lake,
  the bright fifth element, the tower of will. People have memorised myth for millennia; few memorise
  `crisp sheriff solution`. The demonic tongue turns the phrase into something a memory palace can hold.
- **Custody.** A single sheet of paper is a single point of failure. The coven spreads the key across
  keepers so that any *k* restore it and fewer learn nothing.
- **The quantum horizon.** Algorand accounts have been ed25519, which a large quantum computer would
  break. Since consensus v42, Algorand supports native **Falcon-1024** accounts. dmnemonic creates
  their master phrases, shards them, and derives their addresses with Algorand's own Falcon code.

## Quick start

**In a browser:** open `dmnemonic.html` from disk, check that **self-test passed** is shown, and
choose **Summon**.

**On the command line** (Python 3.8+, standard library only):

```sh
git clone https://github.com/cypherpunk4096/dmnemonic && cd dmnemonic
./dmnemonic.py selftest                           # known-answer tests
./dmnemonic.py summon --gloss                     # a new account, both tongues, with meanings
./dmnemonic.py translate --to dmnemonic <words…>  # demonic → wallet words
./dmnemonic.py split -k 3 -n 5 <words…>           # form a 3-of-5 coven
./dmnemonic.py bind "<shard>" "<shard>" "<shard>" # restore from any 3 shards
```

**Post-quantum** (needs Go and a C compiler for the address helper):

```sh
(cd tools/pqaddr && go build -o pqaddr .)
./dmnemonic.py summon --quantum --gloss
```

Full reference: [docs/USAGE.md](docs/USAGE.md). The ceremony for real funds:
[docs/SUMMON.md](docs/SUMMON.md).

## How a mnemonic is made

A key is a large random number. Mnemonics make it copyable by cutting it into 11-bit pieces and
replacing each piece with one of 2,048 (2¹¹) words.

**BIP-39** (Bitcoin, Ethereum) takes 128–256 bits of entropy, appends a few SHA-256 checksum bits and
encodes them as 12–24 words. The phrase is then stretched with PBKDF2-HMAC-SHA512 (2,048 rounds, salt
`"mnemonic"` + optional passphrase) into a 64-byte seed, from which BIP-32/44 derive a tree of keys.

**Algorand** keeps the wordlist and drops everything else. The phrase *is* the key:

```
seed     = 32 random bytes                                   256 bits
words    = seed as 11-bit numbers, little-endian             24 words (264 bits; the top 8 are zero)
checksum = SHA-512/256(seed)[0:2], low 11 bits               word 25
pub      = Ed25519(seed)                                     RFC 8032
address  = base32( pub ‖ SHA-512/256(pub)[-4:] )             58 characters
```

There is no passphrase, no stretching and no derivation tree. That directness is what makes the
demonic tongue possible: a new wordlist over the same numbers is a perfect translation.

## The two tongues

| | dmnemonic | demonic |
|---|---|---|
| wordlist | BIP-39 English (Algorand's) | the grimoire: 64 roots × 32 endings |
| word for index *i* | `english[i]` | `ROOTS[i >> 5] + ENDINGS[i & 31]` |
| read by wallets | yes | no: translate first |
| prefixes accepted | 4+ letters | 6+ letters |
| example | `crisp` | `cernunloch`, "the horned one · lake" |

The 64 **roots** are Irish, Welsh and Gaulish names (druid, the mound-folk, the ogham alphabet, the
fire-feasts, the Morrígan, the Dagda, Manannán, Cernunnos…) and names from the Enochian of Dee and
Kelley, the *Ars Goetia*, Kabbalah and alchemy (zorge, madriax, Abraxas, AGLA, azoth, nigredo, the
qliphoth, Paimon, Vassago, Bael…). The 32 **endings** are mostly Irish words (*mór* great, *dún*
fortress, *lir* sea, *carn* cairn, *loch* lake) plus invented invocatory endings. The full tables,
sources and meanings are in [docs/LORE.md](docs/LORE.md).

The grimoire adds no cryptographic strength. A demonic phrase is exactly as strong as its dmnemonic
twin.

## The coven

The *decentralized* in dmnemonic. Shamir's secret sharing over GF(2⁸) splits the 32-byte key into *n*
shards (n ≤ 15), any *k* of which reconstruct it. With fewer than *k*, every possible key is equally
likely, so the secrecy does not depend on computational limits and quantum computers do not affect it.

- Each shard is **26 words**: a header word (format version, threshold, shard number), 24 share words
  and a checksum.
- Shards can be written in either tongue and bound in any order and any mix of tongues.
- Supplying more than *k* shards triggers a consistency check that catches shards from different covens.

## Quantum

Algorand consensus **v42** (live on mainnet and testnet when this was written, 2026-10-01) enables
native post-quantum accounts signed with **Falcon-1024**, scheme tag `f1` (go-algorand PR #6639). The
backup is a 25-word phrase over 256 bits of master entropy:

```
falcon_seed = SHA-512/256("PQK" ‖ "f1" ‖ entropy)
pk, sk      = Falcon-1024 deterministic keygen(falcon_seed)
address     = SHA-512/256("PQA" ‖ "f1" ‖ salt ‖ pk)     salt: lowest value that is not an Ed25519 point
```

dmnemonic creates these master phrases in both tongues, shards them, and computes the Falcon seed.
The small Go helper `tools/pqaddr` links Algorand's own Falcon library to derive the address. It
reproduces go-algorand's test vector exactly (`ZEJ4BLG3…QTARXU` for entropy `01…20`).

> **Never import a post-quantum master phrase into an ordinary wallet.** The same 32 bytes are a
> valid ed25519 seed, and an Algorand ed25519 address reveals its public key. A quantum attacker
> could recover the entropy from that key and with it the Falcon key.

[docs/QUANTUM.md](docs/QUANTUM.md) covers the practical side in full. It also contains a
doctoral-level technical survey of Falcon: its lineage from GGH through GPV and NTRU trapdoors to
fast Fourier sampling, the construction, Algorand's deterministic profile, implementation hazards,
and references.

## Safeguards

| safeguard | where |
|---|---|
| Known-answer self-test (RFC 8032 Ed25519, SHA-512/256, algosdk mnemonic and address, grimoire, coven and PQ vectors) runs at page load and before every `summon`/`split`/`bind`. Any failure disables key creation. | page, CLI |
| Randomness only from the OS or browser CSPRNG. An incantation is hashed into it and never replaces it. | both |
| No network: the standalone page's Content-Security-Policy is `default-src 'none'`, and it uses no storage. | page |
| Words blurred by default. Revealing them takes a **press and hold** and lasts only for a countdown (15, 30 or 60 s). Holding one word peeks at that word alone, and switching apps re-blurs everything. A **Seal** step checks three random words against your paper copy. | page |
| **Banish** zeroes key buffers and clears the page, and also runs after 5 idle minutes. Clipboard copies are overwritten after 30 s. | page |
| Inputs disable autocomplete and spellcheck, since some browsers send spellcheck text off-device. | page |
| PQ entropy is passed to the helper on stdin, never in argv. The helper never prints the private key. | `tools/pqaddr` |
| Status chips show self-test, network and local-versus-hosted state. | page |
| Mobile layout: 44 px touch targets, 16 px inputs (no iOS zoom), sticky tabs and a bottom toolbar clear of the safe area. | page |

## Repository layout

```
dmnemonic.py            CLI and translator (Python, standard library only)
dmnemonic.html          standalone offline page (built)
src/core.js             browser engine: SHA-512/256, Ed25519, packing, coven, self-test
src/ui.html             page markup, styles and UI logic
src/head.html           search and sharing metadata for the standalone page
assets/                 favicon, Apple touch icon, sharing card and their renderer
build.py                assembles src/ into dmnemonic.html and dist/
dist/                   page fragment for hosting, and SHA256SUMS
tools/pqaddr/           Go helper: PQ master entropy → Algorand Falcon-1024 address
vectors.json            test vectors shared by every implementation
tests/                  unit tests (python3 -m unittest discover tests)
docs/                   SPEC, USAGE, SUMMON, QUANTUM, LORE
LICENSE*                dual license: GPL-3.0-or-later (client side), MIT (backend)
```

## Documentation

| document | contents |
|---|---|
| [docs/SUMMON.md](docs/SUMMON.md) | the ceremony: verify, go offline, self-test, summon, write, seal, coven, banish, test recovery |
| [docs/USAGE.md](docs/USAGE.md) | every command and option, the web page, building, tests |
| [docs/QUANTUM.md](docs/QUANTUM.md) | Algorand PQ accounts in practice, and a technical survey of Falcon with references |
| [docs/LORE.md](docs/LORE.md) | how mnemonics came to be, the two tongues, all 64 roots and 32 endings with sources, the coven, the sigil |
| [docs/SPEC.md](docs/SPEC.md) | the format, precise enough to implement, with test vectors |

## Verification status

- The dmnemonic phrase and address match **algosdk** on random keys and on RFC 8032 vectors.
- The browser engine matches the Python engine bit for bit.
- The PQ address matches **go-algorand's** own `algokey` test vector.
- Coven split and bind interoperate between the page and the CLI.
- **Not externally audited.** Read the code (it is short) and follow [SUMMON.md](docs/SUMMON.md) for
  anything of value.

Requirements: Python ≥ 3.8 built against OpenSSL with SHA-512/256 (standard on current Linux and
macOS); any modern browser; Go ≥ 1.24 and a C compiler for `tools/pqaddr`.

## License

dmnemonic is **dual-licensed by component**:

| component | files | license |
|---|---|---|
| **client side**: the browser encryption engine and page | `src/core.js`, `src/ui.html`, `dmnemonic.html`, `dist/` | [GPL-3.0-or-later](LICENSE-GPL-3.0) |
| **backend**: the CLI and translator, the PQ helper, build, tests, vectors, docs | `dmnemonic.py`, `tools/pqaddr/`, `build.py`, `tests/`, `vectors.json`, `docs/` | [MIT](LICENSE-MIT) |

Every source file names its license in an `SPDX-License-Identifier` line. Anyone who ships a modified
version of the page that creates keys in people's browsers must publish their changes under the GPL,
so users can always inspect the code that handles their keys. The backend stays permissive, so
wallets and services can embed it.

Copyright (C) 2026 Professor Codephreak and the cypherpunk4096 contributors. Both licenses come
WITHOUT ANY WARRANTY.

Third-party material: the BIP-39 English wordlist embedded in `dmnemonic.py` is reused from the
BIP-39 specification, as every Algorand SDK does. The Falcon library that `tools/pqaddr` links at
build time (`github.com/algorand/falcon`, © 2017–2020 Falcon Project) is MIT-licensed and is
fetched by Go, not vendored here.
