#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import datetime
from ..report import Report, VIEW_FILE_TAG
from ..report import utils
from .entity import EntityItem
from .prop import PropertyValue
from .query import EDSQuery


class EDS(object):
    """
    The pyeds.EDS class provides the main data reading functionality to retrieve
    data from Magellan report files. The reading automatically handles correct
    data conversion of retrieved properties and uses appropriate connection
    tables when connected data are retrieved.
    
    Please note that the 'query' provided for filtered reading is not a real SQL
    statement but rather its simplified version. It is now limited just to use
    the column names, simple values defined by '[A-Za-z0-9-_\.%]+', quotes for
    more complicated values and column names, grouping by '()' and following
    operators:
        'AND | OR'
        'IS NULL | IS NOT NULL'
        'IN () | NOT IN ()'
        '<= | >= | != | = | < | > | LIKE'.
    
    Attributes:
        
        Report: pyeds.Report
            Current report file.
    """
    
    
    def __init__(self, report):
        """
        Initializes a new instance of EDS.
        
        Args:
            report: str
                Path to the report file to open.
        """
        
        # init report file
        self._report = Report(report)
    
    
    def __enter__(self):
        """Opens report file connection within 'with' statement."""
        
        self.Open()
        return self
    
    
    def __exit__(self, exc_ty, exc_val, tb):
        """Closes report file connection when 'with' statement ended."""
        
        self.Close()
    
    
    @property
    def Report(self):
        """
        Gets current report file.
        
        Returns:
            pyeds.Report
                Current report file.
        """
        
        return self._report
    
    
    def Open(self):
        """Opens report file connection."""
        
        self._report.Open()
    
    
    def Close(self):
        """Closes report file connection."""
        
        self._report.Close()
    
    
    def GetPath(self, from_entity, to_entity, via=()):
        """
        Gets the shortest connection path between two data types. Please note
        that if there are multiple paths available with the same length it is
        rather undefined, which one is taken. Be sure to use 'via' to get
        requested path.
        
        Args:
            from_entity: str
                Starting data type name.
            
            to_entity: str
                Final data type name.
            
            via: (str,)
                Names of data types required within the path. Note that order
                is not guaranteed.
        
        Returns:
            (str,)
                Sequence of data types names defining the path.
        """
        
        # get data types
        data_type1 = self._report.GetDataType(from_entity)
        data_type2 = self._report.GetDataType(to_entity)
        
        # prepare via
        via = set(self._replace_entity_names(via))
        
        # init buffers
        best_path = None
        best_length = [len(self._report.DataTypes) + 1]
        
        # generate all possible paths
        for path in self._get_paths(data_type1, data_type2, best_length):
            
            # use names only
            path = [x.Name for x in path]
            
            # check if path contains requested data types in-between
            if not via.issubset(path):
                continue
            
            # take shortest
            if not best_path or len(best_path) > len(path):
                best_path = path
                best_length[0] = len(path)
        
        return tuple(best_path)
    
    
    def Count(self, entity, query=None):
        """
        Gets number of items (rows) for given data type.
        
        Args:
            entity: str
                Data type name.
            
            query: str or None
                Items filter.
        
        Returns:
            int
                Number of items.
        """
        
        # get data type
        data_type = self._report.GetDataType(entity)
        
        # count items
        return self._count_items(data_type, query)
    
    
    def CountConnections(self, entity1, entity2, query=None):
        """
        Gets number of connections between specified data type.
        
        Args:
            entity1: str
                Data type name.
            
            entity2: str
                Data type name.
            
            query: str or None
                Connection properties filter.
        
        Returns:
            int
                Number of connections.
        """
        
        # get data type
        data_type1 = self._report.GetDataType(entity1)
        connection = data_type1.GetConnection(entity2)
        
        # count items
        return self._count_items(connection, query)
    
    
    def Read(self, entity, query=None, properties=None, exclude=None, order=None, desc=False, limit=None, offset=0):
        """
        Reads items for specified data type.
        
        Args:
            entity: str
                Data type name.
            
            query: str or None
                Items filter.
            
            properties: (str,) or None
                Names of properties to read. Note that ID properties are always
                retrieved. If set to None, all available properties are
                retrieved.
            
            exclude: (str,) or None
                Names of properties to ignore.
            
            order: str or None
                Property name to use for sorting.
            
            desc: bool
                Use descending order.
            
            limit: int or None
                Number of items to read.
            
            offset: int
                Starting item position.
        
        Yields:
            iter(pyeds.EntityItem,)
                Items iterator.
        """
        
        # make query
        query = self._get_query(query, order, desc, limit, offset)
        
        # read items
        return self._read_items(
            entity = entity,
            query = query,
            include = properties,
            exclude = exclude)
    
    
    def ReadConnected(self, entity, parent, query=None, properties=None, exclude=None, order=None, desc=False, limit=None, offset=0):
        """
        Reads items of specified data type directly connected to given parent.
        This method also retrieves all the connection properties and stores them
        along the own properties of the child item.
        
        Args:
            entity: str
                Data type name.
            
            parent: pyeds.EntityItem
                Parent entity item.
                
            query: str or None
                Items filter.
            
            properties: (str,) or None
                Names of properties to read. Note that ID properties are always
                retrieved. If set to None, all available properties are
                retrieved.
            
            exclude: (str,) or None
                Names of properties to ignore.
            
            order: str or None
                Property name to use for sorting.
            
            desc: bool
                Use descending order.
            
            limit: int or None
                Number of items to read.
            
            offset: int
                Starting item position.
        
        Yields:
            iter(pyeds.EntityItem,)
                Items iterator.
        """
        
        # make query
        query = self._get_query(query, order, desc, limit, offset)
        
        # read items
        return self._read_connected(
            entity = entity,
            parent = parent,
            query = query,
            include = properties,
            exclude = exclude)
    
    
    def ReadHierarchy(self, path, parent=None, keep=None, queries=None, properties=None, excludes=None, orders=None, descs=None, limits=None, offsets=None):
        """
        Reads full hierarchy of items along specified path. For each returned
        item the hierarchy can be accessed via its 'Children' property. This
        method also retrieves all the connection properties and stores them
        along the own properties of the child item.
        
        If a parent item is provided, only the hierarchy of items connected to
        the parent are retrieved. This method then returns iterator over the
        nearest children as defined by the path.
        
        The parameters of this method are logically the same as for the standard
        reading. However, to be able to specify them independently for data
        types along given path, they must be provided as dictionaries, where
        the key is the data type name. If not, they will be applied just to
        the first data type in the path.
        
        Args:
            path: (str,)
                Ordered sequence of data types names defining direct connections
                between items to read.
            
            parent: pyeds.EntityItem or None
                Parent entity item.
                
            keep: (str,)
                List of data types names for which the data should be kept. If
                not set, all data types in the path will be returned.
            
            queries: {str:str,}
                Query string for individual data types names.
            
            properties: {str:(str,),}
                Specific properties to be read for individual data types.
                Note that ID properties are always retrieved. If not provided
                all the properties are retrieved.
            
            excludes: {str:(str,),}
                Specific properties to be ignored for individual data types.
            
            orders: {str:str,}
                Sorting property name for individual data types names.
            
            descs: {str:bool,}
                Use descending order for individual data types names.
            
            limits: {str:int,}
                Number of items to read for individual data types names.
            
            offsets: {str:int,}
                Starting item position for individual data types names.
        
        Yields:
            iter(pyeds.EntityItem,)
                Items iterator.
        """
        
        # apply params to first item if not specified
        if not isinstance(queries, dict):
            queries = {path[0]: queries}
        if not isinstance(properties, dict):
            properties = {path[0]: properties}
        if not isinstance(excludes, dict):
            excludes = {path[0]: excludes}
        if not isinstance(orders, dict):
            orders = {path[0]: orders}
        if not isinstance(descs, dict):
            descs = {path[0]: descs}
        if not isinstance(limits, dict):
            limits = {path[0]: limits}
        if not isinstance(offsets, dict):
            offsets = {path[0]: offsets}
        
        # check args
        path = self._replace_entity_names(path)
        keep = self._replace_entity_names(keep) or path
        queries = self._replace_entity_names(queries) or {}
        properties = self._replace_entity_names(properties) or {}
        excludes = self._replace_entity_names(excludes) or {}
        orders = self._replace_entity_names(orders) or {}
        descs = self._replace_entity_names(descs) or {}
        limits = self._replace_entity_names(limits) or {}
        offsets = self._replace_entity_names(offsets) or {}
        
        # make queries
        for key in path:
            queries[key] = self._get_query(
                queries.get(key, None),
                orders.get(key, None),
                descs.get(key, None),
                limits.get(key, None),
                offsets.get(key, None))
        
        # read hierarchy
        return self._read_hierarchy(
            path = path,
            parent = parent,
            keep = set(keep),
            queries = queries,
            includes = properties,
            excludes = excludes)
    
    
    def ReadMany(self, entity, ids, properties=None, exclude=None):
        """
        Reads items of specified data type for given IDs.
        
        Args:
            entity: str
                Data type name.
            
            ids: ((int,),) or (pyeds.EntityItem,)
                Items IDs.
            
            properties: (str,) or None
                Names of properties to read. Note that ID properties are always
                retrieved. If set to None, all available properties are
                retrieved.
            
            exclude: (str,) or None
                Names of properties to ignore.
        
        Yields:
            iter(pyeds.EntityItem,)
                Items iterator.
        """
        
        # read items
        return self._read_many(
            entity = entity,
            ids = ids,
            include = properties,
            exclude = exclude)
    
    
    def Update(self, items, properties=None):
        """
        Updates specified properties of given items.
        
        Be sure to back up your original results before making any changes! You
        can use the pero.EDS.Report.Backup method. All changes are saved
        immediately.
        
        Note, that all items must be of the same entity type. ID properties,
        connection properties and newly added properties cannot be updated.
        
        Args:
            items: (pyeds.EntityItem,)
                Items to update.
            
            properties: (str,)
                Names of properties to update. If set to None, all modified
                properties will be updated even if modified just for a single
                item.
        """
        
        # check items
        if not items:
            return
        
        # get data type
        data_type = items[0].Type
        
        # check same entity
        if any(d.Type.ID != data_type.ID for d in items):
            raise ValueError("All items must be of the same entity!")
        
        # check if view file exists
        view_available = self._report.HasViewFile()
        
        # retrieve all dirty properties
        if properties is None:
            props = (prop for item in items for prop in item.GetProperties())
            props = (prop for prop in props if (prop.IsDirty and not prop.Type.Virtual))
            properties = set(prop.Type.ColumnName for prop in props)
        
        # check properties
        for prop in properties:
            
            if not data_type.HasColumn(prop):
                raise ValueError("Unknown properties cannot be saved! -> '%s'" % (prop,))
            
            if data_type.GetColumn(prop).Virtual:
                raise ValueError("Custom properties cannot be saved! -> '%s'" % (prop,))
            
            if data_type.GetColumn(prop).IsInViewFile and not view_available:
                raise ValueError("View file properties cannot be saved! Missing view file. -> '%s'" % (prop,))
        
        # no properties
        if not properties:
            return
        
        # update items
        self._update_items(items, properties)
        
        # remove dirty flag
        for item in items:
            for prop in item.GetProperties():
                if prop.Type.ColumnName in properties or prop.Type.DisplayName in properties:
                    prop.Dirty(False)
    
    
    def UpdateTagSettings(self, index, name=None, description=None, color=None, visible=None, persist=True):
        """
        Updates given properties of specified tag bullet.
        
        If changes should be persisted, be sure to back up your original results
        before making any changes! You can use the pero.EDS.Report.Backup
        method.
        
        Args:
            index: int
                Index of the tag bullet to update.
            
            name: str or None
                New display name to be set. If set to None, no changes will be
                made.
            
            description: str or None
                New description to be set. If set to None, no changes will be
                made.
            
            color: (int, int, int, int) or None
                New color to be set. If set to None, no changes will be made.
                Color should be specified as RGBA integers in range of 0-255
                each.
            
            visible: bool or None
                New visibility to be set. If set to None, no changes will be
                made.
            
            persist: bool
                Specifies whether applied changes should be persisted to result
                database.
        """
        
        # update tag settings
        self._update_tag_settings(
            index = index,
            name = name,
            description = description,
            color = color,
            visible = visible,
            persist = persist)
    
    
    def _get_paths(self, data_type1, data_type2, best_length, _length=1, _visited=None):
        """Finds paths between two data types."""
        
        # check length
        current_length = _length + 1
        if best_length[0] <= current_length:
            return
        
        # be sure to set visited
        if _visited is None:
            _visited = set()
        
        # search within direct connections
        for conn in data_type1.Connections:
            
            # get data type
            data_type = conn.DataType1
            if data_type is data_type1:
                data_type = conn.DataType2
            
            # skip used data type
            if data_type in _visited:
                continue
            
            # endpoint reached
            if data_type is data_type2:
                yield [data_type1, data_type2]
                return
        
        # update visited
        visited = set(_visited)
        visited.add(data_type1)
        
        # walk through child connections
        for conn in data_type1.Connections:
            
            # get data type
            data_type = conn.DataType1
            if data_type is data_type1:
                data_type = conn.DataType2
            
            # skip used data type
            if data_type in visited:
                continue
            
            # update visited
            visited.add(data_type)
            
            for path in self._get_paths(data_type, data_type2, best_length, current_length, visited):
                yield [data_type1] + path
    
    
    def _count_items(self, data_type, query=None):
        """Counts items of given data type."""
        
        # get columns
        columns, names, ambiguous = self._get_columns(None, None, data_type)
        if not query:
            columns = []
        
        # attach view file
        needs_view = self._attach_view_file(columns)
        
        # init SQL
        sql = 'SELECT COUNT(*) FROM %s AS %s' % (data_type.TableName, data_type.T_ALIAS)
        values = []
        
        # add view file SQL
        if needs_view:
            sql = self._sql_view_file_select(sql, columns, data_type)
        
        # finalize SQL
        sql, values = self._sql_main_file_finalize(sql, values, query, names)
        
        # execute SQL
        results = self._report.Execute(sql, values)
        count = results.fetchone()[0]
        
        # detach view file
        if needs_view:
            self._report.DetachViewFile()
        
        # return count
        return count
    
    
    def _read_items(self, entity, query=None, include=None, exclude=None):
        """Reads items of given data type name."""
        
        # get data type
        data_type = self._report.GetDataType(entity)
        
        # get columns
        columns, names, ambiguous = self._get_columns(include, exclude, data_type)
        
        # attach view file
        needs_view = self._attach_view_file(columns)
        
        # init SQL
        sql, values = self._sql_main_file_select(columns, data_type, names)
        
        # add view file SQL
        if needs_view:
            sql = self._sql_view_file_select(sql, columns, data_type)
        
        # finalize SQL
        sql, values = self._sql_main_file_finalize(sql, values, query, names)
        
        # execute SQL
        results = self._report.Execute(sql, values)
        
        # yield items
        for item_data in results:
            item = EntityItem(data_type)
            item.SetProperties(self._create_properties(columns, names, **item_data))
            item.Lock()
            yield item
        
        # detach view file
        if needs_view:
            self._report.DetachViewFile()
    
    
    def _read_connected(self, entity, parent, query=None, include=None, exclude=None):
        """Reads directly connected items of given data type name."""
        
        # get data type
        data_type = self._report.GetDataType(entity)
        
        # get connection
        connection = parent.Type.GetConnection(data_type.Name)
        
        # get columns
        columns, names, ambiguous = self._get_columns(include, exclude, data_type, connection)
        
        # attach view file
        needs_view = self._attach_view_file(columns)
        
        # init SQL
        sql, values = self._sql_main_file_select(columns, data_type, names)
        
        # add link IDs
        buff = []
        for column in data_type.IDColumns:
            buff.append('%s%s = %s' % (data_type.TableName, column.ColumnName, names[column.ColumnName]))
        sql += ' INNER JOIN %s %s ON %s' % (connection.TableName, connection.T_ALIAS, ' AND '.join(buff))
        
        # add view file SQL
        if needs_view:
            sql = self._sql_view_file_select(sql, columns, data_type)
        
        # add parent IDs
        buff = []
        for column in parent.Type.IDColumns:
            buff.append('%s%s = ?' % (parent.Type.TableName, column.ColumnName))
            values.append(parent.GetValue(column.ColumnName))
        sql += ' WHERE (%s)' % (' AND '.join(buff))
        
        # finalize SQL
        sql, values = self._sql_main_file_finalize(sql, values, query, names)
        
        # execute SQL
        results = self._report.Execute(sql, values)
        
        # yield items
        for item_data in results:
            item = EntityItem(data_type, connection)
            item.SetProperties(self._create_properties(columns, names, **item_data))
            item.Lock()
            yield item
        
        # detach view file
        if needs_view:
            self._report.DetachViewFile()
    
    
    def _read_hierarchy(self, path, parent, keep=(), queries={}, includes={}, excludes={}):
        """Reads connected items along the given path."""
        
        # get path
        if parent is not None and parent.Type.Name == path[0]:
            path = path[1:]
        
        # get entity
        entity = path[0]
        
        # get specified settings
        query = queries.get(entity, None)
        include = includes.get(entity, None)
        exclude = excludes.get(entity, None)
        
        # use just ID columns if to keep
        if entity not in keep and include is None and len(path) != 1:
            include = []
        
        # read parents
        if parent is None:
            items = self._read_items(
                entity = entity,
                query = query,
                include = include,
                exclude = exclude)
        
        # read children of given parent
        else:
            items = self._read_connected(
                entity = entity,
                parent = parent,
                query = query,
                include = include,
                exclude = exclude)
        
        # end of path reached
        if len(path) == 1:
            for item in items:
                yield item
            return
        
        # read further hierarchy
        for item in items:
            
            # get further children
            children = self._read_hierarchy(
                path = path,
                parent = item,
                keep = keep,
                queries = queries,
                includes = includes,
                excludes = excludes)
            
            # keep this entity
            if entity in keep:
                item.AddChildren(children)
                yield item
            
            # keep children only
            else:
                for child in children:
                    yield child
    
    
    def _read_many(self, entity, ids, include=None, exclude=None):
        """Reads items of given data type name for specified IDs."""
        
        # get data type
        data_type = self._report.GetDataType(entity)
        
        # get columns
        columns, names, ambiguous = self._get_columns(include, exclude, data_type)
        
        # attach view file
        needs_view = self._attach_view_file(columns)
        
        # init SQL
        sql, values = self._sql_main_file_select(columns, data_type, names)
        
        # add view file SQL
        if needs_view:
            sql = self._sql_view_file_select(sql, columns, data_type)
        
        # add IDs to SQL
        id_cols = [names[c.ColumnName] for c in data_type.IDColumns]
        id_cond = ['%s = ?' % c for c in id_cols]
        sql += ' WHERE (%s)' % (' AND '.join(id_cond))
        
        # read items
        for values in ids:
            
            # get IDs
            if isinstance(values, EntityItem):
                values = values.IDs
            
            # execute query
            results = self._report.Execute(sql, values)
            
            # yield items
            for item_data in results:
                item = EntityItem(data_type)
                item.SetProperties(self._create_properties(columns, names, **item_data))
                item.Lock()
                yield item
        
        # detach view file
        if needs_view:
            self._report.DetachViewFile()
    
    
    def _update_items(self, items, include):
        """Updates specified properties of given items."""
        
        # get data type
        data_type = self._report.GetDataType(items[0].Type.Name)
        
        # get IDs
        id_columns = [c for c in data_type.IDColumns]
        
        # get columns
        columns, names, ambiguous = self._get_columns(include, id_columns, data_type)
        
        # attach view file
        needs_view = self._attach_view_file(columns)
        
        # update main file
        self._update_main_file_items(items, columns, data_type)
        
        # update view file
        if needs_view:
            self._update_view_file_items(items, columns, data_type)
        
        # log change
        self._update_last_change("DataTypesColumns", columns)
        
        # commit changes
        self._report.Commit()
        
        # detach view file
        if needs_view:
            self._report.DetachViewFile()
    
    
    def _update_main_file_items(self, items, columns, data_type):
        """Update columns in main file."""
        
        # get columns
        columns = [c.ColumnName for c in columns if not c.IsIDColumn and not c.IsInViewFile]
        
        # skip if not needed
        if not columns:
            return
        
        # get ID columns
        id_columns = [c.ColumnName for c in data_type.IDColumns]
        
        # get columns
        cols = ", ".join('%s = ?' % c for c in columns)
        
        # get IDs
        ids = " AND ".join('%s = ?' % c for c in id_columns)
        
        # make SQL
        sql = 'UPDATE %s SET %s WHERE %s' % (data_type.TableName, cols, ids)
        
        # set values
        values = []
        for i, item in enumerate(items):
            values.append([item.GetProperty(c).RawValue for c in columns + id_columns])
        
        # execute query
        self._report.ExecuteMany(sql, values)
    
    
    def _update_view_file_items(self, items, columns, data_type):
        """Update columns in view file."""
        
        # get columns
        columns = [c.ColumnName for c in columns if c.IsInViewFile]
        
        # skip if not needed
        if not columns:
            return
        
        # get ID columns
        id_columns = [c.ColumnName for c in data_type.IDColumns]
        
        # get values placeholder
        places = ", ".join(["?"] * (len(id_columns) + 1))
        
        # update each table
        for column in columns:
            
            # init SQL
            sql = 'INSERT OR REPLACE INTO %s.%s_%s' % (VIEW_FILE_TAG, data_type.TableName, column)
            
            # add IDs
            ids = ", ".join('%s' % (c,) for c in id_columns)
            sql += ' (%s, %s)' % (ids, column)
            
            # add placeholders
            sql += ' VALUES (%s) ;' % places
            
            # make values
            values = []
            for i, item in enumerate(items):
                values.append([item.GetProperty(c).RawValue for c in id_columns + [column]])
            
            # execute query
            self._report.ExecuteMany(sql, values)
    
    
    def _update_last_change(self, table_name, columns):
        """Updates last change time stamp for given columns."""
        
        # get current time stamp
        stamp = datetime.datetime.now(datetime.timezone.utc).isoformat(sep=" ")
        stamp = stamp.replace('+00:00', 'Z')
        
        # update columns
        for col in columns:
            col.Unlock()
            col.LastChange = stamp
            col.Lock()
        
        # make query
        sql = 'UPDATE %s SET LastChange = ? WHERE ColumnId = ?' % (table_name, )
        
        # get values
        values = [(c.LastChange, c.ID) for c in columns]
        
        # execute query
        self._report.ExecuteMany(sql, values)
    
    
    def _update_tag_settings(self, index, name=None, description=None, color=None, visible=None, persist=True):
        """Updates specified tag box settings."""
        
        # get tag ddmap
        tag_ddmap = None
        for ddmap in self._report.DataDistributionMaps:
            if ddmap.SemanticTerms == "ResultItemDataPurpose/Tags":
                tag_ddmap = ddmap
                break
        
        # check if available
        if tag_ddmap is None:
            raise ValueError("No tags found!")
        
        # get box
        tag_box = tag_ddmap.GetBox(index)
        
        # unlock box
        tag_box.Unlock()
        
        # set name
        if name is not None:
            tag_box.Name = str(name)
        
        # set description
        if description is not None:
            tag_box.Description = str(description)
        
        # set color
        if color is not None:
            r, g, b, a = color if len(color) == 4 else (*color, 255)
            tag_box.Color = utils.argb_int_from_rgba(r, g, b, a)
        
        # set visibility
        if visible is not None:
            tag_box.ExtendedData['EntityItemTagVisibility'] = str(bool(visible))
        
        # lock box
        tag_box.Lock()
        
        # check if should be persisted
        if not persist:
            return
        
        # make SQL for box update
        sql = '''UPDATE DataDistributionBoxes SET
            Name = ?,
            Description = ?,
            Color = ?
            WHERE BoxID = ? AND DataDistributionMapID = ?'''
        
        values = (
            tag_box.Name,
            tag_box.Description,
            tag_box.Color,
            tag_box.ID,
            tag_box.MapID)
        
        # execute query
        self._report.Execute(sql, values)
        
        # make SQL for visibility update
        sql = '''UPDATE DataDistributionBoxExtendedData SET
            ValueString = ?
            WHERE BoxID = ? AND Name = ?'''
        
        values = (
            tag_box.ExtendedData['EntityItemTagVisibility'],
            tag_box.ID,
            'EntityItemTagVisibility')
        
        # execute query
        self._report.Execute(sql, values)
        
        # commit changes
        self._report.Commit()
    
    
    def _get_query(self, query, order, desc, limit, offset):
        """Gets query including order and limit."""
        
        # init query
        query = str(query) if query else ''
        
        # add sorting if not in query
        if order and "ORDER BY " not in query:
            query += ' ORDER BY "%s"' % order
            if desc:
                query += ' DESC'
        
        # add limit if not in query
        if limit and "LIMIT " not in query:
            query += ' LIMIT %d' % limit
        
        # add offset if not in query
        if offset and "OFFSET " not in query:
            query += ' OFFSET %d' % offset
        
        # check query
        if not query:
            return None
        
        # make query
        return EDSQuery(query)
    
    
    def _get_columns(self, include, exclude, *sources):
        """Gets columns to be selected and all available column names."""
        
        columns = []
        names = {}
        ambiguous = False
        
        include = set(include) if include else set()
        exclude = set(exclude) if exclude else set()
        
        # use all sources
        for source in sources:
            
            # get alias
            alias = source.T_ALIAS + "."
            
            # process names
            for column in source.Columns:
                
                # already exists
                if column.ColumnName in names or column.DisplayName in names:
                    ambiguous = True
                
                # make prefixed name
                prefix = "" if column.IsInViewFile else alias
                name = '%s%s' % (prefix, column.ColumnName)
                
                # add to names by column name
                names[column.ColumnName] = name
                
                # add to names by display name
                if column.DisplayName and column.DisplayName not in names:
                    names[column.DisplayName] = name
                
                # skip if not available
                if not column.IsAvailable or not source.IsAvailable:
                    continue
                
                # allways add IDs
                if column.IsIDColumn:
                    columns.append(column)
                    continue
                
                # check excluded
                if column.ColumnName in exclude or column.DisplayName in exclude:
                    continue
                
                # add selected columns or all if none selected
                if not include or column.ColumnName in include or column.DisplayName in include:
                    columns.append(column)
        
        return columns, names, ambiguous
    
    
    def _replace_entity_names(self, original):
        """Replaces entity names to make sure real names are used."""
        
        # check item
        if original is None:
            return None
        
        # replace dictionary keys
        if isinstance(original, dict):
            converted = {}
            for key, value in original.items():
                entity = self._report.GetDataType(key)
                converted[entity.Name] = value
        
        # replace lists
        else:
            converted = []
            for key in original:
                entity = self._report.GetDataType(key)
                converted.append(entity.Name)
        
        return converted
    
    
    def _sql_main_file_select(self, columns, data_type, names):
        """Initializes selection SQL query from data type and requested columns."""
        
        # get selected columns names
        columns = set(names[c.ColumnName] for c in columns)
        
        # ensure ID columns are always present
        for column in data_type.IDColumns:
            columns.add(names[column.ColumnName])
        
        # make identifiers
        cols = ", ".join(columns)
        
        # make SQL
        sql = 'SELECT %s FROM %s AS %s' % (cols, data_type.TableName, data_type.T_ALIAS)
        
        return sql, []
    
    
    def _sql_main_file_finalize(self, sql, values, query, names):
        """Finalizes SQL query by adding conditions, sorting and range."""
        
        # check query
        if not query:
            return sql, values
        
        # init query
        if not isinstance(query, EDSQuery):
            query = EDSQuery(query)
        
        # parse query
        parsed = query.parse(names)
        if parsed is None:
            return sql, values
        
        # add values
        values += parsed['values']
        
        # add constraint
        if parsed['constraint']:
            if " WHERE " in sql:
                sql += ' AND (%s)' % parsed['constraint']
            else:
                sql += ' WHERE %s' % parsed['constraint']
        
        # add order by
        if parsed['orderby']:
            sql += ' %s' % parsed['orderby']
        
        # add limit
        if parsed['limit']:
            sql += ' %s' % parsed['limit']
        
        return sql, values
    
    
    def _sql_view_file_select(self, sql, columns, data_type):
        """Makes SQL to join view file tables and select columns."""
        
        # get columns
        columns = [c.ColumnName for c in columns if not c.IsIDColumn and c.IsInViewFile]
        
        # get ID columns
        id_columns = [c.ColumnName for c in data_type.IDColumns]
        
        # add SQL for each table
        idx = 0
        for column in columns:
            idx += 1
            ids = " AND ".join('%s.%s = V%d.%s' % (data_type.T_ALIAS, c, idx, c) for c in id_columns)
            sql += ' LEFT JOIN %s.%s_%s V%d ON %s' % (VIEW_FILE_TAG, data_type.TableName, column, idx, ids)
        
        return sql
    
    
    def _attach_view_file(self, columns):
        """Attaches the view file if needed."""
        
        # check if view file exists
        if not self._report.HasViewFile():
            return False
        
        # check if needed
        if not any(c.IsInViewFile for c in columns):
            return False
        
        # attach view file
        self._report.AttachViewFile()
        
        return True
    
    
    def _create_properties(self, columns, names, **data):
        """Creates property items from DB data."""
        
        items = []
        
        # create properties
        for column in columns:
            
            # get name
            name = names[column.ColumnName]
            if name not in data:
                name = column.ColumnName
            
            # check if available
            if name not in data:
                continue
            
            # create property
            prop = PropertyValue(column, data[name])
            prop.Lock()
            items.append(prop)
        
        return items
