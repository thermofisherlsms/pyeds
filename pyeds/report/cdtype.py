#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
from .lockable import Lockable
from .binary import Binary


class CustomDataType(Lockable):
    """
    The pyeds.CustomDataType class is used to define a basic type of the stored
    values like string, int, binary, object etc. It is mainly used to convert
    the raw database value into a correct basic type. Note, that further
    conversion of the value may happen later by specific value converters to
    get reach the final value/type.
    
    Attributes:
        
        ID: int
            Unique ID of the type.
        
        Name: str
            Type name.
        
        SystemType: str
            System type name.
    """
    
    
    def __init__(self):
        """Initializes a new instance of CustomDataType."""
        
        super().__init__()
        
        self.ID = None
        self.Name = None
        self.SystemType = None
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return self.Name
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    def Convert(self, value):
        """
        Converts original database value to current type.
        
        This method is not intended to be used by user. It is used automatically
        by the library itself.
        
        Args:
            value: ?
                Native value to be converted.
            
        Returns:
            ?
                Given value converted into current type.
        """
        
        if value is None:
            return None
        
        if self.Name == 'Int':
            return int(value)
        
        if self.Name == 'Int64':
            return int(value)
        
        if self.Name == 'Double':
            return float(value)
        
        if self.Name == 'String':
            return str(value)
        
        if self.Name == 'Boolean':
            return bool(value)
        
        if self.Name == 'Binary':
            return Binary(value)
        
        if self.Name == 'Object':
            return value
        
        message = "'%s' is not known custom data type!" % self.Name
        raise TypeError(message)
    
    
    @staticmethod
    def FromDBData(data):
        """
        Creates instance from database data.
        
        This method is not intended to be used by user. It is used automatically
        by the library itself.
        
        Args:
            data: dict
                Database data.
        
        Returns:
            pyeds.CustomDataType
                Custom data type instance.
        """
        
        custom_data_type = CustomDataType()
        
        custom_data_type.ID = data['Value']
        custom_data_type.Name = data['Name']
        custom_data_type.SystemType = data['SystemType']
        
        return custom_data_type
