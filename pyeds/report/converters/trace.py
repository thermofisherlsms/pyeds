#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import zlib
import struct
from .converter import register, ValueConverter


@register("2282755A-9FAE-4BB6-AA4D-CAE84E46303B")
class TraceConverter(ValueConverter):
    """
    The pyeds.TraceConverter is used to convert chromatogram trace data from
    original binary format into a collection of pyeds.TracePoint items.
    """
    
    
    def Convert(self, value):
        """
        Converts binary trace data.
        
        Args:
            value: pyeds.Binary
                Binary data as stored in result file.
        
        Returns:
            (pyeds.TracePoint,) or None
                Collection of parsed trace points.
        """
        
        # check value
        if not value:
            return None
        
        # parse data
        return TraceParser().parse(value.Value)


class TraceParser(object):
    """
    The pyeds.TraceParser is used to parse a chromatogram trace data from
    original binary format into a collection of pyeds.TracePoint items.
    """
    
    
    def parse(self, data):
        """
        Parses given binary trace data.
        
        Args:
            data: buffer
                Trace data.
        
        Returns:
            (pyeds.TracePoint,) or None
                Collection of parsed trace points.
        """
        
        # check data
        if not data:
            return None
        
        # convert data
        barray = bytearray(data)
        
        # check for old XML format
        if barray[0] == 0x50 and barray[1] == 0x4b:
            print("Old XML trace format is not supported!")
            return None
        
        # unzip data
        if barray[0] == 0x1f and barray[1] == 0x8b:
            barray = bytearray(zlib.decompress(data, 32 + zlib.MAX_WBITS))
        
        # get data
        if barray[0] == 0x0:
            barray = barray[1:]
        
        # get version
        version = int(barray[16])
        
        # get converted guid
        guid = barray[3::-1] + barray[5:3:-1] + barray[7:5:-1] + barray[8:16]
        guid = "".join(format(x, '02X') for x in guid)
        guid = "%s-%s-%s-%s-%s" % (guid[:8], guid[8:12], guid[12:16], guid[16:20], guid[20:])
        
        # get trace data
        barray = barray[17:]
        if not barray:
            return None
        
        # get number of points
        count = struct.unpack('<i', barray[0:4])[0]
        
        # init buffers
        spectra = [None]*count
        times = ()
        intensities = ()
        noise = [None]*count
        masses = [None]*count
        i = 4
        
        # get spectrum IDs
        if barray[i] > 0:
            form = '<' + 'i' * count
            size = struct.calcsize(form)
            spectra = struct.unpack(form, barray[i+1:i+1+size])
            i += size
        
        i += 1
        
        # get RTs in minutes
        if barray[i] > 0:
            form = '<' + 'f' * count
            size = struct.calcsize(form)
            times = struct.unpack(form, barray[i+1:i+1+size])
            i += size
        
        i += 1
        
        # get intensities
        if barray[i] > 0:
            form = '<' + 'f' * count
            size = struct.calcsize(form)
            intensities = struct.unpack(form, barray[i+1:i+1+size])
            i += size
        
        i += 1
        
        # get max noise
        if barray[i] > 0:
            form = '<' + 'f' * count
            size = struct.calcsize(form)
            noise = struct.unpack(form, barray[i+1:i+1+size])
            i += size
        
        i += 1
        
        # get mass
        if version > 1 and barray[i] > 0:
            form = '<' + 'f' * count
            size = struct.calcsize(form)
            masses = struct.unpack(form, barray[i+1:i+1+size])
        
        # make points
        points = []
        
        for i in range(count):
            
            point = TracePoint()
            
            point.RT = times[i] if times else 0.0
            point.Intensity = intensities[i] if intensities else 0.0
            point.Noise = noise[i] if noise else None
            point.Mass = masses[i] if masses else None
            point.SpectrumID = spectra[i] if spectra else None
            
            points.append(point)
        
        return tuple(points)


class TracePoint(object):
    """
    The pyeds.TracePoint is used to hold information about a single
    chromatogram trace point.
    """
    
    def __init__(self):
        """Initializes a new instance of TracePoint."""
        
        self.RT = None
        self.Intensity = None
        self.Noise = None
        self.Mass = None
        self.SpectrumID = None
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        data = "RT:%f Int:%f" % (self.RT, self.Intensity)
        
        if self.Noise is not None:
            data += " Noise:%d" % self.Noise
        
        if self.Mass is not None:
            data += " Mass:%f" % self.Mass
        
        if self.SpectrumID is not None:
            data += " SpectrumID:%d" % self.SpectrumID
        
        return data
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
