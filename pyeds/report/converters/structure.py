#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import re
from .common import register, ZippedStringConverter

# define constants
MOL_PATTERN = re.compile("(?:^(?:(?:\d| ){3}){11}.{0,6}){1}[\s\S]*", re.M)


@register("BC434B48-7273-488B-8590-BB32AEB9712C")
class MolStructureConverter(ZippedStringConverter):
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
        
        # unzip MOL string
        mol = value.Unzipped
        if not mol:
            return None
        
        # filter MOL string
        return "\n\n\n%s" % MOL_PATTERN.search(mol).group(0)
