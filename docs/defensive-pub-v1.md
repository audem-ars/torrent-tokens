# Torrent-Tokens: Defensive Publication v1.0  
> 2024-06-XX  (today’s date)  
> Permanent link: https://github.com/audem-ars/torrent-tokens/releases/tag/v1.0-pub  

## 1. One-liner value prop  
Free, private, real-time LLM inference by stitching everyday devices into one GPU-like swarm.

## 2. High-level flow (normative)  
Shard 4-bit weights into ~5 MB tiles → stream tiles P2P → verify each tile result with a 128-bit checksum and 2-of-3 vote → reward = SRAM_MB × upload_Mb/s ÷ watts.

## 3. Wire format (normative)  
See `src/wire_format.py` for byte-exact TLV specification.

## 4. Reference implementation  
`src/wire_format.py` – MIT licensed.

## 5. Defensive publication intent  
This document is published to establish prior art under 35 U.S.C. § 102(a)(1) and equivalent international statutes.

## 6. License  
MIT – see LICENSE file.