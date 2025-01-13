#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
from .enums import *
from ..report import Lockable


class Column(Lockable):
    """
    Holds a column definition.
    
    Attrs:
        ColumnName: str
            Specifies the table display name.
        
        DataType: str
            Specifies the data format as one of the following values:
                pyeds.scripting.STRING - string,
                pyeds.scripting.INT - integer,
                pyeds.scripting.LONG - long,
                pyeds.scripting.FLOAT - float,
                pyeds.scripting.BOOLEAN - boolean.
        
        ID: str or None
            Specifies the flag that indicates whether the column is an ID as
            one of the following values:
                pyeds.scripting.ID - main ID,
                pyeds.scripting.WORKFLOW_ID - workflow ID,
                pyeds.scripting.OTHER - other ID.
        
        **Options: pyeds.scripting.ColumnOptions
            Additional column options.
    """
    
    
    def __init__(self, column_name, data_type, id_name=None, **options):
        """
        Initializes a new instance of Column.
        
        Args:
            column_name: str
                Specifies the table display name.
            
            data_type: str
                Specifies the data format as one of the following values:
                    pyeds.scripting.STRING - string,
                    pyeds.scripting.INT - integer,
                    pyeds.scripting.LONG - long,
                    pyeds.scripting.FLOAT - float,
                    pyeds.scripting.BOOLEAN - boolean.
            
            id_name: str or None
                Specifies the flag that indicates whether the column is an ID as
                one of the following values:
                    pyeds.scripting.ID - main ID,
                    pyeds.scripting.WORKFLOW_ID - workflow ID,
                    pyeds.scripting.OTHER - other ID.
            
            **options: {str, str}
                Additional column options. See pyeds.scripting.ColumnOptions for
                more information.
        """
        
        super().__init__()
        
        # check name
        if not column_name:
            message = "Column name must be specified!"
            raise ValueError(message)
        
        # check data type
        if data_type not in DATA_TYPE:
            message = "Column data type must be one of the %s! --> '%s'" % (str(DATA_TYPE), data_type)
            raise ValueError(message)
        
        # check ID
        if id_name and id_name not in ID_FLAG:
            message = "ID name must be one of the %s! --> '%s'" % (str(ID_FLAG), id_name)
            raise ValueError(message)
        
        # init attributes
        self.ColumnName = column_name
        self.DataType = data_type
        self.ID = id_name
        self.Options = ColumnOptions(**options)
    
    
    def ToJSON(self):
        """Converts current data to JSON-like object."""
        
        # init data
        data = {}
        
        # add main attributes
        if self.ColumnName:
            data['ColumnName'] = self.ColumnName
        
        if self.DataType:
            data['DataType'] = self.DataType
        
        if self.ID:
            data['ID'] = self.ID
        
        # add options
        options = self.Options.ToJSON()
        if options:
            data['Options'] = options
        
        return data


class ColumnOptions(Lockable):
    """
    Holds additional column options.
    
    Attrs:
        PositionBefore: str
            Specifies the reference column display name before which this column
            will be placed.
        
        PositionAfter: str
            Specifies the reference column display name after which this column
            will be placed.
        
        RelativePosition: int
            Specifies the integer value for relative position of the column.
        
        SpecialCellRenderer: str
            Specifies the alternative presentation used to display the data.
        
        DataGroupName: str
            Specifies related columns grouping name.
        
        FormatString: str
             Specifies how numerical values are formatted and displayed.
             By default, float values have a format string of F5, which means
             they are displayed to 5 significant digits.
        
        PlotType: str
            Specifies the plot type available to plot the column values as one
            of the following values:
                pyeds.scripting.NUMERIC - used for numerical data,
                pyeds.scripting.CATEGORICAL - used for categorical data,
                pyeds.scripting.ORDINAL - used for ordinal data.
        
        DataPurpose: str
            Specifies data purpose description.
    """
    
    
    def __init__(self, **options):
        """Initializes a new instance of the ColumnOptions."""
        
        super().__init__()
        
        # init attributes
        self.PositionBefore = options.get('PositionBefore', None)
        self.PositionAfter = options.get('PositionAfter', None)
        self.RelativePosition = options.get('RelativePosition', None)
        self.SpecialCellRenderer = options.get('SpecialCellRenderer', None)
        self.DataGroupName = options.get('DataGroupName', None)
        self.FormatString = options.get('FormatString', None)
        self.PlotType = options.get('PlotType', None)
        self.DataPurpose = options.get('DataPurpose', None)
    
    
    def ToJSON(self):
        """Converts current data to JSON-like object."""
        
        # init data
        data = {}
        
        # add main attributes
        if self.PositionBefore:
            data['PositionBefore'] = self.PositionBefore
        
        if self.PositionAfter:
            data['PositionAfter'] = self.PositionAfter
        
        if self.RelativePosition:
            data['RelativePosition'] = self.RelativePosition
        
        if self.SpecialCellRenderer:
            data['SpecialCellRenderer'] = self.SpecialCellRenderer
        
        if self.DataGroupName:
            data['DataGroupName'] = self.DataGroupName
        
        if self.FormatString:
            data['FormatString'] = self.FormatString
        
        if self.PlotType:
            data['PlotType'] = self.PlotType
        
        if self.DataPurpose:
            data['DataPurpose'] = self.DataPurpose
        
        return data
