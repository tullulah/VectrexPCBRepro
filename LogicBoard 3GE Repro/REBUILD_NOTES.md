# LogicBoard 3GE Repro — rebuild notes

Clean rebuild off the original Vectrex Rev R6E reference schematic
(`original/Vectrex-Schematic/LogicBoard 3GE`). First repro (`LogicBoard 3GE/`)
built but did not boot. This version ports only deliberate, correctly-wired
substitutions.

## Memory map (decoded from the original 74LS00 + 74LS32 glue)

| Range | Device | Select condition |
|-------|--------|------------------|
| `0x0000–0x7FFF` | Cartridge | `CARTS` = E & !A15 |
| `0xC800–0xCFFF` | RAM (1KB, mirrors) | `RAMS` = A11 & E & A15 & A14 & !A13 |
| `0xD000–0xD7FF` | 6522 VIA (mirrors) | `IOS` = A15 & A14 & !A13 → 6522 /CS2 (pin 23) |
| `0xE000–0xFFFF` | BIOS ROM (8KB) | `ROMS` = A15 & A14 ; `ROMOE` = E & A13 |

Note: A12 is NOT used by the glue (incomplete decode → RAM and VIA mirror within
0xC000–0xDFFF). This is original Vectrex behavior — keep it.

## Substitution 1 — Address glue → single GAL/ATF16V8

Replaces IC202 (74LS00) + IC203 (74LS32). Active-low outputs.
CUPL/WinCUPL form (ready to compile):

```
/* Inputs:  A11 A13 A14 A15 E RnW  (RnW: high=read, low=write) */
/* Outputs (active low except RAM_nWE) */

nROMS   = !(A15 & A14);          /* ROM  /CE   -> 27C512 pin 20 */
nROMOE  = !(E & A13);            /* ROM  /OE   -> 27C512 pin 22 */
nCARTS  = !(E & !A15);           /* cart select -> J201.32       */
nIOS    = !(A15 & A14) # A13;    /* I/O select -> 6522 /CS2 pin23 */
nRAMS   = !(A11 & E) # nIOS;     /* RAM  /CE   -> CY62256 /CE     */
RAM_nWE = RnW # nRAMS;           /* RAM  /WE (gated write)       */
```

6 inputs / 6 outputs → fits an ATF16V8 easily (room left for software banking later).

## Substitution 2 — ROM → 27C512 (PLCC-32 socket) with bank select

8KB BIOS in a 64KB EPROM. DIP-28 pin refs (PLCC-32 differs — map on the symbol):

- A0–A12 → CPU A0–A12 (same as original ROM)
- /CE (pin 20) = `nROMS` ; /OE (pin 22) = `nROMOE` ; Vcc (28)=+5V ; GND (14)=GND
- **A13 (pin 26), A14 (pin 27), A15 (pin 1) → bank-select jumper/DIP-switch** (each to GND or +5V)
- 8 banks × 8KB. Bank 0 (all jumpers GND) = stock BIOS at file offset 0x0000.
  Burn a patched no-logo "fast-boot" BIOS in bank 1 (A13=high), etc.

## Substitution 3 — RAM → single CY62256 (SOP-28 SMD)

Replaces IC204 + IC205 (2× 2114). The 2114 has no /OE.

- A0–A9 → CPU A0–A9 ; A10–A14 → GND
- D0–D7 → data bus (merge the two old nibbles: 2114#1 = D0–3, 2114#2 = D4–7)
- /CE = `nRAMS` ; /WE = `RAM_nWE` ; **/OE = GND**

## Substitution 4 — Sound → YM2149F (40-pin DIP)

Replaces AY-3-8912 (28-pin, scarce). YM2149 = standard AY clone.

- I/O port A = the `SW0–SW7` controller-button read lines (was AY pins 7–14)
- I/O port B = unused (leave NC / tie per datasheet)
- Data bus DA0–7, BC1, BC2, BDIR, /RESET, clock (E), analog A/B/C as original
- Clone/test compatibility: AY-3-8912 pin 2 (TEST1) was the "ground for clones"
  pin — ground the YM2149 equivalent.

## Deferred to v2
Dedicated per-axis X/Y DACs (wobble fix). First board keeps the original analog
vector generator: 1× MC1408 (fed by 6522 port A = P0–7) + CD4052B mux +
sample-hold (Q301/302 2N3905, Q303 2N3904) + LF347/LF353 + 4066.

## Unchanged from original
CPU 68A09, VIA 6522, MC1408, CD4052B, LF347, LF353, 4066, transistors, diodes,
passives.

---

# CAPTURE SPEC (pin-by-pin) — ready for KiCad GUI

## Symbols to use (NO authoring needed — all exist)
| Part | Symbol (library) | Source |
|------|------------------|--------|
| YM2149F sound | `Audio:YM2149` | KiCad stock |
| GAL decode | `Logic_Programmable:ATF16V8Bxx-xxPU` | KiCad stock |
| ROM 27C512 | `Memory_EPROM:27C512PLCC` | reuse from old `LogicBoard 3GE/` |
| RAM CY62256 | `Memory_RAM:CY62256-70PC` | reuse from old `LogicBoard 3GE/` |

The GAL logic is fully designed + simulation-verified in `gal/` (`vectrex_decode.pld`
+ `verify_decode.py` → "ALL CANONICAL CHECKS PASS"). Compile the .pld (WinCUPL /
Quartus / Atmel-ATMISP) to a JEDEC, burn the ATF16V8.

## ATF16V8 pin assignment (matches the .pld)
```
 1  (unused in)       11  (unused in)
 2  A11               12  nROMS    -> 27C512 /CE  (pin 20)
 3  A13               13  nROMOE   -> 27C512 /OE  (pin 22)
 4  A14               14  nCARTS   -> cart J201.32
 5  A15               15  nIOS     -> 6522 /CS2   (pin 23)
 6  E  (6809 E clk)   16  nRAMS    -> CY62256 /CE
 7  RnW               17  RAM_nWE  -> CY62256 /WE
 8  (unused in)       18  nE       -> cart J201.12 (inverted E clock)
 9  (unused in)       19  (unused out)
10  GND               20  VCC
```
NOTE: 6522 CS1 (pin 24) = A12 — wire directly, NOT from the GAL.
NOTE: `~{E}` (inverted E) goes to the CARTRIDGE (J201.12) — the original 74LS00
gate A generated it. It's now GAL output pin 18 (`nE = !E`), not an unused pin.

## YM2149 (40-pin) ← AY-3-8912 net map  (connect each net to this YM2149 pin)
| Net | YM2149 pin | | Net | YM2149 pin |
|-----|-----------|-|-----|-----------|
| GND | 1 (VSS)   | | E (clock)  | 22 |
| CHA | 3 (A)     | | /RESET     | 23 |
| CHB | 4 (B)     | | BC1        | 29 |
| CHC | 38 (C)    | | BC2        | 28 |
| SW0 | 21 (IOA0) | | BDIR       | 27 |
| SW1 | 20        | | P0 (DA0)   | 37 |
| SW2 | 19        | | P1         | 36 |
| SW3 | 18        | | P2         | 35 |
| SW4 | 17        | | P3         | 34 |
| SW5 | 16        | | P4         | 33 |
| SW6 | 15        | | P5         | 32 |
| SW7 | 14 (IOA7) | | P6         | 31 |
| +5V | 40 (VCC)  | | P7 (DA7)   | 30 |

Tie-offs / clone + addressing:
- **TEST1 (pin 39) → GND** (the AY-3-8912 "ground-for-clones" pin, now on the YM2149).
- **A8 (pin 25) → +5V, A9 (pin 24) → GND** — single-PSG select. VERIFY: if the PSG
  never responds, check this first.
- **SEL (pin 26)** → start at +5V for AY-3-8910-compatible pitch at the same clock;
  if audio is an octave off, move to GND. Bench-tune (not a boot blocker).
- **IOB0–7 (pins 6–13) unused** → leave NC (Vectrex 8912 had no port B). Pins 2, 5 = NC.

## 27C512 (PLCC-32) — bank-select wiring
- A0–A12 → CPU A0–A12 ; D0–D7 → data bus
- /CE = `nROMS` ; /OE = `nROMOE` ; Vcc/GND as symbol
- **A13, A14, A15 → 3-way jumper/DIP-switch (each GND or +5V) = bank select.**
  Bank 0 (all GND) = stock BIOS at file offset 0x0000. Burn a no-logo fast-boot
  BIOS in bank 1 (A13=high) etc.

## CY62256 (SOP-28) — wiring
- A0–A9 → CPU A0–A9 ; A10–A14 → GND ; D0–D7 → data bus
- /CE = `nRAMS` ; /WE = `RAM_nWE` ; **/OE = GND**

## INTENTIONAL cross-connections — KEEP (these are NOT errors)
Verified in the original; ERC will warn (multiple_net_names / net_not_bus_member)
but do NOT "fix" them:
- **FIRQ (6809 pin 4) = SW3** — controller button SW3 drives the fast interrupt.
- **CA1 (6522 pin 40) = SW7** — button SW7 also drives the VIA CA1 edge input.
- **6522 CS1 (pin 24) = A12** — separates RAM (0xC800) from VIA (0xD000).
- Power-rail aliases (`+5V`/`+5V_CART`, `GND`/`GNDA`, `-12VA`/`VEE`, `-5VA`/`-5V`)
  are intentional single-point joins.

---

# SMD miniaturization (size pass) + CPU clock

## SMD packages
| Part | Package | Note |
|------|---------|------|
| CPU `HD63C09E` | PLCC-44 | **E variant = external clock** (see below). Emulation mode. |
| VIA `W65C22S` | PLCC-44 | In production. Drop-in for the 6522. CS1=A12, CS2=nIOS. |
| Sound `YM2149` | DIP-40 | Stays through-hole (no SMD AY/YM). |
| Decode `ATF16V8` | SOIC-20 | Decode ONLY (keep it a single-purpose chip — easy to fault-isolate). |
| Clock `74HC74` | SOIC-14 | E/Q generator (below). |

## Substitution 5 — CPU `HD63C09E` + external E/Q clock
The non-E 6809 made its own clock from a crystal; the **E variant has no oscillator
and takes E + Q as INPUTS**. So add a clock chain (verified in `clock/verify_eq.py`):

**6 MHz source** — a **6 MHz SMD oscillator can** (cleanest), or a 74HC04 gate +
the 6 MHz crystal. (The bare crystal Y201 alone can't drive the '74 — needs an
oscillator.)

**74HC74 as a 2-bit Johnson counter → ÷4 quadrature E/Q** (6 MHz ÷ 4 = 1.5 MHz =
stock Vectrex speed):
```
VCC=pin14(+5V)  GND=pin7
6 MHz  -> CLK1 (pin 3) and CLK2 (pin 11)
D1 (pin 2)  = /Q2 (pin 8)        \  Johnson feedback
D2 (pin 12) =  Q1 (pin 5)        /
/PRE1(4) /CLR1(1) /PRE2(10) /CLR2(13) -> all +5V  (inactive)
Q1 (pin 5) = Q  -> CPU Q input
Q2 (pin 9) = E  -> CPU E input + 6522 pin25 + YM2149 clock + ATF16V8 pin6 (E)
```
Result: Q and E are 1.5 MHz, 50% duty, **Q leads E by 90°** (the 6809E requirement).
E is the system bus clock (fans out to VIA, PSG, decode); Q goes only to the CPU.

⚠️ The E-variant CPU pinout differs from the non-E: no XTAL/EXTAL; E/Q are inputs;
handle TSC and the status pins (LIC/AVMA/BUSY/BS/BA) per the HD63C09E datasheet when
placing the PLCC-44 symbol.
