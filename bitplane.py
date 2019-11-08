import numpy as np

def get_bit_plane(img, plane):
    assert 0 <= plane <= 7
    return ((img >> plane) & 1).astype('uint8')

def set_bit_plane(img, plane, plane_img):
    assert 0 <= plane <= 7
    return ((img & ~(1 << plane)) | (np.where(plane_img > 0, 1, 0) << plane)).astype('uint8')