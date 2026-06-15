#!/usr/bin/env python3
"""Verify the 74HC74 2-bit Johnson counter generates 6809E E/Q clocks:
both = clk/4, ~50% duty, Q leading E by 90 degrees (one clk period).

Wiring modelled:
  FF1: D1 = /Q2  -> output Q1 = Q
  FF2: D2 =  Q1  -> output Q2 = E
  both FFs clocked on the same 6MHz rising edge; PRE/CLR inactive.
"""
q1 = q2 = 0          # power-on state (00)
Q, E = [], []
for _ in range(12):                  # 12 source clocks = 3 full E/Q cycles
    Q.append(q1); E.append(q2)
    nq1 = 0 if q2 else 1             # D1 = /Q2
    nq2 = q1                         # D2 =  Q1
    q1, q2 = nq1, nq2

def edges(sig):                      # indices where 0->1
    return [i for i in range(1, len(sig)) if sig[i] and not sig[i-1]]

print("clk : " + "".join("|" for _ in Q))
print("Q   : " + "".join("#" if v else "." for v in Q) + "   (-> CPU Q)")
print("E   : " + "".join("#" if v else "." for v in E) + "   (-> CPU E, VIA, PSG, GAL)")

per_Q = edges(Q)[1]-edges(Q)[0]
per_E = edges(E)[1]-edges(E)[0]
lead  = edges(E)[0]-edges(Q)[0]      # how many clks E rises after Q
dutyQ = sum(Q[:per_Q])/per_Q
print(f"\nQ period = {per_Q} src-clks (=clk/4)   duty = {dutyQ:.0%}")
print(f"E period = {per_E} src-clks (=clk/4)")
print(f"Q leads E by {lead} src-clk = {lead/per_Q*360:.0f} deg")

ok = (per_Q==4 and per_E==4 and lead==1 and dutyQ==0.5)
print("\nRESULT:", "E/Q OK — clk/4, 50% duty, Q leads E 90deg" if ok else "*** FAIL ***")
