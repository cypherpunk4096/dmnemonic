// dmnemonic — Algorand keys in the dmnemonic and demonic tongues
// Copyright (C) 2026 Professor Codephreak and the cypherpunk4096 contributors
// SPDX-License-Identifier: MIT
// Backend component, MIT licensed; see LICENSE-MIT.
//
// pqaddr derives an Algorand native post-quantum (Falcon-1024, scheme "f1")
// account from 32 bytes of master entropy, exactly as go-algorand does
// (cmd/algokey/pq_scheme.go, data/basics/pq_address.go, consensus v42):
//
//	falconSeed = SHA512/256("PQK" || "f1" || entropy)
//	pk, sk     = falcon_det1024_keygen(SHAKE256(falconSeed))
//	salt       = lowest 0..255 whose address is NOT an Ed25519 point
//	address    = SHA512/256("PQA" || "f1" || salt || pk)
//
// It reads the entropy as hex on stdin (never as an argument, which would land
// in shell history and the process list) and prints JSON. The private key is
// never printed.
package main

import (
	"bufio"
	"crypto/sha512"
	"encoding/base32"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"strings"

	"filippo.io/edwards25519"
	"github.com/algorand/falcon"
)

var scheme = []byte("f1")

func checksumAddress(a [32]byte) string {
	sum := sha512.Sum512_256(a[:])
	raw := append(a[:], sum[len(sum)-4:]...)
	return base32.StdEncoding.WithPadding(base32.NoPadding).EncodeToString(raw)
}

func isEdwardsPoint(b []byte) bool {
	_, err := new(edwards25519.Point).SetBytes(b)
	return err == nil
}

func main() {
	line, _ := bufio.NewReader(os.Stdin).ReadString('\n')
	entropy, err := hex.DecodeString(strings.TrimSpace(line))
	if err != nil || len(entropy) != 32 {
		fmt.Fprintln(os.Stderr, "pqaddr: expected 32 bytes of hex entropy on stdin")
		os.Exit(2)
	}
	seed := sha512.Sum512_256(append(append([]byte("PQK"), scheme...), entropy...))
	pk, _, err := falcon.GenerateKey(seed[:])
	if err != nil {
		fmt.Fprintln(os.Stderr, "pqaddr: falcon keygen:", err)
		os.Exit(1)
	}
	for salt := 0; salt <= 255; salt++ {
		pre := append(append(append([]byte("PQA"), scheme...), byte(salt)), pk[:]...)
		addr := sha512.Sum512_256(pre)
		if isEdwardsPoint(addr[:]) {
			continue
		}
		pkSum := sha512.Sum512_256(pk[:])
		json.NewEncoder(os.Stdout).Encode(map[string]any{
			"scheme":           "f1",
			"falcon_seed_hash": hex.EncodeToString(func() []byte { h := sha512.Sum512_256(seed[:]); return h[:8] }()),
			"public_key_bytes": len(pk),
			"public_key_hash":  hex.EncodeToString(pkSum[:]),
			"salt":             salt,
			"address":          checksumAddress(addr),
		})
		return
	}
	fmt.Fprintln(os.Stderr, "pqaddr: no canonical salt for this key")
	os.Exit(1)
}
