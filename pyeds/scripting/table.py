#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
from .enums import *
from ..report import Lockable
from .column import Column


class Table(Lockable):
    """
    Holds a table definition.
    
    Attrs:
        TableName: str
            Specifies the table display name.
        
        DataFile: str
            Specifies the full path to related text file containing actual
            columns values.
        
        DataFormat: str
            Specifies the data format as one of the following values:
                pyeds.scripting.CSV - tab-separated values,
                pyeds.scripting.JSON - JSON format,
                pyeds.scripting.CSV_CONN - used for connection tables.
        
        Options: pyeds.scripting.TableOptions
            Specifies additional options for connection tables.
        
        ColumnDescriptions: (pyeds.scripting.Column,)
            Collection of defined columns.
    """
    
    
    def __init__(self, table_name, data_file, data_format=CSV, **options):
        """
        Initializes a new instance of the Table.
        
        Args:
            table_name: str
                Specifies the table display name.
            
            data_file: str
                Specifies the full path to related text file containing actual
                columns values.
            
            data_format: str
                Specifies the data format as one of the following values:
                    pyeds.scripting.CSV - tab-separated values,
                    pyeds.scripting.CSV_CONN - used for connection tables.
            
            **options: {str, str}
                Additional options for connection tables.
                See pyeds.scripting.TableOptions for more information.
        """
        
        super().__init__()
        
        # check name
        if not table_name:
            message = "Table name must be specified!"
            raise ValueError(message)
        
        # check path
        if not data_file:
            message = "Data file path must be specified!"
            raise ValueError(message)
        
        # check data format
        first_table = options.get('FirstTable', None)
        second_table = options.get('SecondTable', None)
        
        if data_format == CSV and (first_table or second_table):
            message = "Connection table must be flagged using 'pyeds.scripting.CSV_CONN' as data format! '%s'" % data_format
            raise ValueError(message)
        
        if data_format == CSV_CONN and (not first_table or not second_table):
            message = "Connection table must provide both 'FirstTable' and 'SecondTable' names!"
            raise ValueError(message)
        
        if data_format not in DATA_FORMAT:
            message = "Table data format must be one of the %s! --> '%s'" % (str(DATA_FORMAT), data_format)
            raise ValueError(message)
        
        # init attributes
        self.TableName = table_name
        self.DataFile = data_file
        self.DataFormat = data_format
        self.Options = TableOptions(**options)
        
        # init containers
        self._columns = []
        self._values = []
    
    
    @property
    def ColumnDescriptions(self):
        """
        Gets collection of defined columns:
        
        Returns:
            (pyeds.scripting.Column,)
        """
        
        return tuple(self._columns)
    
    
    @property
    def Header(self):
        """Generates table data header."""
        
        return "\t".join(f"\"{col.ColumnName}\"" for col in self._columns)
    
    
    def GetColumn(self, column_name):
        """
        Gets existing column.
        
        Args:
            column_name: str
                Column display name.
        
        Returns:
            pyeds.scripting.Column
        """
        
        for col in self._columns:
            if col.ColumnName == column_name:
                return col
        
        message = "Specified column is does not exist! --> '%s'" % column_name
        raise KeyError(message)
    
    
    def GetIDColumns(self):
        """
        Gets all ID columns.
        
        Returns:
            (pyeds.scripting.Column,)
        """
        
        return [col for col in self._columns if col.ID]
    
    
    def AddColumn(self, column_name, data_type, id_name=None, **options):
        """
        Adds new colum to current table.
        
        Args:
            column_name: str
                Specifies the column display name.
            
            data_type: str
                Specifies the data format as one of the following values:
                    pyeds.scripting.STRING - string,
                    pyeds.scripting.INT - integer,
                    pyeds.scripting.LONG - long,
                    pyeds.scripting.FLOAT - float,
                    pyeds.scripting.BOOLEAN - boolean.
            
            id_name: str or None
                Specifies a flag that indicates whether the column is an ID as
                one of the following values:
                    pyeds.scripting.ID - main ID,
                    pyeds.scripting.WORKFLOW_ID - workflow ID,
                    pyeds.scripting.OTHER - other ID.
            
            **options: {str, str}
                Additional column options. See pyeds.scripting.ColumnOptions for
                more information.
        """
        
        # check lock
        self.AssertUnlocked()
        
        # check name
        for col in self._columns:
            if col.ColumnName == column_name:
                message = "Column with the same name already exists! --> '%s'" % column_name
                raise KeyError(message)
        
        # check ID column
        if self.DataFormat == CSV_CONN and id_name:
            
            # get connected table names
            first_table = self.Options.FirstTable or ''
            second_table = self.Options.SecondTable or ''
            
            # check column name
            if not column_name.startswith(first_table) and not column_name.startswith(second_table):
                message = "ID columns in connection tables should start with one of the tables name! --> '%s'" % column_name
                raise KeyError(message)
        
        # create column
        column = Column(
            column_name = column_name,
            data_type = data_type,
            id_name = id_name,
            **options)
        
        # lock column
        column.Lock()
        
        # add
        self._columns.append(column)
        
        return column
    
    
    def AddRowData(self, *values):
        """Adds all columns data for single row."""
        
        # check size
        if len(values) != len(self._columns):
            message = "Number of values and number of columns must be equal!"
            raise ValueError(message)
        
        # add values
        self._values.append(tuple(values))
    
    
    def ToJSON(self):
        """
        Converts current data to JSON-like object.
        
        Returns:
            {}
        """
        
        # init data
        data = {}
        
        # add main attributes
        if self.TableName:
            data['TableName'] = self.TableName
        
        if self.DataFile:
            data['DataFile'] = self.DataFile
        
        if self.DataFormat:
            data['DataFormat'] = self.DataFormat
        
        # add options
        options = self.Options.ToJSON()
        if options:
            data['Options'] = options
        
        # add columns
        data['ColumnDescriptions'] = []
        for col in self._columns:
            column = col.ToJSON()
            if column:
                data['ColumnDescriptions'].append(column)
        
        return data
    
    
    def ToCSV(self):
        """
        Formats table values into tab-separated values.
        
        Returns:
            str
        """
        
        lines = ("\t".join(map(str, v)) for v in self._values)
        return "\n".join(lines)
    
    
    def Export(self):
        """Saves table data as tab-separated file."""
        
        with open(self.DataFile, 'w', encoding='utf-8') as wf:
            wf.write(self.Header+"\n")
            wf.write(self.ToCSV())


class TableOptions(Lockable):
    """
    Holds additional table options.
    
    Attrs:
        FirstTable: str
            Specifies the display name of the first table to be connected.
        
        SecondTable: str
            Specifies the display name of the second table to be connected.
    """
    
    
    def __init__(self, **options):
        """Initializes a new instance of the TableOptions."""
        
        super().__init__()
        
        # init attributes
        self.FirstTable = options.get('FirstTable', None)
        self.SecondTable = options.get('SecondTable', None)
    
    
    def ToJSON(self):
        """Converts current data to JSON-like object."""
        
        # init data
        data = {}
        
        # add main attributes
        if self.FirstTable:
            data['FirstTable'] = self.FirstTable
        
        if self.SecondTable:
            data['SecondTable'] = self.SecondTable
        
        return data
