import numpy as np

def get_bit_plane(img, plane):
    ''' Returns the `plane`-th bit plane from `img`

        obs.: The output is a ndarray with the same shape as `img`\n
        obs.: Values are either 0 or 1, use `np.where(output > 0, 255, 0)` to replace 1's with 255's '''
    return ((img >> plane) & 1).astype('uint8')

def set_bit_plane(img, plane, plane_img):
    ''' Replaces the `plane`-th bit plane from `img` with `plane_img`

        obs.: `plane_img` is a ndarray with the same shape as `img`\n
        obs.: Values of `plane_img` are expected to be either 0 or 1 '''
    return ((img & ~(1 << plane)) | (np.where(plane_img > 0, 1, 0) << plane)).astype('uint8')

def set_bit_plane_partial(img, plane, plane_img, changed_bits):
    ''' Replaces only the first `changed_bits` values from the `plane`-th bit plane of `img` with `plane_img` '''
    __plane_img = plane_img
    __plane_img.ravel()[changed_bits:] = get_bit_plane(img, plane).ravel()[changed_bits:]
    return set_bit_plane(img, plane, __plane_img)
