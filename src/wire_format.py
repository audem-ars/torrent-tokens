"""
Torrent-Tokens wire format v1.0
MIT licensed. See ../LICENSE
"""
from dataclasses import dataclass
from hashlib import sha256
from struct import pack, unpack
from typing import Tuple

VERSION = 1

# ---------- helpers ----------
def c128(b: bytes) -> bytes:
    """128-bit checksum = first 16 bytes of SHA-256"""
    return sha256(b).digest()[:16]

def frame(msg_type: int, header: bytes, body: bytes) -> bytes:
    """TLV frame: version(1) + msg_type(1) + header_len(2) + body_len(4) + header + body"""
    return pack(">BBHI", VERSION, msg_type, len(header), len(body)) + header + body

def decode_frame(raw: bytes) -> Tuple[int, bytes, bytes]:
    """returns (msg_type, header, body)"""
    if len(raw) < 8:
        raise ValueError("short frame")
    ver, mt, hlen, blen = unpack(">BBHI", raw[:8])
    if ver != VERSION:
        raise ValueError("version mismatch")
    if len(raw) < 8 + hlen + blen:
        raise ValueError("incomplete frame")
    header = raw[8:8 + hlen]
    body = raw[8 + hlen:8 + hlen + blen]
    return mt, header, body

# ---------- message types ----------
@dataclass
class TileMeta:
    model_id: int
    tile_id: int
    tile_kind: int        # 0=weight,1=expert,2=kv_aux,3=codebook
    layer_idx: int
    expert_idx: int       # 0xFFFF if N/A
    tile_bytes: bytes     # the actual 4-bit packed tile

    def encode(self) -> bytes:
        body = self.tile_bytes
        h = pack(">QQIIH", self.model_id, self.tile_id, self.tile_kind,
                 self.layer_idx, self.expert_idx) + c128(body)
        return frame(0, h, body)

    @classmethod
    def decode(cls, header: bytes, body: bytes) -> "TileMeta":
        if len(header) != 34:
            raise ValueError("bad TileMeta header size")
        model_id, tile_id, tile_kind, layer_idx, expert_idx = unpack(">QQIIH", header[:30])
        return cls(model_id, tile_id, tile_kind, layer_idx, expert_idx, body)


@dataclass
class ActivationMsg:
    session_id: int
    step_id: int
    from_tile_id: int
    to_tile_id: int
    actv: bytes          # compressed activation blob

    def encode(self) -> bytes:
        body = self.actv
        h = pack(">QQQQ", self.session_id, self.step_id,
                 self.from_tile_id, self.to_tile_id) + c128(body)
        return frame(1, h, body)

    @classmethod
    def decode(cls, header: bytes, body: bytes) -> "ActivationMsg":
        if len(header) != 32:
            raise ValueError("bad ActivationMsg header size")
        session_id, step_id, from_tile_id, to_tile_id = unpack(">QQQQ", header[:32])
        return cls(session_id, step_id, from_tile_id, to_tile_id, body)


@dataclass
class ResultMsg:
    session_id: int
    step_id: int
    tile_id: int
    vote_group: int       # 0..2 for 2-of-3
    payload: bytes        # partial result tensor
    cycles_hint: int = 0  # optional perf hint

    def encode(self) -> bytes:
        body = self.payload
        h = pack(">QQQIB", self.session_id, self.step_id,
                 self.tile_id, self.cycles_hint, self.vote_group) + c128(body)
        return frame(2, h, body)

    @classmethod
    def decode(cls, header: bytes, body: bytes) -> "ResultMsg":
        if len(header) != 33:
            raise ValueError("bad ResultMsg header size")
        session_id, step_id, tile_id, cycles_hint, vote_group = unpack(">QQQIB", header[:33])
        return cls(session_id, step_id, tile_id, vote_group, body, cycles_hint)


# quick self-test
if __name__ == "__main__":
    t = TileMeta(1, 2, 0, 3, 0xFFFF, b"\x00" * 100)
    raw = t.encode()
    mt, h, b = decode_frame(raw)
    t2 = TileMeta.decode(h, b)
    assert t.tile_id == t2.tile_id
    print("wire_format.py self-test OK")