#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import os.path
import json
import re
from .enums import *
from .table import Table
from ..report import Lockable


class Response(Lockable):
    """
    Holds a node output definition.
    
    Attrs:
        Path:
            Specifies the path to the 'node_response.json' definition file.
        
        WorkingDir: str
            Current working directory (derived from the node response file path).
        
        Tables: (pyeds.scripting.Table, )
            Collection of defined tables.
    """
    
    
    def __init__(self, data_file):
        """Initializes a new instance of the Response."""
        
        super().__init__()
        
        # init attributes
        self.Path = data_file
            
        # set working directory
        (self.WorkingDir, _) = os.path.split(self.Path)
        
        # init containers
        self._tables = []
    
    
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
    
    
    def AddTable(self, table_name):
        """
        Adds new table definition to node response.
        
        Args:
            table_name: str
                Specifies the table display name.
        
        Returns:
            pyeds.scripting.Table
                Initialized table definition.
        """
        
        # check lock
        self.AssertUnlocked()
        
        # check name
        for tbl in self._tables:
            if tbl.TableName == table_name:
                message = "Table with the same name already exists! --> '%s'" % table_name
                raise KeyError(message)
        
        # init path
        data_file = re.sub(INVALID_CHARS, "_", table_name).rstrip(". ")[:255]
        data_file = os.path.join(self.WorkingDir, f"{data_file}.txt")
        
        # create table
        table = Table(
            table_name = table_name,
            data_file = data_file,
            data_format = CSV)
        
        # add
        self._tables.append(table)
        
        return table
    
    
    def AddConnection(self, table_name, first_table, second_table):
        """
        Adds new table definition to node response.
        
        Args:
            table_name: str
                Specifies the table display name.
            
            first_table: str
                Specifies the display name of the first table to be connected.
            
            second_table: str
                Specifies the display name of the second table to be connected.
        
        Returns:
            pyeds.scripting.Table
                Initialized table definition.
        """
        
        # check lock
        self.AssertUnlocked()
        
        # check name
        for tbl in self._tables:
            if tbl.TableName == table_name:
                message = "Table with the same name already exists! --> '%s'" % table_name
                raise KeyError(message)
        
        # init path
        data_file = re.sub(INVALID_CHARS, "_", table_name).rstrip(". ")[:255]
        data_file = os.path.join(self.WorkingDir, f"{data_file}.txt")
        
        # create table
        table = Table(
            table_name = table_name,
            data_file = data_file,
            data_format = CSV_CONN,
            FirstTable = first_table,
            SecondTable = second_table)
        
        # add
        self._tables.append(table)
        
        return table
    
    
    def ToJSON(self):
        """
        Converts response definition to JSON-like object.
        
        Returns:
            {}
        """
        
        # init data
        data = {'Tables': []}
        
        # add tables
        for tbl in self._tables:
            table = tbl.ToJSON()
            if table:
                data['Tables'].append(table)
        
        return data
    
    
    def Export(self):
        """Saves node response definition and table data."""
        
        self.ExportResponse()
        self.ExportTables()
    
    
    def ExportResponse(self):
        """Saves node response definition."""
        
        with open(self.Path, 'w', encoding='utf-8') as wf:
            json.dump(self.ToJSON(), wf, ensure_ascii=False, indent=4)
    
    
    def ExportTables(self):
        """Saves all table data."""
        
        for table in self._tables:
            table.Export()
