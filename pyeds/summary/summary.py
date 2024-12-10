#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import os.path
import shutil
import random
import webbrowser
from ..eds import *
from ..review.helpers import *

# define constants
GRID_VISIBILITY = {0: 'none', 1: 'hidden', 4: 'visible'}
WORKFLOW_MESSAGE_KIND = {0: 'info', 1: 'verbose', 2: 'warning', 3: 'error', 4: 'progress', 5: 'progress', 6: 'temp', 7: 'hint'}
WORKFLOW_MESSAGE_CLASS = {0: '', 1: 'msg_temp', 2: 'msg_warning', 3: 'msg_error', 4: 'msg_temp', 5: 'msg_temp', 6: 'msg_temp', 7: 'hint'}


class Summary(object):
    """
    The pyeds.Summary class provides a useful utility to show details about the
    structure of given Magellan report file. While it provides several methods
    to insert and display details about selected structures only, the most
    easy ways is to call the 'ShowAll' method.
    """
    
    
    def __init__(self, report, folder="summary_data"):
        """
        Initializes a new instance of Summary.
        
        Args:
            report: str
                Path to the report file.
            
            folder: str
                Path to a folder were summary files will be placed.
        """
        
        self._folder = folder
        self._html_file = None
        self._css_file = None
        self._section_level = 0
        
        self._report_path = report
        self._eds = EDS(self._report_path)
    
    
    def __enter__(self):
        """Opens summary within 'with' statement."""
        
        self.Open()
        return self
    
    
    def __exit__(self, exc_ty, exc_val, tb):
        """Closes summary within 'with' statement ended."""
        
        self.Close()
    
    
    def Open(self):
        """Creates and opens summary files."""
        
        # check if opened
        if self._html_file is not None:
            return
        
        # ensure folder exists
        if not os.path.exists(self._folder):
            os.makedirs(self._folder)
        
        # get paths
        html_path = os.path.join(self._folder, "index.html")
        css_path = os.path.join(self._folder, "styles.css")
        
        # clear previous
        if os.path.exists(html_path):
            os.remove(html_path)
        
        if os.path.exists(css_path):
            os.remove(css_path)
        
        # open files
        self._html_file = open(html_path, "a", encoding='utf-8')
        self._css_file = open(css_path, "a", encoding='utf-8')
        
        # open EDS
        self._eds.Open()
        
        # initialize summary
        self._initialize()
    
    
    def Close(self):
        """Finalizes and closes all summary files."""
        
        # check if opened
        if self._html_file is None:
            return
        
        # finalize summary
        self._finalize()
        
        # close HTML file
        self._html_file.close()
        self._html_file = None
        
        # close CSS file
        self._css_file.close()
        self._css_file = None
        
        # close EDS
        self._eds.Close()
    
    
    def Show(self):
        """Shows current summary in browser."""
        
        # ensure finalized and closed
        self.Close()
        
        # get path
        path = os.path.join(self._folder, "index.html")
        path = os.path.abspath(path)
        
        # show in browser
        webbrowser.open('file://'+path, autoraise=1)
    
    
    def ShowAll(self):
        """Makes and shows full summary."""
        
        # make summary
        with self:
            self.InsertGraph()
            self.InsertDataTypesDetails()
            self.InsertConnectionsDetails()
            self.InsertEnumsDetails()
            self.InsertDistributionMapsDetails()
            self.InsertWorkflowsDetails()
        
        # show summary
        self.Show()
    
    
    def ShowSchema(self):
        """Makes and shows full schema."""
        
        # make summary
        with self:
            self.InsertGraph()
            self.InsertDataTypesDetails()
            self.InsertConnectionsDetails()
            self.InsertEnumsDetails()
            self.InsertDistributionMapsDetails()
        
        # show summary
        self.Show()
    
    
    def ShowWorkflows(self):
        """Makes and shows full workflows."""
        
        # make summary
        with self:
            self.InsertWorkflowsDetails()
        
        # show summary
        self.Show()
    
    
    def InsertHeader(self, text, _anchor=""):
        """
        Inserts given text as header of current section level.
        
        Args:
            text: str
                Header text.
        """
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # get level
        level = self._section_level + 1
        
        # get anchor
        if _anchor:
            _anchor = " id=\"%s\"" % _anchor
        
        # make HTML
        html = "  <h%s%s class=\"level%s\">%s</h%s>\n" % (level, _anchor, self._section_level, text, level)
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def OpenSection(self):
        """Opens sub-section."""
        
        # increase current level
        self._section_level += 1
    
    
    def CloseSection(self):
        """Closes sub-section."""
        
        # decrease current level
        if self._section_level:
            self._section_level -= 1
    
    
    def InsertGraph(self, show_enums=True, show_ddmaps=True):
        """Insets graph of all data types."""
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # init buffers
        nodes = []
        links = []
        
        dtypes_lookup = {}
        enums_lookup = {}
        ddmaps_lookup = {}
        
        # add data types
        data_types = self._eds.Report.DataTypes
        for item in data_types:
            dtypes_lookup[item.ID] = len(nodes)
            nodes.append({
                'id': (dtypes_lookup[item.ID], "%d"),
                'name': (item.Name, "\"%s\""),
                'display': (item.DisplayName, "\"%s\""),
                'anchor': ("DataTypeID%s" % item.ID, "\"%s\""),
                'type': ('n_dtype', "\"%s\""),
                'layer': (item.VisibilityStartingLayer, "%d"),
                'visible': (item.Visibility, "%d"),
                'count': (self._eds.Count(item.Name), "%d")
            })
        
        # add enums
        if show_enums:
            for item in self._eds.Report.EnumDataTypes:
                enums_lookup[item.ID] = len(nodes)
                nodes.append({
                    'id': (enums_lookup[item.ID], "%d"),
                    'name': (item.Name, "\"%s\""),
                    'display': (item.Name, "\"%s\""),
                    'anchor': ("EnumID%s" % item.ID, "\"%s\""),
                    'type': ('n_enum', "\"%s\""),
                    'layer': (-1, "%d"),
                    'visible': (-1, "%d"),
                    'count': (-1, "%d")
                })
        
        # add data distribution maps
        if show_ddmaps:
            for item in self._eds.Report.DataDistributionMaps:
                ddmaps_lookup[item.ID] = len(nodes)
                nodes.append({
                    'id': (ddmaps_lookup[item.ID], "%d"),
                    'name': (item.Name, "\"%s\""),
                    'display': (item.Name, "\"%s\""),
                    'anchor': ("DDMapID%s" % item.ID, "\"%s\""),
                    'type': ('n_ddmap', "\"%s\""),
                    'layer': (-1, "%d"),
                    'visible': (-1, "%d"),
                    'count': (-1, "%d")
                })
        
        # add connections
        for item in self._eds.Report.Connections:
            links.append({
                'source': (dtypes_lookup[item.DataTypeID1], "%d"),
                'target': (dtypes_lookup[item.DataTypeID2], "%d"),
                'source_id': (dtypes_lookup[item.DataTypeID1], "%d"),
                'target_id': (dtypes_lookup[item.DataTypeID2], "%d"),
                'anchor': (item.TableName, "\"%s\""),
                'type': ('l_dtype', "\"%s\""),
                'count': (self._eds.CountConnections(item.DataType1.Name, item.DataType2.Name), "%d")
            })
        
        # add links to enums and data distribution maps
        for item in data_types:
            for column in item.Columns:
                
                if show_enums and column.SpecialValueTypeName == 'Enum':
                    links.append({
                        'source': (dtypes_lookup[item.ID], "%d"),
                        'target': (enums_lookup[column.SpecialValueTypeID], "%d"),
                        'source_id': (dtypes_lookup[item.ID], "%d"),
                        'target_id': (enums_lookup[column.SpecialValueTypeID], "%d"),
                        'anchor': ("", "\"%s\""),
                        'type': ('l_enum', "\"%s\""),
                        'count': (-1, "%d")
                    })
                
                if show_ddmaps and column.SpecialValueTypeName == 'DataDistribution':
                    links.append({
                        'source': (dtypes_lookup[item.ID], "%d"),
                        'target': (ddmaps_lookup[column.SpecialValueTypeID], "%d"),
                        'source_id': (dtypes_lookup[item.ID], "%d"),
                        'target_id': (ddmaps_lookup[column.SpecialValueTypeID], "%d"),
                        'anchor': ("", "\"%s\""),
                        'type': ('l_ddmap', "\"%s\""),
                        'count': (-1, "%d")
                    })
        
        # make data file
        data_path = os.path.join(self._folder, "data.js")
        with open(data_path, "w", encoding='utf-8') as data_file:
            
            # add nodes
            data = "var nodesData = [\n"
            for node in nodes:
                
                attrs = []
                for attr in node:
                    value, form = node[attr]
                    form = "%s:%s" % (attr, form)
                    attrs.append(form % value)
                
                data += "  { %s },\n" % ", ".join(attrs)
            data += "];\n\n"
            
            # add links
            data += "var linksData = [\n"
            for link in links:
                
                attrs = []
                for attr in link:
                    value, form = link[attr]
                    form = "%s:%s" % (attr, form)
                    attrs.append(form % value)
                
                data += "  { %s },\n" % ", ".join(attrs)
            data += "];\n"
            
            # write to JS file
            data_file.write(data)
        
        # generate cache blocker
        uncache = ''.join(random.SystemRandom().choice('abcdefghijklmnopqrst') for i in range(5))
        
        # add graph container
        html = "  <div id=\"graph\" class=\"level%d\"></div>\n" % self._section_level
        html += "  <script type=\"text/javascript\" src=\"d3.min.js\"></script>\n"
        html += "  <script type=\"text/javascript\" src=\"data.js#%s\"></script>\n" % uncache
        html += "  <script type=\"text/javascript\" src=\"graph.js\"></script>\n\n"
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def InsertDataTypesDetails(self):
        """Inserts complete summary for defined data types."""
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # show data types
        self.InsertHeader("Data Types")
        self.InsertDataTypes()
        
        # show data types details
        self.OpenSection()
        for data_type in sorted(self._eds.Report.DataTypes, key=lambda x: x.Name):
            anchor = "DataTypeID%s" % data_type.ID
            header = "%s - <em>%s</em>" % (data_type.Name, data_type.DisplayName)
            
            # insert columns
            self.InsertHeader(header, _anchor=anchor)
            self.InsertDataTypeColumns(data_type.Name)
            
            # insert connections
            if data_type.Connections:
                self.OpenSection()
                self.InsertHeader("Connections")
                self.InsertDataTypeConnections(data_type.Name)
                self.CloseSection()
        
        self.CloseSection()
    
    
    def InsertDataTypes(self):
        """Adds table with all data types info."""
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # get data types
        data_types = self._eds.Report.DataTypes
        
        # init table
        html = "  <table class=\"level%d sortable\">\n" % self._section_level
        html += "    <thead>\n"
        html += "      <tr>\n"
        html += "        <th>ID</th>\n"
        html += "        <th>Available</th>\n"
        html += "        <th>Name</th>\n"
        html += "        <th>Table</th>\n"
        html += "        <th>Display Name</th>\n"
        html += "        <th>Description</th>\n"
        html += "        <th>Visibility</th>\n"
        html += "        <th>Layer</th>\n"
        html += "        <th>Items</th>\n"
        html += "        <th>GUID</th>\n"
        html += "      </tr>\n"
        html += "    </thead>\n"
        html += "    <tbody>\n"
        
        # add items
        for data_type in sorted(data_types, key=lambda x: x.Name):
            anchor = "DataTypeID%s" % data_type.ID
            pop = "onmouseover=\"highlightNode('#n_dtype_%s', true)\" onmouseout=\"highlightNode('#n_dtype_%s', false)\"" % (data_type.Name, data_type.Name)
            
            html += "      <tr>\n"
            html += "        <td class=\"right\">%s</td>\n" % data_type.ID
            html += "        <td class=\"center\">%s</td>\n" % data_type.IsAvailable
            html += "        <td><a href=\"#%s\" %s>%s</a></td>\n" % (anchor, pop, data_type.Name)
            html += "        <td><a href=\"#%s\" %s>%s</a></td>\n" % (anchor, pop, data_type.TableName)
            html += "        <td><a href=\"#%s\" %s>%s</a></td>\n" % (anchor, pop, data_type.DisplayName)
            html += "        <td>%s</td>\n" % data_type.Description
            html += "        <td class=\"center\">%s</td>\n" % GRID_VISIBILITY[data_type.Visibility]
            html += "        <td class=\"right\">%s</td>\n" % data_type.VisibilityStartingLayer
            html += "        <td class=\"right\">%s</td>\n" % self._eds.Count(data_type.Name)
            html += "        <td>%s</td>\n" % data_type.GUID
            html += "      </tr>\n"
        
        # finalize table
        html += "    </tbody>\n"
        html += "  </table>\n\n"
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def InsertDataTypeColumns(self, name):
        """Inserts table with data type columns."""
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # get data type
        data_type = self._eds.Report.GetDataType(name)
        
        # init table
        html = "  <table class=\"level%d sortable\">\n" % self._section_level
        html += "    <thead>\n"
        html += "      <tr>\n"
        html += "        <th>ID</th>\n"
        html += "        <th>Available</th>\n"
        html += "        <th>Name</th>\n"
        html += "        <th>Display Name</th>\n"
        html += "        <th>Description</th>\n"
        html += "        <th>Type</th>\n"
        html += "        <th>Special Type</th>\n"
        html += "        <th>Data Purpose</th>\n"
        html += "        <th>Visibility</th>\n"
        html += "        <th>Position</th>\n"
        html += "        <th>Formatting</th>\n"
        html += "        <th>Converter GUID</th>\n"
        html += "        <th>Control GUID</th>\n"
        html += "        <th>Extended Data</th>\n"
        html += "      </tr>\n"
        html += "    </thead>\n"
        html += "    <tbody>\n"
        
        # add items
        for column in sorted(data_type.Columns, key=lambda x: x.ColumnName):
            
            column_name = column.ColumnName
            if column.IsIDColumn:
                column_name = "<strong>%s</strong>" % column_name
            
            anchor = ""
            if column.SpecialValueTypeName == "DataDistribution":
                anchor = "DDMapID%s" % column.SpecialValueTypeID
            elif column.SpecialValueTypeName == "Enum":
                anchor = "EnumID%s" % column.SpecialValueTypeID
            
            nullable = "&nbsp;(?)" if column.Nullable else ""
            
            exdata = ("%s: %s" % (k, v) for k, v in column.ExtendedData.items())
            exdata = "; ".join(exdata)
            
            html += "      <tr>\n"
            html += "        <td class=\"right\">%s</td>\n" % column.ID
            html += "        <td class=\"center\">%s</td>\n" % column.IsAvailable
            html += "        <td>%s</td>\n" % column_name
            html += "        <td>%s</td>\n" % column.DisplayName
            html += "        <td>%s</td>\n" % column.Description
            html += "        <td class=\"center\">%s%s</td>\n" % (column.CustomDataType.Name, nullable)
            html += "        <td class=\"center\"><a href=\"#%s\">%s</a></td>\n" % (anchor, column.SpecialValueTypeName)
            html += "        <td>%s</td>\n" % column.DataPurpose
            html += "        <td class=\"center\">%s</td>\n" % GRID_VISIBILITY[column.DataVisibility]
            html += "        <td class=\"right\">%s</td>\n" % column.VisiblePosition
            html += "        <td class=\"right\">%s</td>\n" % column.FormatString
            html += "        <td>%s</td>\n" % column.ValueTypeGuid
            html += "        <td>%s</td>\n" % column.GridCellControlGuid
            html += "        <td>%s</td>\n" % exdata
            html += "      </tr>\n"
        
        # finalize table
        html += "    </tbody>\n"
        html += "  </table>\n\n"
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def InsertDataTypeConnections(self, name):
        """Inserts table with data type connections."""
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # get data type
        data_type = self._eds.Report.GetDataType(name)
        
        # init table
        html = "  <table class=\"level%d sortable\">\n" % self._section_level
        html += "    <thead>\n"
        html += "      <tr>\n"
        html += "        <th>ID</th>\n"
        html += "        <th>Available</th>\n"
        html += "        <th>Connected Type</th>\n"
        html += "        <th>Display Name</th>\n"
        html += "        <th>Table Name</th>\n"
        html += "        <th>Columns</th>\n"
        html += "        <th>Items</th>\n"
        html += "      </tr>\n"
        html += "    </thead>\n"
        html += "    <tbody>\n"
        
        # get connections
        connections = {}
        for conn in data_type.Connections:
            key = conn.DataType2 if conn.DataType1 is data_type else conn.DataType1
            connections[key] = conn
        
        # add items
        for data_type in sorted(connections, key=lambda x: x.Name):
            conn = connections[data_type]
            anchor1 = "DataTypeID%s" % data_type.ID
            anchor2 = conn.TableName
            columns = ", ".join(x.ColumnName for x in conn.Columns)
            
            html += "      <tr>\n"
            html += "        <td class=\"right\">%s</td>\n" % data_type.ID
            html += "        <td class=\"center\">%s</td>\n" % data_type.IsAvailable
            html += "        <td><a href=\"#%s\">%s</a></td>\n" % (anchor1, data_type.Name)
            html += "        <td><a href=\"#%s\">%s</a></td>\n" % (anchor1, data_type.DisplayName)
            html += "        <td><a href=\"#%s\">%s</a></td>\n" % (anchor2, conn.TableName)
            html += "        <td>%s</td>\n" % columns
            html += "        <td class=\"right\">%s</td>\n" % self._eds.CountConnections(conn.DataType1.Name, conn.DataType2.Name)
            html += "      </tr>\n"
        
        # finalize table
        html += "    </tbody>\n"
        html += "  </table>\n\n"
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def InsertConnectionsDetails(self):
        """Inserts complete summary for defined data types connections."""
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # show connections
        self.InsertHeader("Data Type Connections")
        self.InsertConnections()
        
        # show connections details
        self.OpenSection()
        for conn in sorted(self._eds.Report.Connections, key=lambda x: x.TableName):
            if conn.Columns:
                header = "%s &rarr; %s" % (conn.DataType1.Name, conn.DataType2.Name)
                anchor = conn.TableName
                self.InsertHeader(header, _anchor=anchor)
                self.InsertConnectionColumns(conn.DataType1.Name, conn.DataType2.Name)
        
        self.CloseSection()
    
    
    def InsertConnections(self):
        """Adds table with all connections info."""
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # get connections
        connections = self._eds.Report.Connections
        
        # init table
        html = "  <table class=\"level%d sortable\">\n" % self._section_level
        html += "    <thead>\n"
        html += "      <tr>\n"
        html += "        <th>Connected Type 1</th>\n"
        html += "        <th>Connected Type 2</th>\n"
        html += "        <th>Table Name</th>\n"
        html += "        <th>Items</th>\n"
        html += "      </tr>\n"
        html += "    </thead>\n"
        html += "    <tbody>\n"
        
        # add items
        for conn in sorted(connections, key=lambda x: x.TableName):
            anchor1 = "DataTypeID%s" % conn.DataTypeID1
            anchor2 = "DataTypeID%s" % conn.DataTypeID2
            anchor3 = conn.TableName
            
            html += "      <tr>\n"
            html += "        <td><a href=\"#%s\">%s</a></td>\n" % (anchor1, conn.DataType1.Name)
            html += "        <td><a href=\"#%s\">%s</a></td>\n" % (anchor2, conn.DataType2.Name)
            html += "        <td><a href=\"#%s\">%s</a></td>\n" % (anchor3, conn.TableName)
            html += "        <td class=\"right\">%s</td>\n" % self._eds.CountConnections(conn.DataType1.Name, conn.DataType2.Name)
            html += "      </tr>\n"
        
        # finalize table
        html += "    </tbody>\n"
        html += "  </table>\n\n"
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def InsertConnectionColumns(self, name1, name2):
        """Inserts table with connection columns."""
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # get data type
        connection = self._eds.Report.GetConnection(name1, name2)
        
        # init table
        html = "  <table class=\"level%d sortable\">\n" % self._section_level
        html += "    <thead>\n"
        html += "      <tr>\n"
        html += "        <th>ID</th>\n"
        html += "        <th>Available</th>\n"
        html += "        <th>Name</th>\n"
        html += "        <th>Display Name</th>\n"
        html += "        <th>Description</th>\n"
        html += "        <th>Type</th>\n"
        html += "        <th>Special Type</th>\n"
        html += "        <th>Data Purpose</th>\n"
        html += "        <th>Visibility</th>\n"
        html += "        <th>Position</th>\n"
        html += "        <th>Formatting</th>\n"
        html += "        <th>Control GUID</th>\n"
        html += "      </tr>\n"
        html += "    </thead>\n"
        html += "    <tbody>\n"
        
        # add items
        for column in sorted(connection.Columns, key=lambda x: x.ColumnName):
            
            column_name = column.ColumnName
            if column.IsIDColumn:
                column_name = "<strong>%s</strong>" % column_name
            
            anchor = ""
            if column.SpecialValueTypeName == "DataDistribution":
                anchor = "DDMapID%s" % column.SpecialValueTypeID
            elif column.SpecialValueTypeName == "Enum":
                anchor = "EnumID%s" % column.SpecialValueTypeID
            
            nullable = "&nbsp;(?)" if column.Nullable else ""
            
            html += "      <tr>\n"
            html += "        <td class=\"right\">%s</td>\n" % column.ID
            html += "        <td class=\"center\">%s</td>\n" % column.IsAvailable
            html += "        <td>%s</td>\n" % column_name
            html += "        <td>%s</td>\n" % column.DisplayName
            html += "        <td>%s</td>\n" % column.Description
            html += "        <td class=\"center\">%s%s</td>\n" % (column.CustomDataType.Name, nullable)
            html += "        <td class=\"center\"><a href=\"#%s\">%s</a></td>\n" % (anchor, column.SpecialValueTypeName)
            html += "        <td>%s</td>\n" % column.DataPurpose
            html += "        <td class=\"center\">%s</td>\n" % GRID_VISIBILITY[column.DataVisibility]
            html += "        <td class=\"right\">%s</td>\n" % column.VisiblePosition
            html += "        <td class=\"right\">%s</td>\n" % column.FormatString
            html += "        <td>%s</td>\n" % column.GridCellControlGuid
            html += "      </tr>\n"
        
        # finalize table
        html += "    </tbody>\n"
        html += "  </table>\n\n"
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def InsertEnumsDetails(self):
        """Inserts complete summary for defined enum data types."""
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # show enums
        self.InsertHeader("Enum Data Types")
        self.InsertEnums()
        
        # show enums details
        self.OpenSection()
        for enum in sorted(self._eds.Report.EnumDataTypes, key=lambda x: x.Name):
            anchor = "EnumID%s" % enum.ID
            self.InsertHeader("%s (%s)" % (enum.Name, enum.TypeName), _anchor=anchor)
            self.InsertEnumElements(enum.ID)
        
        self.CloseSection()
    
    
    def InsertEnums(self):
        """Inserts table with defined enum types."""
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # get enums
        enums = self._eds.Report.EnumDataTypes
        
        # init table
        html = "  <table class=\"level%d sortable\">\n" % self._section_level
        html += "    <thead>\n"
        html += "      <tr>\n"
        html += "        <th>ID</th>\n"
        html += "        <th>Name</th>\n"
        html += "        <th>Type Name</th>\n"
        html += "        <th>Flags</th>\n"
        html += "        <th>CV Reference</th>\n"
        html += "        <th>CV ID</th>\n"
        html += "        <th>CV Name</th>\n"
        html += "        <th>CV Definition</th>\n"
        html += "      </tr>\n"
        html += "    </thead>\n"
        html += "    <tbody>\n"
        
        # add items
        for enum in sorted(enums, key=lambda x: x.Name):
            anchor = "EnumID%s" % enum.ID
            
            html += "      <tr>\n"
            html += "        <td class=\"right\">%s</td>\n" % enum.ID
            html += "        <td><a href=\"#%s\">%s</a></td>\n" % (anchor, enum.Name)
            html += "        <td><a href=\"#%s\">%s</a></td>\n" % (anchor, enum.TypeName)
            html += "        <td class=\"center\">%s</td>\n" % bool(enum.IsFlagsEnum)
            html += "        <td>%s</td>\n" % enum.CVReference
            html += "        <td>%s</td>\n" % enum.CVTermId
            html += "        <td>%s</td>\n" % enum.CVTermName
            html += "        <td>%s</td>\n" % enum.CVTermDefinition
            html += "      </tr>\n"
        
        # finalize table
        html += "    </tbody>\n"
        html += "  </table>\n\n"
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def InsertEnumElements(self, enum_id):
        """Inserts table with enum elements."""
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # get enum elements
        enums = self._eds.Report.EnumDataTypes
        enum = next(x for x in enums if x.ID == enum_id)
        elements = enum.Elements
        
        # init table
        html = "  <table class=\"level%d sortable\">\n" % self._section_level
        html += "    <thead>\n"
        html += "      <tr>\n"
        html += "        <th>Value</th>\n"
        html += "        <th>Display Name</th>\n"
        html += "        <th>Abbreviation</th>\n"
        html += "        <th>CV Reference</th>\n"
        html += "        <th>CV ID</th>\n"
        html += "        <th>CV Name</th>\n"
        html += "        <th>CV Definition</th>\n"
        html += "      </tr>\n"
        html += "    </thead>\n"
        html += "    <tbody>\n"
        
        # add items
        for element in sorted(elements, key=lambda x: x.Value):
            html += "      <tr>\n"
            html += "        <td class=\"right\">%s</td>\n" % element.Value
            html += "        <td>%s</td>\n" % element.DisplayName
            html += "        <td>%s</td>\n" % element.Abbreviation
            html += "        <td>%s</td>\n" % element.CVReference
            html += "        <td>%s</td>\n" % element.CVTermId
            html += "        <td>%s</td>\n" % element.CVTermName
            html += "        <td>%s</td>\n" % element.CVTermDefinition
            html += "      </tr>\n"
        
        # finalize table
        html += "    </tbody>\n"
        html += "  </table>\n\n"
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def InsertDistributionMapsDetails(self):
        """Inserts complete summary for defined data distribution maps."""
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # show distribution maps
        self.InsertHeader("Data Distribution Maps")
        self.InsertDistributionMaps()
        
        # show distribution maps details
        self.OpenSection()
        for ddmap in sorted(self._eds.Report.DataDistributionMaps, key=lambda x: x.Name):
            anchor = "DDMapID%s" % ddmap.ID
            self.InsertHeader(ddmap.Name, _anchor=anchor)
            self.InsertDistributionMapBoxes(ddmap.ID)
            self.InsertDistributionMapLevels(ddmap.ID)
        
        self.CloseSection()
    
    
    def InsertDistributionMaps(self):
        """Inserts table with defined data distribution maps."""
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # get data distribution maps
        ddmaps = self._eds.Report.DataDistributionMaps
        
        # init table
        html = "  <table class=\"level%d sortable\">\n" % self._section_level
        html += "    <thead>\n"
        html += "      <tr>\n"
        html += "        <th>ID</th>\n"
        html += "        <th>Name</th>\n"
        html += "        <th>Category Names</th>\n"
        html += "        <th>Description</th>\n"
        html += "        <th>Type</th>\n"
        html += "        <th>Minimum</th>\n"
        html += "        <th>Maximum</th>\n"
        html += "        <th>Semantic Terms</th>\n"
        html += "      </tr>\n"
        html += "    </thead>\n"
        html += "    <tbody>\n"
        
        # add items
        for ddmap in sorted(ddmaps, key=lambda x: x.Name):
            anchor = "DDMapID%s" % ddmap.ID
            
            html += "      <tr>\n"
            html += "        <td class=\"right\">%s</td>\n" % ddmap.ID
            html += "        <td><a href=\"#%s\">%s</a></td>\n" % (anchor, ddmap.Name)
            html += "        <td>%s / %s / %s</td>\n" % (ddmap.SingularCategoryName, ddmap.PluralCategoryName, ddmap.LevelCategoryName)
            html += "        <td>%s</td>\n" % ddmap.Description
            html += "        <td>%s</td>\n" % ddmap.CustomDataType.Name
            html += "        <td class=\"right\">%s</td>\n" % ddmap.MinimumValue
            html += "        <td class=\"right\">%s</td>\n" % ddmap.MaximumValue
            html += "        <td>%s</td>\n" % ddmap.SemanticTerms
            html += "      </tr>\n"
        
        # finalize table
        html += "    </tbody>\n"
        html += "  </table>\n\n"
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def InsertDistributionMapBoxes(self, ddmap_id):
        """Inserts table with data distribution map boxes."""
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # get map boxes
        ddmaps = self._eds.Report.DataDistributionMaps
        ddmap = next(x for x in ddmaps if x.ID == ddmap_id)
        boxes = ddmap.Boxes
        
        # init table
        html = "  <table class=\"level%d sortable\">\n" % self._section_level
        html += "    <thead>\n"
        html += "      <tr>\n"
        html += "        <th>ID</th>\n"
        html += "        <th>Box Name</th>\n"
        html += "        <th>Position</th>\n"
        html += "        <th>Group 1st</th>\n"
        html += "        <th>Description</th>\n"
        html += "        <th>Semantic Terms</th>\n"
        html += "        <th>Color</th>\n"
        html += "      </tr>\n"
        html += "    </thead>\n"
        html += "    <tbody>\n"
        
        # add items
        for box in sorted(boxes, key=lambda x: x.Position):
            color = "rgba(%d,%d,%d,%.2f)" % (rgba_from_argb_int(box.Color))
            
            html += "      <tr>\n"
            html += "        <td class=\"right\">%s</td>\n" % box.ID
            html += "        <td>%s</td>\n" % box.Name
            html += "        <td class=\"right\">%s</td>\n" % box.Position
            html += "        <td class=\"center\">%s</td>\n" % bool(box.IsFirstInGroup)
            html += "        <td>%s</td>\n" % box.Description
            html += "        <td>%s</td>\n" % box.SemanticTerms
            html += "        <td class=\"nopadding\" style=\"background-color: %s;\" title=\"%s\">&nbsp;</td>\n" % (color, color)
            html += "      </tr>\n"
        
        # finalize table
        html += "    </tbody>\n"
        html += "  </table>\n\n"
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def InsertDistributionMapLevels(self, ddmap_id):
        """Inserts table with data distribution map levels."""
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # get map levels
        ddmaps = self._eds.Report.DataDistributionMaps
        ddmap = next(x for x in ddmaps if x.ID == ddmap_id)
        levels = ddmap.Levels
        
        # init table
        html = "  <table class=\"level%d sortable\">\n" % self._section_level
        html += "    <thead>\n"
        html += "      <tr>\n"
        html += "        <th>ID</th>\n"
        html += "        <th>Level Name</th>\n"
        html += "        <th>Position</th>\n"
        html += "        <th>Description</th>\n"
        html += "        <th>Threshold</th>\n"
        html += "        <th>Semantic Terms</th>\n"
        html += "        <th>Color</th>\n"
        html += "      </tr>\n"
        html += "    </thead>\n"
        html += "    <tbody>\n"
        
        # add items
        for level in sorted(levels, key=lambda x: x.Position):
            color = "rgba(%d,%d,%d,%.2f)" % (rgba_from_argb_int(level.Color))
            
            html += "      <tr>\n"
            html += "        <td class=\"right\">%s</td>\n" % level.ID
            html += "        <td>%s</td>\n" % level.Name
            html += "        <td class=\"right\">%s</td>\n" % level.Position
            html += "        <td>%s</td>\n" % level.Description
            html += "        <td class=\"right\">%s</td>\n" % level.Threshold
            html += "        <td>%s</td>\n" % level.SemanticTerms
            html += "        <td class=\"nopadding\" style=\"background-color: %s;\" title=\"%s\">&nbsp;</td>\n" % (color, color)
            html += "      </tr>\n"
        
        # finalize table
        html += "    </tbody>\n"
        html += "  </table>\n\n"
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def InsertWorkflowsDetails(self):
        """Inserts complete summary for defined workflows."""
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # show workflows
        self.InsertHeader("Workflows")
        self.InsertWorkflows()
        
        # show data types details
        self.OpenSection()
        for workflow in self._eds.Report.Workflows:
            anchor = "WorkflowID%s" % workflow.ID
            
            # insert nodes
            self.InsertHeader("%s - Nodes" % workflow.Name, _anchor=anchor)
            self.InsertWorkflowNodes(workflow.ID)
            
            # insert node params
            self.OpenSection()
            for node in sorted(workflow.Nodes, key=lambda x:x.Name):
                anchor = "WorkflowNodeID%s_%s" % (workflow.ID, node.ID)
                
                # insert nodes
                self.InsertHeader(node.Name, _anchor=anchor)
                self.InsertWorkflowNodeParams(workflow.ID, node.ID)
            
            self.CloseSection()
            
            # insert messages
            self.InsertHeader("%s - Messages" % workflow.Name)
            self.InsertWorkflowMessages(workflow.ID)
        
        self.CloseSection()
    
    
    def InsertWorkflows(self):
        """Inserts table with defined workflows."""
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # get workflows
        workflows = self._eds.Report.Workflows
        
        # init table
        html = "  <table class=\"level%d sortable\">\n" % self._section_level
        html += "    <thead>\n"
        html += "      <tr>\n"
        html += "        <th>ID</th>\n"
        html += "        <th>Type</th>\n"
        html += "        <th>Name</th>\n"
        html += "        <th>Description</th>\n"
        html += "        <th>Study</th>\n"
        html += "        <th>User</th>\n"
        html += "        <th>Software</th>\n"
        html += "        <th>Machine</th>\n"
        html += "        <th>Date</th>\n"
        html += "      </tr>\n"
        html += "    </thead>\n"
        html += "    <tbody>\n"
        
        # add items
        for workflow in workflows:
            anchor = "WorkflowID%s" % workflow.ID
            
            html += "      <tr>\n"
            html += "        <td class=\"right\">%s</td>\n" % workflow.ID
            html += "        <td>%s</td>\n" % workflow.Type
            html += "        <td><a href=\"#%s\">%s</a></td>\n" % (anchor, workflow.Name)
            html += "        <td>%s</td>\n" % workflow.Description
            html += "        <td>%s</td>\n" % workflow.Study
            html += "        <td>%s</td>\n" % workflow.User
            html += "        <td>%s</td>\n" % workflow.Software
            html += "        <td>%s</td>\n" % workflow.Machine
            html += "        <td>%s</td>\n" % workflow.Date.strftime("%Y-%m-%d %H:%M:%S")
            html += "      </tr>\n"
        
        # finalize table
        html += "    </tbody>\n"
        html += "  </table>\n\n"
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def InsertWorkflowNodes(self, workflow_id):
        """Inserts table with workflow nodes."""
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # get workflow nodes
        workflows = self._eds.Report.Workflows
        workflow = next(x for x in workflows if x.ID == workflow_id)
        nodes = workflow.Nodes
        
        # init table
        html = "  <table class=\"level%d sortable\">\n" % self._section_level
        html += "    <thead>\n"
        html += "      <tr>\n"
        html += "        <th>ID</th>\n"
        html += "        <th>Name</th>\n"
        html += "        <th>Display Name</th>\n"
        html += "        <th>Description</th>\n"
        html += "        <th>Category</th>\n"
        html += "        <th>Publisher</th>\n"
        html += "        <th>Version</th>\n"
        html += "        <th>ParentNodes</th>\n"
        html += "        <th>GUID</th>\n"
        html += "      </tr>\n"
        html += "    </thead>\n"
        html += "    <tbody>\n"
        
        # add items
        for node in sorted(nodes, key=lambda x: x.Name):
            anchor = "WorkflowNodeID%s_%s" % (workflow.ID, node.ID)
            
            html += "      <tr>\n"
            html += "        <td class=\"right\">%s</td>\n" % node.ID
            html += "        <td><a href=\"#%s\">%s</a></td>\n" % (anchor, node.Name)
            html += "        <td class=\"nowrap\"><a href=\"#%s\">%s</a></td>\n" % (anchor, node.DisplayName)
            html += "        <td>%s</td>\n" % node.Description
            html += "        <td>%s</td>\n" % node.Category
            html += "        <td>%s</td>\n" % node.Publisher
            html += "        <td class=\"center\">%s.%s</td>\n" % (node.MainVersion, node.MinorVersion)
            html += "        <td>%s</td>\n" % str(node.ParentNodes)
            html += "        <td>%s</td>\n" % node.GUID
            html += "      </tr>\n"
        
        # finalize table
        html += "    </tbody>\n"
        html += "  </table>\n\n"
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def InsertWorkflowNodeParams(self, workflow_id, node_id):
        """Inserts table with workflow node parameters."""
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # get workflow node params
        workflows = self._eds.Report.Workflows
        workflow = next(x for x in workflows if x.ID == workflow_id)
        node = next(x for x in workflow.Nodes if x.ID == node_id)
        params = node.Parameters
        
        # init table
        html = "  <table class=\"level%d sortable\">\n" % self._section_level
        html += "    <thead>\n"
        html += "      <tr>\n"
        html += "        <th>Name</th>\n"
        html += "        <th>Display Name</th>\n"
        html += "        <th>Category</th>\n"
        html += "        <th>Purpose</th>\n"
        html += "        <th>DisplayValue</th>\n"
        html += "      </tr>\n"
        html += "    </thead>\n"
        html += "    <tbody>\n"
        
        # add items
        for param in sorted(params, key=lambda x:(x.Category, x.DisplayName)):
            html += "      <tr>\n"
            html += "        <td>%s</td>\n" % param.Name
            html += "        <td>%s</td>\n" % param.DisplayName
            html += "        <td>%s</td>\n" % param.Category
            html += "        <td>%s</td>\n" % param.Purpose
            html += "        <td>%s</td>\n" % param.DisplayValue
            html += "      </tr>\n"
        
        # finalize table
        html += "    </tbody>\n"
        html += "  </table>\n\n"
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def InsertWorkflowMessages(self, workflow_id):
        """Inserts table with workflow messages."""
        
        # assert open
        self._assert_opened()
        
        # open section if necessary
        if not self._section_level:
            self.OpenSection()
        
        # get workflow messages
        workflows = self._eds.Report.Workflows
        workflow = next(x for x in workflows if x.ID == workflow_id)
        messages = workflow.Messages
        
        # init table
        html = "  <table class=\"level%d sortable\">\n" % self._section_level
        html += "    <thead>\n"
        html += "      <tr>\n"
        html += "        <th>ID</th>\n"
        html += "        <th>Time</th>\n"
        html += "        <th>Node Name</th>\n"
        html += "        <th>Kind</th>\n"
        html += "        <th>Message</th>\n"
        html += "      </tr>\n"
        html += "    </thead>\n"
        html += "    <tbody>\n"
        
        # add items
        for msg in sorted(messages, key=lambda x: x.Time):
            color = WORKFLOW_MESSAGE_CLASS[msg.Kind]
            
            html += "      <tr>\n"
            html += "        <td class=\"right\">%s</td>\n" % msg.ID
            html += "        <td class=\"nowrap\">%s</td>\n" % msg.Time.strftime("%Y-%m-%d %H:%M:%S")
            html += "        <td class=\"nowrap\">%s</td>\n" % msg.NodeName
            html += "        <td class=\"%s\">%s</td>\n" % (color, WORKFLOW_MESSAGE_KIND[msg.Kind])
            html += "        <td>%s</td>\n" % msg.Message
            html += "      </tr>\n"
        
        # finalize table
        html += "    </tbody>\n"
        html += "  </table>\n\n"
        
        # write to HTML file
        self._html_file.write(html)
    
    
    def _assert_opened(self):
        """Asserts HTML file is opened."""
        
        if self._html_file is None:
            raise ValueError("Summary file is not opened!")
    
    
    def _initialize(self):
        """Initializes summary file."""
        
        # init HTML
        html = '<?xml version="1.0" encoding="utf-8"?>\n'
        html += '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
        html += '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n'
        html += '<head>\n'
        html += '  <meta http-equiv="content-type" content="text/html; charset=utf-8" />\n'
        html += '  <title>Summary for: %s</title>\n' % self._report_path
        html += '  <link rel="stylesheet" type="text/css" media="all" href="styles.css" />\n'
        html += '  <script type="text/javascript" src="scripts.js"></script>\n'
        html += '</head>\n'
        html += '\n'
        html += '<body>\n'
        html += '  <h1>Summary for: %s</h1>\n\n' % self._report_path
        
        # write to HTML file
        self._html_file.write(html)
        
        # read main CSS
        src_path = os.path.join(os.path.dirname(__file__), "styles.css")
        with open(src_path) as f:
            css = f.read()
        
        # write to CSS file
        self._css_file.write(css)
        
        # copy scripts
        src_path = os.path.join(os.path.dirname(__file__), "scripts.js")
        dst_path = os.path.join(self._folder, "scripts.js")
        shutil.copy(src_path, dst_path)
        
        src_path = os.path.join(os.path.dirname(__file__), "graph.js")
        dst_path = os.path.join(self._folder, "graph.js")
        shutil.copy(src_path, dst_path)
        
        src_path = os.path.join(os.path.dirname(__file__), "d3.min.js")
        dst_path = os.path.join(self._folder, "d3.min.js")
        shutil.copy(src_path, dst_path)
    
    
    def _finalize(self):
        """Finalizes summary file."""
        
        # finalize HTML
        html = '</body>\n'
        html += '</html>\n'
        
        # write to HTML file
        self._html_file.write(html)
