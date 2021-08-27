#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import xml.etree.cElementTree as etree
from .converter import register, ValueConverter


@register("ED0FB1D9-4E07-47E1-B96C-4013B9AFE534")
class MassSpectrumConverter(ValueConverter):
    """
    The pyeds.MassSpectrumConverter is used to convert mass spectrum data from
    original binary format into pyeds.MassSpectrum.
    """
    
    
    def Convert(self, value):
        """
        Converts binary spectrum data.
        
        Args:
            value: pyeds.Binary
                Binary data as stored in result file.
        
        Returns:
            pyeds.MassSpectrum or None
                Parsed spectrum.
        """
        
        # check value
        if not value:
            return None
        
        # parse data
        return MassSpectrumParser().parse(value.Unzipped)


class MassSpectrumParser(object):
    """
    The pyeds.MassSpectrumParser is used to parse mass spectrum data from
    original binary format into pyeds.MassSpectrum.
    """
    
    
    def parse(self, xml):
        """
        Parses given pattern XML.
        
        Args:
            xml: str
                Spectrum XML.
        
        Returns:
            pyeds.MassSpectrum
                Mass spectrum.
        """
        
        # parse XML
        tree = etree.fromstring(xml)
        
        # retrieve spectrum header
        header_elm = tree.find('Header')
        header = self._retrieve_header(header_elm)
        
        # retrieve scan event
        event_elm = tree.find('ScanEvent')
        event = self._retrieve_event(event_elm)
        
        # retrieve precursor info
        precursor_elm = tree.find('PrecursorInfo')
        precursor = self._retrieve_precursor(precursor_elm)
        
        # retrieve centroids data
        peaks_elm = tree.find('PeakCentroids')
        centroids = self._retrieve_centroids(peaks_elm)
        
        # retrieve profile data
        points_elm = tree.find('ProfilePoints')
        profile = self._retrieve_profile(points_elm)
        
        # free memory
        tree.clear()
        
        # create spectrum
        spectrum = MassSpectrum()
        spectrum.Header = header
        spectrum.Event = event
        spectrum.Precursor = precursor
        spectrum.Centroids = centroids
        spectrum.Profile = profile
        
        return spectrum
    
    
    def _retrieve_header(self, header_elm):
        """Retrieves spectrum header."""
        
        # init header
        header = ScanHeader()
        
        # get header data
        if header_elm is not None:
            
            elm = header_elm.find('SpectrumID')
            if elm is not None and elm.text:
                header.SpectrumID = int(elm.text)
            
            elm = header_elm.find('InstrumentName')
            if elm is not None:
                header.InstrumentName = elm.text
            
            elm = header_elm.find('DataType')
            if elm is not None:
                header.DataType = elm.text
            
            elm = header_elm.find('LowPosition')
            if elm is not None and elm.text:
                header.LowPosition = float(elm.text)
            
            elm = header_elm.find('HighPosition')
            if elm is not None and elm.text:
                header.HighPosition = float(elm.text)
            
            elm = header_elm.find('BasePeakPosition')
            if elm is not None and elm.text:
                header.BasePeakPosition = float(elm.text)
            
            elm = header_elm.find('BasePeakIntensity')
            if elm is not None and elm.text:
                header.BasePeakIntensity = float(elm.text)
            
            elm = header_elm.find('TotalIntensity')
            if elm is not None and elm.text:
                header.TotalIntensity = float(elm.text)
            
            # retrieve identifiers
            identifiers_elm = header_elm.find('SpectrumIdentifiers')
            if identifiers_elm:
                for identifier_elm in identifiers_elm.iter('SpectrumIdentifier'):
                    
                    identifier = ScanIdentifier()
                    
                    attr = identifier_elm.get('FileID', None)
                    if attr is not None and attr != "-1" and attr != "":
                        identifier.FileID = int(attr)
                    
                    attr = identifier_elm.get('ScanNumber', None)
                    if attr is not None and attr != "":
                        identifier.ScanNumber = int(attr)
                    
                    attr = identifier_elm.get('MasterScanNumber', None)
                    if attr is not None and attr != "-1" and attr != "":
                        identifier.MasterScanNumber = int(attr)
                    
                    attr = identifier_elm.get('RetentionTime', None)
                    if attr is not None and attr != "":
                        identifier.RetentionTime = float(attr)
                    
                    # add to header
                    header.SpectrumIdentifiers.append(identifier)
        
        return header
    
    
    def _retrieve_event(self, event_elm):
        """Retrieves event data."""
        
        # init event
        event = ScanEvent()
        
        # get scan event data
        if event_elm is not None:
            
            elm = event_elm.find('ActivationTypes')
            if elm is not None:
                event.ActivationTypes = elm.text
            
            energies_elm = event_elm.find('ActivationEnergies')
            if energies_elm is not None:
                event.ActivationEnergies = []
                for elm in energies_elm.iter('double'):
                    event.ActivationEnergies.append(float(elm.text))
            
            elm = event_elm.find('CompensationVoltage')
            if elm is not None and elm.text:
                event.CompensationVoltage = float(elm.text)
            
            elm = event_elm.find('IonizationSource')
            if elm is not None and elm.text:
                event.IonizationSource = elm.text
            
            elm = event_elm.find('IsMultiplexed')
            if elm is not None:
                event.IsMultiplexed = elm.text == 'true'
            
            elm = event_elm.find('IsolationMass')
            if elm is not None and elm.text:
                event.IsolationMass = float(elm.text)
            
            elm = event_elm.find('IsolationWidth')
            if elm is not None and elm.text:
                event.IsolationWidth = float(elm.text)
            
            elm = event_elm.find('IsolationOffset')
            if elm is not None and elm.text:
                event.IsolationOffset = float(elm.text)
            
            elm = event_elm.find('MassAnalyzer')
            if elm is not None:
                event.MassAnalyzer = elm.text
            
            elm = event_elm.find('MSOrder')
            if elm is not None:
                event.MSOrder = elm.text
            
            elm = event_elm.find('Polarity')
            if elm is not None:
                event.Polarity = elm.text
            
            elm = event_elm.find('ResolutionAtMass200')
            if elm is not None and elm.text:
                event.ResolutionAtMass200 = int(elm.text)
            
            elm = event_elm.find('ScanRate')
            if elm is not None:
                event.ScanRate = elm.text
            
            elm = event_elm.find('ScanType')
            if elm is not None:
                event.ScanType = elm.text
        
        return event
    
    
    def _retrieve_precursor(self, precursor_elm):
        """Retrieves precursor data."""
        
        # init precursor
        precursor = PrecursorInfo()
        
        # get precursor data
        if precursor_elm is not None:
            
            attr = precursor_elm.get('Charge', None)
            if attr is not None and attr != "":
                precursor.Charge = int(attr)
            
            attr = precursor_elm.get('Intensity', None)
            if attr is not None and attr != "":
                precursor.Intensity = float(attr)
            
            attr = precursor_elm.get('InstrumentDeterminedCharge', None)
            if attr is not None and attr != "":
                precursor.InstrumentDeterminedCharge = int(attr)
            
            attr = precursor_elm.get('InstrumentDeterminedMonoisotopicMass', None)
            if attr is not None and attr != "":
                precursor.InstrumentDeterminedMonoisotopicMass = float(attr)
            
            attr = precursor_elm.get('IonInjectTime', None)
            if attr is not None and attr != "":
                precursor.IonInjectTime = float(attr)
            
            attr = precursor_elm.get('IsolationMass', None)
            if attr is not None and attr != "":
                precursor.IsolationMass = float(attr)
            
            attr = precursor_elm.get('IsolationOffset', None)
            if attr is not None and attr != "":
                precursor.IsolationOffset = float(attr)
            
            attr = precursor_elm.get('IsolationWidth', None)
            if attr is not None and attr != "":
                precursor.IsolationWidth = float(attr)
            
            attr = precursor_elm.get('PercentIsolationInterference', None)
            if attr is not None and attr != "":
                precursor.PrecursorInterference = float(attr)
            
            attr = precursor_elm.get('PrecursorMassOrigin', None)
            if attr is not None and attr != "":
                precursor.PrecursorMassOrigin = str(attr)
            
            attr = precursor_elm.get('Resolution', None)
            if attr is not None and attr != "":
                precursor.Resolution = int(attr)
            
            attr = precursor_elm.get('SignalToNoise', None)
            if attr is not None and attr != "":
                precursor.SignalToNoise = float(attr)
            
            attr = precursor_elm.get('SinglyChargedMass', None)
            if attr is not None and attr != "":
                precursor.SinglyChargedMass = float(attr)
            
            attr = precursor_elm.get('SpectrumNumber', None)
            if attr is not None and attr != "":
                precursor.SpectrumNumber = int(attr)
            
            # get spectrum header
            header_elm = precursor_elm.find('SpectrumHeader')
            precursor.Header = self._retrieve_header(header_elm)
            
            # get scan event
            event_elm = precursor_elm.find('ScanEvent')
            precursor.Event = self._retrieve_event(event_elm)
            
            # get mono centroids
            peaks_elm = precursor_elm.find('MonoisotopicPeakCentroids')
            precursor.MonoisotopicPeakCentroids = self._retrieve_centroids(peaks_elm)
            
            # get measured centroids
            peaks_elm = precursor_elm.find('MeasuredMonoisotopicPeakCentroids')
            precursor.MeasuredMonoisotopicPeakCentroids = self._retrieve_centroids(peaks_elm)
            
            # get cluster centroids
            peaks_elm = precursor_elm.find('IsotopeClusterPeakCentroids')
            precursor.IsotopeClusterPeakCentroids = self._retrieve_centroids(peaks_elm)
        
        return precursor
    
    
    def _retrieve_centroids(self, peaks_elm):
        """Retrieves centroids data."""
        
        # init centroids
        centroids = []
        
        # retrieve centroids
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
    
    
    def _retrieve_profile(self, points_elm):
        """Retrieves profile data."""
        
        # init profile
        profile = []
        
        # retrieve profile
        if points_elm is not None:
            for point_elm in points_elm.iter('Pt'):
                mz = float(point_elm.get('X', 0))
                ai = float(point_elm.get('Y', 0))
                profile.append((mz, ai))
        
        return tuple(profile)


class MassSpectrum(object):
    """
    The pyeds.MassSpectrum is used to hold information about mass spectrum.
    
    Attributes:
        
        Header: pyeds.ScanHeader
            Contains the spectrum header information.
        
        Event: pyeds.ScanEvent
            Contains the scan event information.
        
        Precursor: pyeds.PrecursorInfo
            Contains the precursor information.
        
        Centroids: (pyeds.Centroid,)
            Collection of spectrum centroids.
        
        Profile: ((float, float),)
            Collection of profile points as ((mz, intensity),)
    """
    
    
    def __init__(self):
        """Initializes a new instance of MassSpectrum."""
        
        self.Header = None
        self.Event = None
        self.Precursor = None
        self.Centroids = None
        self.Profile = None
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return "%s %s" % (self.Header, self.Event)
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    def __getattr__(self, name):
        """Tries to get unknown attribute from header or event."""
        
        if self.Header is not None and hasattr(self.Header, name):
            return getattr(self.Header, name)
        
        if self.Event is not None and hasattr(self.Event, name):
            return getattr(self.Event, name)
        
        raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))


class ScanHeader(object):
    """
    The pyeds.ScanHeader is used to hold information from mass spectrum header.
    """
    
    
    def __init__(self):
        """Initializes a new instance of ScanHeader."""
        
        self.BasePeakIntensity = None
        self.BasePeakPosition = None
        self.DataType = None
        self.HighPosition = None
        self.InstrumentName = None
        self.LowPosition = None
        self.SpectrumID = None
        self.SpectrumIdentifiers = []
        self.TotalIntensity = None
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        data = "#%s" % self.ScanNumber
        
        if self.MasterScanNumber is not None:
            data += "-#%s" % self.MasterScanNumber
        
        if self.RetentionTime is not None:
            
            rts = self.RetentionTime
            if isinstance(rts, float):
                rts = [rts]
            
            rts = ", ".join("%.3f" % rt for rt in rts if rt is not None)
            data += " RT:%s min" % rts
        
        if self.LowPosition is not None and self.HighPosition is not None:
            data += " [%.4f-%.4f]" % (self.LowPosition, self.HighPosition)
        
        return data
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    @property
    def FileID(self):
        """Gets FileID (if single value, otherwise None)."""
        
        values = set(i.FileID for i in self.SpectrumIdentifiers)
        return values.pop() if len(values) == 1 else None
    
    
    @property
    def ScanNumber(self):
        """Gets scan number (if single value, otherwise None)."""
        
        values = self.ScanNumbers
        return values[0] if len(values) == 1 else None
    
    
    @property
    def ScanNumbers(self):
        """Gets scan numbers."""
        
        return tuple(s.ScanNumber for s in self.SpectrumIdentifiers)
    
    
    @property
    def MasterScanNumber(self):
        """Gets master scan number (if single value, otherwise None)."""
        
        values = self.MasterScanNumbers
        return values[0] if len(values) == 1 else None
    
    
    @property
    def MasterScanNumbers(self):
        """Gets master scan numbers."""
        
        return tuple(s.MasterScanNumber for s in self.SpectrumIdentifiers)
    
    
    @property
    def RetentionTime(self):
        """Gets retention time (center if multiple values)."""
        
        values = self.RetentionTimes
        return 0.5*(min(values) + max(values)) if len(values) else None
    
    
    @property
    def RetentionTimes(self):
        """Gets retention times."""
        
        return tuple(s.RetentionTime for s in self.SpectrumIdentifiers)


class ScanIdentifier(object):
    """
    The pyeds.ScanIdentifier is used to hold information from mass spectrum
    identifier.
    """
    
    
    def __init__(self):
        """Initializes a new instance of ScanIdentifier."""
        
        self.FileID = None
        self.MasterScanNumber = None
        self.RetentionTime = None
        self.ScanNumber = None
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        data = "#%s" % self.ScanNumber
        
        if self.MasterScanNumber is not None:
            data += "-#%s" % self.MasterScanNumber
        
        if self.RetentionTime is not None:
            data += " RT:%.3f min" % self.RetentionTime
        
        if self.FileID is not None:
            data += " FileID:%s" % self.FileID
        
        return data
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())


class ScanEvent(object):
    """
    The pyeds.ScanEvent is used to hold information from scan event.
    """
    
    
    def __init__(self):
        """Initializes a new instance of ScanEvent."""
        
        self.ActivationEnergies = None
        self.ActivationTypes = None
        self.CompensationVoltage = None
        self.IonizationSource = None
        self.IsMultiplexed = None
        self.IsolationMass = None
        self.IsolationWidth = None
        self.IsolationOffset = None
        self.MassAnalyzer = None
        self.MSOrder = None
        self.Polarity = None
        self.ResolutionAtMass200 = None
        self.ScanRate = None
        self.ScanType = None
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        data = ""
        
        if self.MSOrder is not None:
            data += "%s" % self.MSOrder
        
        if self.Polarity == 'Positive':
            data += " (+)"
        elif self.Polarity == 'Negative':
            data += " (-)"
        
        if self.MassAnalyzer is not None:
            data += " %s" % self.MassAnalyzer
        
        if self.ActivationTypes is not None:
            data += " %s" % self.ActivationTypes
            
            if self.ActivationEnergies is not None:
                items = ("%.2f" % x for x in self.ActivationEnergies)
                data += ":"+",".join(items)
        
        if self.IsolationMass is not None:
            data += " P:%.4f" % self.IsolationMass
            
            if self.IsolationWidth is not None:
                data += " [%.4f-%.4f]" % (self.IsolationLowMass, self.IsolationHighMass)
        
        if self.CompensationVoltage is not None:
            data += " CV:%s" % self.CompensationVoltage
        
        return data
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    @property
    def IsolationLowMass(self):
        """Gets low isolation mass."""
        
        if self.IsolationMass is None or self.IsolationWidth is None:
            return None
        
        return self.IsolationMass - .5*self.IsolationWidth + (self.IsolationOffset or 0)
    
    
    @property
    def IsolationHighMass(self):
        """Gets high isolation mass."""
        
        if self.IsolationMass is None or self.IsolationWidth is None:
            return None
        
        return self.IsolationMass + .5*self.IsolationWidth + (self.IsolationOffset or 0)


class PrecursorInfo(object):
    """
    The pyeds.PrecursorInfo is used to hold information from precursor info.
    """
    
    
    def __init__(self):
        """Initializes a new instance of PrecursorInfo."""
        
        self.Header = None
        self.Event = None
        
        self.Charge = None
        self.Intensity = None
        self.InstrumentDeterminedCharge = None
        self.InstrumentDeterminedMonoisotopicMass = None
        self.IonInjectTime = None
        self.IsolationMass = None
        self.IsolationOffset = None
        self.IsolationWidth = None
        self.PercentIsolationInterference = None
        self.PrecursorMassOrigin = None
        self.Resolution = None
        self.SignalToNoise = None
        self.SinglyChargedMass = None
        self.SpectrumNumber = None
        
        self.IsotopeClusterPeakCentroids = []
        self.MonoisotopicPeakCentroids = []
        self.MeasuredMonoisotopicPeakCentroids = []
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        data = "P"
        
        if self.IsolationMass is not None:
            data += " %.4f" % self.IsolationMass
        
        if self.Charge is not None:
            data += " (%+d)" % self.Charge
        
        if self.IsolationWidth is not None and self.IsolationMass is not None:
            data += " [%.4f-%.4f]" % (self.IsolationLowMass, self.IsolationHighMass)
        
        return data
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    def __getattr__(self, name):
        """Tries to get unknown attribute from header or event."""
        
        if self.Header is not None and hasattr(self.Header, name):
            return getattr(self.Header, name)
        
        if self.Event is not None and hasattr(self.Event, name):
            return getattr(self.Event, name)
        
        raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))
    
    
    @property
    def IsolationLowMass(self):
        """Gets low isolation mass."""
        
        if self.IsolationMass is None or self.IsolationWidth is None:
            return None
        
        return self.IsolationMass - .5*self.IsolationWidth + (self.IsolationOffset or 0)
    
    
    @property
    def IsolationHighMass(self):
        """Gets high isolation mass."""
        
        if self.IsolationMass is None or self.IsolationWidth is None:
            return None
        
        return self.IsolationMass + .5*self.IsolationWidth + (self.IsolationOffset or 0)


class Centroid(object):
    """
    The pyeds.Centroid is used to hold information about a single mass centroid.
    
    Attributes:
        
        MZ: float
            Mass-to-charge ratio.
        
        Intensity: float
            Absolute intensity.
        
        SN: float or None
            Signal-to-noise ratio.
        
        Charge: int or None
            Instrument assigned charge.
        
        Resolution: int or None
            Profile peak resolution.
    """
    
    
    def __init__(self):
        """Initializes a new instance of Centroid."""
        
        self.MZ = None
        self.Intensity = None
        self.SN = None
        self.Charge = None
        self.Resolution = None
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        data = "MZ:%f Int:%f" % (self.MZ, self.Intensity)
        
        if self.SN is not None:
            data += " SN:%d" % self.SN
        
        if self.Charge is not None:
            data += " Z:%d" % self.Charge
        
        if self.Resolution is not None:
            data += " Res:%d" % self.Resolution
        
        return data
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
