#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import struct
from .common import register, ValueConverter


@register("38448540-6FA7-43CE-9B83-48383DDB282D")
class DoubleArrayConverter(ValueConverter):
    """
    The pyeds.DoubleArrayConverter is used to convert binary arrays of double
    into (float,).
    """
    
    
    def Convert(self, value):
        """
        Converts binary double array.
        
        Args:
            value: pyeds.Binary
                Binary data as stored in result file.
        
        Returns:
            (float,) or None
                Parsed array.
        """
        
        # check value
        if not value:
            return None
        
        # convert data
        barray = bytearray(value.Value)
        
        # get number of points
        count = struct.unpack('<i', barray[0:4])[0]
        
        # get data
        offset = 4
        form = '<' + 'd' * count
        size = struct.calcsize(form)
        data = struct.unpack(form, barray[offset:offset+size])
        
        return data


@register("B8336E98-B9AF-4213-BF96-91D14FE44E99")
class IntArrayConverter(ValueConverter):
    """
    The pyeds.IntArrayConverter is used to convert binary arrays of double
    into (int,).
    """
    
    
    def Convert(self, value):
        """
        Converts binary integer array.
        
        Args:
            value: pyeds.Binary
                Binary data as stored in result file.
        
        Returns:
            (int,) or None
                Parsed array.
        """
        
        # check value
        if not value:
            return None
        
        # convert data
        barray = bytearray(value.Value)
        
        # get number of points
        count = struct.unpack('<i', barray[0:4])[0]
        
        # get data
        offset = 4
        form = '<' + 'i' * count
        size = struct.calcsize(form)
        data = struct.unpack(form, barray[offset:offset+size])
        
        return data
