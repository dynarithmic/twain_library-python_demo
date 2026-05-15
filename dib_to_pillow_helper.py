import ctypes as ct
from PIL import Image

kernel32 = ct.windll.kernel32
kernel32.GlobalLock.argtypes = [ct.c_void_p]
kernel32.GlobalLock.restype = ct.c_void_p
kernel32.GlobalUnlock.argtypes = [ct.c_void_p]
kernel32.GlobalUnlock.restype = ct.c_bool
kernel32.GlobalSize.argtypes = [ct.c_void_p]
kernel32.GlobalSize.restype = ct.c_size_t


class BITMAPINFOHEADER(ct.Structure):
    _fields_ = [
        ("biSize", ct.c_uint32),
        ("biWidth", ct.c_int32),
        ("biHeight", ct.c_int32),
        ("biPlanes", ct.c_uint16),
        ("biBitCount", ct.c_uint16),
        ("biCompression", ct.c_uint32),
        ("biSizeImage", ct.c_uint32),
        ("biXPelsPerMeter", ct.c_int32),
        ("biYPelsPerMeter", ct.c_int32),
        ("biClrUsed", ct.c_uint32),
        ("biClrImportant", ct.c_uint32),
    ]


def dib_handle_to_pil_image(hdib):
    ptr = kernel32.GlobalLock(hdib)
    if not ptr:
        raise RuntimeError("GlobalLock failed")

    try:
        size = kernel32.GlobalSize(hdib)
        dib_bytes = ct.string_at(ptr, size)

    finally:
        kernel32.GlobalUnlock(hdib)

    bih = BITMAPINFOHEADER.from_buffer_copy(dib_bytes)

    width = bih.biWidth
    height = abs(bih.biHeight)
    bpp = bih.biBitCount

    top_down = bih.biHeight < 0
    orientation = 1 if top_down else -1

    row_stride = ((width * bpp + 31) // 32) * 4

    palette_entries = 0
    if bpp <= 8:
        palette_entries = bih.biClrUsed if bih.biClrUsed else (1 << bpp)

    pixel_offset = bih.biSize + palette_entries * 4
    pixel_data = dib_bytes[pixel_offset:]

    if bpp == 24:
        img = Image.frombytes(
            "RGB",
            (width, height),
            pixel_data,
            "raw",
            "BGR",
            row_stride,
            orientation
        )

    elif bpp == 32:
        img = Image.frombytes(
            "RGBA",
            (width, height),
            pixel_data,
            "raw",
            "BGRA",
            row_stride,
            orientation
        )

    elif bpp == 8:
        img = Image.frombytes(
            "P",
            (width, height),
            pixel_data,
            "raw",
            "P",
            row_stride,
            orientation
        )

        palette = []
        palette_offset = bih.biSize

        for i in range(palette_entries):
            b, g, r, _ = dib_bytes[palette_offset + i * 4: palette_offset + i * 4 + 4]
            palette.extend([r, g, b])

        img.putpalette(palette)

    elif bpp == 1:
        img = Image.frombytes(
            "1",
            (width, height),
            pixel_data,
            "raw",
            "1",
            row_stride,
            orientation
        )

    else:
        raise NotImplementedError(f"DIB bit depth not yet supported: {bpp}")

    return img
