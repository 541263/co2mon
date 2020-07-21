#!/usr/bin/env python3

import hid
import time
import struct

def decode_co(data):
    data[0], data[2] = data[2], data[0]
    data[1], data[4] = data[4], data[1]
    data[3], data[7] = data[7], data[3]
    data[5], data[6] = data[6], data[5]
    
    result = bytearray(8)

    result[7] = ((data[6] << 5) & 0xFF) | ((data[7] >> 3) & 0xFF)
    result[6] = ((data[5] << 5) & 0xFF) | ((data[6] >> 3) & 0xFF)
    result[5] = ((data[4] << 5) & 0xFF) | ((data[5] >> 3) & 0xFF)
    result[4] = ((data[3] << 5) & 0xFF) | ((data[4] >> 3) & 0xFF)
    result[3] = ((data[2] << 5) & 0xFF) | ((data[3] >> 3) & 0xFF)
    result[2] = ((data[1] << 5) & 0xFF) | ((data[2] >> 3) & 0xFF)
    result[1] = ((data[0] << 5) & 0xFF) | ((data[1] >> 3) & 0xFF)
    result[0] = ((data[7] << 5) & 0xFF) | ((data[0] >> 3) & 0xFF)
    
    magic_word = b'Htemp99e'

    for i in range(8):
        r = ((magic_word[i] << 4) & 0xFF) | ((magic_word[i] >> 4) & 0xFF)
        if result[i] < r:
            result[i] = 0xFF - r + result[i]
        else:
            result[i] = result[i] - r
    
    #if result[0]+result[1]+result[2] != result[3]:
    #    return 0

    res = (result[1] << 8) + result[2]

    if result[0] == 0x42:
        print("T={0}".format(res * 0.0625 - 273.15))
        return 1
    elif result[0] == 0x50:
        print("CO={0}".format(res))
        return 2
    return 0
    
try:
    h = hid.device()
    h.open(0x04d9, 0xa052)

    h.set_nonblocking(1)

    #h.write(b'8\x00\x00\x00\x00\x00\x00\x00\x00')
    h.send_feature_report([0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
    time.sleep(0.05)

    co = 1
    t = 1
    while co | t:
        d = h.read(8)
        if d:
            n = decode_co(d)
            if n == 1:
                t = 0
            elif n == 2:
                co = 0

    h.close()

except IOError as ex:
    print(ex)
