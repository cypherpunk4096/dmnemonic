/*
 * dmnemonic — Algorand keys in the dmnemonic and demonic tongues
 * Copyright (C) 2026 Professor Codephreak and the cypherpunk4096 contributors
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 * This program is free software: you can redistribute it and/or modify it under
 * the terms of the GNU General Public License as published by the Free Software
 * Foundation, either version 3 of the License, or (at your option) any later
 * version. It is distributed WITHOUT ANY WARRANTY; see LICENSE-GPL-3.0.
 * Client-side component, GPL-3.0-or-later.
 */
"use strict";
// ---- dmnemonic core: bit-identical to dmnemonic.py and algosdk ----

// SHA-512 family. Round constants and IV are derived from prime roots at load.
const M64 = (1n << 64n) - 1n;
function primes(n) { const p = []; for (let i = 2; p.length < n; i++) if (p.every(q => i % q)) p.push(i); return p; }
function iroot(v, k) { // floor(v^(1/k)) for BigInt
  let x = 1n << BigInt(Math.ceil(v.toString(2).length / k));
  for (;;) { const y = ((BigInt(k) - 1n) * x + v / x ** BigInt(k - 1)) / BigInt(k); if (y >= x) return x; x = y; }
}
const PR = primes(80);
const K512 = PR.map(p => iroot(BigInt(p) << 192n, 3) & M64);
const IV512 = PR.slice(0, 8).map(p => iroot(BigInt(p) << 128n, 2) & M64);
const rotr = (x, n) => ((x >> n) | (x << (64n - n))) & M64;

function sha512core(msg, iv) {
  const len = msg.length, padLen = ((len + 17 + 127) >> 7) << 7;
  const b = new Uint8Array(padLen); b.set(msg); b[len] = 0x80;
  let bits = BigInt(len) * 8n;
  for (let i = 0; i < 16; i++) { b[padLen - 1 - i] = Number(bits & 255n); bits >>= 8n; }
  const H = iv.slice(), W = new Array(80);
  for (let off = 0; off < padLen; off += 128) {
    for (let t = 0; t < 16; t++) { let w = 0n; for (let j = 0; j < 8; j++) w = (w << 8n) | BigInt(b[off + t * 8 + j]); W[t] = w; }
    for (let t = 16; t < 80; t++) {
      const s0 = rotr(W[t - 15], 1n) ^ rotr(W[t - 15], 8n) ^ (W[t - 15] >> 7n);
      const s1 = rotr(W[t - 2], 19n) ^ rotr(W[t - 2], 61n) ^ (W[t - 2] >> 6n);
      W[t] = (W[t - 16] + s0 + W[t - 7] + s1) & M64;
    }
    let [a, bb, c, d, e, f, g, h] = H;
    for (let t = 0; t < 80; t++) {
      const S1 = rotr(e, 14n) ^ rotr(e, 18n) ^ rotr(e, 41n), ch = (e & f) ^ (~e & M64 & g);
      const T1 = (h + S1 + ch + K512[t] + W[t]) & M64;
      const S0 = rotr(a, 28n) ^ rotr(a, 34n) ^ rotr(a, 39n), maj = (a & bb) ^ (a & c) ^ (bb & c);
      h = g; g = f; f = e; e = (d + T1) & M64; d = c; c = bb; bb = a; a = (T1 + S0 + maj) & M64;
    }
    [a, bb, c, d, e, f, g, h].forEach((v, i) => { H[i] = (H[i] + v) & M64; });
  }
  const out = new Uint8Array(64);
  H.forEach((v, i) => { for (let j = 0; j < 8; j++) out[i * 8 + j] = Number((v >> BigInt(56 - 8 * j)) & 255n); });
  return out;
}
const sha512 = m => sha512core(m, IV512);
// SHA-512/t IV generation (FIPS 180-4 §5.3.6): hash "SHA-512/256" under IV512 ^ a5a5…
const IV512_256 = (() => {
  const d = sha512core(new TextEncoder().encode("SHA-512/256"), IV512.map(v => v ^ 0xa5a5a5a5a5a5a5a5n));
  return Array.from({ length: 8 }, (_, i) => d.slice(i * 8, i * 8 + 8).reduce((a, x) => (a << 8n) | BigInt(x), 0n));
})();
const sha512_256 = m => sha512core(m, IV512_256).slice(0, 32);

// Lexicons
const GRIMOIRE_WORDS = ROOTS.flatMap(([r]) => SUFFIXES.map(([s]) => r + s));
const gloss = i => `${ROOTS[i >> 5][1]} · ${SUFFIXES[i & 31][1]}`;
function makeLexicon(name, words, prefixMin) {
  const index = new Map(words.map((w, i) => [w, i])), counts = new Map();
  for (const w of words) for (let n = prefixMin; n < w.length; n++) counts.set(w.slice(0, n), (counts.get(w.slice(0, n)) || 0) + 1);
  words.forEach((w, i) => { for (let n = prefixMin; n < w.length; n++) { const p = w.slice(0, n); if (counts.get(p) === 1 && !index.has(p)) index.set(p, i); } });
  return { name, words, lookup: w => index.get(w), suggest: w => words.reduce((b, c) => lev(w, c) < lev(w, b) ? c : b) };
}
function lev(a, b) {
  let prev = Array.from({ length: b.length + 1 }, (_, i) => i);
  for (let i = 1; i <= a.length; i++) {
    const cur = [i];
    for (let j = 1; j <= b.length; j++) cur.push(Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] !== b[j - 1])));
    prev = cur;
  }
  return prev[b.length];
}
const ALGORAND = makeLexicon("dmnemonic", ALGORAND_WORDS, 4);
const GRIMOIRE = makeLexicon("demonic", GRIMOIRE_WORDS, 6);

// Algorand 11-bit little-endian packing
function to11(data) {
  let buf = 0, bits = 0; const out = [];
  for (const b of data) { buf |= b << bits; bits += 8; if (bits >= 11) { out.push(buf & 2047); buf >>>= 11; bits -= 11; } }
  if (bits) out.push(buf & 2047);
  return out;
}
function from11(nums) {
  let buf = 0, bits = 0; const out = [];
  for (const n of nums) { buf |= n << bits; bits += 11; while (bits >= 8) { out.push(buf & 255); buf >>>= 8; bits -= 8; } }
  if (bits) out.push(buf & 255);
  return Uint8Array.from(out);
}
const cat = (...a) => { const o = new Uint8Array(a.reduce((n, x) => n + x.length, 0)); let i = 0; for (const x of a) { o.set(x, i); i += x.length; } return o; };
const hdrBytes = h => h == null ? new Uint8Array(0) : Uint8Array.of(h & 255, h >> 8);
const checksumIndex = d => to11(sha512_256(d).slice(0, 2))[0];
const KINDS = { 25: [32, false], 26: [32, true] };  // a phrase (ed25519 seed or PQ master), or a coven shard
const SEAL_VERSION = 1;

function encode(payload, lex, header = null) {
  const nums = (header == null ? [] : [header]).concat(to11(payload));
  return nums.map(n => lex.words[n]).concat(lex.words[checksumIndex(cat(hdrBytes(header), payload))]);
}
function decode(phrase) {
  const words = phrase.toLowerCase().replace(/[,\d.]+/g, " ").split(/\s+/).filter(Boolean);
  if (!KINDS[words.length]) throw new Error(`${words.length} words. Expected 25 (a phrase) or 26 (a coven shard).`);
  const [nbytes, hasHeader] = KINDS[words.length];
  let lex = [ALGORAND, GRIMOIRE].find(l => words.every(w => l.lookup(w) !== undefined));
  if (!lex) {
    const best = [ALGORAND, GRIMOIRE].reduce((a, b) => words.filter(w => b.lookup(w) !== undefined).length > words.filter(w => a.lookup(w) !== undefined).length ? b : a);
    const bad = words.filter(w => best.lookup(w) === undefined);
    throw new Error(`unknown ${best.name} word(s): ` + bad.map(w => `“${w}” (did you mean “${best.suggest(w)}”?)`).join(", "));
  }
  const nums = words.map(w => lex.lookup(w));
  const header = hasHeader ? nums.shift() : null, chk = nums.pop();
  const raw = from11(nums), payload = raw.slice(0, nbytes);
  if (raw.slice(nbytes).some(x => x)) throw new Error("checksum failed (non-zero padding bits)");
  if (checksumIndex(cat(hdrBytes(header), payload)) !== chk) throw new Error("checksum failed — a word is wrong or out of order");
  return { payload, header, lex };
}

// Ed25519 public key (RFC 8032)
const P = (1n << 255n) - 19n;
const mod = a => ((a % P) + P) % P;
const powm = (b, e) => { let r = 1n; b = mod(b); while (e) { if (e & 1n) r = r * b % P; b = b * b % P; e >>= 1n; } return r; };
const D = mod(-121665n * powm(121666n, P - 2n));
const BX = 15112221349535400772501151409588531511454012693041857206046113283949847762202n;
const BY = 46316835694926478169428394003475163141307993866256225615783033603165251855960n;
function ptAdd([x1, y1, z1, t1], [x2, y2, z2, t2]) {
  const a = mod((y1 - x1) * (y2 - x2)), b = mod((y1 + x1) * (y2 + x2));
  const c = mod(t1 * 2n * D * t2), d = mod(z1 * 2n * z2);
  const e = b - a, f = d - c, g = d + c, h = b + a;
  return [mod(e * f), mod(g * h), mod(f * g), mod(e * h)];
}
function ed25519PublicKey(seed) {
  const h = sha512(seed);
  let a = 0n; for (let i = 31; i >= 0; i--) a = (a << 8n) | BigInt(h[i]);
  a &= (1n << 254n) - 8n; a |= 1n << 254n;
  let r = [0n, 1n, 1n, 0n], p = [BX, BY, 1n, mod(BX * BY)];
  while (a) { if (a & 1n) r = ptAdd(r, p); p = ptAdd(p, p); a >>= 1n; }
  const zi = powm(r[2], P - 2n), x = mod(r[0] * zi);
  let y = mod(r[1] * zi) | ((x & 1n) << 255n);
  const out = new Uint8Array(32); for (let i = 0; i < 32; i++) { out[i] = Number(y & 255n); y >>= 8n; }
  return out;
}
function base32(bytes) {
  const A = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"; let bits = 0, v = 0, s = "";
  for (const b of bytes) { v = (v << 8) | b; bits += 8; while (bits >= 5) { s += A[(v >>> (bits - 5)) & 31]; bits -= 5; } }
  if (bits) s += A[(v << (5 - bits)) & 31];
  return s;
}
const algorandAddress = pub => base32(cat(pub, sha512_256(pub).slice(-4)));
const hex = b => Array.from(b, x => x.toString(16).padStart(2, "0")).join("");
// Algorand native post-quantum accounts (go-algorand #6639, consensus v42):
// the Falcon-1024 seed is SHA-512/256("PQK" || "f1" || entropy). The PQ address
// needs Falcon key generation, which this page does not run (see docs/QUANTUM.md).
const pqFalconSeed = entropy => sha512_256(cat(new TextEncoder().encode("PQKf1"), entropy));
function describe(payload, pq = false) {
  if (!pq) { const pub = ed25519PublicKey(payload); return { kind: "Algorand account (ed25519)", address: algorandAddress(pub), pub }; }
  const id = sha512_256(pqFalconSeed(payload)).slice(0, 8);
  return { kind: "Algorand PQ account (Falcon-1024, scheme f1)", seedId: hex(id), pub: id };
}

// Coven: Shamir over GF(256)
const EXP = new Uint8Array(512), LOG = new Uint8Array(256);
for (let i = 0, x = 1; i < 255; i++) { EXP[i] = x; LOG[x] = i; x ^= (x << 1) ^ (x & 0x80 ? 0x11b : 0); x &= 255; }
for (let i = 255; i < 512; i++) EXP[i] = EXP[i - 255];
const gmul = (a, b) => a && b ? EXP[LOG[a] + LOG[b]] : 0;
const gdiv = (a, b) => a ? EXP[LOG[a] - LOG[b] + 255] : 0;
const randomBytes = n => crypto.getRandomValues(new Uint8Array(n));

// `coeffs` is only for test vectors; normal use draws them from the CSPRNG.
function covenSplit(secret, k, n, coeffs = null) {
  if (!(2 <= k && k <= n && n <= 15)) throw new Error("need 2 ≤ threshold ≤ shards ≤ 15");
  coeffs = coeffs || Array.from({ length: k - 1 }, () => randomBytes(secret.length));
  const shards = [];
  for (let x = 1; x <= n; x++) {
    const y = secret.map((s, i) => { let acc = 0; for (let c = coeffs.length - 1; c >= 0; c--) acc = gmul(acc ^ coeffs[c][i], x); return acc ^ s; });
    shards.push({ header: (SEAL_VERSION << 8) | ((k - 1) << 4) | x, y });
  }
  return shards;
}
function covenBind(shards) {
  const ks = new Set(shards.map(s => (s.header >> 4) & 15));
  if (ks.size !== 1) throw new Error("shards come from covens with different thresholds");
  const k = [...ks][0] + 1, xs = new Map();
  for (const s of shards) { if (s.header >> 8 !== SEAL_VERSION) throw new Error("unknown seal version"); xs.set(s.header & 15, s.y); }
  if (xs.size < k) throw new Error(`this coven needs ${k} distinct shards, got ${xs.size}`);
  const pts = [...xs.entries()].sort((a, b) => a[0] - b[0]);
  const interp = ps => ps[0][1].map((_, i) => ps.reduce((acc, [xj, yj], j) => {
    let num = 1, den = 1;
    ps.forEach(([xm], m) => { if (m !== j) { num = gmul(num, xm); den = gmul(den, xj ^ xm); } });
    return acc ^ gmul(yj[i], gdiv(num, den));
  }, 0));
  const secret = interp(pts.slice(0, k));
  if (pts.length > k && hex(interp(pts.slice(-k))) !== hex(secret)) throw new Error("surplus shards disagree — they are not from the same coven");
  return secret;
}
function gatherEntropy(n, incantation) {
  const raw = randomBytes(n);
  if (!incantation) return raw;
  return sha512(cat(raw, new TextEncoder().encode("\0incantation\0" + incantation))).slice(0, n);
}

// Known-answer tests. Vectors are shared with dmnemonic.py and SPEC.md; the
// ed25519 and Algorand values come from RFC 8032 and algosdk, not from this code.
const unhex = h => Uint8Array.from(h.match(/../g), x => parseInt(x, 16));
const VECTORS = /*@@VECTORS@@*/;
function selfTest() {
  const fails = [], ok = (name, cond) => { if (!cond) fails.push(name); };
  const abc = new TextEncoder().encode("abc");
  try {
    ok("SHA-512", hex(sha512(abc)).startsWith("ddaf35a193617aba"));
    ok("SHA-512/256", hex(sha512_256(abc)) === VECTORS.sha512_256_abc);
    for (const v of VECTORS.accounts) {
      const seed = unhex(v.seed), pub = ed25519PublicKey(seed);
      ok("Ed25519", hex(pub) === v.pub);
      ok("address", algorandAddress(pub) === v.address);
      ok("dmnemonic", encode(seed, ALGORAND).join(" ") === v.dmnemonic);
      ok("demonic", encode(seed, GRIMOIRE).join(" ") === v.demonic);
      ok("decode", hex(decode(v.demonic).payload) === v.seed);
    }
    const c = VECTORS.coven, shards = covenSplit(unhex(c.seed), c.k, c.n, c.coeffs.map(unhex));
    ok("coven split", shards.every((s, i) => encode(s.y, GRIMOIRE, s.header).join(" ") === c.shards[i]));
    ok("coven bind", hex(covenBind(c.shards.slice(-c.k).map(t => { const d = decode(t); return { header: d.header, y: d.payload }; }))) === c.seed);
    const q = VECTORS.quantum;
    ok("PQ phrase", hex(decode(q.demonic).payload) === q.entropy && encode(unhex(q.entropy), ALGORAND).join(" ") === q.dmnemonic);
    ok("PQ Falcon seed", hex(pqFalconSeed(unhex(q.entropy))) === q.falcon_seed);
    ok("lexicon", new Set(GRIMOIRE_WORDS).size === 2048 && !GRIMOIRE_WORDS.some(w => ALGORAND.lookup(w) !== undefined));
    const r1 = randomBytes(64), r2 = randomBytes(64);
    ok("CSPRNG", hex(r1) !== hex(r2) && new Set(r1).size > 16);
  } catch (e) { fails.push("exception: " + e.message); }
  return fails;
}
