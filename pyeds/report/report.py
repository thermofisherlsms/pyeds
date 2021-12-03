#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import datetime
import time
import shutil

from .database import Database
from .column import PropertyColumn
from .conn import DataTypeConnection
from .dtype import DataType
from .cdtype import CustomDataType
from .ddmap import DataDistributionMap, DataDistributionBox, DataDistributionLevel
from .enum import EnumDataType, EnumElement
from .workflow import Workflow, WorkflowMessage

# initializes converters
from .converters import CONVERTERS


class Report(object):
    """
    The pyeds.Report class provides the main access to the Magellan report
    file data. Upon opening any result file the complete schema is retrieved and
    all data structures are initialized automatically. While this class can be
    instantiated manually, this is typically done automatically by tools like
    pyeds.EDS or pyeds.Summary.
    
    Attributes:
        
        Workflows: (pyeds.Workflow,)
            All defined workflows.
        
        DataTypes: (pyeds.DataType,)
            All defined data types.
        
        Connections: (pyeds.DataTypeConnection,)
            All defined data types connections.
        
        EnumDataTypes: (pyeds.EnumDataType,)
            All defined enum data types.
        
        DataDistributionMaps: (pyeds.DataDistributionMap,)
            All defined data distribution maps.
    """
    
    
    def __init__(self, path):
        """
        Initializes a new instance of Report.
        
        Args:
            path: str
                Path to the report file.
        """
        
        # init database file
        self._db = Database(path)
        
        # init buffers
        self._data_types_by_name = {}  # for .Name
        self._data_types_by_display = {}  # for .DisplayName
        self._connections = {}  # for sorted(.ID1, .ID2)
        self._workflows = {}  # for .ID
        
        self._custom_data_types = {}  # for .ID
        self._enum_data_types = {}  # for .ID
        self._data_distribution_maps = {}  # for .ID
        self._converters = {}
        
        # read file structure
        with self:
            self._initialize()
    
    
    def __enter__(self):
        """Opens specified database connection within 'with' statement."""
        
        self.Open()
        return self
    
    
    def __exit__(self, exc_ty, exc_val, tb):
        """Closes database connection when 'with' statement ended."""
        
        self.Close()
    
    
    @property
    def Path(self):
        """
        Gets report file path.
        
        Returns:
            str
                Report file path.
        """
        
        return self._db.path
    
    
    @property
    def Workflows(self):
        """
        Gets workflows stored in current file.
        
        Returns:
            (pyeds.Workflow,)
                All defined workflows.
        """
        
        return tuple(self._workflows.values())
    
    
    @property
    def DataTypes(self):
        """
        Gets data types stored in current file.
        
        Returns:
            (pyeds.DataType,)
                All defined data types.
        """
        
        return tuple(self._data_types_by_name.values())
    
    
    @property
    def Connections(self):
        """
        Gets data types connections stored in current file.
        
        Returns:
            (pyeds.DataTypeConnection,)
                All defined data types connections.
        """
        
        return tuple(self._connections.values())
    
    
    @property
    def EnumDataTypes(self):
        """
        Gets enum data types stored in current file.
        
        Returns:
            (pyeds.EnumDataType,)
                All defined enum data types.
        """
        
        return tuple(self._enum_data_types.values())
    
    
    @property
    def DataDistributionMaps(self):
        """
        Gets data distribution maps stored in current file.
        
        Returns:
            (pyeds.DataDistributionMap,)
                All defined data distribution maps.
        """
        
        return tuple(self._data_distribution_maps.values())
    
    
    def GetDataType(self, data_type_name):
        """
        Gets entity data type for given name.
        
        Args:
            data_type_name: str
                Data type name.
        
        Returns:
            pyeds.DataType
                Entity data type corresponding to the given name.
        """
        
        # get by table name
        if data_type_name in self._data_types_by_name:
            return self._data_types_by_name[data_type_name]
        
        # get by display name
        if data_type_name in self._data_types_by_display:
            return self._data_types_by_display[data_type_name]
        
        # not available
        message = "Report file doesn't contain data type '%s'!" % data_type_name
        raise KeyError(message)
    
    
    def GetConnection(self, data_type_name_1, data_type_name_2):
        """
        Gets data type connection between specified entity data types.
        
        Args:
            data_type_name_1: str
                Data type name.
            
            data_type_name_2: str
                Data type name.
        
        Returns:
            pyeds.DataTypeConnection
                Connection between given data type names.
        """
        
        # get first data type
        data_type = self.GetDataType(data_type_name_1)
        
        # get connection
        connection = data_type.GetConnection(data_type_name_2)
        
        return connection
    
    
    def HasDataType(self, data_type_name):
        """
        Checks if specified entity data type exists.
        
        Args:
            data_type_name: str
                Data type name.
        
        Returns:
            bool
                True if data type exists, False otherwise.
        """
        
        if data_type_name in self._data_types_by_name:
            return True
        
        if data_type_name in self._data_types_by_display:
            return True
        
        return False
    
    
    def Open(self):
        """
        Opens database connection.
        
        Returns:
            bool
                Returns True if new connection was established, False otherwise.
        """
        
        return self._db.connect()
    
    
    def Close(self):
        """Closes database connection."""
        
        self._db.close()
    
    
    def Execute(self, sql, values=()):
        """
        Executes given SQL query and returns new cursor.
        
        Args:
            sql: str
                SQL query.
            
            values: (?,)
                Values to be used within SQL query.
        
        Return:
            sqlite.Cursor
                Cursor pointing to query results.
        """
        
        # assert connection
        self._assert_connection()
        
        # execute sql query
        return self._db.execute(sql, values)
    
    
    def Backup(self):
        """Creates database backup."""
        
        # get time stamp
        stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
        
        # init file name
        filename = "%s_%s.bak" % (self._db.path, stamp)
        
        # duplicate file
        shutil.copy(self._db.path, filename)
    
    
    def _initialize(self):
        """Reads all data structures from current file."""
        
        # initialize value converters
        self._converters = {}
        for key in CONVERTERS:
            converter = CONVERTERS[key]()
            self._converters[key] = converter
        
        # extract schema
        self._extract_custom_data_types()
        self._extract_enum_data_types()
        self._extract_data_distribution_maps()
        self._extract_data_types()
        self._extract_data_type_connections()
        
        # extract workflows
        self._extract_workflows()
        
        # lock items
        for item in self._custom_data_types.values():
            item.Lock()
        
        for item in self._enum_data_types.values():
            item.Lock()
            for elm in item.Elements:
                elm.Lock()
        
        for item in self._data_distribution_maps.values():
            item.Lock()
            for box in item.Boxes:
                box.Lock()
            for level in item.Levels:
                level.Lock()
        
        for item in self._data_types_by_name.values():
            item.Lock()
            for col in item.Columns:
                col.Lock()
        
        for item in self._connections.values():
            item.Lock()
            for col in item.Columns:
                col.Lock()
        
        for item in self._workflows.values():
            item.Lock()
            for msg in item.Messages:
                msg.Lock()
            for node in item.Nodes:
                node.Lock()
                for param in node.Parameters:
                    param.Lock()
    
    
    def _assert_connection(self):
        """Asserts database connection."""
        
        if self._db.conn is None:
            raise ValueError("Database connection is not opened!")
    
    
    def _extract_custom_data_types(self):
        """Reads all custom data types from current file."""
        
        # extract custom data types
        cur = self._db.execute("SELECT * FROM CustomDataTypes")
        for data in cur:
            cdtype = CustomDataType.FromDBData(data)
            self._custom_data_types[cdtype.ID] = cdtype
    
    
    def _extract_enum_data_types(self):
        """Reads all enum data types from current file."""
        
        # extract enum types
        cur = self._db.execute("SELECT * FROM EnumDataTypes")
        for data in cur:
            enum = EnumDataType.FromDBData(data)
            self._enum_data_types[enum.ID] = enum
        
        # extract enum elements
        cur = self._db.execute("SELECT * FROM EnumDataTypeValues")
        for data in cur:
            elm = EnumElement.FromDBData(data)
            self._enum_data_types[elm.EnumID].AddElement(elm)
    
    
    def _extract_data_distribution_maps(self):
        """Reads all data distribution maps from current file."""
        
        # init buffers
        boxes = {}
        levels = {}
        exdata = {}
        
        # extract data distribution maps
        cur = self._db.execute("SELECT * FROM DataDistributionMaps")
        for data in cur:
            ddmap = DataDistributionMap.FromDBData(data)
            self._data_distribution_maps[ddmap.ID] = ddmap
            boxes[ddmap.ID] = []
            levels[ddmap.ID] = []
        
        # extract data distribution boxes
        cur = self._db.execute("SELECT * FROM DataDistributionBoxes")
        for data in cur:
            box = DataDistributionBox.FromDBData(data)
            boxes[box.MapID].append(box)
            exdata[box.ID] = box.ExtendedData
        
        # extract data distribution levels
        cur = self._db.execute("SELECT * FROM DataDistributionLevels")
        for data in cur:
            level = DataDistributionLevel.FromDBData(data)
            levels[level.MapID].append(level)
        
        # extract extended data
        cur = self._db.execute("SELECT * FROM DataDistributionBoxExtendedData")
        for data in cur:
            exdata[data['BoxID']][data['Name']] = data['ValueString']
        
        # pair data
        for dist_map in self._data_distribution_maps.values():
            
            # set custom data type
            if dist_map.CustomDataTypeID:
                dist_map.CustomDataType = self._custom_data_types[dist_map.CustomDataTypeID]
            
            # set boxes
            dist_map.SetBoxes(boxes[dist_map.ID])
            
            # set levels
            dist_map.SetLevels(levels[dist_map.ID])
    
    
    def _extract_data_types(self):
        """Reads all data types from current file."""
        
        # init buffers
        data_types = {}
        columns = {}
        ids = {}
        exdata = {}
        
        # extract data types
        cur = self._db.execute("SELECT * FROM DataTypes")
        for data in cur:
            dtype = DataType.FromDBData(data)
            data_types[dtype.ID] = dtype
            columns[dtype.ID] = []
        
        # extract property columns
        cur = self._db.execute("SELECT * FROM DataTypesColumns")
        for data in cur:
            col = PropertyColumn.FromDBData(data)
            columns[data['DataTypeID']].append(col)
            exdata[col.ID] = col.ExtendedData
        
        # extract data type IDs
        cur = self._db.execute("SELECT * FROM DataTypesIDColumns")
        for data in cur:
            ids[data['ColumnID']] = data['Rank']
        
        # extract extended data
        cur = self._db.execute("SELECT * FROM DataTypesColumnExtendedData")
        for data in cur:
            if data['ColumnID'] in exdata:
                exdata[data['ColumnID']][data['Name']] = data['ValueString']
        
        # finalize columns
        self._finalize_property_columns([y for x in columns for y in columns[x]], ids)
        
        # add columns to data types
        for data_type in data_types.values():
            for column in columns[data_type.ID]:
                data_type.AddColumn(column)
        
        # create lookup tables
        for data_type in data_types.values():
            self._data_types_by_name[data_type.Name] = data_type
            if data_type.DisplayName:
                self._data_types_by_display[data_type.DisplayName] = data_type
    
    
    def _extract_data_type_connections(self):
        """Reads all connections between data types from current file."""
        
        # init buffers
        columns = {}
        ids = {}
        
        # extract connection types
        cur = self._db.execute("SELECT * FROM ConnectedDataTypes")
        for data in cur:
            key = tuple(sorted((data['DataTypeID1'], data['DataTypeID2'])))
            conn = DataTypeConnection.FromDBData(data)
            self._connections[key] = conn
            columns[key] = []
        
        # extract property columns
        cur = self._db.execute("SELECT * FROM ConnectedDataTypesColumns")
        for data in cur:
            key = tuple(sorted((data['DataTypeID1'], data['DataTypeID2'])))
            col = PropertyColumn.FromDBData(data)
            columns[key].append(col)
        
        # extract connection types IDs
        cur = self._db.execute("SELECT * FROM ConnectedDataTypesIDColumns")
        for data in cur:
            ids[data['ColumnID']] = data['Rank']
        
        # finalize columns
        self._finalize_property_columns([y for x in columns for y in columns[x]], ids)
        
        # make data types ID lookup
        data_types = {x.ID: x for x in self._data_types_by_name.values()}
        
        # pair data
        for key, connection in self._connections.items():
            
            # set data types
            connection.DataType1 = data_types[connection.DataTypeID1]
            connection.DataType2 = data_types[connection.DataTypeID2]
            
            # add to data types
            connection.DataType1.AddConnection(connection)
            connection.DataType2.AddConnection(connection)
            
            # add columns
            for column in columns[key]:
                connection.AddColumn(column)
    
    
    def _extract_workflows(self):
        """Extracts workflows."""
        
        # extract workflows
        cur = self._db.execute("SELECT * FROM Workflows")
        for data in cur:
            wf = Workflow.FromDBData(data)
            self._workflows[wf.ID] = wf
        
        # extract messages
        cur = self._db.execute("SELECT * FROM WorkflowMessages")
        for data in cur:
            msg = WorkflowMessage.FromDBData(data)
            if msg.WorkflowID in self._workflows:
                self._workflows[msg.WorkflowID].AddMessage(msg)
    
    
    def _finalize_property_columns(self, columns, ids):
        """Finalizes all property columns by marking ID columns an adding types."""
        
        # finalize columns
        for column in columns:
            
            # mark ID column
            if column.ID in ids:
                column.IDColumnOrder = ids[column.ID]
            
            # set custom data type
            if column.CustomDataTypeID:
                column.CustomDataType = self._custom_data_types[column.CustomDataTypeID]
            
            # set enum data type
            if column.SpecialValueTypeName == 'Enum':
                column.SpecialValueType = self._enum_data_types[column.SpecialValueTypeID]
            
            # set data distribution map
            elif column.SpecialValueTypeName == 'DataDistribution':
                column.SpecialValueType = self._data_distribution_maps[column.SpecialValueTypeID]
            
            # set data type converter
            if column.ValueTypeGuid in self._converters:
                column.ValueTypeConverter = self._converters[column.ValueTypeGuid]
            
            elif column.DataPurpose in self._converters:
                column.ValueTypeConverter = self._converters[column.DataPurpose]
