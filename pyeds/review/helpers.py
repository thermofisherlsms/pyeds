#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import re
import math

# init constants
FORMAT_FLOAT_F = re.compile("^F(\d+)$")
FORMAT_FLOAT_E = re.compile("^0\.(0+)e-0$")
FORMAT_FLOAT_D = re.compile("^0\.(0+)$")
FORMAT_FLOAT_H = re.compile("^0\.(#+)$")


def rgba_from_argb_int(color):
    """
    Converts ARGB int into RGBAr tuple, where RGB are 0-255 and A is 0-1.
    
    Returns:
        (int, int, int, int)
            Red, green, blue and alpha channels.
    """
    
    a = (color >> 24) & 0xFF
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    
    return r, g, b, a / 255.


def argb_int_from_rgba(r, g, b, a):
    """
    Converts RGBA values, where RGBA are 0-255 into ARGB int.
    
    Returns:
        int
            ARGB int.
    """
    
    a = a << 24
    r = r << 16
    g = g << 8
    b = b
    
    return r | g | b | a - 4294967296


def trans_color(color, alpha):
    """
    Makes solid color semi-transparent.
    
    Returns:
        (int, int, int, int)
            Red, green, blue and alpha channels.
    """
    
    if color[3] != 1.:
        return color
    
    return color[0], color[1], color[2], alpha


def format_float(value, formatting):
    """
    Formats float into string according to specified formatting.
    
    Returns:
        str or None
            Formatted number.
    """
    
    # check value
    if isinstance(value, str):
        return value
    
    if value is None:
        return None
    
    # no formatting
    if not formatting:
        return str(value)
    
    # like 0
    if formatting == "0":
        return "{:.0f}".format(value)
    
    # like 0.00
    match = FORMAT_FLOAT_D.match(formatting)
    if match:
        return "{:.{}f}".format(value, len(match.group(1)))
    
    # like F2
    match = FORMAT_FLOAT_F.match(formatting)
    if match:
        return "{:.{}f}".format(value, match.group(1))
    
    # like 0.00e-0
    match = FORMAT_FLOAT_E.match(formatting)
    if match:
        return "{:.{}e}".format(value, len(match.group(1)))
    
    # like 0.##
    match = FORMAT_FLOAT_H.match(formatting)
    if match:
        for i in range(len(match.group(1))):
            if not value % math.pow(1, -i):
                return "{:.{}f}".format(value, i)
        return "{:.{}f}".format(value, len(match.group(1)))
    
    return str(value)
