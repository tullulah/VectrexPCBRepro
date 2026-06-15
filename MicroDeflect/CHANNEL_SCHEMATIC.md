# Deflection Channel — Component-level Schematic (one axis = Channel X, 2xx)

Self-oscillating **hysteretic current-mode** amplifier driving a **full H-bridge**
(U201/U202) into one yoke coil. Channel Y = identical in the 3xx range.
Refs match `COMPONENTS.md` / `BOM_preliminary.csv`.

Single **+5 V** analog/logic supply, signals centered on **Vmid = +2V5**.
Power rail **+18V (VIN ≈ 12–20 V)**, parametric from measured yoke L.
All grounds = star at the bridge PGND.

```
                          +5V                        +18V (VIN)
                           │                            │
 X_AXIS(±5V)─[R202/R203/R204]─► Vset ─[R205]─┬──(+)     │
   (0=center)  scale+offset → U204            │  U205   ── Q ──[U207 &EN]── PWM ─►┌─────┐
                                         R206 │ TLV3501 │            ┌[U206]/Q    │U201 │ VSW_A ─┐
                                              │         └── Q ───────┘   [U208&EN]─PWM─►│legA │        │
                        Vsense ──────────────(−)                                        └─────┘     [R201]
                           ▲                                                          ┌─────┐ shunt   │
                     U203 (INA240, REF=+2V5) ◄── senses I across R201 ── VSW_B ──────►│U202 │◄────────┘
                                                                                      │legB │  YOKE (J201)
   /Q ──[U208 &EN]── PWM_B ───────────────────────────────────────────────────────► └─────┘
```

## Operation (all signals vs AGND, Vmid = +2V5)
- `Vset  = 2.5 V + 0.4·X_AXIS` (R202/R203/R204 network) → demanded current.
- `Vsense = 2.5 V + Gi·R201·I_L` → actual coil current (U203 INA240, REF=+2V5).
- **U205**: `+in = Vset` (with hysteresis via R205/R206), `−in = Vsense`.
  - `Vset > Vsense` → **Q high** → U201=VIN, U202=PGND → **+VIN across coil** → I_L rises.
  - `Vsense > Vset + band` → **Q low** → **−VIN** → I_L falls.
  - Self-oscillates inside the hysteresis band = current bang-bang (inherently stable,
    no loop compensation). Static error ≤ band.

⚠️ Design checks: pick **U203 input polarity** so +VIN drive reads as *rising* Vsense;
pick **U205** polarity for negative feedback (as above).

## Connections

### G — Input scale (X_AXIS → Vset), single-supply friendly
3 resistors into **U204** (½ OPA2196, unity buffer) → `Vset = 0.4·X_AXIS + 2.5 V`
(±5 V → 0.5–4.5 V; never leaves 0–5 V):
| Ref | from → to | value |
|---|---|---|
| R202 | X_AXIS → node | 25 k |
| R203 | +5V → node (sets 2.5 V offset) | 20 k |
| R204 | node → GND | 100 k |

Node → U204(+); U204 out = Vset. Optional **RV201** gain trim (aspect), **RV202** offset
trim (centering). `Ks=0.4` nominal — adjust for full-screen.

### H — Comparator + hysteresis (U205 = TLV3501)
| Ref | from → to | value |
|---|---|---|
| R205 | Vset (U204 out) → U205(+) | 1 k |
| R206 | U205 out (Q) → U205(+) | **PARAM** 100 k |
| — | Vsense (U203 out) → U205(−) | — |

`band ≈ 5 V·R205/(R205+R206) ≈ 50 mV` → `ripple ΔI = band/(Gi·R201)`.
Trim R206 so `fsw ≈ VIN/(2·L·ΔI)` lands ~200 kHz–1 MHz.

### I — Logic (Q → bridge PWM, with enable)
- **U206** (74LVC1G04): in = Q → out = /Q.
- **U207** (74LVC1G08): PWM_A = Q & EN → U201 PWM pin.
- **U208** (74LVC1G08): PWM_B = /Q & EN → U202 PWM pin.
- `EN` low → both PWM low → both legs LS-on → coil brakes (safe state).

### E — Power stage: U201 (leg A) & U202 (leg B), CSD97394Q4M
Per leg (use TI's KiCad symbol for pin numbers):
- `VIN`  → **+18V** (local bulk C207 + ceramic C208/C209, tight loop to PGND)
- `PGND` → power ground (star)
- `VSW`  → bridge output: U201→SW_A, U202→SW_B. Coil between SW_A and SW_B, **R201**
  (shunt) in series on the SW_A side; U203 senses across R201.
- `VDD`  → **+5V** (C203/C205 = 1 µF, C204/C206 = 0.1 µF)
- `BOOT` → C201/C202 = 0.1 µF bootstrap to its own VSW
- `PWM`  → from U207 (leg A) / U208 (leg B)
- DISABLE/3-state pin (if any) → tie per datasheet; we gate via U207/U208 anyway.

### F — Current sense: U203 (INA240A1)
- Inputs across R201; `REF` pin → **+2V5** (bidirectional); out (Vsense) → U205(−).
- C210 = 0.1 µF decoupling.

### J — Yoke
- J201 (Conn_01x02): the X coil, between SW_A (via R201) and SW_B.

## Power (on the Power sheet, 1xx — see COMPONENTS.md)
Rails reach this channel by power-symbol name: **+18V** (U101 boost), **+5V** (U102
buck), **+2V5** (U103 REF3325), **GND**. `EN` arrives as a global label from the spot
killer (tie to +5V for bench bring-up).

## Parametric sizing (after yoke L & Rb measured, and I_pk known)
1. **R201**: `≈ 2 V / (Gi · I_pk)` (keeps Vsense in 0.5–4.5 V). Ex: I_pk=1 A, Gi=20 → 0.1 Ω.
2. **+18V / VIN** (full bridge → ±VIN, headroom 2·VIN):
   `2·VIN ≳ L·(di/dt)_max + I_pk·Rb`, `(di/dt)_max = ΔI_fullscreen / t_vector`.
   Raise VIN instead of rewinding.
3. **R206 (hysteresis)** → `ΔI = band/(Gi·R201)` (~5–10 % of I_pk); `fsw ≈ VIN/(2·L·ΔI)`.
4. **Input scale (R202–R204 / RV201)**: X_AXIS = +5 V → I_L = +I_pk (full screen);
   RV201 trims aspect, RV202 centers.

## Notes
- Pure hysteretic = simplest, stable. For tighter linearity later, insert a PI/integrator
  before U205 (→ self-oscillating sliding mode).
- Layout: VIN→legs→coil→PGND switching loop tiny; keep U203/U205 away from the switch
  node; high fsw so the coil filters ripple (no spot blur).
- `Z_AXIS` is NOT used here — route it straight through to the HV board cathode driver.
