#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
from .undefined import UNDEF
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
        self._value = UNDEF
        self._dirty = False
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return "%s(%s)" % (self._type, self.Value)
    
    
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
        
        # convert value if needed
        if self._value is UNDEF:
            self._value = self._convert_value(self.RawValue)
        
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
    
    
    @property
    def IsDirty(self):
        """
        Gets property dirty flag.
        
        Returns:
            bool:
                Current flag state.
        """
        
        return self._dirty
    
    
    @property
    def IsEditable(self):
        """
        Gets value indicating whether property is allowed to be changed.
        
        Returns:
            bool:
                Editable state.
        """
        
        return bool(self._type.AllowEdit)
    
    
    def SetValue(self, value):
        """
        Sets given value to property.
        
        Note that the property must be unlocked first.
        
        Args:
            value: ?
                Value to set.
        """
        
        # convert naive value
        value = self._create_value(value)
        
        # skip if same
        if value == self.Value:
            return
        
        # convert to raw value
        raw_value = self._revert_value(value)
        
        # check null
        if raw_value is None and not self._type.Nullable:
            message = "'%s' is not nullable!" % (self._type.ColumnName,)
            raise ValueError(message)
        
        # set values
        self._value = value
        self._raw_value = raw_value
        
        # mark as dirty
        self._dirty = True
    
    
    def Dirty(self, value):
        """
        Gets or sets property dirty flag.
        
        Args:
            value: bool
                Flag value is set.
        """
        
        # unlock if needed
        locked = self.Locked()
        if locked:
            self.Unlock()
        
        # set value
        self._dirty = bool(value)
        
        # lock if needed
        if locked:
            self.Lock()
    
    
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
    
    
    def _revert_value(self, value):
        """Reverts final value to raw type."""
        
        # apply specific converter (e.g. traces, spectra)
        if self._type.ValueTypeConverter is not None:
            value = self._type.ValueTypeConverter.Revert(value)
        
        # convert value from special value type (e.g. enum, ddmap)
        if self._type.SpecialValueType is not None:
            value = self._type.SpecialValueType.Revert(value)
        
        # convert value from custom data type (e.g. string, int, binary)
        if self._type.CustomDataType is not None:
            value = self._type.CustomDataType.Revert(value)
        
        return value
    
    
    def _create_value(self, value):
        """Creates final value from naive data."""
        
        # apply specific converter (e.g. traces, spectra)
        if self._type.ValueTypeConverter is not None:
            return self._type.ValueTypeConverter.Create(value)
        
        # convert value to special value type (e.g. enum, ddmap)
        if self._type.SpecialValueType is not None:
            return self._type.SpecialValueType.Create(value)
        
        # convert value to custom data type (e.g. string, int, binary)
        if self._type.CustomDataType is not None:
            return self._type.CustomDataType.Create(value)
        
        return value
