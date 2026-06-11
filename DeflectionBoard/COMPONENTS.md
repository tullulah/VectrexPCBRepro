# Deflection Board — Components by group

Reference-designator scheme: **Power = 1xx · Channel X = 2xx · Channel Y = 3xx**.
`BOM_preliminary.csv` is the flat single-source-of-truth; this file is the readable
grouped view and shows **which sheet each group lives on**.

---

## Sheet: POWER (1xx)

### A — Input 7.5 V
| Ref | Value | Function |
|---|---|---|
| J101 | 7.5V_IN | power input connector |
| D101 | SS34 | reverse-polarity protection |
| C101 | 100µF/25V | input bulk |
| C102 | 10µF/25V | input decoupling |

### B — Boost 7.5 V → 18 V (VIN)
| Ref | Value | Function |
|---|---|---|
| U101 | TPS55340 | boost IC |
| L101 | 6.8µH ≥5A | boost inductor |
| D102 | SS54 | boost rectifier |
| R101 | 137k | FB top (→18V) |
| R102 | 10k | FB bottom |
| R103 | 10k | COMP R (per datasheet) |
| C103 | 2.2nF | COMP C (per datasheet) |
| C104 | 10nF | soft-start (per datasheet) |
| C105, C106 | 22µF/25V | boost input |
| C107, C108 | 22µF/25V | boost output |
| C109 | 0.1µF | boost output HF |

### C — Buck 5 V
| Ref | Value | Function |
|---|---|---|
| U102 | AP63205 | buck IC (from +7V5) |
| L102 | 4.7µH | buck inductor |
| R104 | 53.6k | FB top (→5V) |
| R105 | 10k | FB bottom |
| C110 | 10µF | buck input |
| C111 | 22µF | buck output |

### D — 2.5 V reference (Vmid)
| Ref | Value | Function |
|---|---|---|
| U103 | REF3325 | 2.5V reference |
| C112 | 0.1µF | decoupling |
| C113 | 1µF | decoupling |

---

## Sheet: DEFLECTION_CHANNEL — X = 2xx · Y = 3xx (same parts)

### E — Power stage (H-bridge)
| Ref | Value | Function |
|---|---|---|
| U201 | CSD97394Q4M | leg A |
| U202 | CSD97394Q4M | leg B |
| R201 | **PARAMETRIC** (~0.1Ω 2512) | R_sense (shunt) |
| C201, C202 | 0.1µF | BOOT leg A / B |
| C203, C205 | 1µF | VDD leg A / B |
| C204, C206 | 0.1µF | VDD HF leg A / B |
| C207 | 22µF/25V | VIN local bulk |
| C208, C209 | 0.1µF | VIN local A / B |

### F — Current sense
| Ref | Value | Function |
|---|---|---|
| U203 | INA240A1 | current sense (REF=Vmid) |
| C210 | 0.1µF | decoupling |

### G — Input scale (X_AXIS → Vset)
| Ref | Value | Function |
|---|---|---|
| U204 | OPA2196 | buffer (unit A; unit B spare) |
| C211 | 0.1µF | decoupling |
| R202 | 25k | Rin1 (from X_AXIS) |
| R203 | 20k | Rin2 (from +5V, offset) |
| R204 | 100k | Rf (to GND) |
| RV201 | 10k | gain trim (optional) |
| RV202 | 10k | offset/centering trim (optional) |

### H — Comparator + hysteresis
| Ref | Value | Function |
|---|---|---|
| U205 | TLV3501 | comparator |
| C212 | 0.1µF | decoupling |
| R205 | 1k | Rin (Vset → comparator +) |
| R206 | **PARAMETRIC** (~100k) | Rhys (hysteresis) |

### I — Logic (enable + /Q)
| Ref | Value | Function |
|---|---|---|
| U206 | 74LVC1G04 | inverter (/Q) |
| U207 | 74LVC1G08 | AND: PWM_A = Q & EN |
| U208 | 74LVC1G08 | AND: PWM_B = /Q & EN |
| C213 | 0.1µF | decoupling |

### J — Yoke
| Ref | Value | Function |
|---|---|---|
| J201 | Conn_01x02 | yoke X coil |

---

## Power symbols & signals (no reference designator)
- **Power symbols** (auto-connect by name across all sheets):
  `+7V5`, `+18V` (=VIN), `+5V`, `+2V5` (=VMID), `GND`, plus `PWR_FLAG` on each generated rail.
- **Signal:** `EN` (global label) — from the spot killer; tie to `+5V` for bench bring-up.

## Not on these sheets yet
- **Interface / spot-killer activity detector** → its own sheet (4xx), TBD.
- **Z_AXIS** passes straight through to the HV board (not used here).
