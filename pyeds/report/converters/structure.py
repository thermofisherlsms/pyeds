#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import re
from .converter import register, ValueConverter
from ..binary import Binary

# define constants
MOL_PATTERN = re.compile("(?:^(?:(?:\d| ){3}){11}.{0,6}){1}[\s\S]*", re.M)


@register("BC434B48-7273-488B-8590-BB32AEB9712C")
class MolStructureConverter(ValueConverter):
    """
    The pyeds.MolStructureConverter class is used to convert binary data of
    structure into a MOL string.
    """
    
    
    def Convert(self, value):
        """
        Converts zipped binary data into MOL string.
        
        Args:
            value: pyeds.Binary
                Binary data as stored in result file.
        
        Returns:
            str or None
                MOL string.
        """
        
        # check value
        if not value:
            return None
        
        # check type
        if not isinstance(value, Binary):
            message = "Value must be of type pyeds.Binary! -> %s" % (type(value))
            raise TypeError(message)
        
        # unzip MOL string
        mol = value.Unzip()
        if not mol:
            return None
        
        # filter MOL string
        return "\n\n\n%s" % MOL_PATTERN.search(mol).group(0)
    
    
    def Revert(self, value):
        """
        Reverts MOL string back to Binary.
        
        Args:
            value: str
                MOL string.
        
        Returns:
            pyeds.Binary
                MOL string compressed into Binary.
        """
        
        # check value
        if not value:
            return None
        
        # check type
        if not isinstance(value, str):
            message = "Value must be of type str! -> %s" % (type(value))
            raise TypeError(message)
        
        # compress MOL string
        compressed = Binary.Zip(value)
        
        # create binary
        return Binary(compressed)
