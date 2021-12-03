#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
from ..report import Lockable


class PropertyValue(Lockable):
    """
    The pyeds.PropertyValue class is used to hold the actual value of a property
    retrieved by pyeds.EDS reader and stored within pyeds.EntityItem, as well as
    the full definition of the value type.
    
    The value itself (as 'Value') is right after the reading automatically
    converted into its final type by applying specified converters. The original
    value can be accessed vie 'RawValue' attribute if necessary. The full type
    definition can be accessed via 'Type' attribute.
    
    Attributes:
        
        Type: pyeds.PropertyColumn
            Property type definition.
        
        Value: ?
            Property value converted into its final type.
        
        RawValue: ?
            Original value as stored in the database.
    """
    
    
    def __init__(self, property_type, value):
        """
        Initializes a new instance of PropertyValue.
        
        Args:
            property_type: pyeds.PropertyColumn
                Value type definition.
            
            value: ?
                Raw value as stored in the database.
        """
        
        super().__init__()
        
        self._type = property_type
        self._raw_value = value
        self._value = self._convert_value(value)
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return "%s(%s)" % (self._type, self._value)
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    def __eq__(self, other):
        """Equal operator."""
        
        if self is other:
            return True
        
        if isinstance(other, PropertyValue):
            return self.RawValue == other.RawValue
        
        else:
            return self.Value == other
    
    
    def __ne__(self, other):
        """Not equal operator."""
        
        return not self.__eq__(other)
    
    
    @property
    def Type(self):
        """
        Gets property type definition.
        
        Returns:
            pyeds.PropertyColumn
                Type definition.
        """
        
        return self._type
    
    
    @property
    def Value(self):
        """
        Gets current value converted into its final type.
        
        Returns:
            ?
                Property value.
        """
        
        return self._value
    
    
    @property
    def RawValue(self):
        """
        Gets original value as stored in the database.
        
        Returns:
            ?
                Original value.
        """
        
        return self._raw_value
    
    
    def _convert_value(self, value):
        """Converts raw value to final type."""
        
        # convert value to custom data type (e.g. string, int, binary)
        if self._type.CustomDataType is not None:
            value = self._type.CustomDataType.Convert(value)
        
        # convert value to special value type (e.g. enum, ddmap)
        if self._type.SpecialValueType is not None:
            value = self._type.SpecialValueType.Convert(value)
        
        # apply specific converter (e.g. traces, spectra)
        if self._type.ValueTypeConverter is not None:
            value = self._type.ValueTypeConverter.Convert(value)
        
        return value
