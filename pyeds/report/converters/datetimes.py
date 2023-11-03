#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
from datetime import datetime
from .converter import register, ValueConverter


@register("1BDE1686-0CF2-4921-832B-B1EEFF4EB779")
class DateTime(ValueConverter):
    """
    The pyeds.DateTime is used to convert datetime string with format
     %m/%d/%Y %H:%M:%S into datetime object.
    """
    
    
    def Convert(self, value):
        """
        Converts string to datetime.
        
        Args:
            value: str
                String data as stored in result file.
        
        Returns:
            datetime or None
                Parsed datetime.
        """
        
        # check value
        if not value:
            return None
        
        return datetime.strptime(value, '%m/%d/%Y %H:%M:%S')
