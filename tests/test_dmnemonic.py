# dmnemonic — Algorand keys in the dmnemonic and demonic tongues
# Copyright (C) 2026 Professor Codephreak and the cypherpunk4096 contributors
# SPDX-License-Identifier: MIT
# Backend component, MIT licensed; see LICENSE-MIT.
"""Run: python3 -m unittest discover tests   (algosdk cross-checks skip if it is not installed)"""
import base64, os, random, secrets, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import dmnemonic as d

try:
    from algosdk import account, mnemonic
except ImportError:
    mnemonic = None


class Lexicons(unittest.TestCase):
    def test_sizes_and_disjoint(self):
        self.assertEqual(len(set(d.GRIMOIRE_WORDS)), 2048)
        self.assertFalse(set(d.GRIMOIRE_WORDS) & set(d.ALGORAND_WORDS))


class Phrases(unittest.TestCase):
    def test_roundtrip_both_tongues(self):
        seed = secrets.token_bytes(32)
        for lex in (d.ALGORAND, d.GRIMOIRE):
            words = d.encode(seed, lex)
            self.assertEqual(len(words), 25)
            self.assertEqual(d.decode(" ".join(words))[0], seed)

    def test_legacy_lengths_rejected(self):
        with self.assertRaises(d.PhraseError):
            d.decode(" ".join(d.encode(secrets.token_bytes(48), d.GRIMOIRE)))

    def test_bad_checksum(self):
        words = d.encode(secrets.token_bytes(32), d.GRIMOIRE)
        words[3] = d.GRIMOIRE_WORDS[(d.GRIMOIRE.lookup(words[3]) + 1) % 2048]
        with self.assertRaises(d.PhraseError):
            d.decode(" ".join(words))

    @unittest.skipIf(mnemonic is None, "algosdk not installed")
    def test_matches_algosdk(self):
        for _ in range(100):
            seed = secrets.token_bytes(32)
            sk = base64.b64encode(seed + d.ed25519_public_key(seed)).decode()
            self.assertEqual(" ".join(d.encode(seed, d.ALGORAND)), mnemonic.from_private_key(sk))
            self.assertEqual(d.algorand_address(d.ed25519_public_key(seed)), account.address_from_private_key(sk))


class PostQuantum(unittest.TestCase):
    V = d.VECTORS["quantum"]

    def test_falcon_seed_domain(self):
        e = bytes.fromhex(self.V["entropy"])
        self.assertEqual(d.pq_falcon_seed(e), d.sha512_256(b"PQK" + b"f1" + e))
        self.assertNotEqual(d.pq_falcon_seed(e), e)

    @unittest.skipIf(d.pq_helper() is None, "tools/pqaddr not built")
    def test_go_algorand_vector(self):
        acct = d.pq_account(bytes.fromhex(self.V["entropy"]))
        self.assertEqual((acct["address"], acct["salt"]), (self.V["pq_address"], self.V["salt"]))


class Coven(unittest.TestCase):
    def test_any_k_of_n(self):
        seed = secrets.token_bytes(32)
        shards = d.coven_split(seed, 3, 5)
        for _ in range(10):
            self.assertEqual(d.coven_bind(random.sample(shards, 3)), seed)

    def test_too_few(self):
        with self.assertRaises(d.PhraseError):
            d.coven_bind(d.coven_split(secrets.token_bytes(32), 3, 5)[:2])

    def test_mixed_covens_detected(self):
        a = d.coven_split(secrets.token_bytes(32), 2, 3)
        b = d.coven_split(secrets.token_bytes(32), 2, 3)
        with self.assertRaises(d.PhraseError):
            d.coven_bind([a[0], a[1], b[2]])

    def test_shard_phrase_roundtrip(self):
        h, y = d.coven_split(secrets.token_bytes(32), 2, 2)[0]
        payload, header, _ = d.decode(" ".join(d.encode(y, d.GRIMOIRE, h)))
        self.assertEqual((header, payload), (h, y))




if __name__ == "__main__":
    unittest.main()
