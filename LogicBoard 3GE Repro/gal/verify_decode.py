#!/usr/bin/env python3
"""Verify the Vectrex address-decode GAL equations against the canonical
Rev R6E memory map. Models vectrex_decode.pld exactly and sweeps the full
64KB space, reporting selected device per region and flagging any overlaps."""

def decode(addr, E=1, RnW=1):
    A11 = (addr >> 11) & 1
    A12 = (addr >> 12) & 1
    A13 = (addr >> 13) & 1
    A14 = (addr >> 14) & 1
    A15 = (addr >> 15) & 1
    # active-low GAL outputs (0 = asserted) — mirrors the .pld equations
    nROMS   = 0 if (A15 and A14) else 1
    nROMOE  = 0 if (E and A13) else 1
    nCARTS  = 0 if (E and not A15) else 1
    nIOS    = 0 if ((A15 and A14) and not A13) else 1
    nRAMS   = 0 if (A11 and E and A15 and A14 and not A13) else 1
    # device selected (chip-level, includes external A12 on the 6522 CS1)
    rom  = (nROMS == 0 and nROMOE == 0)
    cart = (nCARTS == 0)
    via  = (A12 == 1 and nIOS == 0)
    ram  = (nRAMS == 0)
    sel = [n for n, v in (("CART", cart), ("RAM", ram), ("VIA", via), ("ROM", rom)) if v]
    return sel

def regions(E=1):
    out, start, prev = [], 0, None
    for a in range(0x10000):
        s = tuple(decode(a, E=E))
        if s != prev:
            if prev is not None:
                out.append((start, a - 1, prev))
            start, prev = a, s
    out.append((start, 0xFFFF, prev))
    return out

print("=== Decoded regions (E=1, read) ===")
overlaps = []
for lo, hi, sel in regions():
    tag = ",".join(sel) if sel else "(none/open bus)"
    flag = "  <-- OVERLAP" if len(sel) > 1 else ""
    if len(sel) > 1:
        overlaps.append((lo, hi, sel))
    print(f"  0x{lo:04X}-0x{hi:04X}  {tag}{flag}")

print("\n=== Assertions vs canonical Vectrex map ===")
checks = [
    (0x0000, ["CART"]), (0x7FFF, ["CART"]),
    (0x8000, []),                       # open between cart and IO
    (0xC800, ["RAM"]),  (0xCFFF, ["RAM"]),
    (0xD000, ["VIA"]),  (0xD7FF, ["VIA"]),
    (0xE000, ["ROM"]),  (0xFFFF, ["ROM"]),
]
ok = True
for addr, want in checks:
    got = decode(addr)
    status = "OK " if got == want else "FAIL"
    if got != want:
        ok = False
    print(f"  [{status}] 0x{addr:04X}: got {got or '[]'} want {want or '[]'}")

print("\n=== Latent overlaps (expected: 0xD800-0xDFFF RAM+VIA mirror) ===")
for lo, hi, sel in overlaps:
    print(f"  0x{lo:04X}-0x{hi:04X}: {','.join(sel)}")

print("\nRESULT:", "ALL CANONICAL CHECKS PASS" if ok else "*** CHECK FAILED ***")
