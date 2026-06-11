# Vectrex Micro — Deflection Board — Design Notes

Part of the **Vectrex Micro** project (3.5" B&W magnetic CRT). Modular design:
this board does **deflection (X/Y) only** and is meant to be **generic / parametric**
(re-trimmed, not redesigned, for a different yoke). A separate **HV / tube board**
handles flyback HV, focus, screen, heater, cathode/Z drive and the spot-killer
grid-cutoff output.

## 1. Signal & power interface (from LogicBoard 3GE)

Source = `LogicBoard 3GE` connector **J301 "Video"** (Molex KK-254, 1x04):

| Signal | Meaning | Range | Used by |
|---|---|---|---|
| `X_AXIS` | X deflection setpoint (integrator out) | ≈ ±5 V (≈±4 V usable), 0 V = center | this board |
| `Y_AXIS` | Y deflection setpoint | ≈ ±5 V, 0 V = center | this board |
| `Z_AXIS` | intensity / blanking | ~0..+5 V (TBD) | **passes through to HV board** |
| `GND` | analog ground | — | both |

Levels inferred from the LogicBoard analog rails (±5 V: nets +5V / -5V / -5VA →
integrator outputs are rail-bounded). **TODO: confirm exact J301 pin order and the
real X/Y/Z swing by measurement.**

## 2. Architecture decision

**Switching (Class-D) current-mode deflection driver — NOT linear.** Inspired by
Jeroen Domburg (Sprite_tm) using a TI **CSD97394Q4M** power stage. The yoke coil is
the inductor of a switching converter; a **closed current loop** forces coil current
(= beam position) to track X/Y. Avoids rewinding the yoke (di/dt forced with full
VIN pulses at ~90% efficiency) and the current loop linearizes geometry vs L/Rb.

Chosen (2026-06): **self-oscillating hysteretic current loop + full H-bridge
(2× CSD97394Q4M per axis).**
- Hysteretic: simplest, fastest bring-up, fits the analog X/Y. Trade-off: variable
  fsw → watch EMI near the CRT (keep effective fsw high so PWM ripple doesn't fatten
  the spot).
- Full bridge: ±VIN across the coil → 2× slew, headroom for an as-yet-unmeasured
  (possibly high-L vertical) yoke. Can be populated as half-bridge initially.

## 3. Per-channel topology (X and Y identical)

```
X_AXIS ─► [buffer / scale + offset] ─► Vset
                                        │
              (Vset − Vsense) ─► [integrator] ─► [comparator + hysteresis] ─► Q
                                                                               │
                       Q ──► PWM leg A (CSD97394 #1)                           │
                      /Q ──► PWM leg B (CSD97394 #2)  ◄── [inverter] ◄─────────┘
                       │
     SW_A ─► [shunt R_sense] ─► YOKE coil ─► SW_B
                       │
                 [INA240] ─► Vsense   (closes the loop)
```

- Q high → +VIN across coil (current ramps up); Q low → −VIN (ramps down).
  Hysteresis sets ripple & fsw; the integrator removes static error → good linearity.
- Each CSD97394Q4M takes **1 PWM + enable**; leg A = Q, leg B = /Q. Shared **enable**
  = "deflection OK" line (driven by the spot-killer / fault logic).
- INA240 senses coil current bidirectionally (good PWM common-mode rejection).

## 4. Committed (yoke-independent) vs Parametric

**Committed now:** CSD97394Q4M power stages, INA240 current sense, input buffer/
integrator op-amps, hysteretic comparator + inverter, VIN boost, 5 V rail (driver
VDD + logic), connectors.

**Parametric — fill after measuring the yoke (L & Rb of each coil):**
- `R_sense` (shunt) value
- `VIN` exact (≈12–20 V)
- loop compensation R/C + hysteresis band
- output scaling (full-screen current)
- half- vs full-bridge population

## 5. Spot killer (split across boards)

- **Deflection-activity detector lives HERE:** differentiate + rectify `Vsense_X`
  and `Vsense_Y`, sum → "movement present" signal out via J_SK.
- **Grid (G1) cutoff output + "HV present" sense live on the HV board.** If activity
  disappears (or HV not ready), the HV board blanks the beam. Also gates the bridge
  `enable`.

## 6. Power

- Input: 7.5 V (donor TV adapter, 850 mA) — **likely needs a bigger supply** once
  total deflection power is known.
- Boost **7.5 V → ~18 V** (VIN for the H-bridges).
- **5 V** rail: CSD97394Q4M driver bias (VDD) + op-amps/comparator/logic.
- INA240 reference at mid-rail for bidirectional sensing.

## 7. KiCad structure (suggested)

- New project **"DeflectionBoard"** (separate from LogicBoard — modular).
- Hierarchical sheet **"Deflection_Channel"** instantiated 2× (X, Y).
- Sheet **"Power"** (boost + 5 V).
- Sheet **"Interface"** (activity detector + connectors).
- Place committed parts; leave parametric values as `TBD` with comments.

## 8. Open TODOs

- [ ] Measure yoke L & Rb (H and V) → set R_sense, VIN, bridge population, loop comp.
- [ ] Confirm J301 pin order + real X/Y/Z levels.
- [ ] Pick specific boost IC + inductor after power budget.
- [ ] CSD97394Q4M details: VDD bias, bootstrap cap, PWM input logic threshold, enable/3-state.
- [ ] Decide J_SK pinout (activity, enable/fault, GND, …) jointly with the HV board.
