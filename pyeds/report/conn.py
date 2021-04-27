#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
from .lockable import Lockable


class DataTypeConnection(Lockable):
    """
    The pyeds.DataTypeConnection class is used to hold all the information about
    registered connection between two entities.
    
    Attributes:
        
        DataTypeID1: int
            Unique ID of the first entity data type.
        
        DataTypeID2: int
            Unique ID of the first entity data type.
        
        DataType1: pyeds.DataType
            Definition of the first entity data type.
        
        DataType2: pyeds.DataType
            Definition of the second entity data type.
        
        TableName: str
            Name of the database connection table.
        
        IDColumns: (pyeds.PropertyColumn,)
            Collection of ID property columns sorted by rank.
        
        Columns: (pyeds.PropertyColumn,)
            Collection of available property columns.
    """
    
    
    def __init__(self):
        """Initializes a new instance of DataTypeConnection."""
        
        super().__init__()
        
        self.DataTypeID1 = None
        self.DataTypeID2 = None
        self.DataType1 = None
        self.DataType2 = None
        self.TableName = None
        
        self._columns_by_name = {}
        self._columns_by_display = {}
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return "%s -> %s" % (self.DataType1, self.DataType2)
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    @property
    def IDColumns(self):
        """
        Gets ID property columns sorted by column order.
        
        Returns:
            (pyeds.PropertyColumn,)
                ID property columns.
        """
        
        columns = (x for x in self._columns_by_name.values() if x.IsIDColumn)
        return tuple(sorted(columns, key=lambda x:x.IDColumnOrder))
    
    
    @property
    def Columns(self):
        """
        Gets all property columns.
        
        Returns:
            (pyeds.PropertyColumn,)
                Available property columns.
        """
        
        return tuple(self._columns_by_name.values())
    
    
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
        message = "'%s' doesn't contain column '%s'!" % (self.TableName, column_name)
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
    
    
    def AddColumn(self, column):
        """
        Adds given property column.
        
        This method is not intended to be used by user. It is used automatically
        by the library itself.
        
        Args:
            column: pyeds.PropertyColumn
                Property column to be added.
        """
        
        self._columns_by_name[column.ColumnName] = column
        if column.DisplayName:
            self._columns_by_display[column.DisplayName] = column
    
    
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
            pyeds.DataTypeConnection
                Connection data type instance.
        """
        
        connection = DataTypeConnection()
        
        connection.DataTypeID1 = data['DataTypeID1']
        connection.DataTypeID2 = data['DataTypeID2']
        connection.TableName = data['ConnectedTableName']
        
        return connection
