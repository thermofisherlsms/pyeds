#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
from .lockable import Lockable


class EnumDataType(Lockable):
    """
    The pyeds.EnumDataType class is used to hold all the information about a
    specific enum type. It provide access to details of all defined elements as
    well as conversion function between int and the element itself.
    
    Attributes:
    
        ID: int
            Unique ID of the enum.
        
        TypeName: str
            Magellan type name.
        
        IsFlagsEnum: bool
            Specifies whether the enum is flags enum.
        
        CVReference: str
            Controlled vocabulary reference.
        
        CVTermId: str
            Controlled vocabulary term ID.
        
        CVTermName: str
            Controlled vocabulary term name.
        
        CVTermDefinition: str
            Controlled vocabulary term definition.
        
        Elements: (pyeds.EnumElement,)
            Defined elements.
    """
    
    
    def __init__(self):
        """Initializes a new instance of EnumDataType."""
        
        super().__init__()
        
        self.ID = None
        self.TypeName = None
        self.IsFlagsEnum = None
        
        self.CVReference = None
        self.CVTermId = None
        self.CVTermName = None
        self.CVTermDefinition = None
        
        self._elements = {}  # for .Value
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        names = self.TypeName.split(",")
        names = names[0].split(".")
        
        return names[-1]
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    @property
    def Elements(self):
        """
        Gets all available elements of current enum type.
        
        Returns:
            (pyeds.EnumElement,)
                Available elements.
        """
        
        return tuple(self._elements.values())
    
    
    def AddElement(self, element):
        """
        Adds enum element to current enum type.
        
        This method is not intended to be used by user. It is used automatically
        by the library itself.
        
        Args:
            element: pyeds.EnumElement
                Element to be added.
        """
        
        self._elements[element.Value] = element
    
    
    def GetElement(self, value):
        """
        Gets enum element for given value.
        
        Args:
            value: int
                Enum value for which to get the element definition.
        
        Returns:
            pyeds.EnumElement
                Enum element definition.
        """
        
        if value not in self._elements:
            message = "'%s' doesn't contain value '%s'!" % (self.TypeName, value)
            raise KeyError(message)
        
        return self._elements[value]
    
    
    def GetElements(self, value):
        """
        Gets enum elements for given value. This is mainly used for flags enums
        to get all elements included in given value.
        
        Args:
            value: int
                Enum value for which to get the element definitions.
        
        Returns:
            (pyeds.EnumElement,)
                Included enum element definitions.
        """
        
        # init elements
        elements = []
        
        # direct match
        if value in self._elements:
            elements.append(self._elements[value])
        
        # check zero
        elif value == 0:
            pass
        
        # check flags enum
        elif not self.IsFlagsEnum:
            pass
        
        # get elements
        else:
            for el in self._elements:
                if el != 0 and (value & el) == el:
                    elements.append(self._elements[el])
        
        return tuple(elements)
    
    
    def Convert(self, value):
        """
        Parses raw DB value into enum element.
        
        Args:
            value: int
                Raw value as stored in DB.
        
        Returns:
            pyeds.EnumValue
                Parsed value.
        """
        
        # check value
        if value is None:
            return None
        
        # create value
        val = EnumValue()
        val.Type = self
        val.Value = int(value)
        val.Lock()
        
        return val
    
    
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
            pyeds.EnumDataType
                Enum data type instance.
        """
        
        enum_data_type = EnumDataType()
        
        enum_data_type.ID = data['EnumID']
        enum_data_type.TypeName = data['EnumType']
        enum_data_type.IsFlagsEnum = data['IsFlagsEnum']
        
        enum_data_type.CVReference = data['CVReference']
        enum_data_type.CVTermId = data['CVTermId']
        enum_data_type.CVTermName = data['CVTermName']
        enum_data_type.CVTermDefinition = data['CVTermDefinition']
        
        enum_data_type.Name = data['EnumType'].split(',')[0].split('.')[-1]
        
        return enum_data_type


class EnumElement(Lockable):
    """
    The pyeds.EnumElement class is used to hold all the information about a
    particular enum element.
    
    Attributes:
        
        EnumID: int
            Unique ID of parent enum.
        
        Value: int
            Actual value.
        
        DisplayName: str
            Human-readable display name.
        
        Abbreviation:
            Human-readable abbreviation.
        
        CVReference:
            Controlled vocabulary term reference.
            
        CVTermId:
            Controlled vocabulary term ID.
        
        CVTermName:
            Controlled vocabulary term name.
        
        CVTermDefinition:
            Controlled vocabulary term definition.
    """
    
    
    def __init__(self):
        """Initializes a new instance of EnumElement."""
        
        super().__init__()
        
        self.EnumID = None
        self.Value = None
        self.DisplayName = None
        self.Abbreviation = None
        
        self.CVReference = None
        self.CVTermId = None
        self.CVTermName = None
        self.CVTermDefinition = None
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return self.DisplayName
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    def __eq__(self, other):
        """Equal operator."""
        
        if self is other:
            return True
        
        if isinstance(other, int):
            return self.Value == other
        
        if not isinstance(other, EnumElement):
            return False
        
        return (self.Value == other.Value
            and self.EnumID == other.EnumID)
    
    
    def __ne__(self, other):
        """Not equal operator."""
        
        return not self.__eq__(other)
    
    
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
            pyeds.EnumElement
                Enum element instance.
        """
        
        enum_element = EnumElement()
        
        enum_element.EnumID = data['EnumID']
        enum_element.Value = data['Value']
        enum_element.DisplayName = data['DisplayName']
        enum_element.Abbreviation = data['Abbreviation']
        
        enum_element.CVReference = data['CVReference']
        enum_element.CVTermId = data['CVTermId']
        enum_element.CVTermName = data['CVTermName']
        enum_element.CVTermDefinition = data['CVTermDefinition']
        
        return enum_element


class EnumValue(Lockable):
    """
    The pyeds.EnumValue class is used to hold actual value of enum property.
    
    Attributes:
        
        Type: pyeds.EnumDataType
            Full definition of the enum.
        
        Value: int
            Actual value.
        
        IsFlagsEnum: bool
            Specifies whether the enum is flags enum.
        
        Elements: (pyeds.EnumElement,)
            Parsed value.
        
        DisplayName: str
            Human-readable display name.
    """
    
    
    def __init__(self):
        """Initializes a new instance of EnumValue."""
        
        super().__init__()
        
        self.Type = None
        self.Value = None
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return self.DisplayName
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    def __eq__(self, other):
        """Equal operator."""
        
        if self is other:
            return True
        
        if isinstance(other, int):
            return self.Value == other
        
        if isinstance(other, EnumElement):
            return self.Value == other.Value
        
        if not isinstance(other, EnumValue):
            return False
        
        return self.Value == other.Value
    
    
    def __ne__(self, other):
        """Not equal operator."""
        
        return not self.__eq__(other)
    
    
    def __contains__(self, value):
        """Checks if current value equals or contains (for flags) given value."""
        
        return self.Contains(value)
    
    
    @property
    def IsFlagsEnum(self):
        """Checks whether this value is flags enum."""
        
        return self.Type.IsFlagsEnum
    
    
    @property
    def Elements(self):
        """
        Gets current value as pyeds.EnumElements.
        
        Returns:
            (pyeds.EnumElement,)
                Current elements.
        """
        
        return self.Type.GetElements(self.Value)
    
    
    @property
    def DisplayName(self):
        """Gets current value display name."""
        
        elements = [e.DisplayName or str(e) for e in self.Elements]
        return "|".join(elements)
    
    
    def Contains(self, value):
        """
        Checks whether current value equals or contains (for flags) given value.
        
        Args:
            value: int, pyeds.EnumValue or pyeds.EnumElement
                Value to check.
        
        Returns:
            bool
                Returns True if current value equals or contains (for flags)
                given value.
        """
        
        # compare directly
        if self == value:
            return True
        
        # check flags
        if not self.IsFlagsEnum:
            return False
        
        # get int value
        if isinstance(value, (EnumValue, EnumElement)):
            value = value.Value
        
        # check zeros
        if self.Value == 0 or value == 0:
            return False
        
        # compare flags
        return (self.Value & value) == value
