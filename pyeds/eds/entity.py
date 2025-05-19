#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
from ..report import Lockable, PropertyColumn
from .prop import PropertyValue


class EntityItem(Lockable):
    """
    The pyeds.EntityItem class is used to hold the actual data of a single item
    retrieved by pyeds.EDS reader. Each property value can be accessed directly
    using its name (e.g. item.Area or item.MolecularWeight) or via the
    'GetValue' method. The property itself can be accessed via 'GetProperty'
    method. Connection properties are accessible exactly the same way. Beside
    actual data, each item also stores the full definition of the type (as
    'Type') and used connection to its parent data type (as 'Connection').
    
    Attributes:
        
        Type: pyeds.DataType
            Entity type definition.
        
        Connection: pyeds.DataTypeConnection or None
            Definition of the connection to used parent item.
        
        Properties: (str,)
            Available properties names.
        
        Children: (pyeds.EntityItem,)
            Child items retrieved by hierarchical reading.
    """
    
    
    def __init__(self, data_type, connection=None):
        """
        Initializes a new instance of EntityItem.
        
        Args:
            data_type: pyeds.DataType
                Entity type definition.
            
            connection: pyeds.DataTypeConnection or None
                Connection type definition to used parent data type.
        """
        
        super().__init__()
        
        self._type = data_type
        self._connection = connection
        self._properties = []
        self._names = {}
        self._children = []
        self._ids = ()
    
    
    def __getattr__(self, attr):
        """
        Gets requested property value.
        
        Args:
            attr: str
                Property name.
        
        Returns:
            ?
                Requested property value.
        """
        
        if attr.startswith('_'):
            super().__getattribute__(attr)
        
        return self.GetValue(attr, silent=False)
    
    
    def __getitem__(self, item):
        """
        Gets requested property value.
        
        Args:
            item: str
                Property name.
        
        Returns:
            ?
                Requested property value.
        """
        
        return self.GetValue(item, silent=False)
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        names = [p.Type.ColumnName for p in self._properties]
        return "%s (%s)" % (self._type.Name, ", ".join(names))
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    @property
    def Type(self):
        """
        Gets entity data type.
        
        Returns:
            pyeds.DataType
                Entity type definition.
        """
        
        return self._type
    
    
    @property
    def Connection(self):
        """
        Gets connection data type to used parent.
        
        Returns:
            pyeds.DataTypeConnection or None
                Connection definition.
        """
        
        return self._connection
    
    
    @property
    def Properties(self):
        """
        Gets all retrieved properties, including connection properties.
        
        Returns:
            (pyeds.PropertyValue,)
                All defined properties.
        """
        
        return tuple(sorted(self._properties, key=lambda p: p.Type.ColumnName))
    
    
    @property
    def Children(self):
        """
        Gets child entity items attached by hierarchical reading.
        
        Returns:
            (pyeds.EntityItem,)
                Child items.
        """
        
        return tuple(self._children)
    
    
    @property
    def IDs(self):
        """
        Gets item unique ID values.
        
        Returns:
            (int,)
                Item IDs.
        """
        
        return self._ids
    
    
    def GetValue(self, prop_name, default=None, silent=True):
        """
        Gets requested property value by its name.
        
        Args:
            prop_name: str
                Property name.
            
            default: any
                Default value to return if property does not exist.
            
            silent: bool
                If set to True and property does not exist, default value is
                returned.
        
        Returns:
            ?
                Requested property value.
        """
        
        # get property
        if prop_name in self._names:
            return self._properties[self._names[prop_name]].Value
        
        # return default
        if silent:
            return default
        
        # not available
        message = "'%s' doesn't contain property '%s'!" % (self._type.Name, prop_name)
        raise KeyError(message)
    
    
    def GetProperty(self, prop_name):
        """
        Gets requested property by its name.
        
        Args:
            prop_name: str
                Property name.
        
        Returns:
            pyeds.PropertyValue
                Requested property.
        """
        
        # get property
        if prop_name in self._names:
            return self._properties[self._names[prop_name]]
        
        # not available
        message = "'%s' doesn't contain property '%s'!" % (self._type.Name, prop_name)
        raise KeyError(message)
    
    
    def GetProperties(self, data_purpose=None):
        """
        Gets all properties with corresponding data purpose. If 'data_purpose'
        is set to None, all properties are returned.
        
        Args:
            data_purpose: str or None
                Data purpose.
        
        Returns:
            (pyeds.PropertyValue,)
                Properties corresponding to given data purpose.
        """
        
        # return all
        if data_purpose is None:
            return tuple(self._properties)
        
        # get matching data purpose
        props = []
        for prop in self._properties:
            if prop.Type.DataPurpose == data_purpose:
                props.append(prop)
        
        return tuple(props)
    
    
    def GetFlatChildren(self, level=1):
        """Gets child entity items of specified level."""
        
        # yield current children
        if level == 1:
            for child in self.Children:
                yield child
            return
        
        # yield deeper children
        for child in self.Children:
            for item in child.GetFlatChildren(level-1):
                yield item
    
    
    def SetValue(self, prop_name, value):
        """
        Sets given value to specified property.
        
        Args:
            prop_name: str
                Property name.
            
            value: ?
                Value to set.
        """
        
        # get property
        prop = self.GetProperty(prop_name)
        
        # set value to property
        prop.Unlock()
        prop.SetValue(value)
        prop.Lock()
    
    
    def SetProperties(self, props):
        """
        Sets property values from given data.
        
        This method is not intended to be used by user. It is used automatically
        by the library itself.
        
        Args:
            props: (pyeds.PropertyValue,)
                Properties to set.
        """
        
        # add properties
        self._properties += props
        
        # lookup column names
        for i, prop in enumerate(self._properties):
            if prop.Type.ColumnName not in self._names:
                self._names[prop.Type.ColumnName] = i
        
        # lookup display names
        for i, prop in enumerate(self._properties):
            if prop.Type.DisplayName and prop.Type.DisplayName not in self._names:
                self._names[prop.Type.DisplayName] = i
        
        # reset IDs
        self._ids = tuple(self.GetValue(c.ColumnName) for c in self._type.IDColumns)
    
    
    def HasProperty(self, prop_name):
        """
        Checks if given property name exists in this item.
        
        Args:
            prop_name: str
                Property name.
        
        Returns:
            bool
                True if property exists, False otherwise.
        """
        
        return prop_name in self._names
    
    
    def AddChildren(self, items):
        """
        Adds child entity items.
        
        This method is not intended to be used by user. It is used automatically
        by the library itself.
        
        Args:
            items: (pyeds.EntityItem,)
                Entity items to be added.
        """
        
        for item in items:
            self._children.append(item)
    
    
    def AddValue(self, value, name, position=None, align=None, template=None, converter=None):
        """
        Adds user value to current item. This method should be used to include
        custom values into a pyeds.Review. Note that when added, the value is
        locked and can no longer be changed.
        
        Args:
            value: any
                Value to be added.
            
            name: str
                Unique name of the property. Also used as a column header.
            
            position: int or None
                Column position. If set to None, column will be added as the
                very last column.
            
            align: int or None
                Cell alignment as 1 - left, 2 - center or 3 - right.
            
            template: str or None
                Python formatting string (e.g.'{:.2f}') to be used when the
                value is shown in a review.
            
            converter: str or None
                Unique identifier used to register the value converter, which
                should be used when the value is shown in a review. Typically
                this is a specific GridCellControlGuid or DataPurpose.
        """
        
        # check existing
        if name in self._names:
            message = "The '%s' property already exists in '%s'!" % (name, self._type.Name)
            raise ValueError(message)
        
        # get position
        if position is None:
            position = 1 + max((0, *(p.Type.VisiblePosition for p in self._properties)))
        
        # init column definition
        column = PropertyColumn(virtual=True)
        column.ColumnName = name
        column.DisplayName = name
        column.FormatString = template
        column.VisiblePosition = position
        column.TextHAlign = align
        column.GridCellControlGuid = converter
        column.Lock()
        
        # make property
        prop = PropertyValue(column, value)
        prop.Lock()
        
        # add property
        self._properties.append(prop)
        self._names[name] = len(self._properties) - 1
    
    
    def Check(self, value=True):
        """
        Sets current checked state according to given value.
        
        Note that the updated value is not persisted automatically in the
        database. This must be done manually by 'pyeds.EDS.Update' method.
        
        Args:
            value: bool
                Checked state to set.
        """
        
        # check if checkable
        if 'Checked' not in self._names:
            message = "'%s' is not checkable!" % (self._type.Name,)
            raise ValueError(message)
        
        # update property
        self.SetValue('Checked', bool(value))
    
    
    def Tag(self, index, value=True):
        """
        Sets specified tag state according to given value.
        
        Note that if an invisible tag is set, it does not make it visible. This
        must be done manually in the main application.
        
        Note that the updated value is not persisted automatically in the
        database. This must be done manually by 'pyeds.EDS.Update' method.
        
        Args:
            index: int
                Index of the tag to set.
            
            value: bool
                Tag state to set.
        """
        
        # check if taggable
        if 'Tags' not in self._names:
            message = "'%s' is not taggable!" % (self._type.Name,)
            raise ValueError(message)
        
        # get property
        prop = self.GetProperty('Tags')
        
        # get or init tags
        if prop.Value is None:
            tags = [None] * len(prop.Type.SpecialValueType.Boxes)
        else:
            tags = list(prop.Value.Values)
        
        # update value
        tags[index] = value or None
        
        # update property
        self.SetValue('Tags', tags)
    
    
    def Tagged(self, index):
        """
        Gets specified tag state.
        
        Args:
            index: int
                Index of the tag to get.
        
        Returns:
            bool
                Returns True if specified tag is set to True, False otherwise.
        """
        
        # check if taggable
        if 'Tags' not in self._names:
            message = "'%s' is not taggable!" % (self._type.Name,)
            raise ValueError(message)
        
        # get property
        prop = self.GetProperty('Tags')
        
        # no tags set
        if prop.Value is None:
            return False
        
        # get specified tag
        return prop.Value.Values[index] is True
    
    
    def ClearTags(self):
        """Clears all tags."""
        
        # check if taggable
        if 'Tags' not in self._names:
            message = "'%s' is not taggable!" % (self._type.Name,)
            raise ValueError(message)
        
        # reset tags
        self.SetValue('Tags', None)
