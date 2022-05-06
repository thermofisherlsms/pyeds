#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
from .converter import register, ImageValueConverter


@register("MassSpectrumItem")
class SpectrumImageConverter(ImageValueConverter):
    """Converts mass spectrum trace into SVG image."""
    
    IMAGE_FORMAT = 'svg'
    
    
    def Convert(self, item, width=800, height=200, zoom=None, title=None, **kwargs):
        """
        Converts mass spectrum into SVG image. Requires matplotlib package.
        
        Args:
            item: pyeds.EntityItem
                Item to convert
            
            width: int
                Image width.
            
            height: int
                Image height.
            
            zoom: (float, float) or None
                X-axis range.
            
            title: str
                Trace title.
        
        Returns:
            image: str or None
                SVG image data.
        """
        
        # check modules
        try:
            from . import plotting
        except ImportError:
            return None
        
        # get scan
        scan = item.Spectrum
        if scan is None:
            return None
        
        # get data
        xy = [[(c.MZ, 0.), (c.MZ, c.Intensity)] for c in scan.Centroids]
        labels = [(c.MZ, c.Intensity, "%.4f" % c.MZ) for c in scan.Centroids]
        
        # apply zoom
        if zoom is not None:
            idx1, idx2 = plotting.crop(xy, zoom[0], zoom[1], lambda d: d[0][0])
            xy = xy[idx1:idx2]
            labels = labels[idx1:idx2]
        
        # get title
        if title is None:
            title = str(scan)
        
        # init plot
        plot = plotting.prepare(
            x_label = "m/z",
            y_label = "a.i.",
            width = width,
            height = height)
        
        # plot data
        plotting.lines(plot, xy, label=title, linewidth=1, color="#1f77b4")
        plotting.zoom(plot, x_range=zoom)
        plotting.margins(plot)
        plotting.labels(plot, labels)
        plotting.legend(plot, bool(title), fontsize=8)
        
        # make SVG image
        return plotting.svg(plot)
