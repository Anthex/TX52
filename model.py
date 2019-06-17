import math

CONST_N_SADOWSKI = 10.0
CONST_C_SADOWSKI = 10.0
CONST_CELERITY = 3E8

def Sadowski_RSSI_FROM_D(d, n=CONST_N_SADOWSKI, c=CONST_C_SADOWSKI):
    return -10.0 * n * math.log10(d) + c

def Sadowski_D_FROM_RSSI(rssi, n=CONST_N_SADOWSKI, c=CONST_C_SADOWSKI):
    return pow(10, ((c-rssi)/(10*n)))

def FriisLike(rssi, Pe=20, i=3.5, f=868E6, Ge=3.0, Gr=3.0): #dBm, dBm, ø, Hz, dBi, dBi, dBm
    λ = CONST_CELERITY / f
    return λ / (4.0 * 3.141592 * pow(10, (rssi-Pe-Ge-Gr)/(10*i)))