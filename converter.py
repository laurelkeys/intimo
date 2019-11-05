import numpy as np

MIN_INT8, MAX_INT8 = -128, 127
MIN_UINT8, MAX_UINT8 = 0, 255
MIN_INT16, MAX_INT16 = -32768, 32767
MIN_UINT16, MAX_UINT16 = 0, 65535

def int8_to_uint8(v_int8):
    v_int8 = v_int8.astype('int16')
    v_int8 -= MIN_INT8 # [-128, 127] -> [0, 255]
    return v_int8.astype('uint8')

def uint8_to_int8(v_uint8):
    v_uint8 = v_uint8.astype('int16')
    v_uint8 += MIN_INT8 # [0, 255] -> [-128, 127]
    return v_uint8.astype('int8')

def int16_to_int8(v_int16):
    # subdivide int16 into 2 int8's, called x and y (0 and 1 are the offsets in bytes)
    dt = np.dtype((np.int16, { 'x': (np.int8, 0), 'y': (np.int8, 1) }))
    view = v_int16.view(dtype=dt)
    v_int8 = np.empty((view['y'].size + view['x'].size,), dtype='int8')
    v_int8[0::2] = view['y']
    v_int8[1::2] = view['x']
    return v_int8

def int8_to_int16(v_int8):
    view_y = v_int8[0::2].astype('int16')
    view_x = v_int8[1::2].astype('int16')
    v_int16 = (view_y << 8) | (view_x & ((1 << 8) - 1))
    return v_int16

if __name__ == "__main__":
    a = np.array([x for x in range(MIN_INT16, MAX_INT16)], dtype='int16')
    print(a.dtype, a.shape, a)
    print(np.array([bin(x) for x in a]))
    b = int16_to_int8(a)
    print(b.dtype, b.shape, b)
    print(np.array([bin(x) for x in b]))
    c = int8_to_int16(b)
    print(c.dtype, c.shape, c)
    print(np.array([bin(x) for x in c]))
    print()
    print((a == c))
    print((a == c).all())

# ref.: https://stackoverflow.com/questions/25298592/converting-32-bit-integer-into-array-of-four-8-bit-integers-in-python