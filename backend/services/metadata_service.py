"""
FILE: backend/services/metadata_service.py
PURPOSE: SAFE photo-metadata viewer / cleaner for images the user voluntarily
uploads to their OWN local server. Processed in memory only - never saved,
never sent elsewhere. Shows only metadata that is explicitly present (no
inference) and can produce a metadata-free COPY.
"""
import io

from PIL import ExifTags, Image, ImageOps

ALLOWED = {"JPEG", "PNG", "WEBP", "TIFF"}
GPS_IFD = 0x8825


class ImageError(ValueError):
    pass


def _open(data: bytes):
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except Exception as exc:  # noqa: BLE001
        raise ImageError("File is not a readable image.") from exc
    if img.format not in ALLOWED:
        raise ImageError("Unsupported image type (use JPEG, PNG, WEBP or TIFF).")
    return img


def _deg(v):
    d, m, s = (float(x) for x in v)
    return d + m / 60 + s / 3600


def inspect_metadata(data: bytes) -> dict:
    img = _open(data)
    exif = img.getexif()
    fields = {}
    for tag, val in exif.items():
        if tag == GPS_IFD:
            continue
        name = ExifTags.TAGS.get(tag, f"Tag {tag}")
        if isinstance(val, bytes):
            val = f"<{len(val)} bytes>"
        fields[name] = str(val)[:120]
    gps = None
    gps_ifd = exif.get_ifd(GPS_IFD) if exif else {}
    if gps_ifd:
        try:
            lat = _deg(gps_ifd[2]) * (-1 if gps_ifd.get(1) == "S" else 1)
            lon = _deg(gps_ifd[4]) * (-1 if gps_ifd.get(3) == "W" else 1)
            gps = {"latitude": round(lat, 5), "longitude": round(lon, 5)}
        except Exception:  # noqa: BLE001
            gps = {"note": "GPS block present but unreadable"}
    other = {k: str(v)[:120] for k, v in img.info.items()
             if k not in ("exif", "icc_profile") and isinstance(v, (str, int, float))}
    lowered = {k.lower() for k in fields}
    flags = {
        "has_gps": gps is not None,
        "has_device": bool({"make", "model"} & lowered),
        "has_timestamp": bool({"datetime", "datetimeoriginal"} & lowered),
        "has_software": "software" in lowered,
    }
    return {"format": img.format, "size": list(img.size), "fields": fields, "gps": gps,
            "other": other, "flags": flags, "field_count": len(fields) + (1 if gps else 0)}


def strip_metadata(data: bytes):
    """Return (bytes, format) of a clean copy rebuilt from pixels only."""
    img = _open(data)
    fmt = img.format
    img = ImageOps.exif_transpose(img)  # keep visual orientation before dropping EXIF
    if fmt == "JPEG" and img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    clean = Image.new(img.mode, img.size)
    clean.paste(img)
    out = io.BytesIO()
    clean.save(out, format=fmt)
    return out.getvalue(), fmt
