*simple inv for tran sim
vin 1 0 pulse 0 1.8 2ns 2ns 2ns 15ns 35ns
vcc 3 0 1.8
mn1 2 1 0 0 nmos w=2u l=1u
mp1 2 1 3 3 pmos w=4u l=1u
.tran 0.2ns 80ns
.dc vin 0 1.8 0.02
.print dc V(2)
.print tran v(1) v(2)
.END