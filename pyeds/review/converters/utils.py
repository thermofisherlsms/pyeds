#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
from . icons import *


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


def rgba_to_hex(color_rgba):
    """Converts color to hex format."""
    
    return "#%02x%02x%02x%02x" % color_rgba


def make_warning_icon(label=None, width=None):
    """Creates SVG for warning icon with optional label."""
    
    # get label tag
    label_tag = LABEL_TAG % label if label else ""
    
    # get width
    if width is None:
        width = len(label) * 10 if label else 16
    
    return ICON_WARNING % (max(width, 16), label_tag)
