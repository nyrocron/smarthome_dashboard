def pressure_at_sealevel(pressure, altitude):
    return pressure / (1 - (altitude / 44330)) ** 5.255
