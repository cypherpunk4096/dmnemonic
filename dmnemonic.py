#!/usr/bin/env python3
# dmnemonic — Algorand keys in the dmnemonic and demonic tongues
# Copyright (C) 2026 Professor Codephreak and the cypherpunk4096 contributors
# SPDX-License-Identifier: MIT
# Backend component, MIT licensed; see LICENSE-MIT.
"""
dmnemonic — a standalone, stdlib-only Algorand mnemonic forge with two tongues.

  * dmnemonic  — the *decentralized* mnemonic: the standard Algorand 25-word
                 phrase (BIP-39 English list, Algorand packing) plus "coven"
                 sharding, a k-of-n Shamir split so no single holder owns the key.
  * demonic    — the same key, spoken in the Grimoire lexicon: 2048 summoning
                 words built from Old Irish / Welsh / Gaulish roots and
                 Enochian, Goetic and alchemical names.

Both tongues map 1:1 onto Algorand's 11-bit word indices, so a demonic phrase is
just a re-skin of a real Algorand account: translate it back and any Algorand
wallet will accept it.

Quantum mode forges an Algorand native post-quantum master phrase (consensus
v42, Falcon-1024 scheme "f1"): 25 words of 256-bit entropy, from which go-algorand
derives the Falcon seed as SHA-512/256("PQK" || "f1" || entropy). The PQ address
needs Falcon key generation, done by the small Go helper in tools/pqaddr.

No dependencies. Ed25519 and Shamir-over-GF(256) are implemented below.
"""
import argparse
import base64
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys

# ---------------------------------------------------------------------------
# Lexicons
# ---------------------------------------------------------------------------

ALGORAND_WORDS = """
abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid
acoustic acquire across act action actor actress actual adapt add addict address adjust admit adult advance
advice aerobic affair afford afraid again age agent agree ahead aim air airport aisle alarm album
alcohol alert alien all alley allow almost alone alpha already also alter always amateur amazing among
amount amused analyst anchor ancient anger angle angry animal ankle announce annual another answer antenna antique
anxiety any apart apology appear apple approve april arch arctic area arena argue arm armed armor
army around arrange arrest arrive arrow art artefact artist artwork ask aspect assault asset assist assume
asthma athlete atom attack attend attitude attract auction audit august aunt author auto autumn average avocado
avoid awake aware away awesome awful awkward axis baby bachelor bacon badge bag balance balcony ball
bamboo banana banner bar barely bargain barrel base basic basket battle beach bean beauty because become
beef before begin behave behind believe below belt bench benefit best betray better between beyond bicycle
bid bike bind biology bird birth bitter black blade blame blanket blast bleak bless blind blood
blossom blouse blue blur blush board boat body boil bomb bone bonus book boost border boring
borrow boss bottom bounce box boy bracket brain brand brass brave bread breeze brick bridge brief
bright bring brisk broccoli broken bronze broom brother brown brush bubble buddy budget buffalo build bulb
bulk bullet bundle bunker burden burger burst bus business busy butter buyer buzz cabbage cabin cable
cactus cage cake call calm camera camp can canal cancel candy cannon canoe canvas canyon capable
capital captain car carbon card cargo carpet carry cart case cash casino castle casual cat catalog
catch category cattle caught cause caution cave ceiling celery cement census century cereal certain chair chalk
champion change chaos chapter charge chase chat cheap check cheese chef cherry chest chicken chief child
chimney choice choose chronic chuckle chunk churn cigar cinnamon circle citizen city civil claim clap clarify
claw clay clean clerk clever click client cliff climb clinic clip clock clog close cloth cloud
clown club clump cluster clutch coach coast coconut code coffee coil coin collect color column combine
come comfort comic common company concert conduct confirm congress connect consider control convince cook cool copper
copy coral core corn correct cost cotton couch country couple course cousin cover coyote crack cradle
craft cram crane crash crater crawl crazy cream credit creek crew cricket crime crisp critic crop
cross crouch crowd crucial cruel cruise crumble crunch crush cry crystal cube culture cup cupboard curious
current curtain curve cushion custom cute cycle dad damage damp dance danger daring dash daughter dawn
day deal debate debris decade december decide decline decorate decrease deer defense define defy degree delay
deliver demand demise denial dentist deny depart depend deposit depth deputy derive describe desert design desk
despair destroy detail detect develop device devote diagram dial diamond diary dice diesel diet differ digital
dignity dilemma dinner dinosaur direct dirt disagree discover disease dish dismiss disorder display distance divert divide
divorce dizzy doctor document dog doll dolphin domain donate donkey donor door dose double dove draft
dragon drama drastic draw dream dress drift drill drink drip drive drop drum dry duck dumb
dune during dust dutch duty dwarf dynamic eager eagle early earn earth easily east easy echo
ecology economy edge edit educate effort egg eight either elbow elder electric elegant element elephant elevator
elite else embark embody embrace emerge emotion employ empower empty enable enact end endless endorse enemy
energy enforce engage engine enhance enjoy enlist enough enrich enroll ensure enter entire entry envelope episode
equal equip era erase erode erosion error erupt escape essay essence estate eternal ethics evidence evil
evoke evolve exact example excess exchange excite exclude excuse execute exercise exhaust exhibit exile exist exit
exotic expand expect expire explain expose express extend extra eye eyebrow fabric face faculty fade faint
faith fall false fame family famous fan fancy fantasy farm fashion fat fatal father fatigue fault
favorite feature february federal fee feed feel female fence festival fetch fever few fiber fiction field
figure file film filter final find fine finger finish fire firm first fiscal fish fit fitness
fix flag flame flash flat flavor flee flight flip float flock floor flower fluid flush fly
foam focus fog foil fold follow food foot force forest forget fork fortune forum forward fossil
foster found fox fragile frame frequent fresh friend fringe frog front frost frown frozen fruit fuel
fun funny furnace fury future gadget gain galaxy gallery game gap garage garbage garden garlic garment
gas gasp gate gather gauge gaze general genius genre gentle genuine gesture ghost giant gift giggle
ginger giraffe girl give glad glance glare glass glide glimpse globe gloom glory glove glow glue
goat goddess gold good goose gorilla gospel gossip govern gown grab grace grain grant grape grass
gravity great green grid grief grit grocery group grow grunt guard guess guide guilt guitar gun
gym habit hair half hammer hamster hand happy harbor hard harsh harvest hat have hawk hazard
head health heart heavy hedgehog height hello helmet help hen hero hidden high hill hint hip
hire history hobby hockey hold hole holiday hollow home honey hood hope horn horror horse hospital
host hotel hour hover hub huge human humble humor hundred hungry hunt hurdle hurry hurt husband
hybrid ice icon idea identify idle ignore ill illegal illness image imitate immense immune impact impose
improve impulse inch include income increase index indicate indoor industry infant inflict inform inhale inherit initial
inject injury inmate inner innocent input inquiry insane insect inside inspire install intact interest into invest
invite involve iron island isolate issue item ivory jacket jaguar jar jazz jealous jeans jelly jewel
job join joke journey joy judge juice jump jungle junior junk just kangaroo keen keep ketchup
key kick kid kidney kind kingdom kiss kit kitchen kite kitten kiwi knee knife knock know
lab label labor ladder lady lake lamp language laptop large later latin laugh laundry lava law
lawn lawsuit layer lazy leader leaf learn leave lecture left leg legal legend leisure lemon lend
length lens leopard lesson letter level liar liberty library license life lift light like limb limit
link lion liquid list little live lizard load loan lobster local lock logic lonely long loop
lottery loud lounge love loyal lucky luggage lumber lunar lunch luxury lyrics machine mad magic magnet
maid mail main major make mammal man manage mandate mango mansion manual maple marble march margin
marine market marriage mask mass master match material math matrix matter maximum maze meadow mean measure
meat mechanic medal media melody melt member memory mention menu mercy merge merit merry mesh message
metal method middle midnight milk million mimic mind minimum minor minute miracle mirror misery miss mistake
mix mixed mixture mobile model modify mom moment monitor monkey monster month moon moral more morning
mosquito mother motion motor mountain mouse move movie much muffin mule multiply muscle museum mushroom music
must mutual myself mystery myth naive name napkin narrow nasty nation nature near neck need negative
neglect neither nephew nerve nest net network neutral never news next nice night noble noise nominee
noodle normal north nose notable note nothing notice novel now nuclear number nurse nut oak obey
object oblige obscure observe obtain obvious occur ocean october odor off offer office often oil okay
old olive olympic omit once one onion online only open opera opinion oppose option orange orbit
orchard order ordinary organ orient original orphan ostrich other outdoor outer output outside oval oven over
own owner oxygen oyster ozone pact paddle page pair palace palm panda panel panic panther paper
parade parent park parrot party pass patch path patient patrol pattern pause pave payment peace peanut
pear peasant pelican pen penalty pencil people pepper perfect permit person pet phone photo phrase physical
piano picnic picture piece pig pigeon pill pilot pink pioneer pipe pistol pitch pizza place planet
plastic plate play please pledge pluck plug plunge poem poet point polar pole police pond pony
pool popular portion position possible post potato pottery poverty powder power practice praise predict prefer prepare
present pretty prevent price pride primary print priority prison private prize problem process produce profit program
project promote proof property prosper protect proud provide public pudding pull pulp pulse pumpkin punch pupil
puppy purchase purity purpose purse push put puzzle pyramid quality quantum quarter question quick quit quiz
quote rabbit raccoon race rack radar radio rail rain raise rally ramp ranch random range rapid
rare rate rather raven raw razor ready real reason rebel rebuild recall receive recipe record recycle
reduce reflect reform refuse region regret regular reject relax release relief rely remain remember remind remove
render renew rent reopen repair repeat replace report require rescue resemble resist resource response result retire
retreat return reunion reveal review reward rhythm rib ribbon rice rich ride ridge rifle right rigid
ring riot ripple risk ritual rival river road roast robot robust rocket romance roof rookie room
rose rotate rough round route royal rubber rude rug rule run runway rural sad saddle sadness
safe sail salad salmon salon salt salute same sample sand satisfy satoshi sauce sausage save say
scale scan scare scatter scene scheme school science scissors scorpion scout scrap screen script scrub sea
search season seat second secret section security seed seek segment select sell seminar senior sense sentence
series service session settle setup seven shadow shaft shallow share shed shell sheriff shield shift shine
ship shiver shock shoe shoot shop short shoulder shove shrimp shrug shuffle shy sibling sick side
siege sight sign silent silk silly silver similar simple since sing siren sister situate six size
skate sketch ski skill skin skirt skull slab slam sleep slender slice slide slight slim slogan
slot slow slush small smart smile smoke smooth snack snake snap sniff snow soap soccer social
sock soda soft solar soldier solid solution solve someone song soon sorry sort soul sound soup
source south space spare spatial spawn speak special speed spell spend sphere spice spider spike spin
spirit split spoil sponsor spoon sport spot spray spread spring spy square squeeze squirrel stable stadium
staff stage stairs stamp stand start state stay steak steel stem step stereo stick still sting
stock stomach stone stool story stove strategy street strike strong struggle student stuff stumble style subject
submit subway success such sudden suffer sugar suggest suit summer sun sunny sunset super supply supreme
sure surface surge surprise surround survey suspect sustain swallow swamp swap swarm swear sweet swift swim
swing switch sword symbol symptom syrup system table tackle tag tail talent talk tank tape target
task taste tattoo taxi teach team tell ten tenant tennis tent term test text thank that
theme then theory there they thing this thought three thrive throw thumb thunder ticket tide tiger
tilt timber time tiny tip tired tissue title toast tobacco today toddler toe together toilet token
tomato tomorrow tone tongue tonight tool tooth top topic topple torch tornado tortoise toss total tourist
toward tower town toy track trade traffic tragic train transfer trap trash travel tray treat tree
trend trial tribe trick trigger trim trip trophy trouble truck true truly trumpet trust truth try
tube tuition tumble tuna tunnel turkey turn turtle twelve twenty twice twin twist two type typical
ugly umbrella unable unaware uncle uncover under undo unfair unfold unhappy uniform unique unit universe unknown
unlock until unusual unveil update upgrade uphold upon upper upset urban urge usage use used useful
useless usual utility vacant vacuum vague valid valley valve van vanish vapor various vast vault vehicle
velvet vendor venture venue verb verify version very vessel veteran viable vibrant vicious victory video view
village vintage violin virtual virus visa visit visual vital vivid vocal voice void volcano volume vote
voyage wage wagon wait walk wall walnut want warfare warm warrior wash wasp waste water wave
way wealth weapon wear weasel weather web wedding weekend weird welcome west wet whale what wheat
wheel when where whip whisper wide width wife wild will win window wine wing wink winner
winter wire wisdom wise wish witness wolf woman wonder wood wool word work world worry worth
wrap wreck wrestle wrist write wrong yard year yellow you young youth zebra zero zone zoo
""".split()

# 64 roots (6 high bits of the 11-bit index) — accents stripped, some shortened.
ROOTS = [
    # Old Irish / Gaelic / Welsh / Gaulish
    ("draoi", "druid"), ("sidhe", "folk of the mounds"), ("ogam", "tree-script"),
    ("samhain", "summer's end"), ("beltan", "bright fire"), ("imbolc", "ewe's milk feast"),
    ("lugh", "the many-skilled"), ("brigid", "the exalted"), ("morrigan", "phantom queen"),
    ("dagda", "the good god"), ("nuada", "silver hand"), ("manann", "lord of the sea"),
    ("cernun", "the horned one"), ("badb", "battle crow"), ("macha", "sovereignty"),
    ("fiach", "raven"), ("dubh", "black"), ("geis", "sacred taboo"),
    ("tuath", "the people"), ("annwn", "the otherworld"), ("awen", "flowing spirit"),
    ("nemeton", "sacred grove"), ("fili", "seer-poet"), ("imbas", "illumination"),
    ("cailleach", "veiled hag"), ("caoin", "keening"), ("ceo", "mist"),
    ("anam", "soul"), ("slua", "host of the dead"), ("fomor", "giants below the sea"),
    ("ailm", "fir (ogham A)"), ("uath", "hawthorn (ogham H)"),
    # Enochian / Goetic / Hermetic / alchemical
    ("zorge", "be friendly (Enochian)"), ("madriax", "the heavens (Enochian)"),
    ("vorsg", "over you (Enochian)"), ("goho", "thus says (Enochian)"),
    ("zacar", "move! (Enochian)"), ("iad", "god (Enochian)"),
    ("babalon", "the scarlet woman"), ("hekas", "be far, profane ones"),
    ("abrax", "Abraxas"), ("agla", "AGLA, the notariqon"),
    ("tetra", "the four letters"), ("sigil", "seal"), ("goetia", "the howling art"),
    ("azoth", "universal solvent"), ("lumen", "light"), ("nox", "night"),
    ("umbra", "shadow"), ("aether", "fifth element"), ("ourob", "tail-devourer"),
    ("thelema", "will"), ("athame", "ritual blade"), ("nigredo", "the blackening"),
    ("albedo", "the whitening"), ("rubedo", "the reddening"), ("sephir", "emanation"),
    ("qliph", "the husks"), ("paimon", "a king of the Goetia"),
    ("vassago", "prince of finding (Goetia)"), ("astaroth", "duke of secrets (Goetia)"),
    ("belial", "the worthless one (Goetia)"), ("bael", "first king (Goetia)"),
    ("lilit", "night spirit"),
]

# 32 endings (5 low bits). Gaelic where real, otherwise invocatory.
SUFFIXES = [
    ("mor", "great"), ("nach", "invocatory"), ("roth", "wheel"), ("zael", "angelic ending"),
    ("thar", "beyond"), ("dun", "fortress"), ("vex", "invocatory"), ("kiel", "angelic ending"),
    ("gal", "valour"), ("bal", "place (from baile)"), ("cor", "circle"), ("drim", "ridge"),
    ("finn", "bright"), ("goth", "voice (from guth)"), ("hael", "angelic ending"), ("lir", "sea"),
    ("mael", "devotee"), ("neth", "invocatory"), ("pra", "invocatory"), ("quor", "invocatory"),
    ("rin", "secret (from rún)"), ("sul", "eye (from súil)"), ("tor", "tower"), ("vash", "invocatory"),
    ("wyr", "fate (Old English wyrd)"), ("xas", "invocatory"), ("yth", "invocatory"), ("zor", "invocatory"),
    ("carn", "cairn"), ("loch", "lake"), ("seth", "invocatory"), ("fael", "angelic ending"),
]

GRIMOIRE_WORDS = [r + s for r, _ in ROOTS for s, _ in SUFFIXES]


def gloss(index):
    r, rg = ROOTS[index >> 5]
    s, sg = SUFFIXES[index & 31]
    return f"{rg} · {sg}"


class Lexicon:
    def __init__(self, name, words, prefix_min):
        assert len(words) == 2048 and len(set(words)) == 2048, name
        self.name, self.words = name, words
        self.index = {w: i for i, w in enumerate(words)}
        # Accept any unambiguous prefix of at least prefix_min letters.
        counts = {}
        for w in words:
            for n in range(prefix_min, len(w)):
                counts[w[:n]] = counts.get(w[:n], 0) + 1
        for i, w in enumerate(words):
            for n in range(prefix_min, len(w)):
                if counts[w[:n]] == 1 and w[:n] not in self.index:
                    self.index[w[:n]] = i

    def lookup(self, word):
        return self.index.get(word)

    def suggest(self, word):
        return min(self.words, key=lambda w: _levenshtein(word, w))


def _levenshtein(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


ALGORAND = Lexicon("dmnemonic", ALGORAND_WORDS, 4)
GRIMOIRE = Lexicon("demonic", GRIMOIRE_WORDS, 6)
LEXICONS = {"algorand": ALGORAND, "dmnemonic": ALGORAND, "grimoire": GRIMOIRE, "demonic": GRIMOIRE}
assert not set(ALGORAND_WORDS) & set(GRIMOIRE_WORDS)

# ---------------------------------------------------------------------------
# Algorand mnemonic packing (identical to algosdk/mnemonic.py)
# ---------------------------------------------------------------------------


def sha512_256(data):
    return hashlib.new("sha512_256", data).digest()


def to_11_bit(data):
    buf = bits = 0
    out = []
    for b in data:
        buf |= b << bits
        bits += 8
        if bits >= 11:
            out.append(buf & 2047)
            buf >>= 11
            bits -= 11
    if bits:
        out.append(buf & 2047)
    return out


def from_11_bit(nums):
    buf = bits = 0
    out = bytearray()
    for n in nums:
        buf |= n << bits
        bits += 11
        while bits >= 8:
            out.append(buf & 255)
            buf >>= 8
            bits -= 8
    if bits:
        out.append(buf & 255)
    return bytes(out)


def checksum_index(data):
    return to_11_bit(sha512_256(data)[:2])[0]


# phrase kinds: word count -> (payload bytes, has coven header)
KINDS = {
    25: (32, False),  # Algorand ed25519 seed, or a PQ master phrase
    26: (32, True),   # coven shard of either
}

SEAL_VERSION = 1


class PhraseError(ValueError):
    pass


def encode(payload, lex, header=None):
    nums = ([header] if header is not None else []) + to_11_bit(payload)
    chk_data = (header.to_bytes(2, "little") if header is not None else b"") + payload
    return [lex.words[n] for n in nums] + [lex.words[checksum_index(chk_data)]]


def detect_lexicon(words):
    for lex in (ALGORAND, GRIMOIRE):
        if all(lex.lookup(w) is not None for w in words):
            return lex
    # Report against whichever tongue matched more words.
    best = max((ALGORAND, GRIMOIRE), key=lambda l: sum(l.lookup(w) is not None for w in words))
    bad = [w for w in words if best.lookup(w) is None]
    hints = ", ".join(f"'{w}' (did you mean '{best.suggest(w)}'?)" for w in bad)
    raise PhraseError(f"unknown {best.name} word(s): {hints}")


def decode(phrase):
    """Return (payload, header_or_None, lexicon)."""
    words = phrase.lower().replace(",", " ").split()
    if len(words) not in KINDS:
        raise PhraseError(f"{len(words)} words — expected one of {sorted(KINDS)}")
    nbytes, has_header = KINDS[len(words)]
    lex = detect_lexicon(words)
    nums = [lex.lookup(w) for w in words]
    header = nums.pop(0) if has_header else None
    chk = nums.pop()
    raw = from_11_bit(nums)
    payload, extra = raw[:nbytes], raw[nbytes:]
    if any(extra):
        raise PhraseError("checksum failed (non-zero padding bits)")
    chk_data = (header.to_bytes(2, "little") if header is not None else b"") + payload
    if checksum_index(chk_data) != chk:
        raise PhraseError("checksum failed — a word is wrong or out of order")
    return payload, header, lex


# ---------------------------------------------------------------------------
# Ed25519 public key derivation (RFC 8032), extended coordinates
# ---------------------------------------------------------------------------

_P = 2**255 - 19
_L = 2**252 + 27742317777372353535851937790883648493
_D = -121665 * pow(121666, _P - 2, _P) % _P
_BX = 15112221349535400772501151409588531511454012693041857206046113283949847762202
_BY = 46316835694926478169428394003475163141307993866256225615783033603165251855960
_B = (_BX, _BY, 1, _BX * _BY % _P)


def _pt_add(p, q):
    x1, y1, z1, t1 = p
    x2, y2, z2, t2 = q
    a = (y1 - x1) * (y2 - x2) % _P
    b = (y1 + x1) * (y2 + x2) % _P
    c = t1 * 2 * _D * t2 % _P
    d = z1 * 2 * z2 % _P
    e, f, g, h = b - a, d - c, d + c, b + a
    return (e * f % _P, g * h % _P, f * g % _P, e * h % _P)


def _pt_mul(p, n):
    r = (0, 1, 1, 0)
    while n:
        if n & 1:
            r = _pt_add(r, p)
        p = _pt_add(p, p)
        n >>= 1
    return r


def ed25519_public_key(seed):
    h = hashlib.sha512(seed).digest()
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    x, y, z, _ = _pt_mul(_B, a)
    zi = pow(z, _P - 2, _P)
    x, y = x * zi % _P, y * zi % _P
    return (y | ((x & 1) << 255)).to_bytes(32, "little")


def algorand_address(pub):
    return base64.b32encode(pub + sha512_256(pub)[-4:]).decode().rstrip("=")


# ---------------------------------------------------------------------------
# Algorand native post-quantum accounts (go-algorand #6639, consensus v42)
# ---------------------------------------------------------------------------

PQ_SCHEME = b"f1"  # Falcon-1024, deterministic signing profile


def pq_falcon_seed(entropy):
    """cmd/algokey/pq_scheme.go derivePQKeySeed: SHA-512/256("PQK" || scheme || entropy)."""
    return sha512_256(b"PQK" + PQ_SCHEME + entropy)


def pq_helper():
    """Locate the pqaddr helper: $DMNEMONIC_PQADDR, tools/pqaddr/pqaddr, or PATH."""
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (os.environ.get("DMNEMONIC_PQADDR"), os.path.join(here, "tools", "pqaddr", "pqaddr"), shutil.which("pqaddr")):
        if cand and os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
    return None


def pq_account(entropy):
    """Return the helper's JSON (address, salt, public-key hash) or None if it is not built.
    The entropy goes over stdin, never argv, so it stays out of the process list."""
    helper = pq_helper()
    if not helper:
        return None
    out = subprocess.run([helper], input=entropy.hex() + "\n", capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise PhraseError("pqaddr failed: " + out.stderr.strip())
    return json.loads(out.stdout)


# ---------------------------------------------------------------------------
# Coven: Shamir secret sharing over GF(256)
# ---------------------------------------------------------------------------

_EXP = [0] * 512
_LOG = [0] * 256
_x = 1
for _i in range(255):
    _EXP[_i] = _x
    _LOG[_x] = _i
    _x ^= (_x << 1) ^ (0x11B if _x & 0x80 else 0)  # multiply by generator 3
    _x &= 0xFF
for _i in range(255, 512):
    _EXP[_i] = _EXP[_i - 255]


def _gmul(a, b):
    return 0 if a == 0 or b == 0 else _EXP[_LOG[a] + _LOG[b]]


def _gdiv(a, b):
    return 0 if a == 0 else _EXP[_LOG[a] - _LOG[b] + 255]


def coven_split(secret, k, n, coeffs=None):
    """`coeffs` is only for test vectors; normal use draws them from the OS CSPRNG."""
    if not 2 <= k <= n <= 15:
        raise PhraseError("need 2 <= threshold <= shards <= 15")
    coeffs = coeffs or [secrets.token_bytes(len(secret)) for _ in range(k - 1)]
    shards = []
    for x in range(1, n + 1):
        y = bytearray()
        for i, s in enumerate(secret):
            acc = 0
            for c in reversed(coeffs):  # Horner
                acc = _gmul(acc ^ c[i], x)
            y.append(acc ^ s)
        header = (SEAL_VERSION << 8) | ((k - 1) << 4) | x
        shards.append((header, bytes(y)))
    return shards


def coven_bind(shards):
    """shards: list of (header, y). Returns the secret."""
    ks = {(h >> 4) & 15 for h, _ in shards}
    if len(ks) != 1:
        raise PhraseError("shards come from covens with different thresholds")
    k = ks.pop() + 1
    xs = {}
    for h, y in shards:
        if h >> 8 != SEAL_VERSION:
            raise PhraseError(f"unknown seal version {h >> 8}")
        xs[h & 15] = y
    if len(xs) < k:
        raise PhraseError(f"this coven needs {k} distinct shards, got {len(xs)}")

    def interpolate(points):
        out = bytearray()
        for i in range(len(points[0][1])):
            acc = 0
            for j, (xj, yj) in enumerate(points):
                num = den = 1
                for m, (xm, _) in enumerate(points):
                    if m != j:
                        num = _gmul(num, xm)
                        den = _gmul(den, xj ^ xm)
                acc ^= _gmul(yj[i], _gdiv(num, den))
            out.append(acc)
        return bytes(out)

    pts = sorted(xs.items())
    secret = interpolate(pts[:k])
    # With surplus shards, every k-subset must agree — catches a mixed coven.
    if len(pts) > k and interpolate(pts[-k:]) != secret:
        raise PhraseError("surplus shards disagree — they are not from the same coven")
    return secret


# ---------------------------------------------------------------------------
# Known-answer self-test (vectors shared with dmnemonic.html and SPEC.md;
# ed25519/Algorand values come from RFC 8032 and algosdk, not from this file)
# ---------------------------------------------------------------------------

VECTORS = {
    "sha512_256_abc": "53048e2681941ef99b2e29b76b4c7dabe4c2d0c634fc6d46e0e2f13107e7af23",
    "accounts": [
        {
            "seed": "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
            "pub": "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a",
            "address": "25NJQAMCWEFLPVKL73J4SZAHHIHOC4XT3KTCGJNPAINGR5YHKENMEF5QTE",
            "dmnemonic": "crisp sheriff solution ten remove object chair enhance future rather biology era myth image swap crash coffee scatter buffalo depart day twist advance about unfair",
            "demonic": "cernunloch aetherfinn thelemator rubedovash azothlir babalonmor dagdahael tuathrin imbasrin goetiapra imbolcquor annwnroth zacarrin sluacor albedoyth cernunquor manannbal umbrazael brigidgoth machator machamor paimoncarn draoifael draoizael vassagogal"
        },
        {
            "seed": "4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb",
            "pub": "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c",
            "address": "HVABPQ7IIOEVVEVXBKTU2G36XSOJQLGPF3CJNDGAZVK7CKXUMYGA6EOE6Y",
            "dmnemonic": "praise case eternal verb combine issue reject senior match element poem rail believe small provide private network hammer edit term panther puppy tag abstract bone",
            "demonic": "tetrafinn morriganxas annwnfinn astarothrin manannlir fomorsul azothkiel umbraloch vorsgvex geisloch aglawyr goetiakiel imbolcdun thelemazael sigilkiel tetraxas iadvex ceothar geisquor rubedozor hekasseth sigilmael rubedobal draoikiel lughcor"
        }
    ],
    "coven": {
        "seed": "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
        "k": 3,
        "n": 5,
        "coeffs": [
            "202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f",
            "404142434445464748494a4b4c4d4e4f505152535455565758595a5b5c5d5e5f"
        ],
        "shards": [
            "dagdanach fiachloch geismor lilitvash albedokiel fomorbal zorgemor dagdator nuadavash awenrin cernunseth dagdapra tuathpra awenpra ceocor albedoroth awenmael morriganbal dubhlir manannfinn fiachvex baelvex astarothcarn draoikiel draoimor thelemacor",
            "dagdaroth babalonvex babalonkiel caoinquor vorsgtor nuadazor tuathpra annwnrin manannlir cernunsul caoincarn tetrahael baelseth paimonkiel fiachthar umbrator imbolcyth ogamvex vassagovex babalonxas nuadasul brigidmael mananntor ourobwyr draoizael belialkiel",
            "dagdazael iadvex lughdrim nemetonpra gohovex paimonloch awenpra annwnfinn annwnfinn fiachsul qliphmael babalonlir lilithael nuadanach dagdathar umbrahael fomorxas sidhevex anamcor tetrawyr mananndun rubedotor badbtor ourobmor draoimor vorsgrin",
            "dagdathar manannneth nigredoquor aglasul nemetonbal hekasdun lumennach qliphloch mananntor athamethar zacarneth samhainzael fiachpra nigredolir iadsul qliphwyr umbrafinn nemetonvex hekaswyr hekasnach vorsgbal azothpra fiachyth albedothar draoimor umbrasul",
            "dagdadun morriganneth nemetonfael iadrin awenxas imbaszael abraxnach qliphdun annwnsul rubedothar beltanloch fiachroth macharoth imbolcbal gohosul qliphmor abraxlir filivex brigidrin sigilmor gohoxas fomorrin dagdayth albedocarn draoizael morriganhael"
        ]
    },
    "quantum": {
        "source": "go-algorand cmd/algokey/pq_test.go TestPQGenerateUsesMnemonicSizedEntropy",
        "scheme": "f1",
        "entropy": "0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20",
        "dmnemonic": "dizzy army link gate asthma dragon expect arch pave deal always baby category age post bid actual good minimum script demand shy abstract ability move",
        "demonic": "dubhnach samhainmor zorgemael cailleachroth samhainmael dubhmael awenroth ogamwyr abraxfinn machanach sidhecarn beltangal dagdanach sidhevex tetradun imbolcmael draoivash caoinzael gohogal umbragoth machaneth aethercarn draoikiel draoinach zacarvex",
        "falcon_seed": "ff681836d409831e7a16231bfcf1fca8e0a27b17a2389ff76ce1a7232af4609a",
        "pq_address": "ZEJ4BLG3XWAUUZQGCEDJLYIC6D2NCWHRSX5DJMDPE54PXXR7G3PCQTARXU",
        "salt": 5
    }
}


def self_test():
    fails = []

    def ok(name, cond):
        if not cond:
            fails.append(name)

    try:
        ok("SHA-512/256", sha512_256(b"abc").hex() == VECTORS["sha512_256_abc"])
        for v in VECTORS["accounts"]:
            seed = bytes.fromhex(v["seed"])
            pub = ed25519_public_key(seed)
            ok("Ed25519", pub.hex() == v["pub"])
            ok("address", algorand_address(pub) == v["address"])
            ok("dmnemonic", " ".join(encode(seed, ALGORAND)) == v["dmnemonic"])
            ok("demonic", " ".join(encode(seed, GRIMOIRE)) == v["demonic"])
            ok("decode", decode(v["demonic"])[0] == seed)
        c = VECTORS["coven"]
        shards = coven_split(bytes.fromhex(c["seed"]), c["k"], c["n"], [bytes.fromhex(x) for x in c["coeffs"]])
        ok("coven split", [" ".join(encode(y, GRIMOIRE, h)) for h, y in shards] == c["shards"])
        decoded = [decode(t) for t in c["shards"][-c["k"]:]]
        bound = coven_bind([(header, payload) for payload, header, _ in decoded])
        ok("coven bind", bound.hex() == c["seed"])
        q = VECTORS["quantum"]
        entropy = bytes.fromhex(q["entropy"])
        ok("PQ phrase", decode(q["demonic"])[0] == entropy and " ".join(encode(entropy, ALGORAND)) == q["dmnemonic"])
        ok("PQ Falcon seed", pq_falcon_seed(entropy).hex() == q["falcon_seed"])
        if pq_helper():
            ok("PQ address (go-algorand vector)", pq_account(entropy)["address"] == q["pq_address"])
        r1, r2 = secrets.token_bytes(64), secrets.token_bytes(64)
        ok("CSPRNG", r1 != r2 and len(set(r1)) > 16)
    except Exception as e:  # any crash is a failure, never a pass
        fails.append(f"exception: {e}")
    return fails


# ---------------------------------------------------------------------------
# Presentation
# ---------------------------------------------------------------------------


def gather_entropy(nbytes, incantation=None):
    raw = secrets.token_bytes(nbytes)
    if not incantation:
        return raw
    # Extra input is hashed *into* the OS randomness; it can never weaken it.
    return hashlib.sha512(raw + b"\x00incantation\x00" + incantation.encode()).digest()[:nbytes]


def describe(payload, pq=False):
    if not pq:
        return {"kind": "Algorand account (ed25519)",
                "address": algorand_address(ed25519_public_key(payload))}
    info = {"kind": "Algorand PQ account (Falcon-1024, scheme f1)",
            "seed id": sha512_256(pq_falcon_seed(payload))[:8].hex()}
    acct = pq_account(payload)
    if acct:
        info["address"] = acct["address"]
        info["salt"] = acct["salt"]
    else:
        info["address"] = "build tools/pqaddr (docs/QUANTUM.md) or run: algokey pq import -m '<dmnemonic phrase>'"
    return info


def render(words, lex, show_gloss=False, numbered=True):
    lines = []
    for i, w in enumerate(words, 1):
        g = gloss(lex.lookup(w)) if show_gloss and lex is GRIMOIRE else ""
        lines.append(f"{i:>3}. {w:<14}{g}".rstrip() if numbered else w)
    return "\n".join(lines)


PQ_WARNING = ("This is a post-quantum master phrase. Never import it into an ed25519 wallet:\n"
              "an ed25519 key published on-chain would let a quantum attacker recover the\n"
              "entropy, and with it the Falcon key.")


def _print_identity(payload, pq=False):
    for k, v in describe(payload, pq).items():
        print(f"  {k:<12} {v}")


def cmd_summon(a):
    seed = gather_entropy(32, a.incantation)
    algo, grim = encode(seed, ALGORAND), encode(seed, GRIMOIRE)
    print("⛧ summoned\n")
    _print_identity(seed, a.quantum)
    if a.quantum:
        print("\n" + PQ_WARNING)
    if a.tongue in ("both", "dmnemonic"):
        print(f"\n— dmnemonic ({len(algo)} words, Algorand-compatible) —\n{render(algo, ALGORAND)}")
    if a.tongue in ("both", "demonic"):
        print(f"\n— demonic ({len(grim)} words, grimoire tongue) —\n{render(grim, GRIMOIRE, a.gloss)}")
    print("\nWrite these down offline. Anyone holding either phrase holds the key.")


def cmd_reveal(a):
    payload, header, lex = decode(" ".join(a.phrase))
    if header is not None:
        k, x = ((header >> 4) & 15) + 1, header & 15
        print(f"coven shard #{x} (threshold {k}) in the {lex.name} tongue — bind {k} shards to reveal")
        return
    print(f"valid {lex.name} phrase" + (" (read as a PQ master phrase)" if a.pq else ""))
    _print_identity(payload, a.pq)
    if not a.pq:
        print("  (if this is a post-quantum master phrase, add --pq)")


def cmd_translate(a):
    payload, header, lex = decode(" ".join(a.phrase))
    target = LEXICONS[a.to] if a.to else (GRIMOIRE if lex is ALGORAND else ALGORAND)
    words = encode(payload, target, header)
    print(" ".join(words) if a.oneline else render(words, target, a.gloss))


def cmd_split(a):
    payload, header, lex = decode(" ".join(a.phrase))
    if header is not None:
        raise PhraseError("that is already a shard")
    target = LEXICONS[a.tongue] if a.tongue else lex
    print(f"⛧ coven of {a.shards}, any {a.threshold} may bind\n")
    _print_identity(payload, a.pq)
    for h, y in coven_split(payload, a.threshold, a.shards):
        print(f"\n— shard {h & 15} of {a.shards} —")
        print(" ".join(encode(y, target, h)))


def cmd_bind(a):
    shards = []
    for s in a.shards:
        payload, header, _ = decode(s)
        if header is None:
            raise PhraseError("not a shard: " + " ".join(s.split()[:3]) + " …")
        shards.append((header, payload))
    secret = coven_bind(shards)
    print("⛧ bound\n")
    _print_identity(secret, a.pq)
    target = LEXICONS[a.tongue]
    print("\n" + render(encode(secret, target), target, a.gloss))


def cmd_selftest(a):
    fails = self_test()
    if fails:
        print("✗ self-test FAILED: " + ", ".join(fails))
        return 1
    print("✓ self-test passed (SHA-512/256, Ed25519 RFC 8032, Algorand address + mnemonic, grimoire, coven, PQ seed, CSPRNG)")
    print("✓ PQ address matches go-algorand's algokey test vector" if pq_helper()
          else "· PQ address check skipped: tools/pqaddr is not built (docs/QUANTUM.md)")
    return 0


def cmd_lexicon(a):
    for i, w in enumerate(GRIMOIRE_WORDS):
        print(f"{i:>4}  {w:<14} {gloss(i)}" if a.gloss else w)


def main(argv=None):
    p = argparse.ArgumentParser(prog="dmnemonic", description=__doc__.split("\n\n")[0].strip())
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("summon", help="forge a new account in both tongues")
    s.add_argument("--quantum", action="store_true", help="Algorand native post-quantum (Falcon-1024) master phrase")
    s.add_argument("--tongue", choices=["both", "dmnemonic", "demonic"], default="both")
    s.add_argument("--incantation", help="extra entropy mixed into the OS randomness")
    s.add_argument("--gloss", action="store_true", help="show meanings of grimoire words")
    s.set_defaults(fn=cmd_summon)

    s = sub.add_parser("reveal", help="validate a phrase and show its address")
    s.add_argument("phrase", nargs="+")
    s.add_argument("--pq", action="store_true", help="treat the phrase as a post-quantum master phrase")
    s.set_defaults(fn=cmd_reveal)

    s = sub.add_parser("translate", help="convert between dmnemonic and demonic tongues")
    s.add_argument("phrase", nargs="+")
    s.add_argument("--to", choices=["dmnemonic", "demonic"])
    s.add_argument("--gloss", action="store_true")
    s.add_argument("--oneline", action="store_true")
    s.set_defaults(fn=cmd_translate)

    s = sub.add_parser("split", help="shard a phrase into a k-of-n coven")
    s.add_argument("phrase", nargs="+")
    s.add_argument("-k", "--threshold", type=int, default=3)
    s.add_argument("-n", "--shards", type=int, default=5)
    s.add_argument("--tongue", choices=["dmnemonic", "demonic"])
    s.add_argument("--pq", action="store_true", help="treat the phrase as a post-quantum master phrase")
    s.set_defaults(fn=cmd_split)

    s = sub.add_parser("bind", help="recombine coven shards (each shard as one quoted argument)")
    s.add_argument("shards", nargs="+")
    s.add_argument("--tongue", choices=["dmnemonic", "demonic"], default="dmnemonic")
    s.add_argument("--gloss", action="store_true")
    s.add_argument("--pq", action="store_true", help="treat the phrase as a post-quantum master phrase")
    s.set_defaults(fn=cmd_bind)

    s = sub.add_parser("selftest", help="run the known-answer tests")
    s.set_defaults(fn=cmd_selftest)

    s = sub.add_parser("lexicon", help="print the 2048-word grimoire")
    s.add_argument("--gloss", action="store_true")
    s.set_defaults(fn=cmd_lexicon)

    a = p.parse_args(argv)
    if a.cmd in ("summon", "split", "bind"):
        fails = self_test()
        if fails:
            print("✗ refusing to forge keys: self-test failed: " + ", ".join(fails), file=sys.stderr)
            return 2
    try:
        return a.fn(a) or 0
    except PhraseError as e:
        print(f"✗ {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
