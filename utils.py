import numpy as np


def azel_to_cartesian(
    azimuth, elevation, r=1.0, degrees=True, az_from="x", clockwise=False
):
    """
    Convert azimuth/elevation to Cartesian coordinates (x, y, z).

    Conventions:
      - elevation: angle from the XY-plane toward +Z (horizon=0, zenith=+90°)
      - r: radius (distance)
      - azimuth reference and direction are configurable:

        az_from="x" (or "east"):
          az=0 along +X (East). If clockwise=False, az increases CCW toward +Y (North).
          If clockwise=True, az increases CW toward -Y.

        az_from="north" (or "y"):
          az=0 along +Y (North). If clockwise=True (navigation), az increases toward +X (East).
          If clockwise=False, az increases CCW toward -X (West).

    Args:
        azimuth: scalar or array-like
        elevation: scalar or array-like
        r: scalar or array-like radius
        degrees: if True, interpret az/el in degrees; else radians
        az_from: "x"/"east" or "y"/"north"
        clockwise: True for clockwise azimuth increase, False for counterclockwise

    Returns:
        ndarray[..., 3] with components [x, y, z]
    """
    az = np.asarray(azimuth, dtype=float)
    el = np.asarray(elevation, dtype=float)
    rad = np.asarray(r, dtype=float)

    if degrees:
        az = np.deg2rad(az)
        el = np.deg2rad(el)

    # Map to base convention: az measured from +X, increasing CCW
    ref = str(az_from).lower()
    if ref in ("x", "+x", "east", "e"):
        base_az = -az if clockwise else az
    elif ref in ("y", "+y", "north", "n"):
        # From +Z (North/forward) to +X (East/right) is -90° (CW) or +90° (CCW) shift.
        base_az = (np.pi / 2 - az) if clockwise else (az + np.pi / 2)
    else:
        raise ValueError("az_from must be 'x'/'east' or 'y'/'north'")

    cos_el = np.cos(el)
    x = rad * cos_el * np.cos(base_az)  # +right / -left
    y = rad * np.sin(el)  # +up / -down
    z = rad * cos_el * np.sin(base_az)  # +forward / -behind

    # Round outputs to 3 decimal places
    x = np.round(x, 3)
    y = np.round(y, 3)
    z = np.round(z, 3)

    return np.stack((x, y, z), axis=-1)
