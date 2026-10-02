# dmnemonic format specification

Format version 1. `dmnemonic.py` and `dmnemonic.html` both implement it, and both check themselves
against [`vectors.json`](../vectors.json) before they create or read a key.

## 1. Packing (identical to Algorand)

`to11(bytes)` reads bytes in order into a little-endian bit buffer and emits 11-bit groups, low bits
first. A trailing partial group is emitted zero-padded at the top. `from11` is the inverse. When
decoding, any byte beyond the payload length must be zero.

`checksum(data) = to11(SHA-512/256(data)[0:2])[0]`

This matches `algosdk/mnemonic.py` and go-algorand's `crypto/passphrase`.

## 2. Tongues

| tongue | word for 11-bit index *i* |
|---|---|
| dmnemonic | `BIP39_ENGLISH[i]`, the list Algorand uses |
| demonic | `ROOTS[i >> 5] + SUFFIXES[i & 31]`: 64 roots × 32 endings, in the order given in `dmnemonic.py` |

The two lists share no words, so a decoder detects the tongue from the words themselves. A decoder
accepts any unique prefix of at least 4 letters (dmnemonic) or 6 letters (demonic).

## 3. Phrases

| words | layout | payload |
|---|---|---|
| 25 | `to11(entropy)` (24 words) + `checksum(entropy)` | 32 bytes |
| 26 | `header` + `to11(y)` (24 words) + `checksum(le16(header) ‖ y)` | a coven shard of 32 bytes |

A 25-word phrase carries 32 bytes and nothing else. The phrase does not record what the bytes are
for. Two readings are defined:

- **ed25519 account.** The 32 bytes are the Ed25519 seed (RFC 8032).
  `address = base32_nopad(pub ‖ SHA-512/256(pub)[-4:])` with `pub = Ed25519(seed)`.
- **Post-quantum master phrase** (go-algorand #6639, consensus v42, scheme `f1` = Falcon-1024):
  ```
  falcon_seed = SHA-512/256("PQK" ‖ "f1" ‖ entropy)
  pk, sk      = falcon_det1024_keygen(SHAKE256(falcon_seed))
  salt        = least s in 0..255 such that SHA-512/256("PQA" ‖ "f1" ‖ s ‖ pk) is not a valid Ed25519 point encoding
  pq_address  = base32_nopad(A ‖ SHA-512/256(A)[-4:]),  A = SHA-512/256("PQA" ‖ "f1" ‖ salt ‖ pk)
  ```
  Tools show a *seed id*, `hex(SHA-512/256(falcon_seed)[0:8])`, which names the seed without revealing it.

The same 32 bytes must never be used under both readings. See [QUANTUM.md](QUANTUM.md) §1.4.

## 4. Coven (Shamir over GF(2⁸))

The field is GF(2⁸) with reduction polynomial `0x11B`. Each secret byte `s` gets its own polynomial
`f(x) = s + c₁x + … + c₍ₖ₋₁₎x^(k-1)` with uniformly random coefficient bytes. Shard `x`
(1 ≤ x ≤ n ≤ 15) holds `y = f(x)` for every byte. The 11-bit header word is
`version (3 bits, = 1) | k − 1 (4 bits) | x (4 bits)`. Binding uses Lagrange interpolation at 0.
If more than `k` shards are given, two different `k`-subsets must give the same secret, or binding
fails. That check catches shards mixed in from different covens.

## 5. Test vectors (excerpt; the full set is in `vectors.json`)

**RFC 8032 test 1 seed** `9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60`

- pub `d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a`
- address `25NJQAMCWEFLPVKL73J4SZAHHIHOC4XT3KTCGJNPAINGR5YHKENMEF5QTE` (algosdk)
- dmnemonic `crisp sheriff solution ten remove object chair enhance future rather biology era myth image swap crash coffee scatter buffalo depart day twist advance about unfair` (algosdk)
- demonic `cernunloch aetherfinn thelemator rubedovash azothlir babalonmor dagdahael tuathrin imbasrin goetiapra imbolcquor annwnroth zacarrin sluacor albedoyth cernunquor manannbal umbrazael brigidgoth machator machamor paimoncarn draoifael draoizael vassagogal`

**Coven of that seed**, k = 3, n = 5, coefficient bytes `c₁ = 20 21 … 3f`, `c₂ = 40 41 … 5f`:

- shard 1: `dagdanach fiachloch geismor lilitvash albedokiel fomorbal zorgemor dagdator nuadavash awenrin cernunseth dagdapra tuathpra awenpra ceocor albedoroth awenmael morriganbal dubhlir manannfinn fiachvex baelvex astarothcarn draoikiel draoimor thelemacor`
- shard 2: `dagdaroth babalonvex babalonkiel caoinquor vorsgtor nuadazor tuathpra annwnrin manannlir cernunsul caoincarn tetrahael baelseth paimonkiel fiachthar umbrator imbolcyth ogamvex vassagovex babalonxas nuadasul brigidmael mananntor ourobwyr draoizael belialkiel`
- shard 3: `dagdazael iadvex lughdrim nemetonpra gohovex paimonloch awenpra annwnfinn annwnfinn fiachsul qliphmael babalonlir lilithael nuadanach dagdathar umbrahael fomorxas sidhevex anamcor tetrawyr mananndun rubedotor badbtor ourobmor draoimor vorsgrin`
- shard 4: `dagdathar manannneth nigredoquor aglasul nemetonbal hekasdun lumennach qliphloch mananntor athamethar zacarneth samhainzael fiachpra nigredolir iadsul qliphwyr umbrafinn nemetonvex hekaswyr hekasnach vorsgbal azothpra fiachyth albedothar draoimor umbrasul`
- shard 5: `dagdadun morriganneth nemetonfael iadrin awenxas imbaszael abraxnach qliphdun annwnsul rubedothar beltanloch fiachroth macharoth imbolcbal gohosul qliphmor abraxlir filivex brigidrin sigilmor gohoxas fomorrin dagdayth albedocarn draoizael morriganhael`

**Post-quantum master phrase**: entropy `01 02 … 20`, taken from go-algorand cmd/algokey/pq_test.go TestPQGenerateUsesMnemonicSizedEntropy

- dmnemonic `dizzy army link gate asthma dragon expect arch pave deal always baby category age post bid actual good minimum script demand shy abstract ability move`
- demonic `dubhnach samhainmor zorgemael cailleachroth samhainmael dubhmael awenroth ogamwyr abraxfinn machanach sidhecarn beltangal dagdanach sidhevex tetradun imbolcmael draoivash caoinzael gohogal umbragoth machaneth aethercarn draoikiel draoinach zacarvex`
- falcon_seed `ff681836d409831e7a16231bfcf1fca8e0a27b17a2389ff76ce1a7232af4609a`
- pq_address `ZEJ4BLG3XWAUUZQGCEDJLYIC6D2NCWHRSX5DJMDPE54PXXR7G3PCQTARXU` (salt 5; asserted by go-algorand's own test)

## 6. Security properties and limits

- Entropy comes only from the OS or browser CSPRNG. An optional incantation is mixed in as
  `SHA-512(random ‖ 0x00 "incantation" 0x00 ‖ text)[0:32]` and cannot reduce it.
- Fewer than `k` shards give no information about the secret (Shamir 1979). The header reveals `k` and `x` by design.
- The demonic tongue adds no security. It is an encoding.
- The browser's Ed25519 code uses BigInt arithmetic and is not constant-time. It only derives public
  keys and never signs.

## 7. Format history

- **2026-10-01, initial release.** A quantum mode wrote a 48-byte seed as 36 words (37 for shards),
  following the earlier 48-byte `FalconSeed`. go-algorand has since set `FalconSeedSize = 32` and
  defined native PQ accounts from 25-word master phrases, so that mode was withdrawn the same day.
  Decoders reject 36- and 37-word phrases.
