#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
from .lockable import Lockable


class PropertyColumn(Lockable):
    """
    The pyeds.PropertyColumn class is used to hold all the meta-data of an
    entity property. These information are used to convert raw database values
    into their final type as well as to apply expected formatting when reviewing
    the data.
    
    Attributes:
        
        ID: int
            Unique ID of the property.
            
        Guid: str
            GUID of the property.
        
        ColumnName: str
            Real database column name.
        
        DisplayName: str
            Display-friendly name of the column. This is typically used as the
            column header within desktop apps.
        
        Description: str
            Basic column descriptions. This is typically used as the column
            header tooltip within desktop apps.
        
        DataPurpose: str
            Semantic description of the property.
        
        Nullable: int
            Specifies if value can be null.
        
        DefaultValue: ?
            Specifies the default value used if no real value is set.
        
        CustomDataType: pyeds.CustomDataType
            Definition of a basic type of the values stored in this column
            (e.g. string, int, binary). It is later used to convert raw
            database value into a correct type.
        
        CustomDataTypeID: int
            Unique ID of the basic data type.
        
        SpecialValueType: ? or None
            Instance of a more specific but still rather generic data type
            definition (e.g. pyeds.EnumDataType, pyeds.DataDistributionMap). It
            holds all the meta-data about the final data type and it is used to
            convert the database value from the basic type into the final type.
        
        SpecialValueTypeID: int
            Unique ID of a special value type.
        
        SpecialValueTypeName: str
            Unique name of the type like 'Enum' or 'DataDistribution'.
        
        ValueTypeConverter: pyeds.ValueConverter or None
            Instance of a specific value converter used to convert a database
            value into the final type. Unlike the 'SpecialValueType', which is
            still somewhat generic (e.g. enum), this is used for very specific
            data types like traces, spectra etc. or it can be any user-defined
            registered converter. Note that the order of conversions is as
            follows: CustomDataType, SpecialValueType, ValueTypeConverter.
        
        ValueTypeGuid: str
            GUID of a value converter.
        
        LastChange: str
            Date and time of the last change.
        
        IDColumnOrder: int or None
            Order of the column in item IDs. This is None if the column is not
            used as ID.
        
        ExtendedData: {str:str}
            Extended data values.
    """
    
    
    def __init__(self):
        """Initializes a new instance of PropertyColumn."""
        
        super().__init__()
        
        self.ID = None
        self.ColumnName = None
        self.CustomDataType = None
        self.CustomDataTypeID = None
        self.DefaultValue = None
        self.Nullable = None
        self.ValueTypeGuid = None
        self.ValueTypeConverter = None
        self.SpecialValueType = None
        self.SpecialValueTypeID = None
        self.SpecialValueTypeName = None
        self.LastChange = None
        self.IDColumnOrder = None
        self.DataPurpose = None
        self.Guid = None
        self.ExtendedData = {}
        
        # display options
        self.DisplayName = None
        self.Description = None
        self.FormatString = None
        self.SortDirection = None
        self.DataVisibility = None
        self.VisiblePosition = None
        self.AllowEdit = None
        self.TextHAlign = None
        self.ColumnWidth = None
        self.GridCellControlGuid = None
        self.BackgroundColor = None
        
        # plotting options
        self.PlotType = None
        
        # text export options
        self.TextExport = None
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        data_type = self.CustomDataType.Name
        if self.SpecialValueTypeName:
            data_type = "%s/%s" % (data_type, self.SpecialValueTypeName)
        
        return "%s(%s)" % (self.ColumnName, data_type)
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    @property
    def IsIDColumn(self):
        """
        Gets the value indicating if this property is used as ID.
        
        Returns:
            bool
                True if this is ID property, False otherwise.
        """
        
        if self.IDColumnOrder is None:
            return False
        
        return self.IDColumnOrder > 0
    
    
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
            pyeds.PropertyColumn
                Property column instance.
        """
        
        property_column = PropertyColumn()
        
        property_column.ID = data['ColumnID']
        property_column.ColumnName = data['DBColumnName']
        property_column.CustomDataTypeID = data['CustomDataType']
        property_column.DefaultValue = data['DefaultValue']
        property_column.Nullable = data['Nullable']
        property_column.ValueTypeGuid = data['ValueType']
        property_column.SpecialValueTypeName = data['SpecialValueType']
        property_column.SpecialValueTypeID = data['SpecialValueTypeID']
        property_column.LastChange = data['LastChange']
        property_column.DataPurpose = data['Property_SemanticDescription']
        property_column.Guid = data['Property_Guid']
        
        property_column.DisplayName = data['Property_DisplayName']
        property_column.Description = data['Property_Description']
        property_column.FormatString = data['Property_FormatString']
        property_column.SortDirection = data['Property_SortDirection']
        
        property_column.DataVisibility = data['Grid_DataVisibility']
        property_column.VisiblePosition = data['Grid_VisiblePosition']
        property_column.AllowEdit = data['Grid_AllowEdit']
        property_column.TextHAlign = data['Grid_TextHAlign']
        property_column.ColumnWidth = data['Grid_ColumnWidth']
        property_column.GridCellControlGuid = data['Grid_GridCellControlGuid']
        property_column.BackgroundColor = data['Grid_Background']
        
        property_column.PlotType = data['Plot_PlotType']
        
        property_column.TextExport = data['TextExport_Supported']
        
        return property_column
