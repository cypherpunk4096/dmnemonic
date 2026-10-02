# Usage

dmnemonic comes in two forms that share one format ([SPEC.md](SPEC.md)) and one set of test vectors:

- **`dmnemonic.py`**: a command-line tool and translator. Python 3.8+ standard library only.
- **`dmnemonic.html`**: a single offline web page. Open it from disk in any modern browser.

Both work without a network. A third piece, **`tools/pqaddr`**, is an optional Go helper that turns
a post-quantum master phrase into its Algorand address ([QUANTUM.md](QUANTUM.md)).

## Install

```sh
git clone https://github.com/cypherpunk4096/dmnemonic
cd dmnemonic
./dmnemonic.py selftest
```

Nothing to install. To use the post-quantum address helper (needs Go ≥ 1.24 and a C compiler):

```sh
(cd tools/pqaddr && go build -o pqaddr .)
./dmnemonic.py selftest     # now also checks go-algorand's PQ vector
```

The CLI finds the helper at `tools/pqaddr/pqaddr`, on your `PATH`, or at `$DMNEMONIC_PQADDR`.

## The command line

```
dmnemonic {summon, reveal, translate, split, bind, selftest, lexicon}
```

`summon`, `split` and `bind` run the self-test first and refuse to work if it fails.

### summon: create a new key

```sh
./dmnemonic.py summon                       # ordinary Algorand account, both tongues
./dmnemonic.py summon --gloss               # add the meaning of each demonic word
./dmnemonic.py summon --tongue demonic      # print only one tongue (dmnemonic | demonic | both)
./dmnemonic.py summon --quantum             # post-quantum Falcon-1024 master phrase
./dmnemonic.py summon --incantation "…"     # mix extra text into the randomness
```

Output: the kind of key, its address (or, for `--quantum`, its seed id and, with the helper, its PQ
address), then the 25 numbered words in each tongue. The 25th word is the checksum.

### reveal: check a phrase and show its address

```sh
./dmnemonic.py reveal <25 words…>
./dmnemonic.py reveal --pq <25 words…>      # read it as a post-quantum master phrase
```

Either tongue works. The tongue is detected from the words. Unique prefixes are accepted (4+
letters for dmnemonic, 6+ for demonic), and mistakes get a suggestion:

```
$ ./dmnemonic.py reveal cernunloch aetherfinn thelemator rubedovash azothlir babalonmor dagdahael tuathrin imbasrin goetiapra imbolcquor annwnroth zacarrin sluacor albedoyth cernunquor manannbal umbrazael brigidgoth machator machamor paimoncarn dreoifael draoizael vassagogal
✗ unknown demonic word(s): 'dreoifael' (did you mean 'draoifael'?)
```

A 26-word coven shard is recognised and reported as a shard.

### translate: convert between tongues

```sh
./dmnemonic.py translate <words…>                    # to the other tongue
./dmnemonic.py translate --to dmnemonic <words…>     # explicit target
./dmnemonic.py translate --gloss <words…>            # with meanings
./dmnemonic.py translate --oneline <words…>          # one line, ready to paste into a wallet
```

Shards translate too: the header word is kept, so a shard stays a shard.

Example, using the RFC 8032 test key (never use a published key for funds):

```
$ ./dmnemonic.py translate --oneline cernunloch aetherfinn thelemator rubedovash azothlir babalonmor dagdahael tuathrin imbasrin goetiapra imbolcquor annwnroth zacarrin sluacor albedoyth cernunquor manannbal umbrazael brigidgoth machator machamor paimoncarn draoifael draoizael vassagogal
crisp sheriff solution ten remove object chair enhance future rather biology era myth image swap crash coffee scatter buffalo depart day twist advance about unfair
```

### split: form a coven

```sh
./dmnemonic.py split -k 3 -n 5 <words…>                    # 3-of-5, in the phrase's own tongue
./dmnemonic.py split -k 2 -n 3 --tongue demonic <words…>   # choose the shard tongue
./dmnemonic.py split --pq -k 3 -n 5 <words…>               # show the PQ identity above the shards
```

Limits: 2 ≤ k ≤ n ≤ 15. Each shard is 26 words.

### bind: restore from shards

```sh
./dmnemonic.py bind "<shard>" "<shard>" "<shard>"     # each shard quoted as one argument
./dmnemonic.py bind --tongue demonic --gloss "<shard>" …
./dmnemonic.py bind --pq "<shard>" …
```

Shards can be in different tongues and in any order. Extra shards beyond *k* are cross-checked, so
shards from two different covens are detected rather than producing a wrong key.

### selftest

Runs the known-answer tests and reports which passed. It exits non-zero on failure.

### lexicon

```sh
./dmnemonic.py lexicon            # the 2,048 demonic words, one per line, index order
./dmnemonic.py lexicon --gloss    # with index and meaning; print this as an offline translation table
```

## The web page

Open `dmnemonic.html` from disk. Five tabs:

| tab | what it does |
|---|---|
| **Summon** | Choose *Account · ed25519* or *Quantum · Falcon-1024*, optionally add an incantation, and choose **Summon**. Shows the sigil, the address or seed id, both tongues, and the **Seal** check. |
| **Reveal & Translate** | Paste a phrase or shard in either tongue. Shows its identity and both tongues. Tick *post-quantum master phrase* to read it as PQ. |
| **Coven** | Split a phrase into k-of-n shards in either tongue, or paste shards (one per line) to bind them. |
| **Lore** | How mnemonics are made, the two tongues, quantum mode, and the safeguards. |
| **Grimoire** | Search all 2,048 words by word, root, meaning or dmnemonic equivalent. |

Controls on every tab:

- **Show words / Hide words**: words are blurred by default.
- **Banish all**: zeroes the key bytes and clears the page. It also runs after 5 idle minutes.
- **Copy** buttons put text on the clipboard and overwrite it 30 seconds later.

The status chips show the self-test result, whether the browser is online, and whether this is the
local file or a hosted copy. Use the local file, offline, for real keys. Hosted copies are for
learning and testnet.

## Building the page

The page is assembled from `src/`:

```sh
./build.py
```

| output | purpose |
|---|---|
| `dmnemonic.html` | the standalone page, with a Content-Security-Policy that blocks all network access |
| `dist/demonic-creator.html` | the same page without the document skeleton, for hosts that add their own |
| `dist/SHA256SUMS` | hashes of both outputs |

`build.py` also copies the page into `~/DeltaVerse/pages/` if that directory exists.

## Tests

```sh
python3 -m unittest discover tests
```

The tests cover round trips in both tongues, checksum rejection, legacy-length rejection, the coven
(any *k* of *n*, too few shards, mixed covens), the PQ seed derivation, and self-test tamper
detection. With `algosdk` installed they also compare 100 random keys against it. With
`tools/pqaddr` built they check go-algorand's PQ address vector.
