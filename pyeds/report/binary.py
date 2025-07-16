#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import zlib
import zipfile
from io import BytesIO


class Binary(object):
    """
    The pyeds.Binary class is used to hold the actual binary data retrieved by
    pyeds.EDS reader. The actual value can be accessed via 'Value'
    property.
    
    Since most of the binary data are compressed, this class provides
    a convenient way to apply appropriate decompression and get the data in its
    native form via 'Unzip' method.
    
    Attributes:
        
        Value: buffer
            Raw data as stored in database.
    """
    
    
    def __init__(self, value):
        """Initializes a new instance of Binary."""
        
        self._value = value
    
    
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
    
    
    def Unzip(self):
        """
        Gets unzipped value.
        
        Returns:
            ?
                Decompressed value.
        """
        
        # use zipfile
        data = BytesIO(self._value)
        if zipfile.is_zipfile(data):
            with zipfile.ZipFile(data) as zf:
                name = zf.namelist()[0]
                return zf.read(name)
        
        # use zlib
        elif self._value:
            data = zlib.decompress(self._value, wbits=32+zlib.MAX_WBITS)
            if data:
                return data.decode("utf-8")
        
        return None
    
    
    @staticmethod
    def Zip(value):
        """
        Gets zipped version of given data using zlib.
        
        Args:
            value: ?
                Native value to zip.
        
        Returns:
            ?
                Compressed value.
        """
        
        # check value
        if value is None:
            return None
        
        # encode string
        if isinstance(value, str):
            value = value.encode('utf-8')
        
        # using compress
        return zlib.compress(value)
    
    
    @staticmethod
    def ZipFile(value, filename="cfile"):
        """
        Gets zipped version of given data using zipfile.
        
        Args:
            value: ?
                Native value to zip.
            
            filename: str
                Zipped file name.
        
        Returns:
            ?
                Compressed value.
        """
        
        # check value
        if value is None:
            return None
        
        # init buffer
        buff = BytesIO()
        
        # compress to file
        with zipfile.ZipFile(buff, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr(filename, value)
        
        # get value and close
        compressed = buff.getvalue()
        buff.close()
        
        return compressed
