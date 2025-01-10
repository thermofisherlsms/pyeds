#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
from .lockable import Lockable


class DataType(Lockable):
    """
    The pyeds.DataType class is used to hold all the meta-data of an entity data
    type.
    
    Attributes:
        
        ID: int
            Unique data type ID.
        
        Name: str
            Unique data type name.
        
        TableName: str
            Actual name of the database table.
        
        GUID:
            Unique GUID identifier.
        
        Version: int
            Used data type version.
        
        LastChange: str
            Date and time of the last change.
        
        DisplayName:
            Display-friendly name of the type. This is typically used as the
            table header within desktop apps.
        
        Description: str
            Basic type descriptions. This is typically used as the table header
            tooltip within desktop apps.
        
        IDColumns: (pyeds.PropertyColumn,)
            Collection of ID property columns sorted by rank.
        
        Columns: (pyeds.PropertyColumn,)
            Collection of available property columns.
        
        Connections: (pyeds.DataTypeConnection,)
            Available direct connections.
    """
    
    T_ALIAS = "T1"
    
    
    def __init__(self):
        """Initializes a new instance of DataType."""
        
        super().__init__()
        
        # mark available types
        self.IsAvailable = True
        
        # main attributes
        self.ID = None
        self.Name = None
        self.TableName = None
        self.GUID = None
        self.Version = None
        self.LastChange = None
        
        # display options
        self.DisplayName = None
        self.Description = None
        self.Visibility = None
        self.VisiblePosition = None
        self.VisibilityStartingLayer = None
        
        self._columns_by_name = {}
        self._columns_by_display = {}
        
        self._connections_by_name = {}
        self._connections_by_display = {}
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return self.Name
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    @property
    def IDColumns(self):
        """
        Gets sorted ID property columns.
        
        Returns:
            (pyeds.PropertyColumn,)
                Sorted ID property columns.
        """
        
        columns = (x for x in self._columns_by_name.values() if x.IsIDColumn)
        return tuple(sorted(columns, key=lambda x: x.IDColumnOrder))
    
    
    @property
    def Columns(self):
        """
        Gets all property columns.
        
        Returns:
            (pyeds.PropertyColumn,)
                Available property columns.
        """
        
        return tuple(self._columns_by_name.values())
    
    
    @property
    def Connections(self):
        """
        Gets connections to other data types.
        
        Returns:
            (pyeds.DataTypeConnection,)
                Available direct connections.
        """
        
        return tuple(self._connections_by_name.values())
    
    
    def GetColumn(self, column_name):
        """
        Gets column by its name.
        
        Args:
            column_name: str
                Property column name.
        
        Returns:
            pyeds.PropertyColumn
                Property column corresponding to given name.
        """
        
        # get by column name
        if column_name in self._columns_by_name:
            return self._columns_by_name[column_name]
        
        # get by display name
        if column_name in self._columns_by_display:
            return self._columns_by_display[column_name]
        
        # not available
        message = "'%s' doesn't contain column '%s'!" % (self.Name, column_name)
        raise KeyError(message)
    
    
    def GetColumns(self, data_purpose=None):
        """
        Gets all columns with corresponding data purpose.
        
        Args:
            data_purpose: str or None
                Data purpose.
        
        Returns:
            (pyeds.PropertyColumn,)
                Property columns corresponding to given data purpose.
        """
        
        columns = []
        for name, column in self._columns_by_name.items():
            if data_purpose is None or column.DataPurpose == data_purpose:
                columns.append(column)
        
        return tuple(columns)
    
    
    def GetConnection(self, data_type_name):
        """
        Gets connection to specified data type.
        
        Args:
            data_type_name: str
                Data type name.
        
        Returns:
            pyeds.DataTypeConnection
                Connection to specified data type.
        """
        
        # get by table name
        if data_type_name in self._connections_by_name:
            return self._connections_by_name[data_type_name]
        
        # get by display name
        if data_type_name in self._connections_by_display:
            return self._connections_by_display[data_type_name]
        
        # not available
        message = "'%s' doesn't contain direct connection to '%s'!" % (self.Name, data_type_name)
        raise KeyError(message)
    
    
    def HasColumn(self, column_name):
        """
        Checks if given column name exists in this type.
        
        Args:
            column_name: str
                Property column name.
        
        Returns:
            bool
                True if column exists, False otherwise.
        """
        
        if column_name in self._columns_by_name:
            return True
        
        if column_name in self._columns_by_display:
            return True
        
        return False
    
    
    def HasConnection(self, data_type_name):
        """
        Checks if given data type is connected to this type.
        
        Args:
            data_type_name: str
                Data type name.
        
        Returns:
            bool
                True if connection exists, False otherwise.
        """
        
        if data_type_name in self._connections_by_name:
            return True
        
        if data_type_name in self._connections_by_display:
            return True
        
        return False
    
    
    def AddColumn(self, column):
        """
        Adds given property column.
        
        This method is not intended to be used by user. It is used automatically
        by the library itself.
        
        Args:
            column: pyeds.PropertyColumn
                Property column to be added.
        """
        
        # check lock
        self.AssertUnlocked()
        
        # add column
        self._columns_by_name[column.ColumnName] = column
        if column.DisplayName:
            self._columns_by_display[column.DisplayName] = column
    
    
    def AddConnection(self, connection):
        """
        Adds given data type connection.
        
        This method is not intended to be used by user. It is used automatically
        by the library itself.
        
        Args:
            connection: pyeds.DataTypeConnection
                Data type connection to be added.
        """
        
        # check lock
        self.AssertUnlocked()
        
        # get connected data type
        connected_data_type = connection.DataType2
        if connected_data_type is self:
            connected_data_type = connection.DataType1
        
        # add connection
        self._connections_by_name[connected_data_type.Name] = connection
        if connected_data_type.DisplayName:
            self._connections_by_display[connected_data_type.DisplayName] = connection
    
    
    def Disable(self):
        """Marks current data type and all columns as unavailable."""
        
        self.IsAvailable = False
        
        # mark columns
        for column in self.Columns:
            column.Disable()
        
        # mark connections
        for connection in self.Connections:
            connection.Disable()
    
    
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
            pyeds.DataType
                Data type instance.
        """
        
        data_type = DataType()
        
        data_type.ID = data['DataTypeID']
        data_type.Name = data['Name']
        data_type.TableName = data['TableName']
        data_type.GUID = data['DataTypeIdentifier']
        data_type.Version = data['Version']
        data_type.LastChange = data['LastChange']
        
        data_type.DisplayName = data['DisplayName']
        data_type.Description = data['Description']
        data_type.Visibility = data['Visibility']
        data_type.VisiblePosition = data['VisiblePosition']
        data_type.VisibilityStartingLayer = data['VisibilityStartingLayer']
        
        return data_type
