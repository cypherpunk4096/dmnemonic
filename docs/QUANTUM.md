# Quantum

This document has two parts. **Part I** is practical: what Algorand's native post-quantum accounts
are, how dmnemonic makes and protects their master phrases, and how to derive the address.
**Part II** is a technical treatment of Falcon, the signature scheme behind those accounts, written
at the level of a doctoral survey with full references.

---

## Part I — Post-quantum accounts in practice

### 1.1 What changed on Algorand

Algorand accounts have been controlled by Ed25519 keys since launch (Bernstein et al. 2012;
Josefsson and Liusvaara 2017). Ed25519 rests on the elliptic-curve discrete-logarithm problem, which
Shor's algorithm solves in polynomial time on a large fault-tolerant quantum computer (Shor 1997).

Falcon already protected one corner of the protocol: the **state proofs** that let other chains
verify Algorand history are built from Falcon signatures (Micali et al. 2021). In July 2026,
go-algorand PR #6639 ("txn: native PQ accounts") extended Falcon to ordinary accounts:

- a new `pqsig` transaction signature envelope `{sch, slt, pk, sig}`,
- the scheme tag `f1` for Falcon-1024 with a deterministic signing profile (`f2`, Falcon-512, is reserved),
- `algokey pq` commands to generate, import and sign.

Consensus version **v42** sets `EnablePQSchemeFalcon1024 = true`. When this was written
(2026-10-01), mainnet and testnet both reported v42 as their current protocol, so post-quantum
accounts are live.

### 1.2 How a PQ account is derived

The backup is an ordinary-looking 25-word Algorand mnemonic over 256 bits of **master entropy**.
go-algorand derives everything else from it:

```
entropy     = 32 random bytes                          (the 25-word phrase)
falcon_seed = SHA-512/256("PQK" ‖ "f1" ‖ entropy)      cmd/algokey/pq_scheme.go  derivePQKeySeed
pk, sk      = Falcon-1024 deterministic keygen         github.com/algorand/falcon  falcon_det1024_keygen
              (SHAKE256 PRNG seeded with falcon_seed)
salt        = lowest 0…255 such that the address below
              is NOT a valid Ed25519 point encoding     data/basics/pq_address.go  CanonicalPQAddressSalt
address     = SHA-512/256("PQA" ‖ "f1" ‖ salt ‖ pk)     data/basics/pq_address.go  PQAddress
```

Two design points matter for users:

- **Domain separation.** `"PQK"` and the scheme tag make the Falcon seed a different value from the
  entropy, and a future scheme (`f2`, …) would get an unrelated seed from the same entropy.
- **The salt.** An address that happens to decode as an Ed25519 point would, in principle, admit an
  Ed25519 key. Searching for the lowest salt that lands *off* the curve removes that path. About half of
  random 32-byte strings are valid points, so the salt is usually a small number (the test vector
needs 5).

### 1.3 What dmnemonic does

| | Python CLI | browser page |
|---|---|---|
| make the 25-word PQ master phrase in both tongues | `summon --quantum` | Summon → Quantum · Falcon-1024 |
| translate, reveal, shard, bind | yes, with `--pq` | yes, with the post-quantum checkbox |
| Falcon seed and seed id | yes | yes |
| PQ **address** | yes, through `tools/pqaddr` | no: points to `tools/pqaddr` or `algokey` |

The address requires Falcon-1024 key generation: an NTRU-equation solver over large integers, an
FFT, and a SHAKE256 PRNG, all of which must match the reference bit for bit. Rather than
re-implement that, the repository ships a 90-line Go helper, `tools/pqaddr`. It links Algorand's own
Falcon library (`github.com/algorand/falcon` v0.1.0, the one go-algorand uses) and repeats the
derivation above. It reproduces go-algorand's test vector from `cmd/algokey/pq_test.go`:

```
entropy 01 02 03 … 20  →  ZEJ4BLG3XWAUUZQGCEDJLYIC6D2NCWHRSX5DJMDPE54PXXR7G3PCQTARXU  (salt 5)
```

`dmnemonic.py selftest` checks this vector whenever the helper is built.

**Build the helper** (Go ≥ 1.24 and a C compiler, because the Falcon library uses cgo):

```sh
cd tools/pqaddr && go build -o pqaddr . && cd ../..
./dmnemonic.py selftest        # → ✓ PQ address matches go-algorand's algokey test vector
./dmnemonic.py summon --quantum --gloss
```

The helper reads entropy as hex on **stdin**, never as an argument, so it stays out of shell history
and the process list. It prints the address, salt and a hash of the public key, and never prints the
private key.

**Cross-check with Algorand's own tool**, if you have go-algorand installed:

```sh
algokey pq import -m "<the 25 dmnemonic words>" -k pq.key   # restores the PQ key
algokey pq info -k pq.key                                    # shows the address
```

A demonic phrase must first be translated back: `./dmnemonic.py translate --to dmnemonic --oneline <words…>`.

### 1.4 The one rule: never cross the readings

A 25-word phrase carries 32 bytes. They are valid as an **Ed25519 seed** and valid as **PQ master
entropy**, and nothing in the words says which you meant.

Suppose a PQ master phrase is also imported into Pera or Defly as an ordinary account. An Algorand
ed25519 address *is* the public key plus a checksum, so once that address is funded, shared or shown
anywhere, the public key is public. An adversary with a cryptographically relevant quantum
computer runs Shor's algorithm on it, recovers the Ed25519 seed (which *is* the entropy), computes
`SHA-512/256("PQK" ‖ "f1" ‖ entropy)`, regenerates the Falcon key, and drains the PQ account. The
Falcon layer would have been bypassed entirely.

So:

- Use a PQ master phrase **only** with PQ tooling (`algokey pq`, `tools/pqaddr`, `--pq`).
- Label the paper: `PQ · Falcon-1024 · f1`. dmnemonic prints the warning on every PQ summon.
- Never "check" a PQ phrase by pasting it into an ordinary wallet.

### 1.5 What quantum computers do and do not threaten here

| component | best known quantum attack | effect |
|---|---|---|
| Ed25519 accounts | Shor (1997): polynomial time | broken once the public key is known |
| 256-bit entropy / SHA-512/256 preimages | Grover (1996): square-root speed-up | about 128-bit security, which remains adequate |
| Falcon-1024 | no known algorithm better than classical lattice reduction plus generic speed-ups | rated NIST category 5 |
| Shamir coven shards | none applies: security is information-theoretic | unaffected |
| the demonic encoding | not cryptographic | unaffected |

Some chains hash the public key into the address, so an account that has never signed keeps its key
hidden. Algorand does not: an ed25519 address is the public key plus a checksum, so every ed25519
account exposes its key as soon as its address is known. Only PQ accounts remove the dependence on
elliptic curves.

---

## Part II — Falcon: a technical survey

### Abstract

Falcon ("Fast-Fourier Lattice-based Compact Signatures over NTRU") is a hash-and-sign signature
scheme. It instantiates the Gentry–Peikert–Vaikuntanathan (GPV) framework over NTRU lattices and uses
a fast Fourier sampler to produce short lattice vectors whose distribution leaks nothing about the
secret basis (Fouque et al. 2020; Gentry, Peikert and Vaikuntanathan 2008; Ducas and Prest 2016).
Among the signatures NIST selected for standardisation in 2022, it has the smallest combined
public-key-plus-signature size, which suits a ledger that stores every signature forever. This survey
places Falcon in its lineage, sets out its mathematics, and explains why Algorand chose a
*deterministic* profile of it. It then reviews the known weaknesses of the construction, chiefly
floating-point arithmetic and side channels, and what they mean for a wallet.

### 1. The problem Falcon solves

Classical signatures (RSA, ECDSA, EdDSA) rest on factoring or discrete logarithms, both broken by
Shor's algorithm (Shor 1997). Post-quantum signatures replace them with problems for which no
quantum speed-up beyond generic search is known. The leading families are:

- **lattice-based** (Falcon; ML-DSA, also called Dilithium),
- **hash-based** (SPHINCS+, now SLH-DSA),
- **multivariate**, **code-based** and **isogeny-based** constructions, which are less mature.

For a blockchain the binding constraint is size. Every transaction carries a signature, and every
account that has transacted exposes a public key. Falcon-1024 has a 1,793-byte public key (the size
`tools/pqaddr` reports) and signatures of roughly 1.3 kB. Comparable ML-DSA parameters need roughly
twice the combined bytes, and SLH-DSA signatures are an order of magnitude larger. Falcon pays for its
compactness with implementation complexity. Most of this survey is about that trade.

### 2. Lineage

**2.1 GGH and its failure.** The first lattice signatures, GGH (Goldreich, Goldwasser and Halevi
1997) and NTRUSign (Hoffstein et al. 2003), signed by rounding a target point to a nearby lattice
point using a secret short basis (Babai's round-off; Babai 1986). Each signature leaked a sample from
the *parallelepiped* spanned by the secret basis. Nguyen and Regev (2006; journal version 2009) showed
that a few thousand signatures suffice to recover that parallelepiped, and with it the key. The
lesson set the agenda for the next decade: **a signature's distribution must not depend on the secret
basis.**

**2.2 GPV: hash-and-sign done right.** Gentry, Peikert and Vaikuntanathan (2008) replaced
deterministic rounding with *discrete Gaussian sampling*. Given a target `c`, the signer samples a
lattice point near `c` from a discrete Gaussian centred on `c`, using a randomised nearest-plane
algorithm in the style of Klein (2000). The output distribution depends only on the public lattice
and a width parameter σ, provided σ exceeds the *smoothing parameter* scaled by the Gram–Schmidt norm
of the secret basis. The scheme is existentially unforgeable in the random-oracle model, reducing to
the Short Integer Solution (SIS) problem. Boneh et al. (2011) later showed that GPV-style hash-and-sign
also holds in the *quantum* random-oracle model, the setting that matters once adversaries can query
the hash in superposition.

**2.3 NTRU lattices.** GPV over arbitrary lattices is impractical, because keys are matrices of
dimension in the thousands. NTRU (Hoffstein, Pipher and Silverman 1998) supplies lattices with
polynomial structure, so a key is a few polynomials in `Z[x]/(xⁿ + 1)`. Ducas, Lyubashevsky and Prest
(2014) showed that NTRU lattices admit short trapdoor bases of near-optimal Gram–Schmidt norm, which
lets GPV sampling run with a small σ and therefore produce short signatures.

**2.4 Fast Fourier sampling.** Klein's sampler costs `O(n²)`. Ducas and Prest (2016) introduced
*fast Fourier orthogonalisation*. It exploits the tower of cyclotomic fields
`Q[x]/(x^{2^k} + 1)` to compute an LDL* decomposition of the basis as a binary tree (the "ffLDL tree"),
and to sample in `O(n log n)`. Falcon is that sampler, NTRU trapdoors and GPV assembled into one
scheme (Fouque et al. 2020; see Prest 2015 for the underlying thesis). Faster key generation came from
the field-norm technique of Pornin and Prest (2019).

### 3. The construction

Let `n = 1024` (Falcon-1024) or `512`, `q = 12289` (a prime with `q ≡ 1 mod 2n`, so the NTT applies),
and `R = Z[x]/(xⁿ + 1)`.

**Key generation.**

1. Sample short `f, g ∈ R` with coefficients from a discrete Gaussian, retrying until `f` is
   invertible mod `q` and the Gram–Schmidt norm of the resulting basis is small enough.
2. Solve the **NTRU equation** `fG − gF = q` for short `F, G ∈ R`. Pornin and Prest (2019) do this
   recursively with field norms down the tower, then Babai-reduce `(F, G)` against `(f, g)`.
3. The public key is `h = g · f⁻¹ mod q`. The secret basis of the NTRU lattice
   `Λ_h = {(u, v) : u + v·h ≡ 0 mod q}` is
   ```
   B = | g  −f |
       | G  −F |
   ```
   It is precomputed in FFT form together with its ffLDL tree, whose leaves are normalised by σ.

The public key is `h` encoded at 14 bits per coefficient: 1 + 1024·14/8 = 1,793 bytes.

**Signing** a message `m`:

1. Draw a 40-byte salt `r`. Compute `c = HashToPoint(r ‖ m) ∈ Z_q[x]/(xⁿ + 1)` with SHAKE256 and
   rejection sampling.
2. Compute the preimage `t = (c, 0) · B⁻¹` in FFT form, and run **ffSampling** down the tree to get
   `z` such that `s = (t − z) · B` is short. Then `s = (s₁, s₂)` satisfies `s₁ + s₂·h ≡ c mod q`.
3. If `‖s‖² > ⌊β²⌋`, restart. Otherwise output `(r, Compress(s₂))`. Only `s₂` is sent, because the
   verifier can recompute `s₁`.

**Verification.** Recompute `c`, set `s₁ = c − s₂·h mod q` (centred), and accept if and only if
`‖(s₁, s₂)‖² ≤ ⌊β²⌋`. Verification is one NTT-based polynomial multiplication. It is cheap even next
to Ed25519, which is why #6639 adds no extra CPU fee component for `f1`.

**Security.** Forging requires a short vector `(s₁, s₂)` with `s₁ + s₂h = c` for a fresh random `c`.
That is SIS on the NTRU lattice, and in the (quantum) random-oracle model it reduces to the hardness
of approximate shortest-vector problems on NTRU lattices (Gentry, Peikert and Vaikuntanathan 2008;
Boneh et al. 2011; Fouque et al. 2020). Concrete security is estimated from the cost of the best
lattice-reduction attacks (BKZ with sieving). Falcon-512 is placed at NIST category 1 and Falcon-1024
at category 5.

### 4. Determinism: Algorand's profile

Standard Falcon signing is randomised twice over: by the salt `r` and by the Gaussian sampler's
randomness. Two signatures of the same message differ, which complicates consensus code (identical
inputs should give identical bytes), test vectors and audits. Algorand's library
(`github.com/algorand/falcon`) adds a **deterministic** profile, specified in `falcon-det.pdf` in that
repository and selected by the `f1` tag ("Falcon-1024 using a deterministic signing profile",
`protocol/pq_scheme.go`). Signing is derandomised (the exact construction is given in `falcon-det.pdf`), so a given key and
message always yield the same signature. Signatures use the fixed-length "CT" encoding
(`FalconMaxSignatureSize = cfalcon.CTSignatureSize`), which avoids variable-length parsing.

Key generation is deterministic in any case: `falcon_det1024_keygen` seeds a SHAKE256 PRNG with the
32-byte Falcon seed. That is why a 25-word phrase can recreate a Falcon key exactly, and why
`tools/pqaddr` can reproduce go-algorand's addresses.

Determinism has a known cost. Derandomised lattice signers are exposed to *fault attacks*: if the
same message is signed twice and one computation is perturbed, the two outputs can be compared. This
is the classic risk of deterministic signing in general. Hardware wallets that implement `f1` should
therefore protect the signing path against faults.

### 5. Implementation hazards

**Floating point.** ffSampling and key generation use IEEE-754 double-precision FFTs. Results must be
bit-exact across platforms, or the same seed would yield different keys on different machines. The
reference implementation therefore offers both native `double` arithmetic (where the platform is
trusted to be IEEE-exact) and an integer emulation (`fpr.c`) that is portable and constant-time. A
from-scratch JavaScript port would have to reproduce this behaviour exactly. That is the main reason
dmnemonic links the reference code through `tools/pqaddr` instead of re-implementing Falcon in the
page.

**Side channels.** The Gaussian sampler and the floating-point operations are classic timing and
power targets (Kocher 1996). Karabulut and Aysu (2021) recovered Falcon keys from electromagnetic
traces of the reference FFT on an embedded device. Constant-time sampling and masking are active
research topics. For dmnemonic the exposure is limited: the helper only runs key generation once, on
the user's own machine, and never signs.

**Key-generation retries.** `f` and `g` are resampled until the basis quality bound holds, so
key-generation time varies with the seed. That variation reveals at most information about rejected
candidates, not the accepted key, but it is one more reason to run it offline.

### 6. Objections, answered

*"Lattice assumptions are younger than factoring."* True. The NTRU problem dates from 1996–98, and
structured-lattice cryptanalysis is still improving. The hedge is diversity: Algorand's `pqsig`
envelope carries a scheme tag, so a second scheme (`f2`, or a hash-based one) can be added by protocol
upgrade without changing addresses already in use. Hash-based SLH-DSA rests on weaker assumptions but
costs roughly ten times the bytes.

*"Why not ML-DSA, NIST's primary choice?"* ML-DSA is simpler and easier to make constant-time. For a
ledger that stores every signature permanently, Falcon's size advantage compounds. Algorand already
operated Falcon in state proofs, so the choice reuses audited code.

*"A 25-word phrase is the weakest link."* Partly true. The master entropy has 256 bits, so Grover
leaves about 128 bits. The real risk is the cross-reading described in §1.4, which is operational,
not mathematical. dmnemonic addresses it with labelling, the `--pq` reading and warnings. The coven
removes the single point of failure that one paper backup represents.

### References

- Babai, L. (1986). "On Lovász' lattice reduction and the nearest lattice point problem." *Combinatorica* 6(1): 1–13.
- Bernstein, D. J., Duif, N., Lange, T., Schwabe, P. and Yang, B.-Y. (2012). "High-speed high-security signatures." *Journal of Cryptographic Engineering* 2(2): 77–89.
- Boneh, D., Dagdelen, Ö., Fischlin, M., Lehmann, A., Schaffner, C. and Zhandry, M. (2011). "Random oracles in a quantum world." *ASIACRYPT 2011*, LNCS 7073. Springer.
- Ducas, L., Lyubashevsky, V. and Prest, T. (2014). "Efficient identity-based encryption over NTRU lattices." *ASIACRYPT 2014*, LNCS 8874. Springer.
- Ducas, L. and Prest, T. (2016). "Fast Fourier orthogonalization." *Proceedings of ISSAC 2016*. ACM.
- Fouque, P.-A., Hoffstein, J., Kirchner, P., Lyubashevsky, V., Pornin, T., Prest, T., Ricosset, T., Seiler, G., Whyte, W. and Zhang, Z. (2020). "Falcon: Fast-Fourier lattice-based compact signatures over NTRU." Specification v1.2, NIST Post-Quantum Cryptography Standardization, Round 3.
- Gentry, C., Peikert, C. and Vaikuntanathan, V. (2008). "Trapdoors for hard lattices and new cryptographic constructions." *Proceedings of STOC 2008*. ACM.
- Goldreich, O., Goldwasser, S. and Halevi, S. (1997). "Public-key cryptosystems from lattice reduction problems." *CRYPTO '97*, LNCS 1294. Springer.
- Grover, L. K. (1996). "A fast quantum mechanical algorithm for database search." *Proceedings of STOC 1996*. ACM.
- Hoffstein, J., Howgrave-Graham, N., Pipher, J., Silverman, J. H. and Whyte, W. (2003). "NTRUSign: Digital signatures using the NTRU lattice." *CT-RSA 2003*, LNCS 2612. Springer.
- Hoffstein, J., Pipher, J. and Silverman, J. H. (1998). "NTRU: A ring-based public key cryptosystem." *Algorithmic Number Theory (ANTS-III)*, LNCS 1423. Springer.
- Josefsson, S. and Liusvaara, I. (2017). *Edwards-Curve Digital Signature Algorithm (EdDSA)*. RFC 8032. IETF.
- Karabulut, E. and Aysu, A. (2021). "FALCON Down: Breaking FALCON post-quantum signature scheme through side-channel attacks." *Proceedings of DAC 2021*. IEEE/ACM.
- Klein, P. (2000). "Finding the closest lattice vector when it's unusually close." *Proceedings of SODA 2000*. ACM–SIAM.
- Kocher, P. C. (1996). "Timing attacks on implementations of Diffie-Hellman, RSA, DSS, and other systems." *CRYPTO '96*, LNCS 1109. Springer.
- Micali, S., Reyzin, L., Vlachos, G., Wahby, R. S. and Zeldovich, N. (2021). "Compact certificates of collective knowledge." *IEEE Symposium on Security and Privacy 2021*.
- Nguyen, P. Q. and Regev, O. (2009). "Learning a parallelepiped: Cryptanalysis of GGH and NTRU signatures." *Journal of Cryptology* 22(2): 139–160. (Conference version: EUROCRYPT 2006.)
- Pornin, T. and Prest, T. (2019). "More efficient algorithms for the NTRU key generation using the field norm." *PKC 2019*, LNCS 11443. Springer.
- Prest, T. (2015). *Gaussian Sampling in Lattice-Based Cryptography*. PhD thesis, École Normale Supérieure.
- Shamir, A. (1979). "How to share a secret." *Communications of the ACM* 22(11): 612–613.
- Shor, P. W. (1997). "Polynomial-time algorithms for prime factorization and discrete logarithms on a quantum computer." *SIAM Journal on Computing* 26(5): 1484–1509.

**Primary code sources** (go-algorand, read 2026-10-01): PR #6639 "txn: native PQ accounts" (merged
2026-07-10); `crypto/falconWrapper.go`; `cmd/algokey/pq_scheme.go`; `data/basics/pq_address.go`;
`protocol/pq_scheme.go`; `config/consensus.go` (v42); `cmd/algokey/pq_test.go`. Falcon library:
`github.com/algorand/falcon` v0.1.0, including `falcon-det.pdf`.
