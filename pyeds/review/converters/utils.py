#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
from . icons import *

# define enums
ICON_INFO = "info"
ICON_WARNING = "warning"
ICON_ERROR = "error"
ICON_STOP = "stop"

ICONS = {
    ICON_INFO: ICON_INFO_SVG,
    ICON_WARNING: ICON_WARNING_SVG,
    ICON_ERROR: ICON_ERROR_SVG,
    ICON_STOP: ICON_STOP_SVG}


def interpolate_color(color_a_rgba, color_b_rgba, pos):
    """Interpolates color between specified colors."""
    
    # interpolate channels
    r = int(color_a_rgba[0] + pos * (color_b_rgba[0] - color_a_rgba[0]))
    g = int(color_a_rgba[1] + pos * (color_b_rgba[1] - color_a_rgba[1]))
    b = int(color_a_rgba[2] + pos * (color_b_rgba[2] - color_a_rgba[2]))
    a = int(color_a_rgba[3] + pos * (color_b_rgba[3] - color_a_rgba[3]))
    
    # check channels
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    a = max(0, min(255, a))
    
    return r, g, b, a


def rgba_to_hex(r, g, b, a=255):
    """Converts color to hex format."""
    
    return "#%02x%02x%02x%02x" % (r, g, b, a)


def make_icon(icon, label=None, width=None):
    """Creates SVG for warning icon with optional label."""
    
    # get icon
    icon = ICONS[icon]
    
    # get label tag
    label_tag = LABEL_TAG % label if label else ""
    
    # get width
    if width is None:
        width = len(label) * 10 if label else 16
    
    return icon % (max(width, 16), label_tag)
