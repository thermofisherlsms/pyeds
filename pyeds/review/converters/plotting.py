#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
from io import StringIO
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from matplotlib.collections import LineCollection


def prepare(x_label="", y_label="", width=800, height=200, dpi=72):
    """
    Initializes a matplotlib plot.
    
    Args:
        x_label: str
            X-axis label.
        
        y_label: str
            Y-axis label.
        
        width: int
            Image width.
        
        height: int
            Image height.
        
        dpi: int
            Image DPI.
    
    Returns:
        matplotlib.pyplot
            Plot with basic initialization applied.
    """
    
    # init figure
    fig = plt.figure()
    fig.set_dpi(dpi)
    fig.set_size_inches(width/dpi, height/dpi)
    fig.set_tight_layout(True)
    
    # init axes
    plt.xlabel(x_label, fontsize=9, fontweight='bold')
    plt.ylabel(y_label, fontsize=9, fontweight='bold')
    
    plt.gca().xaxis.set_minor_locator(AutoMinorLocator())
    plt.gca().yaxis.set_minor_locator(AutoMinorLocator())
    plt.gca().yaxis.get_offset_text().set_fontsize(8)
    plt.gca().tick_params(axis='both', labelsize=8)
    
    plt.gca().set_axisbelow(True)
    plt.autoscale(True)
    
    # init gridlines
    plt.grid(axis='both', which='major', linewidth=1, color="#e6e6e6ff")
    plt.grid(axis='both', which='minor', linewidth=1, color="#f5f5f5ff")
    
    # set margins
    plt.margins(0)
    
    return plt


def plot(plot, x, y, **kwargs):
    """
    Adds series to plot. By default this is displayed as continuous line.
    Refer to matplotlib.pyplot.plot() help for more info. X and y coordinates
    are expected to be in user's data units.
    
    Args:
        plot: matplotlib.pyplot
            Plot to which series should be added.
        
        x: (float,)
            Collection of x-coordinates in user units.
        
        y: (float,)
            Collection of y-coordinates in user units.
        
        title: str
            Series legend.
    """
    
    # add series
    return plot.plot(x, y, **kwargs)


def fill(plot, x, y, **kwargs):
    """
    Adds series to plot. By default this is displayed as filled polygon area.
    Refer to matplotlib.pyplot.fill() help for more info. X and y coordinates
    are expected to be in user's data units.
    
    Args:
        plot: matplotlib.pyplot
            Plot to which series should be added.
        
        x: (float,)
            Collection of x-coordinates in user units.
        
        y: (float,)
            Collection of y-coordinates in user units.
        
        title: str
            Series legend.
    """
    
    # add series
    return plot.fill(x, y, **kwargs)


def lines(plot, lines, **kwargs):
    """
    Adds individual lines (e.g. centroids) to plot.
    Refer to matplotlib.collections.LineCollection help for more info.
    
    Args:
        plot: matplotlib.pyplot
            Plot to which series should be added.
        
        lines: (((float, float), (float, float)),)
            Collection of lines to add as ((x0, y0), (x1, y1)) each. X and y
            coordinates are expected to be in user's data units.
        
        title: str
            Series legend.
    """
    
    # add series
    ax = plot.gca()
    ax.add_collection(LineCollection(lines, **kwargs))
    ax.autoscale()


def svg(plot, close=True):
    """
    Creates SVG code and closes plot.
    
    Args:
        plot: matplotlib.pyplot
            Plot from which the SVG should be made.
    
    Returns:
        str
            SVG code.
    """
    
    # make SVG
    svg_file = StringIO()
    plot.savefig(svg_file, format='svg')
    svg = svg_file.getvalue()
    svg_file.close()
    
    # close plot
    if close:
        plot.close()
    
    return svg


def labels(plot, labels, size=7, offset=3, spacing=3, overlap=False):
    """
    Adds labels to plot.
    
    Args:
        plot: matplotlib.pyplot
            Plot to which labels should be added.
        
        labels: ((float, float, str),)
            Collection of labels to add as (x, y, label) each. X and y
            coordinates are expected to be in user units.
        
        size: int
            Font size.
        
        offset: int
            Y-offset of the label string from given coordinates.
        
        spacing: int
            Required minimum spacing around each label.
        
        overlap: bool
            If set to false, some labels will be hidden to avoid overlaps.
    """
    
    # check labels
    if not labels:
        return
    
    # get objects
    ax = plot.gca()
    fig = plot.gcf()
    dpi = fig.get_dpi()
    
    # get renderer
    try:
        rndr = fig.canvas.get_renderer()
    except AttributeError:
        rndr = fig.canvas.renderer
    
    # add labels
    occ = []
    for x, y, label in sorted(labels, key=lambda d: d[1], reverse=True):
        
        # apply y-offset
        if offset:
            x, y = ax.transData.transform((x, y))
            x, y = ax.transData.inverted().transform((x, y+offset))
        
        # add text
        text = plot.text(x, y, label, ha='center', size=size)
        
        # get bbox
        bbox = text.get_window_extent(rndr, dpi)
        bbox = (bbox.x0-spacing, bbox.y0-spacing, bbox.x1+spacing, bbox.y1+spacing)
        
        # check overlap
        if overlap is False and any(overlaps(bbox, b) for b in occ):
            text.set_visible(False)
            continue
        
        # remember used space
        occ.append(bbox)


def zoom(plot, x_range=None, y_range=None):
    """
    Applies axes ranges.
    
    Args:
        plot: matplotlib.pyplot
            Plot to which zoom should be applied.
        
        x_range: (float, float) or None
            X-axis range.
        
        y_range: (float, float) or None
            Y-axis range.
    """
    
    if x_range is not None:
        plot.xlim(x_range)
    
    if y_range is not None:
        plot.ylim(y_range)


def margins(plot, margins=(20, 20, 5, 20)):
    """
    Applies given margins as (top, left, bottom, right).
    
    Args:
        plot: matplotlib.pyplot
            Plot to which margins should be added.
        
        margins: (float, float, float, float) or None
            Margins to be applied as (top, right, bottom, left).
    """
    
    # get axes
    ax = plot.gca()
    
    # get current ranges
    xmin, xmax = plot.xlim()
    ymin, ymax = plot.ylim()
    
    # convert to display units
    xmin, ymin = ax.transData.transform((xmin, ymin))
    xmax, ymax = ax.transData.transform((xmax, ymax))
    
    # add margins
    if margins[0]:
        ymax += margins[0]
    if margins[1]:
        xmin -= margins[1]
    if margins[2]:
        ymin -= margins[2]
    if margins[3]:
        xmax += margins[3]
    
    # convert back into real units
    xmin, ymin = ax.transData.inverted().transform((xmin, ymin))
    xmax, ymax = ax.transData.inverted().transform((xmax, ymax))
    
    # set new limits
    plot.xlim((xmin, xmax))
    plot.ylim((ymin, ymax))


def legend(plot, show=True, **kwargs):
    """
    Enables or disables plot legend. Refer to matplotlib.pyplot.legend() help
    for more info.
    
    Args:
        plot: matplotlib.pyplot
            Plot to which margins should be added.
        
        show: bool
            Specifies whether legend should be shown.
    """
    
    # disable legend
    if not show:
        
        legend = plot.gca().get_legend()
        if legend:
            legend.remove()
        
        return
    
    # show legend
    plot.legend(**kwargs)


def overlaps(box1, box2):
    """
    Checks whether two boxes have any overlap.
    
    Args:
        box1: (float, float, float, float)
            Box coordinates as (x0, y0, x1, y1).
        
        box2: (float, float, float, float)
            Box coordinates as (x0, y0, x1, y1).
    
    Returns:
        bool
            True if there is any overlap between given boxes.
    """
    
    if not ((box1[0] <= box2[0] <= box1[2])
        or (box1[0] <= box2[2] <= box1[2])
        or (box2[0] <= box1[0] and box2[2] >= box1[2])):
        return False
    
    if not ((box1[1] <= box2[1] <= box1[3])
        or (box1[1] <= box2[3] <= box1[3])
        or (box2[1] <= box1[1] and box2[3] >= box1[3])):
        return False
    
    return True


def bisect(sequence, value, key=None, side='left'):
    """
    Uses binary search to find index where if given value inserted, the order
    of items is preserved. The collection of items is assumed to be sorted in
    ascending order.
    
    Args:
        sequence: list or tuple
            Collection of items ordered by searched value.
        
        value: int or float
            Value to be searched.
        
        key: callable or None
            Function to be used to get specific value from item.
        
        side: str
            If 'left' is used, index of the first suitable location is
            returned. If 'right' is used, the last such index is returned.
    
    Returns:
        int
            Index of the exact or next higher item.
    """
    
    has_key = key is not None
    lo = 0
    hi = len(sequence)
    
    if side == 'left':
        while lo < hi:
            mid = (lo + hi) // 2
            if value <= (key(sequence[mid]) if has_key else sequence[mid]):
                hi = mid
            else:
                lo = mid + 1
    
    elif side == 'right':
        while lo < hi:
            mid = (lo + hi) // 2
            if value < (key(sequence[mid]) if has_key else sequence[mid]):
                hi = mid
            else:
                lo = mid + 1
    
    else:
        message = "Unknown side specified! -> '%s'" % side
        raise ValueError(message)
    
    return lo


def crop(sequence, minimum, maximum, key=None, extend=False):
    """
    Calculates crop indices for given sequence and range. Optionally the range
    can be extended by adding additional adjacent points to each side. Such
    extension might be useful to display zoomed lines etc. Note that this method
    assumes that given sequence is sorted ascendantly.
    
    Args:
        sequence: list or tuple
            Collection of items ordered by searched value.
        
        minimum: float
            Crop range minimum.
        
        maximum: float
            Crop range maximum.
        
        key: callable or None
            Function to be used to get specific value from item.
        
        extend: bool
            If set to True additional adjacent point is added to each side.
    
    Returns:
        (int, int)
            Cropping indexes.
    """
    
    # get indices
    left_idx = bisect(sequence, minimum, key, 'left')
    right_idx = bisect(sequence, maximum, key, 'right')
    
    # extend range by adjacent values
    if extend and left_idx > 0:
        left_idx = bisect(sequence[:left_idx], sequence[left_idx-1], key, 'left')
    
    if extend and right_idx < len(sequence):
        right_idx += bisect(sequence[right_idx:], sequence[right_idx], key, 'right')
    
    return left_idx, right_idx
