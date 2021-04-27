#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import zlib
import zipfile
from io import BytesIO


class Binary(object):
    """
    The pyeds.Binary class is used to hold the actual binary data retrieved by
    retrieved by pyeds.EDS reader. The actual value can be accessed via 'Value'
    property. Since most of the binary data are compressed, this class provides
    a convenient way to apply appropriate decompression and get the data in its
    native form via 'Unzipped' property.
    
    Attributes:
        
        Value: buffer
            Raw data as stored in database.
        
        Unzipped: ?
            Decompressed value.
    """
    
    
    def __init__(self, value):
        """Initializes a new instance of Binary."""
        
        self._value = value
        self._unzipped = None
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return "Binary Data"
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    @property
    def Value(self):
        """
        Gets raw value.
        
        Returns:
            buffer
                Raw data as stored in database.
        """
        
        return self._value
    
    
    @property
    def Unzipped(self):
        """
        Gets unzipped value.
        
        Returns:
            ?
                Decompressed value.
        """
        
        if self._unzipped is None:
            
            # use zipfile
            data = BytesIO(self._value)
            if zipfile.is_zipfile(data):
                
                with zipfile.ZipFile(data) as zf:
                    name = zf.namelist()[0]
                    self._unzipped = zf.read(name)
            
            # use zlib
            elif self._value:
                mol_string = zlib.decompress(self._value, wbits=32 + zlib.MAX_WBITS)
                if mol_string:
                    self._unzipped = mol_string.decode("utf-8") 
        
        return self._unzipped
