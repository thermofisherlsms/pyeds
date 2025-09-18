#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
from .converter import register, ImageValueConverter
from .utils import make_icon, ICON_INFO

# define constants
RT_EPSILON = 0.00001


@register("XicTraceItem")
class TraceImageConverter(ImageValueConverter):
    """Converts chromatogram trace into SVG image."""
    
    IMAGE_FORMAT = 'svg'
    
    
    def Convert(self, item, width=800, height=200, zoom=None, title=None, peaks=None, **kwargs):
        """
        Converts trace item into SVG image. Requires matplotlib package.
        
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
            
            peaks: (pyeds.EntityItem,) or ((pyeds.EntityItem,),)
                Individual peaks or groups of peaks to be displayed together
                with the trace. Individual peaks are displayed as separate
                areas, grouped peaks are combined into single area. Each peak
                must be an EntityItem having a PeakModel property
                (e.g. ChromatogramPeakItem).
        
        Returns:
            image: str or None
                SVG image data.
        """
        
        # check modules
        try:
            from . import plotting
        except ImportError:
            return make_icon(ICON_INFO, "no matplotlib")
        
        # get trace
        trace = item.Trace
        if trace is None:
            return None
        
        # init plot
        plot = plotting.prepare(
            x_label = "rt [min]",
            y_label = "a.i.",
            width = width,
            height = height)
        
        # plot peaks
        self._plot_peaks(plotting, plot, trace, peaks)
        
        # plot trace data
        trace_x = [p.RT for p in trace]
        trace_y = [p.Intensity for p in trace]
        plotting.plot(plot, trace_x, trace_y, label=title, linewidth=1, color="#1f77b4")
        
        # autoscale Y
        y_range = None
        if zoom:
            idx1, idx2 = plotting.crop(trace_x, zoom[0], zoom[1])
            points = trace_y[idx1:idx2]
            if points:
                y_range = (min(0, min(points)), max(0, max(points)))
        
        # finalize plot
        plotting.zoom(plot, x_range=zoom, y_range=y_range)
        plotting.margins(plot)
        plotting.legend(plot, bool(title), fontsize=8, loc=1)
        
        # make SVG image
        return plotting.svg(plot)
    
    
    def _plot_peaks(self, plotting, plot, trace, peaks):
        """Plots peaks."""
        
        # check peaks
        if not peaks:
            return
        
        # plot groups
        for group in peaks:
            
            # plot combined peak
            if isinstance(group, (list, tuple)):
                self._plot_combined_peak(plotting, plot, trace, group)
            
            # plot single peak
            else:
                self._plot_single_peak(plotting, plot, trace, group)
    
    
    def _plot_single_peak(self, plotting, plot, trace, peak):
        """Plots single peak using its own profile."""
        
        # set trace
        peak.PeakModel.SetTrace(trace)
        
        # get profile
        profile_x = [p[0] for p in peak.PeakModel.Profile]
        profile_y = [p[1] for p in peak.PeakModel.Profile]
        
        # make fill
        fill_x = []
        fill_y = []
        
        for p in peak.PeakModel.Profile:
            if (peak.RightRT - p[0]) < -RT_EPSILON:
                break
            if (peak.LeftRT - p[0]) <= RT_EPSILON:
                fill_x.append(p[0])
                fill_y.append(peak.PeakModel.GetFullIntensityAtRT(p[0]))
        
        # add baseline to fill
        fill_x.insert(0, peak.LeftRT)
        fill_y.insert(0, peak.PeakModel.GetBaselineAtRT(peak.LeftRT))
        fill_x.append(peak.RightRT)
        fill_y.append(peak.PeakModel.GetBaselineAtRT(peak.RightRT))
        
        # init RT marks
        apex = ((peak.ApexRT, 0), (peak.ApexRT, peak.ApexIntensity))
        left_edge = ((peak.LeftRT, 0), (peak.LeftRT, peak.ApexIntensity))
        right_edge = ((peak.RightRT, 0), (peak.RightRT, peak.ApexIntensity))
        
        # plot peak
        plotting.fill(plot, fill_x, fill_y, alpha=0.3, zorder=1)
        plotting.plot(plot, profile_x, profile_y, linewidth=2, zorder=2)
        plotting.lines(plot, (apex, ), linewidth=2, color="#ff5555", zorder=3)
        plotting.lines(plot, (left_edge, right_edge), linewidth=1, color="#ff5555", zorder=4)
    
    
    def _plot_combined_peak(self, plotting, plot, trace, peaks):
        """Plots combined peak using given trace raster."""
        
        # init raster
        raster = self._make_trace_raster(trace, peaks)
        
        # check raster
        if len(raster) == 0:
            return
        
        # set trace
        for peak in peaks:
            peak.PeakModel.SetTrace(trace)
        
        # get RT range
        left_rt = min(p.LeftRT for p in peaks)
        right_rt = max(p.RightRT for p in peaks)
        
        # get cumulative function
        cum_fn = sum
        if any(not p.PeakModel.Cumulative for p in peaks):
            cum_fn = max
        
        # init profile
        profile_x = raster[:]
        profile_y = []
        
        # calc profile
        for rt in profile_x:
            profile_y.append(cum_fn(p.PeakModel.GetFullIntensityAtRT(rt) for p in peaks))
        
        # init fill
        fill_x = profile_x[:]
        fill_y = profile_y[:]
        
        # add baseline points
        fill_x.insert(0, left_rt)
        fill_y.insert(0, cum_fn(p.PeakModel.GetBaselineAtRT(left_rt) for p in peaks))
        fill_x.append(right_rt)
        fill_y.append(cum_fn(p.PeakModel.GetBaselineAtRT(right_rt) for p in peaks))
        
        # get apex
        apex_rt = sum(p.ApexRT*p.Area for p in peaks)/sum(p.Area for p in peaks)
        apex_ai = cum_fn(p.PeakModel.GetFullIntensityAtRT(apex_rt) for p in peaks)
        apex = ((apex_rt, 0), (apex_rt, apex_ai))
        
        # plot peak
        plotting.fill(plot, fill_x, fill_y, alpha=0.3, zorder=1)
        plotting.plot(plot, profile_x, profile_y, linewidth=1, zorder=2)
        plotting.lines(plot, (apex, ), linewidth=1, color="#ff5555", zorder=3)
    
    
    def _make_trace_raster(self, trace, peaks):
        """Makes raster using given trace and peaks."""
        
        # get RT range
        left_rt = min(p.LeftRT for p in peaks)
        right_rt = max(p.RightRT for p in peaks)
        
        # make raster
        raster = []
        for p in trace:
            if (right_rt - p.RT) < -RT_EPSILON:
                break
            if (left_rt - p.RT) <= RT_EPSILON:
                raster.append(p.RT)
        
        return raster
