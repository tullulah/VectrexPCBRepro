# Deflection Board — Wiring guide (from → to, with pin numbers)

Format: `Ref.PIN(name)`. Pin numbers taken from the symbols you actually placed.
Rails (`+7.5V`,`+15V`,`+5V`,`+2V5`,`GND`) are **power symbols** → connect by name.
Put a `PWR_FLAG` on every rail (`+7.5V`,`+15V`,`+5V`,`+2V5`,`GND`).

## Pinouts (reference)
```
TPS55340  U101 : 1,2=SW  3=VIN  4=EN  5=SS  6=SYNC  7=AGND  8=COMP  9=FB  10=FREQ  11=NC  12,13,14=PGND  15=EPAD
AP63205   U102 : 1=FB  2=EN  3=IN  4=GND  5=SW  6=BST
REF3325   U103 : 1=IN  2=OUT  3=GND
diode     D    : 1=K(cathode)  2=A(anode)
CSD97394  U201/U202 : 1=SKIP#  2=VDD  3=PGND  4=VSW  5=VIN  6=BOOT_R  7=BOOT  8=PWM  9=PAD
INA240A1  U203 : 1=IN-  2=GND  3=REF2  4=GND  5=OUT  6=VS  7=REF1  8=IN+
OPA2196   U204 : 1=OUTA  2=-INA  3=+INA  4=V-  5=+INB  6=-INB  7=OUTB  8=V+
TLV3501   U205 : 1=NC  2=IN-  3=IN+  4=V-  5=NC  6=OUT  7=V+  8=SHDN
74LVC1G04 U206 : 2=A(in)  4=Y(out)  3=GND  5=VCC   (1=NC)
74LVC1G08 U207/U208 : 1=A  2=B  4=Y(out)  3=GND  5=VCC
```

---

## SHEET: POWER

### A — Input
```
J101.1 → D101.2(A)
D101.1(K) → +7.5V            (+7.5V symbol + PWR_FLAG)
J101.2 → GND
C101.1,C102.1 → +7.5V        C101.2,C102.2 → GND
```

### B — Boost U101 (TPS55340) → +15V
```
U101.3(VIN) → +7.5V
U101.4(EN)  → +7.5V                 (or 100k pull-up)
+7.5V → L101.1
L101.2 → U101.1(SW) , U101.2(SW) , D102.2(A)     ← BOTH SW pins to the switch node
D102.1(K) → +15V                    (+15V symbol + PWR_FLAG)
C105.1,C106.1 → +7.5V   C105.2,C106.2 → GND      (input caps)
C107.1,C108.1,C109.1 → +15V   .2 → GND           (output caps)
R101.1 → +15V   R101.2 → U101.9(FB)              (FB top)
R102.1 → U101.9(FB)   R102.2 → GND               (FB bottom)
U101.8(COMP) → R103.1 ; R103.2 → C103.1 ; C103.2 → GND
U101.5(SS) → C104.1 ; C104.2 → GND
U101.10(FREQ) → R106.1 ; R106.2 → GND            ← ADD R106 = 78.7k (RT, fsw~600kHz)
U101.6(SYNC) → GND                               (or no-connect flag)
U101.7(AGND), 12,13,14(PGND), 15(EPAD) → GND
```

### C — Buck U102 (AP63205) → +5V
```
U102.3(IN) → +7.5V
U102.2(EN) → +7.5V
U102.6(BST) → C114.1 ; C114.2 → U102.5(SW)       (bootstrap)
U102.5(SW) → L102.1 ; L102.2 → +5V               (+5V symbol + PWR_FLAG)
C110.1 → +7.5V  C110.2 → GND                     (input cap)
C111.1 → +5V    C111.2 → GND                     (output cap)
R104.1 → +5V    R104.2 → U102.1(FB)              (FB top)
R105.1 → U102.1(FB)  R105.2 → GND                (FB bottom)
U102.4(GND) → GND
```

### D — Reference U103 (REF3325) → +2V5
```
U103.1(IN) → +5V
U103.3(GND) → GND
U103.2(OUT) → +2V5                  (+2V5 symbol + PWR_FLAG)  ← unify name with channel!
C112.1 → +5V   C112.2 → GND         (input decoupling)
C113.1 → +2V5  C113.2 → GND         (output cap)
```

---

## SHEET: DEFLECTION_CHANNEL  (X; Y identical in 3xx)

Input `AXIS_IN` = hierarchical label (root maps it to X_AXIS / Y_AXIS).
`EN` = global label. Rails by power symbol.

### G — Input scale → Vset  (U204 OPA2196, unit A)
```
-- gain/aspect: RV201 (3-pin trimpot) as a rheostat in series with R202 --
AXIS_IN → RV201.1 ; RV201.2(wiper) → R202.1 ; R202.2 → N1 ; RV201.3 → RV201.2(wiper)
-- coarse center (fixed): R203 from +5V sets nominal 2.5 V --
+5V → R203.1 ; R203.2 → N1
-- fine center trim: RV202 (3-pin trimpot) divider, wiper injected via R207 --
RV202.1 → +5V ; RV202.3 → GND ; RV202.2(wiper) → R207.1 ; R207.2 → N1
-- bottom leg --
R204.1 → N1 ; R204.2 → GND
N1 → U204.3(+INA)
U204.2(-INA) → U204.1(OUTA)         (unity buffer)
U204.1(OUTA) → Vset
U204.8(V+) → +5V ; U204.4(V-) → GND
C211.1 → +5V ; C211.2 → GND
```
*(N1 = junction of R202.2/R203.2/R207.2/R204.1/U204.3 — a wire node, label optional.)*
*(R203 = coarse center; RV202+R207(100k) = fine ± center trim (gentle, barely touches gain);
RV201 = gain/aspect. Tie RV201's unused end (3) to the wiper so it can't float.)*

### F — Current sense  (U203 INA240A1, R201 shunt)
```
U201.4(VSW) → R201.1 ; R201.2 → J201.1     (shunt in coil path, SW_A side)
U203.8(IN+) → R201.1 ; U203.1(IN-) → R201.2
U203.7(REF1) → +2V5 ; U203.3(REF2) → +2V5
U203.6(VS) → +5V ; U203.2(GND),4(GND) → GND
U203.5(OUT) → Vsense
C210.1 → +5V ; C210.2 → GND
```

### H — Comparator + hysteresis  (U205 TLV3501)
```
Vset → R205.1 ; R205.2 → N2
U205.6(OUT,Q) → R206.1 ; R206.2 → N2        (hysteresis)
N2 → U205.3(IN+)
Vsense → U205.2(IN-)
U205.6(OUT) → Q
U205.7(V+) → +5V ; U205.4(V-) → GND
U205.8(SHDN) → +5V                          (enable)
C212.1 → +5V ; C212.2 → GND
```

### I — Logic  (U206 inv, U207/U208 AND)
```
U206.2(A) → Q ; U206.4(Y) → /Q
U207.1(A) → Q ;  U207.2(B) → EN ;  U207.4(Y) → PWM_A
U208.1(A) → /Q ; U208.2(B) → EN ;  U208.4(Y) → PWM_B
U206.5,U207.5,U208.5 (VCC) → +5V ;  .3(GND) → GND
C213.1 → +5V ; C213.2 → GND
R208(10k) : +5V → EN  (pull-up, NOT a direct tie)   ; EN → U207.2, U208.2
  EN is high by default (enabled); spot killer pulls it low on fault. Keeps +5V rail separate.
```

### E — Power stage  (U201 leg A, U202 leg B = CSD97394Q4M)
```
-- leg A (U201) --
U201.5(VIN) → +15V ;  U201.3(PGND) → GND ;  U201.9(PAD) → GND
U201.2(VDD) → +5V ;   C203.1→+5V C203.2→GND ;  C204.1→+5V C204.2→GND
U201.1(SKIP#) → +5V                         ← forced-PWM (synchronous both ways)
U201.7(BOOT) → C201.1 ; C201.2 → U201.4(VSW)   ; U201.6(BOOT_R) → U201.7(BOOT)
U201.8(PWM) → PWM_A
U201.4(VSW) → R201.1            (= SW_A → shunt → coil)

-- leg B (U202) --
U202.5(VIN) → +15V ;  U202.3(PGND) → GND ;  U202.9(PAD) → GND
U202.2(VDD) → +5V ;   C205.1→+5V C205.2→GND ;  C206.1→+5V C206.2→GND
U202.1(SKIP#) → +5V
U202.7(BOOT) → C202.1 ; C202.2 → U202.4(VSW)   ; U202.6(BOOT_R) → U202.7(BOOT)
U202.8(PWM) → PWM_B
U202.4(VSW) → J201.2            (= SW_B → other coil terminal)

C207.1→+15V C207.2→GND  (VIN bulk) ; C208,C209 .1→+15V .2→GND (VIN local A/B)
```

### J — Yoke  (J201)
```
J201.1 → R201.2     (coil terminal 1, SW_A side via shunt)
J201.2 → U202.4(VSW)   (coil terminal 2, SW_B)
```

---

## Root sheet (top)
- Input connector (mate to LogicBoard **J301**): `X_AXIS, Y_AXIS, Z_AXIS, GND`.
  `X_AXIS` → ChannelX sheet-pin `AXIS_IN` ; `Y_AXIS` → ChannelY `AXIS_IN`.
  `Z_AXIS` → through to HV board (unused here).
- Rails reach both channels by power-symbol name; `EN` global label to both.

## New parts to add (not in original placement)
- **R106** = 78.7k RT resistor, U101.10(FREQ)→GND (fsw≈600kHz; RFREQ[kΩ]=57500·fsw[kHz]^-1.03).
- **C114** = buck bootstrap (already added).
- **R207** = 100k offset-injection resistor (RV202 wiper → N1).
- **RV201/RV202** → change to 3-pin `Device:R_Potentiometer_Trim` (10k). Pins: 1,3 = ends, 2 = wiper.

## Checks
- `+2V5` (channel) vs `+2.5V` (power): **must be the same name** or Vmid won't cross.
- U203 IN+/IN−: +VIN drive must make Vsense rise (else swap).
- U205: +in=Vset, −in=Vsense (negative feedback).
- CSD97394 `SKIP#` HIGH = forced PWM → the low-side sinks current, needed to apply −VIN.
- Run **ERC** after wiring.
