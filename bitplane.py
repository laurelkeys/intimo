import numpy as np

def get_bit_plane(img, plane):
    return ((img >> plane) & 1).astype('uint8')

def set_bit_plane(img, plane, plane_img):
    return ((img & ~(1 << plane)) | (np.where(plane_img > 0, 1, 0) << plane)).astype('uint8')

def set_bit_plane_partial(img, plane, plane_img, changed_bits):
    __plane_img = plane_img
    __plane_img.ravel()[changed_bits:] = get_bit_plane(img, plane).ravel()[changed_bits:]
    return set_bit_plane(img, plane, __plane_img)