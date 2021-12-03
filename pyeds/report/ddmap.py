#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import struct
from .lockable import Lockable
from .binary import Binary

# define constants
_FORMAT = {'Int': "i?", 'Int64': "q?", 'Double': "d?", 'Boolean': "??"}
_TYPE = {'Int': int, 'Int64': int, 'Double': float, 'Boolean': bool}


class DataDistributionMap(Lockable):
    """
    The pyeds.DataDistributionMap class is used to hold all the information
    about an in-cell mini tables called data distribution maps. These are used
    to pack multiple values of the same data types e.g. areas from multiple
    files. Detailed information about specific box (column) can be accessed via
    'Boxes' attribute. In addition, a map can hold information about specific
    data levels, for which the details are accessible via 'Levels' attribute.
    
    If levels are defined, the 'GetLevel' method can be used to get appropriate
    level for given value.
    
    Attributes:
        
        ID: int
            Unique map ID.
        
        Name: str
            Name of the map.
        
        Description: str
            Description or the map.
        
        SemanticTerms: str
            Semantic description of the map.
        
        CustomDataType: pyeds.CustomDataType
            Definition of a basic type of the values stored in the boxes (e.g.
            string, int, binary). It is later used to convert raw value into a
            correct type.
        
        CustomDataTypeID: int
            Unique ID of the basic data type.
        
        Boxes: (pyeds.DataDistributionBox,)
            Sorted available boxes.
        
        Levels: (pyeds.DataDistributionLevel,)
            Sorted available levels.
    """
    
    
    def __init__(self):
        """Initializes a new instance of DataDistributionMap."""
        
        super().__init__()
        
        self.ID = None
        self.Name = None
        self.Description = None
        self.SingularCategoryName = None
        self.PluralCategoryName = None
        self.LevelCategoryName = None
        self.SuppressedFilters = None
        self.SemanticTerms = None
        self.CustomDataTypeID = None
        self.CustomDataType = None
        self.MinimumValue = None
        self.MaximumValue = None
        
        self._boxes = tuple()
        self._levels = tuple()
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return self.Name
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    def __len__(self):
        """Gets number of available boxes."""
        
        return len(self._boxes)
    
    
    @property
    def Boxes(self):
        """
        Gets defined boxes in correct order.
        
        Returns:
            (pyeds.DataDistributionBox,)
                Defined boxes.
        """
        
        return self._boxes
    
    
    @property
    def Levels(self):
        """
        Gets defined levels in correct order.
        
        Returns:
            (pyeds.DataDistributionLevel,)
                Defined levels.
        """
        
        return self._levels
    
    
    def GetBox(self, index):
        """
        Gets box definition at specified index.
        
        Args:
            index: int
                Box index.
        
        Returns:
            pyeds.DataDistributionBox
                Box definition at specified index.
        """
        
        return self.Boxes[index]
    
    
    def GetBoxes(self, semantic_terms):
        """
        Gets all boxes with corresponding semantic terms.
        
        Args:
            semantic terms: str
                Semantic terms.
        
        Returns:
            (pyeds.DataDistributionBox,)
                Boxes corresponding to given semantic terms.
        """
        
        boxes = []
        for box in self._boxes:
            if box.SemanticTerms == semantic_terms:
                boxes.append(box)
        
        return tuple(boxes)
    
    
    def GetLevel(self, value):
        """
        Gets level corresponding to given value.
        
        Args:
            value: int, float or None
                Value for which to get the level.
        
        Returns:
            pyeds.DataDistributionLevel or None
                Corresponding level or None if no levels available.
        """
        
        # check value
        if value is None:
            return None
        
        # check levels
        if not self._levels:
            return None
        
        # get level
        for level in self._levels:
            if value < level.Threshold:
                return level
        
        # use last one
        return self._levels[-1]
    
    
    def SetBoxes(self, boxes):
        """
        Sets current boxes.
        
        This method is not intended to be used by user. It is used automatically
        by the library itself.
        
        Args:
            boxes: (pyeds.DataDistributionBox,)
                Boxes to be added.
        """
        
        self._boxes = tuple(sorted(boxes, key=lambda x: x.Position))
    
    
    def SetLevels(self, levels):
        """
        Sets current levels.
        
        This method is not intended to be used by user. It is used automatically
        by the library itself.
        
        Args:
            levels: (pyeds.DataDistributionLevel,)
                Levels to be added.
        """
        
        self._levels = tuple(sorted(levels, key=lambda x: x.Position))
    
    
    def Convert(self, value):
        """
        Converts original database value to data distribution value.
        
        This method is not intended to be used by user. It is used automatically
        by the library itself.
        
        Args:
            value: pyeds.Binary or None
                Original database value to be converted.
        
        Returns:
            pyeds.DataDistributionValue or None
                Parsed data distribution value.
        """
        
        # check value
        if value is None:
            return None
        
        # get size and format
        size = len(self.Boxes)
        f = _FORMAT[self.CustomDataType.Name]
        
        # unpack data
        data = struct.unpack_from("<"+f*size, value.Value)
        values = [data[2*i] for i in range(size)]
        flags = [data[2*i+1] for i in range(size)]
        
        # clear unset values
        for i, flag in enumerate(flags):
            if flag is False:
                values[i] = None
        
        # create value
        val = DataDistributionValue(self, values)
        val.Lock()
        
        return val
    
    
    def Revert(self, value):
        """
        Reverts data distribution value back to binary value.
        
        This method is not intended to be used by user. It is used automatically
        by the library itself.
        
        Args:
            value: pyeds.DataDistributionValue or None
                Data distribution value.
        
        Returns:
            pyeds.Binary or None
                Value converted into original database type.
        """
        
        # check value
        if value is None:
            return None
        
        # check type
        if not isinstance(value, DataDistributionValue):
            message = "Value must be of type pyeds.DataDistributionValue! -> %s" % (type(value))
            raise TypeError(message)
        
        # get size and format
        size = len(self.Boxes)
        f = _FORMAT[self.CustomDataType.Name]
        
        # prepare data
        data = [0] * (2*size)
        for i, val in enumerate(value.Values):
            if val is None or val is False:
                data[2*i] = 0
                data[2*i+1] = False
            else:
                data[2*i] = val
                data[2*i+1] = True
        
        # pack data
        buffer = struct.pack("<"+f*size, *data)
        
        # create binary
        binary = Binary(buffer)
        
        return binary
    
    
    def Create(self, value):
        """
        Creates data distribution value from naive data:
        
        This method is not intended to be used by user. It is used automatically
        by the library itself.
        
        Args:
            value: pyeds.DataDistributionValue, tuple or list
                Naive value to be converted.
        
        Returns:
            pyeds.DataDistributionValue or None
                Parsed data distribution value.
        """
        
        # check None
        if value is None:
            return True
        
        # get values from ddmap
        if isinstance(value, DataDistributionValue):
            value = value.Values
        
        # check type
        if not isinstance(value, (list, tuple)):
            message = "Value must be of type pyeds.DataDistributionValue, tuple or list! -> %s" % (type(value),)
            raise TypeError(message)
        
        # check size
        if len(value) != len(self._boxes):
            message = "Value has incorrect length!"
            raise ValueError(message)
        
        # check values
        t = _TYPE[self.CustomDataType.Name]
        for item in value:
            if item is not None and not isinstance(item, (t,)):
                message = "Values must be of type %s! -> %s" % (t, type(item))
                raise TypeError(message)
        
        # create value
        val = DataDistributionValue(self, value)
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
            pyeds.DataDistributionMap
                Data distribution map instance.
        """
        
        distribution_map = DataDistributionMap()
        
        distribution_map.ID = data['ID']
        distribution_map.Name = data['Name']
        distribution_map.SingularCategoryName = data['SingularCategoryName']
        distribution_map.PluralCategoryName = data['PluralCategoryName']
        distribution_map.LevelCategoryName = data['LevelCategoryName']
        distribution_map.SuppressedFilters = data['SuppressedFilters']
        distribution_map.Description = data['Description']
        distribution_map.SemanticTerms = data['SemanticTerms']
        distribution_map.CustomDataTypeID = data['CustomDataType']
        distribution_map.MinimumValue = data['MinimumValue']
        distribution_map.MaximumValue = data['MaximumValue']
        
        return distribution_map


class DataDistributionBox(Lockable):
    """
    The pyeds.DataDistributionBox class is used to hold all the information
    about individual boxes of a pyeds.DataDistributionMap.
    
    Attributes:
        
        ID: int
            Unique box ID.
        
        MapID: int
            Unique ID of the parent map.
        
        Name: str
            Display-friendly name of the box. This is typically used as the
            column header within desktop apps.
        
        Description: str or None
            Basic box descriptions. This is typically used as the column
            header tooltip within desktop apps.
        
        SemanticTerms: str or None
            Semantic description of the box.
        
        Position: int
            One-based position of the box.
        
        Index: int
            Zero-based position of the box.
        
        IsFirstInGroup: int
            Specifies if the box is first of its kind and defines a start of a
            group. This is typically used to visually separate groups.
        
        Color: int or None
            Attached color. To convert stored value into RGBA tuple use the
            'pyeds.review.rgba_from_argb_int' function.
        
        ExtendedData: {str:str}
            Extended data values.
    """
    
    
    def __init__(self):
        """Initializes a new instance of DataDistributionBox."""
        
        super().__init__()
        
        self.ID = None
        self.MapID = None
        self.Name = None
        self.Position = None
        self.Description = None
        self.SemanticTerms = None
        self.Color = None
        self.IsFirstInGroup = None
        self.ExtendedData = {}
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return self.Name
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    @property
    def Index(self):
        """
        Gets box index.
        
        Returns:
            int
                Zero-based box index.
        """
        
        return self.Position - 1
    
    
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
            pyeds.DataDistributionBox
                Data distribution box instance.
        """
        
        distribution_box = DataDistributionBox()
        
        distribution_box.ID = data['BoxID']
        distribution_box.MapID = data['DataDistributionMapID']
        distribution_box.Name = data['Name']
        distribution_box.Position = data['Position']
        distribution_box.Description = data['Description']
        distribution_box.SemanticTerms = data['SemanticTerms']
        distribution_box.Color = data['Color']
        distribution_box.IsFirstInGroup = data['IsFirstInGroup']
        
        return distribution_box


class DataDistributionLevel(Lockable):
    """
    The pyeds.DataDistributionLevel class is used to hold all the information
    about individual levels of a pyeds.DataDistributionMap.
    
    Attributes:
        
        ID: int
            Unique level ID.
        
        MapID: int
            Unique ID of the parent map.
        
        Name: str
            Display-friendly name of the level.
        
        Description: str or None
            Basic level descriptions.
        
        SemanticTerms: str or None
            Semantic description of the level.
        
        Position: int
            One-based position of the level.
        
        Threshold: int or float
            Threshold value of the level.
        
        Color: int or None
            Attached color. To convert stored value into RGBA tuple use the
            'pyeds.review.rgba_from_argb_int' function.
    """
    
    
    def __init__(self):
        """Initializes a new instance of DataDistributionLevel."""
        
        super().__init__()
        
        self.ID = None
        self.MapID = None
        self.Name = None
        self.Position = None
        self.Description = None
        self.SemanticTerms = None
        self.Color = None
        self.Threshold = None
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return self.Name
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
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
            pyeds.DataDistributionLevel
                Data distribution level instance.
        """
        
        distribution_level = DataDistributionLevel()
        
        distribution_level.ID = data['LevelID']
        distribution_level.MapID = data['DataDistributionMapID']
        distribution_level.Name = data['Name']
        distribution_level.Position = data['Position']
        distribution_level.Description = data['Description']
        distribution_level.SemanticTerms = data['SemanticTerms']
        distribution_level.Color = data['Color']
        distribution_level.Threshold = data['Threshold']
        
        return distribution_level


class DataDistributionValue(Lockable):
    """
    The pyeds.DataDistributionValue class is used to hold actual values of an
    in-cell mini table. Several utility functions are available to easily get
    a box or level info.
    
    Attributes:
        
        Type: pyeds.DataDistributionMap
            Full definition of the distribution map.
        
        Values: (?,)
            Actual map values.
    """
    
    
    def __init__(self, ddmap_type, values):
        """
        Initializes a new instance of DataDistributionValue.
        
        Args:
            ddmap_type: pyeds.DataDistributionMap
                Map definition.
            
            values: (?,)
                Actual values.
        """
        
        super().__init__()
        
        self._type = ddmap_type
        self._values = tuple(values)
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return str(self._values)
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    def __getitem__(self, index):
        """
        Gets value at specified index.
        
        Args:
            index: int
                Value index.
        
        Returns:
            ?
                Value at specified index.
        """
        
        return self.GetValue(index)
    
    
    def __len__(self):
        """Gets number of available boxes."""
        
        return len(self._values)
    
    
    def __iter__(self):
        """Gets values iterator."""
        
        return self._values.__iter__()
    
    
    @property
    def Type(self):
        """
        Gets map definition.
        
        Returns:
            pyeds.DataDistributionMap
                Map definition.
        """
        
        return self._type
    
    
    @property
    def Values(self):
        """
        Gets current values.
        
        Returns:
            (?,)
                Actual map values.
        """
        
        return self._values
    
    
    def GetValue(self, index):
        """
        Gets value at specified index.
        
        Args:
            index: int
                Value index.
        
        Returns:
            ?
                Value at specified index.
        """
        
        return self._values[index]
    
    
    def GetBox(self, index):
        """
        Gets box definition at specified index.
        
        Args:
            index: int
                Box index.
        
        Returns:
            pyeds.DataDistributionBox
                Box definition at specified index.
        """
        
        return self._type.GetBox(index)
    
    
    def GetLevel(self, index):
        """
        Gets level of the value at specified index.
        
        Args:
            index: int
                Value index.
        
        Returns:
            pyeds.DataDistributionLevel or None
                Corresponding level or None if no levels available.
        """
        
        value = self.GetValue(index)
        return self._type.GetLevel(value)
