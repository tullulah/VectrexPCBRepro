# Capture checklist — what to do in KiCad (Phase 1)

Everything below is fully specified in `REBUILD_NOTES.md`. This is the running
order. Open `LogicBoard 3GE Repro.kicad_sch`. Re-run ERC after each block:
`kicad-cli sch export netlist` / the ERC button.

Prep work already done (no GUI needed):
- ✅ Project base = clean copy of the original Rev R6E schematic.
- ✅ GAL logic designed + simulation-verified (`gal/vectrex_decode.pld`, `verify_decode.py`).
- ✅ All replacement symbols exist in stock KiCad libs (no authoring).
- ✅ Pin-by-pin maps, BOM, ERC triage written.

## Order of operations

1. **Annotate** (Tools → Annotate Schematic) to clear the inherited annotation
   errors before anything else.

2. **GAL decode** — delete IC202 (74LS00) + IC203 (74LS32). Place
   `Logic_Programmable:ATF16V8Bxx-xxPU`. Wire per the pin table in REBUILD_NOTES
   (in: A11,A13,A14,A15,E,RnW → pins 2-7 ; out: nROMS,nROMOE,nCARTS,nIOS,nRAMS,
   RAM_nWE → pins 12-17). Net names already exist on the old glue wires — just
   move the labels to the GAL pins.
   ⚠️ Wire **6522 CS1 (pin 24) = A12 directly** (not from GAL).

3. **ROM** — swap IC201 to `Memory_EPROM:27C512PLCC`. A0-A12 + D0-D7 + /CE=nROMS
   /OE=nROMOE as before. Route **A13/A14/A15 to a 3-way DIP-switch / jumpers**
   (bank select). Burn BIOS at bank 0 (offset 0x0000).

4. **RAM** — replace IC204+IC205 with one `Memory_RAM:CY62256-70PC`. A0-A9, D0-D7,
   /CE=nRAMS, /WE=RAM_nWE, **/OE=GND**, A10-A14=GND.

5. **Sound** — swap IC208 to `Audio:YM2149`. Re-map every net to the 40-pin layout
   per the YM2149 table. TEST1(39)=GND. A8(25)=+5V, A9(24)=GND. SEL(26)=+5V
   (bench-tune). IOB0-7 NC.

6. **ERC pass** — target 0 unconnected + 0 real errors. Keep the intentional
   warnings (FIRQ=SW3, CA1=SW7, rail aliases) — see ERC_PUNCHLIST.md.

7. **Phase 2** — assign footprints (reuse the SMD set from the old `LogicBoard 3GE/`
   where valid: CY62256 SOP-28, etc.; 27C512 = PLCC-32 socket; YM2149 = DIP-40 or
   socket; ATF16V8 = SOIC-20/DIP-20).

8. **Phase 3-5** — ERC clean → PCB layout → route → DRC clean → gerbers.

## Boot bring-up reminder (why the last board failed)
The #1 suspect was the 27C512 ROM mapping. With this build: A13/14/15 on jumpers,
BIOS burned at the matching bank → the CPU reads valid reset vectors at
0xFFFE/0xFFFF. If it still doesn't boot, scope the E clock, /RESET, and verify
nROMS/nROMOE assert in 0xE000-0xFFFF.
