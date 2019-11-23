import numpy as np

def encode(bgr_img, bit_plane, message_uint8, debug=False):
    height, width, depth = bgr_img.shape
    max_bytes = height * width * depth // 8
    max_bits = max_bytes * 8 # we can only store whole byte words

    message_bits = np.unpackbits(message_uint8)
    if message_bits.size > max_bits:
        print(f"message_bits.size > max_bits ({message_bits.size})")
        message_bits = message_bits[:max_bits]
    
    r_message = message_bits[0::3]; r_length = r_message.size
    g_message = message_bits[1::3]; g_length = g_message.size
    b_message = message_bits[2::3]; b_length = b_message.size
    
    # NOTE OpenCV uses BGR order
    r = bgr_img[..., 2].ravel()
    g = bgr_img[..., 1].ravel()
    b = bgr_img[..., 0].ravel()

    # hide message in bit_plane
    mask = 1 << bit_plane
    r[:r_length] = (r[:r_length] & ~mask) | (r_message << bit_plane)
    g[:g_length] = (g[:g_length] & ~mask) | (g_message << bit_plane)
    b[:b_length] = (b[:b_length] & ~mask) | (b_message << bit_plane)
    
    if debug:
        print(f"bit_plane={bit_plane}")
        print(f"max_bytes={max_bytes}")
        print(f"max_bits={max_bits}")
        print(f"message_bits.size={message_bits.size}")
        print(f"(r, g, b)_length=({r_length}, {g_length}, {b_length})")
        print(f"bgr_img.shape={bgr_img.shape} | message_uint8.shape={message_uint8.shape}")
        print(f"bgr_img.size={bgr_img.size}   | message_uint8.size={message_uint8.size}")
        print(f"bgr_img.dtype={bgr_img.dtype} | message_uint8.dtype={message_uint8.dtype}")

    return np.dstack((b.reshape((height, width)), 
                      g.reshape((height, width)), 
                      r.reshape((height, width))))
    
def decode(bgr_img, bit_plane):
    mask = 1 << bit_plane
    __img = (bgr_img & mask) >> bit_plane

    # NOTE OpenCV uses BGR order
    b_message = __img[..., 0].ravel()
    g_message = __img[..., 1].ravel()
    r_message = __img[..., 2].ravel()
    
    # retrieve message from bit_plane
    message_bits = np.dstack((r_message, g_message, b_message)).ravel()
    max_bits = message_bits.size
    while max_bits % 8 != 0:
        max_bits -= 1 # we can only store whole byte words
    
    message_uint8 = np.packbits(message_bits[:max_bits])
    return message_uint8
