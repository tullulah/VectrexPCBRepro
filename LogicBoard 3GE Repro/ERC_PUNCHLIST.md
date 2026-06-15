# ERC punch-list — LogicBoard 3GE Repro

Baseline ERC on the freshly-copied original = **290 violations**. Almost all are
benign / expected for a schematic-only project. Triage below.

## IGNORE (benign / expected)
| Count | Type | Why |
|------:|------|-----|
| 176 | `lib_symbol_mismatch` | Embedded symbols differ from the linked lib. Clears when symbols are re-linked / updated from library during capture. |
| 67  | `footprint_link_issues` | No footprint lib configured yet. Resolved in Phase 2 (footprint assignment). |
| 34  | `lib_symbol_issues` | Minor issues in the custom "Vectrex LogicBoard" symbols (pin-type quirks). Cosmetic. |

## KEEP — intentional, do NOT "fix"
| Count | Type | What |
|------:|------|------|
| 5 | `multiple_net_names` | Power-rail aliases (+5V/+5V_CART, GND/GNDA, -12VA/VEE, -5VA/-5V) **and** the deliberate FIRQ=SW3 / CA1=SW7 joins. All correct per the original. |
| 2 | `net_not_bus_member` | FIRQ / CA1 touching the SW[0..7] bus — same intentional joins as above. |

## FIX during capture (real, minor)
| Count | Type | Action |
|------:|------|--------|
| 3 | `power_pin_not_driven` | e.g. IC201 pin 14 GND "not driven". Add a `PWR_FLAG` on GNDD/+5V rails (or it resolves once the new ROM/RAM/decode symbols bring proper power pins). |
| 1 | `duplicate_pins` | IC201 (old ROM symbol) pin 26 NC on two nets. **Disappears** when IC201 is swapped to `Memory_EPROM:27C512PLCC`. |
| 1 | `label_multiple_wires` | Tidy the offending label/wire junction. |
| 1 | `unconnected_wire_endpoint` | Tidy one dangling wire end. |

## Target after capture
0 unconnected, 0 real errors. Remaining acceptable: lib/footprint mismatches until
Phase 2, and the KEEP-list warnings (which can be silenced with ERC exclusions).

## Re-run ERC with:
```
kicad-cli sch erc --output erc.rpt "LogicBoard 3GE Repro.kicad_sch"
```
