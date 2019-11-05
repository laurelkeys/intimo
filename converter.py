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
    return np.stack((view['x'], view['y']), axis=-1)

def int8_to_int16(v_int8):
    view_x, view_y = np.split(v_int8, 2, axis=-1)
    return (view_y.reshape(-1).astype('int16') << 8) + view_x.reshape(-1).astype('int16')

if __name__ == "__main__":
    # FIXME
    a = np.array([MIN_INT16, MIN_INT16+1, 
                  -3, -2, -1, 0, 1, 2, 3, 
                  MAX_INT16-1, MAX_INT16], dtype='int16')
    print(a)
    b = int16_to_int8(a)
    print(b)
    c = int8_to_int16(b)
    print(c)
    print()
    print((a == c))
    print((a == c).all())

# ref.: https://stackoverflow.com/questions/25298592/converting-32-bit-integer-into-array-of-four-8-bit-integers-in-python