#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import os.path
import json
from ..report import Lockable
from .table import Table
from .enums import *


class NodeArgs(Lockable):
    """
    Holds a node input definition.
    
    Attrs:
        Args:
            Specifies the given node script arguments.
        
        IsDevel:
            If True, the node is executed in development mode.
        
        Path:
            Specifies the path to the 'node_args.json' definition file.
        
        Version:
            Specifies the format version.
        
        CurrentWorkflowID:
            Specifies the workflow ID.
        
        ResultFilePath:
            Specifies the full path to current state of the result file.
        
        ExpectedResponsePath: str
            Specifies the full path to expected node response definition.
        
        NodeParameters: {str: str}
            Provided node parameters.
        
        Tables: (pyeds.scripting.Table,)
            Collection of defined tables.
    """
    
    
    def __init__(self, args):
        """
        Initializes a new instance of the NodeArgs.
        
        Args:
            args: [str]
                Node commandline arguments.
        """
        
        super().__init__()
        
        # get args
        self.Args = args
        self.IsDevel = args[1] == '-devel'
        
        # get main path
        if self.IsDevel:
            self.Path = 'node_args.json'
        else:
            self.Path = args[1]
        
        # init attributes
        self.Version = None
        self.CurrentWorkflowID = None
        self.ResultFilePath = None
        self.ExpectedResponsePath = None
        self.NodeParameters = {}
        
        # init containers
        self._tables = []
        
        # load data
        self._load()
        
        # lock
        self.Lock()
    
    
    @property
    def Tables(self):
        """
        Gets collection of defined tables:
        
        Returns:
            (pyeds.scripting.Table,)
        """
        
        return tuple(self._tables)
    
    
    def GetTable(self, table_name):
        """
        Gets existing table.
        
        Args:
            table_name: str
                Table display name.
        
        Returns:
            pyeds.scripting.Table
        """
        
        for tbl in self._tables:
            if tbl.TableName == table_name:
                return tbl
        
        message = "Specified table does not exist! --> '%s'" % table_name
        raise KeyError(message)
    
    
    def _load(self):
        """Loads data from NODE_ARGS JSON file."""
        
        # check path
        if not self.Path:
            message = "NODE_ARGS path is not specified!"
            raise IOError(message)
        
        if not os.path.exists(self.Path):
            message = "Specified NODE_ARGS path does not exist! --> '%s'" % self.Path
            raise IOError(message)
        
        # read data
        with open(self.Path, 'r') as rf:
            
            # load JSON
            data = json.load(rf)
            
            # get main attributes
            self.Version = data.get('Version', None)
            self.CurrentWorkflowID = data.get('CurrentWorkflowID', None)
            self.ResultFilePath = data.get('ResultFilePath', None)
            self.ExpectedResponsePath = data.get('ExpectedResponsePath', None)
            
            # get node params
            self.NodeParameters = data.get('NodeParameters', {})
            
            # get tables
            for tbl in data.get('Tables', []):
                
                # init table
                table = Table(
                    table_name = tbl['TableName'],
                    data_file = tbl['DataFile'],
                    data_format = tbl.get('DataFormat', CSV),
                    **tbl.get('Options', {}))
                
                # add columns
                for col in tbl.get('ColumnDescriptions', []):
                    
                    # init column
                    column = table.AddColumn(
                        column_name = col['ColumnName'],
                        data_type = col['DataType'],
                        id_name = col.get('ID', None),
                        **col.get('Options', {}))
                    
                    # lock column
                    column.Lock()
                    column.Options.Lock()
                
                # lock table
                table.Lock()
                
                # add table
                self._tables.append(table)
