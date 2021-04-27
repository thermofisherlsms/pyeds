#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import math
import zipfile
import base64
import xml.etree.cElementTree as eTree
from io import BytesIO
from .common import register, ValueConverter

# define constants
GAUSSIAN_FWHM = 2*math.sqrt(-2*math.log(0.5)) / math.sqrt(2)
GAUSSIAN_AREA = 2*math.sqrt(-2*math.log(0.5)) / math.sqrt(2*math.pi)

MODEL_GAUSS = 'Gauss'
MODEL_GAMMA = 'Gamma'
MODEL_LINEAR = 'Linear'

RT_EPSILON = 0.00001


@register("3A2A8593-FC7D-4FA1-9AD1-F5BF580AD85F")
class PeakModelValueConverter(ValueConverter):
    """
    The pyeds.TraceConverter is used to convert chromatogram trace data from
    original binary format into a collection of pyeds.TracePoint items.
    """
    
    
    def Convert(self, value):
        """
        Converts binary peak model data.
        
        Args:
            value: pyeds.Binary
                Binary data as stored in result file.
        
        Returns:
            pyeds.PeakModel or None
                Parsed peak model.
        """
        
        # check value
        if not value:
            return None
        
        # parse data
        return PeakModelParser().parse(value.Unzipped)


class PeakModelParser(object):
    """
    The pyeds.PeakModelParser is used to parse a chromatogram peak model data
    into corresponding pyeds.PeakModel item.
    """
    
    
    def parse(self, xml):
        """
        Parses given peak XML.
        
        Args:
            xml: str
                Peak XML.
        
        Returns:
            pyeds.PeakModel
                Parsed peak.
        """
        
        # parse XML
        tree = eTree.fromstring(xml)
        
        # get model guid
        guid = None
        guid_elm = tree.find('PeakGuid')
        if guid_elm is not None:
            guid = guid_elm.text
        
        # get model version
        version = 1
        version_elm = tree.find('Version')
        if version_elm is not None:
            version = int(version_elm.text)
        
        # get model data
        data = None
        data_elm = tree.find('Data')
        if data_elm is not None:
            data = data_elm.text
        
        # free memory
        tree.clear()
        
        # check data
        if not data:
            return None
        
        # decode peak data
        peak_data = base64.b64decode(data)
        
        # unzip peak data
        peak_xml = None
        stream = BytesIO(peak_data)
        if zipfile.is_zipfile(stream):
            with zipfile.ZipFile(stream) as zf:
                peak_xml = zf.read(zf.namelist()[0])
        
        # check XML
        if not peak_xml:
            return None
        
        # parse interpolated peak
        if guid == "5C9FB331-DC4E-4081-A93B-7905AD71AC1C":
            return InterpolatedPeakModelParser().parse(peak_xml, version)
        
        # parse simple Gaussian peak
        elif guid == "CE49D6BA-2A9C-4914-8061-CDF63C579CB5":
            return GaussianPeakModelParser().parse(peak_xml, version)
        
        # parse PPD peak
        elif guid == "E0078D5E-42B2-4901-929A-671629B91072":
            return PPDPeakModelParser().parse(peak_xml, version)
        
        # parse Pyco peak
        elif guid == "2A9838C3-FEFB-41D1-8CB5-0F29201C960E":
            return PycoPeakModelParser().parse(peak_xml, version)
        
        raise ValueError("Unknown peak model!")


class InterpolatedPeakModelParser(object):
    """
    The pyeds.InterpolatedPeakModelParser is used to parse an interpolated
    chromatogram peak model data into a pyeds.InterpolatedPeakModel item.
    """
    
    
    def parse(self, xml, version):
        """
        Parses given binary peak model data.
        
        Args:
            xml: str
                Peak data XML.
            
            version: int
                Peak model version.
        
        Returns:
            pyeds.InterpolatedPeakModel
                Parsed peak.
        """
        
        # check XML
        if not xml:
            return None
        
        # parse peak XML
        peak_elm = eTree.fromstring(xml)
        peak_data = self._parse_peak_model(peak_elm)
        peak_elm.clear()
        
        # create peak
        return self._make_peak(peak_data, version)
    
    
    def _parse_peak_model(self, peak_elm):
        """Parser peak model element."""
        
        # init peak data container
        peak_data = {
            'apex_rt': None,
            'left_rt': None,
            'right_rt': None,
            'method': None,
            'rt_curve': [],
            'ai_curve': []}
        
        # get main values
        elm = peak_elm.find('ApexRT')
        if elm is not None:
            peak_data['apex_rt'] = float(elm.text)
        
        elm = peak_elm.find('LeftRT')
        if elm is not None:
            peak_data['left_rt'] = float(elm.text)
        
        elm = peak_elm.find('RightRT')
        if elm is not None:
            peak_data['right_rt'] = float(elm.text)
        
        elm = peak_elm.find('Method')
        if elm is not None:
            peak_data['method'] = elm.text
        
        # get RT curve
        elm = peak_elm.find('CurvePointsRT')
        if elm is not None:
            for point in elm.iter('float'):
                peak_data['rt_curve'].append(float(point.text))
        
        # get ai curve
        elm = peak_elm.find('CurvePointsIntensity')
        if elm is not None:
            for point in elm.iter('float'):
                peak_data['ai_curve'].append(float(point.text))
        
        return peak_data
    
    
    def _make_peak(self, peak_data, version):
        """Creates pyeds.InterpolatedPeakModel object from raw data."""
        
        # init peak
        peak = InterpolatedPeakModel()
        
        peak.ApexRT = peak_data['apex_rt']
        peak.LeftRT = peak_data['left_rt']
        peak.RightRT = peak_data['right_rt']
        peak.Method = peak_data['method']
        peak.Trace = tuple(zip(peak_data['rt_curve'], peak_data['ai_curve']))
        
        # set baseline
        peak.LeftBaseline = peak.Trace[0][1]
        peak.RightBaseline = peak.Trace[-1][1]
        
        # init profile
        ai = [peak.GetFullIntensityAtRT(rt) for rt in peak_data['rt_curve']]
        peak.Profile = tuple(zip(peak_data['rt_curve'], ai))
        
        return peak


class GaussianPeakModelParser(object):
    """
    The pyeds.GaussianPeakModelParser is used to parse a simulated Gaussian
    chromatogram peak model data into a pyeds.GaussianPeakModel item.
    """
    
    
    def parse(self, xml, version):
        """
        Parses given binary peak model data.
        
        Args:
            xml: str
                Peak data XML.
            
            version: int
                Peak model version.
        
        Returns:
            pyeds.GaussianPeakModel
                Parsed peak.
        """
        
        # check XML
        if not xml:
            return None
        
        # parse peak XML
        peak_elm = eTree.fromstring(xml)
        peak_data = self._parse_peak_model(peak_elm)
        peak_elm.clear()
        
        # create peak
        return self._make_peak(peak_data, version)
    
    
    def _parse_peak_model(self, peak_elm):
        """Parser peak model element."""
        
        # init peak data container
        peak_data = {
            'apex_rt': None,
            'apex_int': None,
            'left_rt': None,
            'left_base': None,
            'right_rt': None,
            'right_base': None,
            'fwhm': None}
        
        # get main values
        elm = peak_elm.find('ApexRT')
        if elm is not None:
            peak_data['apex_rt'] = float(elm.text)
        
        elm = peak_elm.find('ApexIntensity')
        if elm is not None:
            peak_data['apex_int'] = float(elm.text)
        
        elm = peak_elm.find('LeftRT')
        if elm is not None:
            peak_data['left_rt'] = float(elm.text)
        
        elm = peak_elm.find('LeftBaseline')
        if elm is not None:
            peak_data['left_base'] = float(elm.text)
        
        elm = peak_elm.find('RightRT')
        if elm is not None:
            peak_data['right_rt'] = float(elm.text)
        
        elm = peak_elm.find('RightBaseline')
        if elm is not None:
            peak_data['right_base'] = float(elm.text)
        
        elm = peak_elm.find('FWHM')
        if elm is not None:
            peak_data['fwhm'] = float(elm.text)
        
        return peak_data
    
    
    def _make_peak(self, peak_data, version):
        """Creates pyeds.GaussianPeakModel object from raw data."""
        
        # init peak
        peak = GaussianPeakModel()
        
        peak.ApexRT = peak_data['apex_rt']
        peak.ApexIntensity = peak_data['apex_int']
        peak.LeftRT = peak_data['left_rt']
        peak.LeftBaseline = peak_data['left_base']
        peak.RightRT = peak_data['right_rt']
        peak.RightBaseline = peak_data['right_base']
        peak.FWHM = peak_data['fwhm']
        
        # calc area
        peak.Area = 60 * peak.ApexIntensity * peak.FWHM / GAUSSIAN_AREA
        
        # init profile
        raster = make_raster(peak.LeftRT, peak.RightRT, peak.FWHM)
        ai = [peak.GetFullIntensityAtRT(rt) for rt in raster]
        peak.Profile = tuple(zip(raster, ai))
        
        return peak


class PPDPeakModelParser(object):
    """
    The pyeds.PPDPeakModelParser is used to parse a PPD chromatogram peak model
    data into a pyeds.PPDPeakModel item.
    """
    
    
    def parse(self, xml, version):
        """
        Parses given binary peak model data.
        
        Args:
            xml: str
                Peak data XML.
            
            version: int
                Peak model version.
        
        Returns:
            pyeds.PPDPeakModel
                Parsed peak.
        """
        
        # check XML
        if not xml:
            return None
        
        # parse peak XML
        peak_elm = eTree.fromstring(xml)
        peak_data = self._parse_peak_model(peak_elm)
        peak_elm.clear()
        
        # create peak
        return self._make_peak(peak_data, version)
    
    
    def _parse_peak_model(self, peak_elm):
        """Parser peak model element."""
        
        # init peak data container
        peak_data = {
            'apex_rt': None,
            'apex_int': None,
            'left_rt': None,
            'left_base': None,
            'right_rt': None,
            'right_base': None,
            'fitted_function': None,
            'fitted_rt': None,
            'fitted_int': None,
            'fitted_width': None,
            'fitted_asymmetry': None,
            'peaks': []}
        
        # get main values
        elm = peak_elm.find('ApexRT')
        if elm is not None:
            peak_data['apex_rt'] = float(elm.text)
        
        elm = peak_elm.find('ApexIntensity')
        if elm is not None:
            peak_data['apex_int'] = float(elm.text)
        
        elm = peak_elm.find('LeftRT')
        if elm is not None:
            peak_data['left_rt'] = float(elm.text)
        
        elm = peak_elm.find('LeftBaseline')
        if elm is not None:
            peak_data['left_base'] = float(elm.text)
        
        elm = peak_elm.find('RightRT')
        if elm is not None:
            peak_data['right_rt'] = float(elm.text)
        
        elm = peak_elm.find('RightBaseline')
        if elm is not None:
            peak_data['right_base'] = float(elm.text)
        
        elm = peak_elm.find('FittedFunction')
        if elm is not None:
            peak_data['fitted_function'] = elm.text
        
        elm = peak_elm.find('FittedRT')
        if elm is not None:
            peak_data['fitted_rt'] = float(elm.text)
        
        elm = peak_elm.find('FittedIntensity')
        if elm is not None:
            peak_data['fitted_int'] = float(elm.text)
        
        elm = peak_elm.find('FittedWidth')
        if elm is not None:
            peak_data['fitted_width'] = float(elm.text)
        
        elm = peak_elm.find('FittedAsymmetry')
        if elm is not None:
            peak_data['fitted_asymmetry'] = float(elm.text)
        
        # get merged peaks
        elm = peak_elm.find('MergedPeaks')
        if elm is not None:
            for subpeak_elm in elm.iter('PPDPeakModel'):
                subpeak_data = self._parse_peak_model(subpeak_elm)
                peak_data['peaks'].append(subpeak_data)
        
        return peak_data
    
    
    def _make_peak(self, peak_data, version):
        """Creates pyeds.PPDPeakModel object from raw data."""
        
        # fix incorrectly stored fitted params
        if version == 1:
            self._fix_fitted_params(peak_data)
        
        # init peak
        peak = PPDPeakModel()
        
        peak.ApexRT = peak_data['apex_rt']
        peak.ApexIntensity = peak_data['apex_int']
        peak.LeftRT = peak_data['left_rt']
        peak.LeftBaseline = peak_data['left_base']
        peak.RightRT = peak_data['right_rt']
        peak.RightBaseline = peak_data['right_base']
        
        peak.FittedFunction = peak_data['fitted_function']
        peak.FittedRT = peak_data['fitted_rt']
        peak.FittedIntensity = peak_data['fitted_int']
        peak.FittedWidth = peak_data['fitted_width']
        peak.FittedAsymmetry = peak_data['fitted_asymmetry']
        
        # add merged peaks
        if peak_data['peaks']:
            merged = []
            for child_data in peak_data['peaks']:
                child = self._make_peak(child_data, version)
                merged.append(child)
            peak.MergedPeaks = tuple(sorted(merged, key=lambda p: p.ApexIntensity, reverse=True))
        
        # calc FWHM
        if peak.FittedFunction == MODEL_GAUSS:
            peak.FWHM = GAUSSIAN_FWHM * peak.FittedWidth
        elif peak.FittedFunction == MODEL_GAMMA:
            peak.FWHM = math.sqrt(8.0 * math.log(2.0) * (peak.FittedAsymmetry - 1.0)) / peak.FittedWidth
        
        # calc area
        if peak.MergedPeaks:
            peak.Area = sum(p.Area for p in peak.MergedPeaks)
        elif peak.FittedFunction == MODEL_GAUSS:
            peak.Area = 60 * peak.FittedIntensity * GAUSSIAN_FWHM * peak.FittedWidth / GAUSSIAN_AREA
        elif peak.FittedFunction == MODEL_GAMMA:
            peak.Area = 60 * 100 * peak.FittedIntensity
        
        # init profile
        raster = make_raster(peak.LeftRT, peak.RightRT, peak.FWHM)
        ai = [peak.GetFullIntensityAtRT(rt) for rt in raster]
        peak.Profile = tuple(zip(raster, ai))
        
        return peak
    
    
    def _fix_fitted_params(self, peak_data):
        """Corrects incorrectly stored fitted params."""
        
        # fix params
        peak_data['fitted_rt'] = peak_data['apex_rt']
        peak_data['fitted_int'] = peak_data['apex_int']
        
        # fix Gamma apex
        if peak_data['fitted_function'] == MODEL_GAMMA:
            
            peak_data['apex_rt'] = peak_data['fitted_rt'] + (peak_data['fitted_asymmetry'] - 1) / peak_data['fitted_width']
            
            peak_data['apex_int'] = calc_gamma_ai(
                x = peak_data['apex_rt'],
                amplitude = peak_data['fitted_int'],
                start = peak_data['fitted_rt'],
                flow = peak_data['fitted_width'],
                mixing = peak_data['fitted_asymmetry'])


class PycoPeakModelParser(object):
    """
    The pyeds.PycoPeakModelParser is used to parse a Pyco chromatogram peak
    model data into a pyeds.PycoPeakModel item.
    """
    
    
    def parse(self, xml, version):
        """
        Parses given binary peak model data.
        
        Args:
            xml: str
                Peak data XML.
            
            version: int
                Peak model version.
        
        Returns:
            pyeds.PycoPeakModel
                Parsed peak.
        """
        
        # check XML
        if not xml:
            return None
        
        # parse peak XML
        peak_elm = eTree.fromstring(xml)
        peak_data = self._parse_peak_model(peak_elm)
        peak_elm.clear()
        
        # create peak
        return self._make_peak(peak_data, version)
    
    
    def _parse_peak_model(self, peak_elm):
        """Parser peak model element."""
        
        # init peak data container
        peak_data = {
            'apex_rt': None,
            'left_rt': None,
            'left_base': None,
            'right_rt': None,
            'right_base': None,
            'width': None,
            'method': None,
            'rt_curve': [],
            'int_curve': []}
        
        # get main values
        elm = peak_elm.find('ApexRT')
        if elm is not None:
            peak_data['apex_rt'] = float(elm.text)
        
        elm = peak_elm.find('LeftRT')
        if elm is not None:
            peak_data['left_rt'] = float(elm.text)
        
        elm = peak_elm.find('LeftBaseline')
        if elm is not None:
            peak_data['left_base'] = float(elm.text)
        
        elm = peak_elm.find('RightRT')
        if elm is not None:
            peak_data['right_rt'] = float(elm.text)
        
        elm = peak_elm.find('RightBaseline')
        if elm is not None:
            peak_data['right_base'] = float(elm.text)
        
        elm = peak_elm.find('Width')
        if elm is not None:
            peak_data['width'] = float(elm.text)
        
        elm = peak_elm.find('Method')
        if elm is not None:
            peak_data['method'] = elm.text
        
        # get RT curve
        elm = peak_elm.find('CurvePointsRT')
        if elm is not None:
            for point in elm.iter('float'):
                peak_data['rt_curve'].append(float(point.text))
        
        # get ai curve
        elm = peak_elm.find('CurvePointsIntensity')
        if elm is not None:
            for point in elm.iter('float'):
                peak_data['int_curve'].append(float(point.text))
        
        return peak_data
    
    
    def _make_peak(self, peak_data, version):
        """Creates pyeds.PycoPeakModel object from raw data."""
        
        # init peak
        peak = PycoPeakModel()
        
        peak.ApexRT = peak_data['apex_rt']
        peak.LeftRT = peak_data['left_rt']
        peak.LeftBaseline = peak_data['left_base']
        peak.RightRT = peak_data['right_rt']
        peak.RightBaseline = peak_data['right_base']
        peak.FWHM = peak_data['width']
        peak.Method = peak_data['method']
        peak.Trace = tuple(zip(peak_data['rt_curve'], peak_data['int_curve']))
        
        # init profile
        ai = [peak.GetFullIntensityAtRT(rt) for rt in peak_data['rt_curve']]
        peak.Profile = tuple(zip(peak_data['rt_curve'], ai))
        
        return peak


class PeakModel(object):
    """
    The pyeds.PeakModel serves as a base class for various types of peak models.
    
    Attrs:
        ApexRT: float
            Apex retention time in minutes.
        
        LeftRT: float
            Left retention time in minutes.
        
        RightRT: float
            Right retention time in minutes.
        
        LeftBaseline: float
            Intensity of left baseline point.
        
        RightBaseline: float
            Intensity of right baseline point.
        
        Profile: ((float, float),)
            Peak full intensity profile as (rt, ai) points.
    """
    
    MODEL = "Unknown"
    
    def __init__(self):
        """Initializes a new instance of PeakModel."""
        
        self.ApexRT = None
        self.LeftRT = None
        self.RightRT = None
        self.LeftBaseline = 0
        self.RightBaseline = 0
        self.Profile = None
        self.Cumulative = True
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        data = "[%s] RT:%.3f (%.3f-%.3f)" % (self.MODEL, self.ApexRT, self.LeftRT, self.RightRT)
        
        if self.LeftBaseline:
            data += " LB:%.0f" % self.LeftBaseline
        
        if self.RightBaseline:
            data += " RB:%.0f" % self.RightBaseline
        
        return data
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    def SetTrace(self, trace):
        """
        Sets given trace into the peak. This is mainly used for visualization of
        peaks having no model nor the own trace. It might have no effect for
        other types of nodes.
        
        Args:
            trace: pyeds.Trace
                Trace to set.
        """
        
        pass
    
    
    def GetFullIntensityAtRT(self, rt):
        """
        Calculates total intensity (including baseline) at given retention time.
        
        Args:
            rt: float
                Retention time in minutes.
        
        Returns:
            float
                Peak ai at given retention time.
        """
        
        return self.GetIntensityAtRT(rt) + self.GetBaselineAtRT(rt)
    
    
    def GetIntensityAtRT(self, rt):
        """
        Calculates intensity above baseline at given retention time.
        
        Args:
            rt: float
                Retention time in minutes.
        
        Returns:
            float
                Peak intensity above baseline at given retention time.
        """
        
        raise NotImplementedError()
    
    
    def GetBaselineAtRT(self, rt):
        """
        Calculates baseline intensity at given retention time as linear
        interpolation between left and right baseline points.
        
        Args:
            rt: float
                Retention time in minutes.
        
        Returns:
            float
                Peak baseline intensity at given retention time.
        """
        
        # check peak range
        if equals(rt, self.LeftRT):
            return self.LeftBaseline
        
        if equals(rt, self.RightRT):
            return self.RightBaseline
        
        if rt < self.LeftRT or rt > self.RightRT:
            return 0
        
        # interpolate in-between
        return self.LeftBaseline + (self.RightBaseline - self.LeftBaseline) * (rt - self.LeftRT) / (self.RightRT - self.LeftRT)


class InterpolatedPeakModel(PeakModel):
    """
    The pyeds.InterpolatedPeakModel represents a chromatographic peak model
    created by trace interpolation.
    
    Attrs:
        Method: str
            Interpolation method.
        
        Trace: ((float, float),)
            Peak original trace profile as (rt, ai) points. This should be the
            original trace without baseline correction etc.
    """
    
    MODEL = "Interpolated"
    
    def __init__(self):
        """Initializes a new instance of InterpolatedPeakModel."""
        
        super().__init__()
        
        self.Method = None
        self.Trace = None
    
    
    def GetIntensityAtRT(self, rt):
        """
        Calculates intensity above baseline at given retention time.
        
        Args:
            rt: float
                Retention time in minutes.
        
        Returns:
            float
                Peak intensity above baseline at given retention time.
        """
        
        # interpolate linear
        if self.Method == MODEL_LINEAR:
            return max(0, calc_linear_ai(rt, self.Trace) - self.GetBaselineAtRT(rt))
        
        raise ValueError("Unknown interpolation method!")


class GaussianPeakModel(PeakModel):
    """
    The pyeds.GaussianPeakModel represents a chromatographic peak model created
    by Gaussian shape simulation.
    
    Attrs:
        FWHM: float
            Peak width at half maximum in minutes.
        
        Area: float
            Peak area in seconds*counts.
        
        ApexIntensity: float
            Apex intensity above baseline.
    """
    
    MODEL = "Gaussian"
    
    def __init__(self):
        """Initializes a new instance of GaussianPeakModel."""
        
        super().__init__()
        
        self.ApexIntensity = None
        self.FWHM = None
        self.Area = None
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        data = super().__str__()
        
        if self.FWHM:
            data += " FWHM:%.3f" % self.FWHM
        
        if self.Area:
            data += " Area:%.0f" % self.Area
        
        if self.ApexIntensity:
            data += " Int:%.0f" % self.ApexIntensity
        
        return data
    
    
    def GetIntensityAtRT(self, rt):
        """
        Calculates intensity above baseline at given retention time.
        
        Args:
            rt: float
                Retention time in minutes.
        
        Returns:
            float
                Peak intensity above baseline at given retention time.
        """
        
        width = self.FWHM / GAUSSIAN_FWHM
        return calc_gaussian_ai(rt, self.ApexIntensity, self.ApexRT, width)


class PPDPeakModel(PeakModel):
    """
    The pyeds.PPDPeakModel represents a chromatographic peak model used by PPD
    peak detection algorithm.
    
    Attrs:
        FWHM: float
            Peak width at half maximum in minutes.
        
        Area: float
            Peak area in seconds*counts.
        
        ApexIntensity: float
            Apex intensity above baseline.
    """
    
    MODEL = "PPD"
    
    def __init__(self):
        """Initializes a new instance of PPDPeakModel."""
        
        super().__init__()
        
        self.ApexIntensity = None
        self.FWHM = None
        self.Area = None
        
        self.FittedFunction = None
        self.FittedRT = None
        self.FittedIntensity = None
        self.FittedWidth = None
        self.FittedAsymmetry = None
        
        self.MergedPeaks = ()
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        data = super().__str__()
        
        if self.FWHM:
            data += " FWHM:%.3f" % self.FWHM
        
        if self.Area:
            data += " Area:%.0f" % self.Area
        
        if self.ApexIntensity:
            data += " Int:%.0f" % self.ApexIntensity
        
        if self.MergedPeaks:
            for peak in self.MergedPeaks:
                data += "\n\t%s" % peak
        
        elif self.FittedFunction == MODEL_GAUSS:
            data += " (%s" % self.FittedFunction.upper()
            data += " Center:%.3f" % self.FittedRT
            data += " Amp:%.0f" % self.FittedIntensity
            data += " Width:%.3f" % self.FittedWidth
            data += ")"
        
        elif self.FittedFunction == MODEL_GAMMA:
            data += " (%s" % self.FittedFunction.upper()
            data += " Start:%.3f" % self.FittedRT
            data += " Amp:%.3f" % self.FittedIntensity
            data += " Flow:%.3f" % self.FittedWidth
            data += " Mix:%.3f" % self.FittedAsymmetry
            data += ")"
        
        return data
    
    
    def GetIntensityAtRT(self, rt):
        """
        Calculates intensity above baseline at given retention time.
        
        Args:
            rt: float
                Retention time in minutes.
        
        Returns:
            float
                Peak intensity above baseline at given retention time.
        """
        
        if self.MergedPeaks:
            return sum(p.GetIntensityAtRT(rt) for p in self.MergedPeaks)
        
        if self.FittedFunction == MODEL_GAUSS:
            return calc_gaussian_ai(rt, self.FittedIntensity, self.FittedRT, self.FittedWidth)
        
        elif self.FittedFunction == MODEL_GAMMA:
            return calc_gamma_ai(rt, self.FittedIntensity, self.FittedRT, self.FittedWidth, self.FittedAsymmetry)
        
        raise ValueError("Unknown peak model function!")


class PycoPeakModel(PeakModel):
    """
    The pyeds.PycoPeakModel represents a chromatographic peak model used by Pyco
    peak detection algorithm.
    
    Attrs:
        FWHM: float
            Peak width at half maximum in minutes.
        
        Trace: ((float, float),)
            Peak processed trace profile as (rt, intensity) points. This should
            include baseline correction, gap filling etc.
    """
    
    MODEL = "Pyco"
    
    def __init__(self):
        """Initializes a new instance of PycoPeakModel."""
        
        super().__init__()
        
        self.FWHM = None
        self.Method = None
        self.Trace = None
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        data = super().__str__()
        
        if self.FWHM:
            data += " FWHM:%.3f" % self.FWHM
        
        return data
    
    
    def SetTrace(self, trace, cumulative=False):
        """
        Sets given trace into the peak and generate profile. Once the trace is
        set, it cannot be changed.
        
        Args:
            trace: pyeds.Trace
                Trace to set.
            
            cumulative: bool
                If set to True the trace is considered as the original trace
                from which the peak was detected. Therefore the peak can be
                summed up with other peaks (having different trace). If set to
                False, the trace is shared with other peaks so maximum for each
                RT is used when combining the peaks.
        """
        
        # set only if not available
        if self.Trace is None or len(self.Trace) == 0:
            
            # set trace
            self.Trace = tuple((p.RT, p.Intensity) for p in trace)
            self.Cumulative = cumulative
            
            # init profile
            left_idx = bisearch(self.LeftRT, self.Trace)
            right_idx = min(bisearch(self.RightRT, self.Trace) + 1, len(trace))
            self.Profile = tuple((p.RT, p.Intensity) for p in trace[left_idx:right_idx])
    
    
    def GetIntensityAtRT(self, rt):
        """
        Calculates intensity above baseline at given retention time.
        
        Args:
            rt: float
                Retention time in minutes.
        
        Returns:
            float
                Peak intensity above baseline at given retention time.
        """
        
        # interpolate linear
        if self.Method == MODEL_LINEAR:
            return max(0, calc_linear_ai(rt, self.Trace))
        
        raise ValueError("Unknown interpolation method!")


def calc_linear_ai(x, profile, epsilon=RT_EPSILON):
    """Calculates intensity by linear interpolation."""
    
    # find equal or next higher
    idx = bisearch(x, profile, epsilon)
    
    # outside
    if idx == len(profile):
        return 0
    
    # direct match
    if equals(x, profile[idx][0], epsilon):
        return profile[idx][1]
    
    # outside
    if x == 0:
        return 0
    
    # get adjacent points
    p1 = profile[idx - 1]
    p2 = profile[idx]
    
    # same
    if p1[1] == p2[1]:
        return p1[1]
    
    # interpolate
    a = float(p2[1] - p1[1]) / float(p2[0] - p1[0])
    b = p1[1] - a * p1[0]
    
    return a * x + b


def calc_gaussian_ai(x, amplitude, center, width):
    """Calculates intensity in Gaussian model."""
    
    return amplitude * math.exp(-math.pow(x - center, 2) / (width * width))


def calc_gamma_ai(x, amplitude, start, flow, mixing):
    """Calculates intensity in Gamma model."""
    
    # no asymmetry
    if mixing == 1:
        return amplitude * flow * math.exp(-flow * (x - start))
    
    # get shift from start
    diff = x - start
    if diff <= 0:
        return 0
    
    # calc intensity
    intensity = 0
    intensity += math.log(abs(amplitude))
    intensity += mixing * math.log(abs(flow))
    intensity += (mixing - 1.0) * math.log(diff)
    intensity -= calc_log_gamma(mixing)
    intensity -= flow * diff
    intensity = math.exp(intensity) * 100.
    
    return intensity


def calc_log_gamma(asymmetry):
    """Calculates log gamma."""
    
    powers = [1.0]
    for i in range(7):
        powers.append(powers[i] / asymmetry)
    
    log_gamma = (asymmetry - 0.5) * math.log(abs(asymmetry)) - asymmetry + 0.918938533204673
    log_gamma += powers[1] / 12.0
    log_gamma -= powers[3] / 360.0
    log_gamma += powers[5] / 1260.0
    log_gamma += powers[7] / 1680.0
    
    return log_gamma


def make_raster(minimum, maximum, fwhm, ppf=10):
    """
    Creates raster for peak simulation.
    
    Args:
        minimum: float
            Maximum raster value.
    
        maximum: float
            Maximum raster value.
    
        fwhm: float
            Peak width at half maximum.

        ppf: int
            Number of points per fwhm.
    
    Returns:
        (float,)
            Simulated raster coordinates.
    """
    
    diff = fwhm / ppf
    points = int((maximum - minimum) / diff)
    raster = [minimum + i * diff for i in range(points)]
    
    if raster[-1] < maximum:
        raster.append(maximum)
    
    return tuple(raster)


def equals(x1, x2, epsilon=RT_EPSILON):
    """Returns true if difference between given values is bellow epsilon."""
    
    return abs(x1-x2) <= epsilon


def bisearch(x, profile, epsilon=RT_EPSILON):
    """Use binary search to find index of equal or next higher x-value."""
    
    idx = 0
    hi = len(profile)
    
    while idx < hi:
        mid = (idx + hi) // 2
        if x < profile[mid][0] or equals(x, profile[mid][0], epsilon):
            hi = mid
        else:
            idx = mid + 1
    
    return idx
