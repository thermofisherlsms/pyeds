#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import xml.etree.cElementTree as etree
from .converter import register, ValueConverter
from .spectrum import Centroid


@register("2FB4BD3B-DB6D-4794-92DF-C62D41B7599F")
class IsotopePatternConverter(ValueConverter):
    """
    The pyeds.IsotopePatternConverter is used to convert isotope pattern data from
    original binary format into pyeds.IsotopePattern.
    """
    
    
    def Convert(self, value):
        """
        Converts binary pattern data.
        
        Args:
            value: pyeds.Binary
                Binary data as stored in result file.
        
        Returns:
            pyeds.IsotopePattern or None
                Parsed pattern.
        """
        
        # check value
        if not value:
            return None
        
        # parse data
        return IsotopePatternParser().parse(value.Unzip())


class IsotopePatternParser(object):
    """
    The pyeds.IsotopePatternParser is used to parse isotope pattern data from
    original binary format into pyeds.IsotopePattern.
    """
    
    
    def parse(self, xml):
        """
        Parses given pattern XML.
        
        Args:
            xml: str
                Pattern XML.
        
        Returns:
            pyeds.IsotopePattern
                Parsed pattern.
        """
        
        # parse XML
        tree = etree.fromstring(xml)
        
        # retrieve header data
        header = self._retrieve_header(tree)
        
        # retrieve centroids data
        centroids = self._retrieve_centroids(tree)
        
        # free memory
        tree.clear()
        
        # create pattern
        pattern = IsotopePattern()
        pattern.Header = header
        pattern.Centroids = centroids
        
        return pattern
    
    
    def _retrieve_header(self, pattern_elm):
        """Retrieves header data."""
        
        # init header
        header = PatternHeader()
        
        # retrieve values
        elm = pattern_elm.find('PatternID')
        if elm is not None:
            header.PatternID = int(elm.text)
        
        elm = pattern_elm.find('MonoisotopicMass')
        if elm is not None:
            header.MonoisotopicMass = float(elm.text)
        
        elm = pattern_elm.find('Charge')
        if elm is not None:
            header.Charge = int(elm.text)
        
        elm = pattern_elm.find('Resolution')
        if elm is not None:
            header.Resolution = float(elm.text)
        
        elm = pattern_elm.find('IsReliable')
        if elm is not None:
            header.IsReliable = elm.text == 'true'
        
        elm = pattern_elm.find('Correlation')
        if elm is not None:
            header.Correlation = float(elm.text)
        
        elm = pattern_elm.find('Separation')
        if elm is not None:
            header.Separation = float(elm.text)
        
        elm = pattern_elm.find('Goodness')
        if elm is not None:
            header.Goodness = float(elm.text)
        
        elm = pattern_elm.find('TotalError')
        if elm is not None:
            header.TotalError = float(elm.text)
        
        return header
    
    
    def _retrieve_centroids(self, pattern_elm):
        """Retrieves centroids data."""
        
        # init centroids
        centroids = []
        
        # retrieve centroids
        peaks_elm = pattern_elm.find('PatternPeaks')
        if peaks_elm is not None:
            
            for peak_elm in peaks_elm.iter('Peak'):
                
                centroid = Centroid()
                
                centroid.MZ = float(peak_elm.get('X', 0))
                centroid.Intensity = float(peak_elm.get('Y', 0))
                centroid.Charge = int(peak_elm.get('Z', None))
                centroid.SN = float(peak_elm.get('SN', None))
                centroid.Resolution = float(peak_elm.get('R', None))
                
                centroids.append(centroid)
        
        return tuple(centroids)


class IsotopePattern(object):
    """
    The pyeds.IsotopePattern is used to hold information about isotope pattern.
    """
    
    
    def __init__(self):
        """Initializes a new instance of IsotopePattern."""
        
        self.Header = None
        self.Centroids = None
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return str(self.Header)
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())


class PatternHeader(object):
    """
    The pyeds.PatternHeader is used to hold additional information about isotope
    pattern.
    """
    
    
    def __init__(self):
        """Initializes a new instance of PatternHeader."""
        
        self.PatternID = None
        self.MonoisotopicMass = None
        self.Charge = None
        self.Resolution = None
        
        self.IsReliable = None
        self.Correlation = None
        self.Separation = None
        self.Goodness = None
        self.TotalError = None
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return "MZ:%f Res:%d Z:%d" % (self.MonoisotopicMass, self.Resolution, self.Charge)
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
