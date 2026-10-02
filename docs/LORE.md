# Lore

> *Words carry no power of their own here. Each one is an 11-bit number, and the power is in the
> number. The words only make the number easier to remember.*

## The making of a mnemonic

A wallet key is a large random number, and people are bad at writing down large random numbers.
In 2013 Bitcoin's BIP-39 settled on a convention: cut the number into 11-bit pieces and replace each
piece with one word from a fixed list of 2,048 (2¹¹). A word is easier to copy correctly than a
string of hex. The list was chosen so that the first four letters identify each word. One final word
carries a checksum, so a copying mistake is usually caught.

Algorand reused the English list and the 11-bit cut, but kept the scheme simpler than BIP-39:

```
32 random bytes  →  24 words  →  + 1 checksum word  =  25 words
```

There is no passphrase, no PBKDF2 stretching and no derivation tree. The phrase *is* the key. That
directness is what lets dmnemonic swap the words while keeping the key.

## The two tongues

**dmnemonic** is Algorand's own tongue: the BIP-39 English list, read by every Algorand wallet. The
*d* is for *decentralized*. A dmnemonic can be broken into a **coven** of shards, so that no single
keeper holds the key.

**demonic** is the grimoire tongue. It uses the same numbers in the same order with the same
checksum, but the 2,048 words are made by fusing two parts:

```
word = ROOT[ index >> 5 ] + ENDING[ index & 31 ]      64 roots × 32 endings = 2,048 words
```

The high six bits choose one of 64 **roots**: names from Irish, Welsh and Gaulish myth and the ogham
alphabet, then names from the Enochian of Dee and Kelley, the *Ars Goetia*, Kabbalah and alchemy.
The low five bits choose one of 32 **endings**, mostly Gaelic words of place and quality, with some
invented invocatory endings. So `draoi` (druid) + `mor` (great) gives **`draoimor`**, "druid · great".

The first words of the RFC 8032 test key show the correspondence:

| demonic | meaning | dmnemonic |
|---|---|---|
| cernunloch | the horned one · lake | crisp |
| aetherfinn | fifth element · bright | sheriff |
| thelemator | will · tower | solution |
| rubedovash | the reddening · invocatory | ten |
| azothlir | universal solvent · sea | remove |

Spelling is simplified to plain ASCII: accents are dropped and some names are shortened (`manann`
for Manannán, `cernun` for Cernunnos, `ourob` for ouroboros). That way every word types on any
keyboard and the 2,048 words stay unique.

## The 64 roots

| # | root | meaning | source | indices |
|---|---|---|---|---|
| 0 | `draoi` | druid | Irish *draoi*, druid | 0–31 |
| 1 | `sidhe` | folk of the mounds | Irish *síde*, the fairy mounds and their people | 32–63 |
| 2 | `ogam` | tree-script | Old Irish *ogam*, the stroke alphabet | 64–95 |
| 3 | `samhain` | summer's end | Irish feast of 1 November, the year's turning | 96–127 |
| 4 | `beltan` | bright fire | *Bealtaine*, the May fire-feast | 128–159 |
| 5 | `imbolc` | ewe's milk feast | the February feast, linked to Brigid | 160–191 |
| 6 | `lugh` | the many-skilled | *Lug*, god of every craft | 192–223 |
| 7 | `brigid` | the exalted | *Brigit*, goddess of poetry, smithcraft, healing | 224–255 |
| 8 | `morrigan` | phantom queen | *Morrígan*, war and prophecy | 256–287 |
| 9 | `dagda` | the good god | *In Dagda*, father-god of the Túatha Dé Danann | 288–319 |
| 10 | `nuada` | silver hand | *Nuadu Airgetlám*, the king with a silver arm | 320–351 |
| 11 | `manann` | lord of the sea | *Manannán mac Lir*, lord of the sea | 352–383 |
| 12 | `cernun` | the horned one | *Cernunnos*, the antlered god of the Gaulish Pillar of the Boatmen | 384–415 |
| 13 | `badb` | battle crow | *Badb*, battle-crow goddess | 416–447 |
| 14 | `macha` | sovereignty | *Macha*, sovereignty goddess of Ulster | 448–479 |
| 15 | `fiach` | raven | Irish *fiach*, raven | 480–511 |
| 16 | `dubh` | black | Irish *dubh*, black | 512–543 |
| 17 | `geis` | sacred taboo | *geis*, a sacred prohibition laid on a hero | 544–575 |
| 18 | `tuath` | the people | *túath*, a people or petty kingdom | 576–607 |
| 19 | `annwn` | the otherworld | Welsh *Annwn*, the otherworld | 608–639 |
| 20 | `awen` | flowing spirit | Welsh *awen*, poetic inspiration | 640–671 |
| 21 | `nemeton` | sacred grove | Gaulish *nemeton*, sacred grove | 672–703 |
| 22 | `fili` | seer-poet | Irish *fili*, the poet-seer class | 704–735 |
| 23 | `imbas` | illumination | *imbas forosnai*, the illumination of the poets | 736–767 |
| 24 | `cailleach` | veiled hag | *Cailleach*, the veiled hag of winter | 768–799 |
| 25 | `caoin` | keening | Irish *caoineadh*, keening for the dead | 800–831 |
| 26 | `ceo` | mist | Irish *ceo*, mist | 832–863 |
| 27 | `anam` | soul | Irish *anam*, soul | 864–895 |
| 28 | `slua` | host of the dead | *sluagh*, the host of the restless dead | 896–927 |
| 29 | `fomor` | giants below the sea | *Fomóire*, the giants from under the sea | 928–959 |
| 30 | `ailm` | fir (ogham A) | *ailm*, ogham letter A (pine or fir) | 960–991 |
| 31 | `uath` | hawthorn (ogham H) | *úath*, ogham letter H (hawthorn) | 992–1023 |
| 32 | `zorge` | be friendly (Enochian) | Enochian (Dee and Kelley, 1580s), 'be friendly unto me' | 1024–1055 |
| 33 | `madriax` | the heavens (Enochian) | Enochian, 'O ye heavens' | 1056–1087 |
| 34 | `vorsg` | over you (Enochian) | Enochian, 'over you' | 1088–1119 |
| 35 | `goho` | thus says (Enochian) | Enochian, 'saith' | 1120–1151 |
| 36 | `zacar` | move! (Enochian) | Enochian, 'move', the opening of the Calls | 1152–1183 |
| 37 | `iad` | god (Enochian) | Enochian, 'God' | 1184–1215 |
| 38 | `babalon` | the scarlet woman | Enochian, taken up by Crowley's Thelema | 1216–1247 |
| 39 | `hekas` | be far, profane ones | Greek *hekas, hekas, este bebeloi*, 'far, far, ye profane' | 1248–1279 |
| 40 | `abrax` | Abraxas | *Abraxas*, the Gnostic aeon of the 365 heavens | 1280–1311 |
| 41 | `agla` | AGLA, the notariqon | Kabbalistic notariqon of *Atah Gibor Le-olam Adonai* | 1312–1343 |
| 42 | `tetra` | the four letters | the Tetragrammaton | 1344–1375 |
| 43 | `sigil` | seal | Latin *sigillum*, seal | 1376–1407 |
| 44 | `goetia` | the howling art | Greek *goēteia*, sorcery; the first book of the *Lesser Key of Solomon* | 1408–1439 |
| 45 | `azoth` | universal solvent | alchemical universal solvent | 1440–1471 |
| 46 | `lumen` | light | Latin, light | 1472–1503 |
| 47 | `nox` | night | Latin, night | 1504–1535 |
| 48 | `umbra` | shadow | Latin, shadow | 1536–1567 |
| 49 | `aether` | fifth element | the fifth element | 1568–1599 |
| 50 | `ourob` | tail-devourer | *ouroboros*, the serpent eating its tail | 1600–1631 |
| 51 | `thelema` | will | Greek, will; Crowley's *Book of the Law* (1904) | 1632–1663 |
| 52 | `athame` | ritual blade | the ritual knife of modern witchcraft | 1664–1695 |
| 53 | `nigredo` | the blackening | first stage of the alchemical Great Work | 1696–1727 |
| 54 | `albedo` | the whitening | second stage, the whitening | 1728–1759 |
| 55 | `rubedo` | the reddening | final stage, the reddening | 1760–1791 |
| 56 | `sephir` | emanation | *sefirot*, the ten emanations of the Kabbalistic Tree | 1792–1823 |
| 57 | `qliph` | the husks | *qliphoth*, the husks or shells | 1824–1855 |
| 58 | `paimon` | a king of the Goetia | *Paimon*, a king among the 72 spirits of the *Ars Goetia* | 1856–1887 |
| 59 | `vassago` | prince of finding (Goetia) | *Vassago*, a prince of the *Ars Goetia* who finds lost things | 1888–1919 |
| 60 | `astaroth` | duke of secrets (Goetia) | *Astaroth*, a duke of the *Ars Goetia* | 1920–1951 |
| 61 | `belial` | the worthless one (Goetia) | Hebrew *bəliyyaʿal*, worthlessness; a king of the *Ars Goetia* | 1952–1983 |
| 62 | `bael` | first king (Goetia) | *Bael*, the first spirit of the *Ars Goetia* | 1984–2015 |
| 63 | `lilit` | night spirit | *Lilith*, the night spirit of Jewish folklore | 2016–2047 |

## The 32 endings

Most endings are real Irish words, simplified (`mór`, `dún`, `ler`, `druim`, `súil`). The ones marked
*invocatory* or *angelic ending* are invented sounds, modelled on the `-el` and `-ael` endings of
angel names. They carry no meaning and make no claim to any tradition.

| # | ending | meaning |
|---|---|---|
| 0 | `mor` | great |
| 1 | `nach` | invocatory |
| 2 | `roth` | wheel |
| 3 | `zael` | angelic ending |
| 4 | `thar` | beyond |
| 5 | `dun` | fortress |
| 6 | `vex` | invocatory |
| 7 | `kiel` | angelic ending |
| 8 | `gal` | valour |
| 9 | `bal` | place (from baile) |
| 10 | `cor` | circle |
| 11 | `drim` | ridge |
| 12 | `finn` | bright |
| 13 | `goth` | voice (from guth) |
| 14 | `hael` | angelic ending |
| 15 | `lir` | sea |
| 16 | `mael` | devotee |
| 17 | `neth` | invocatory |
| 18 | `pra` | invocatory |
| 19 | `quor` | invocatory |
| 20 | `rin` | secret (from rún) |
| 21 | `sul` | eye (from súil) |
| 22 | `tor` | tower |
| 23 | `vash` | invocatory |
| 24 | `wyr` | fate (Old English wyrd) |
| 25 | `xas` | invocatory |
| 26 | `yth` | invocatory |
| 27 | `zor` | invocatory |
| 28 | `carn` | cairn |
| 29 | `loch` | lake |
| 30 | `seth` | invocatory |
| 31 | `fael` | angelic ending |

## The coven

A coven is a circle of keepers. Shamir's secret sharing (Shamir 1979) splits a key into *n* shards
so that any *k* of them restore it and any *k − 1* reveal nothing at all. The guarantee is
mathematical, not computational, so no quantum computer changes it. Each shard is 26 words: a
**header word** that records the threshold and the shard number, 24 words of share, and a checksum.
Shards can be written in either tongue and bound in any order.

## The sigil

Each summoning draws a sigil: a pentagram-like star and a path through thirteen points on a circle.
It is computed from the **public** key (for a post-quantum phrase, from a hash of the Falcon seed),
never from the secret. You can show it, and it helps you tell two accounts apart at a glance. It is
an identicon, not a security device.

## A note on what this is

The demonic tongue is a cultural and mnemonic layer. It is not a cryptographic one. A demonic phrase
is exactly as strong as the dmnemonic phrase it translates to: 256 bits of entropy from the operating
system's random generator. The names were chosen because they have been remembered for centuries.
The grimoires and the myth cycles were mnemonic systems long before seed phrases, and that is the
only power claimed for them here.
