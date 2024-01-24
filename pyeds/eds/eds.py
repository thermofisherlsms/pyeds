#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import datetime
from ..report import Report
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
                Names of data types required within the path.
        
        Returns:
            (str,)
                Sequence of data types names defining the path.
        """
        
        # get data types
        data_type1 = self._report.GetDataType(from_entity)
        data_type2 = self._report.GetDataType(to_entity)
        
        # prepare via
        via = set(via)
        
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
        
        # get column names
        names, ambiguous = self._get_column_names(data_type)
        
        # init query
        sql = 'SELECT COUNT(*) FROM "%s"' % data_type.TableName
        values = []
        
        # finalize query
        sql, values = self._sql_finalize_select(sql, values, names, query)
        
        # execute SQL query
        results = self._report.Execute(sql, values)
        
        # return count
        return results.fetchone()[0]
    
    
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
        
        # get column names
        names, ambiguous = self._get_column_names(connection)
        
        # init query
        sql = 'SELECT COUNT(*) FROM "%s"' % connection.TableName
        values = []
        
        # finalize query
        sql, values = self._sql_finalize_select(sql, values, names, query)
        
        # execute SQL query
        results = self._report.Execute(sql, values)
        
        # return count
        return results.fetchone()[0]
    
    
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
        
        # read items
        return self._read_items(
            entity = entity,
            query = query,
            columns = properties,
            exclude = exclude,
            order = order,
            desc = desc,
            limit = limit,
            offset = offset)
    
    
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
        
        # read items
        return self._read_connected(
            entity = entity,
            parent = parent,
            query = query,
            columns = properties,
            exclude = exclude,
            order = order,
            desc = desc,
            limit = limit,
            offset = offset)
    
    
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
        
        # read hierarchy
        return self._read_hierarchy(
            path = path,
            parent = parent,
            keep = set(keep),
            queries = queries,
            columns = properties,
            excludes = excludes,
            orders = orders,
            descs = descs,
            limits = limits,
            offsets = offsets)
    
    
    def ReadMany(self, entity, ids, properties=None, exclude=None):
        """
        Reads items of specified data type for given IDs.
        
        Args:
            entity: str
                Data type name.
            
            ids: ((int,),)
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
            columns = properties,
            exclude = exclude)
    
    
    def Update(self, items, properties=None, save=True):
        """
        Updates specified properties of given items.
        
        Be sure to back up your original results before making any changes! You
        can use the pero.EDS.Report.Backup method.
        
        Note, that all items must be of the same entity type. ID properties,
        connection properties and newly added properties cannot be updated.
        
        Args:
            items: (pyeds.EntityItem,)
                Items to update.
            
            properties: (str,)
                Names of properties to update. If set to None, all modified
                properties will be updated even if modified just for a single
                item.
            
            save: bool
                If set to True, database changes are commit. Otherwise, all the
                changes are lost when current connection closes.
        """
        
        # check items
        if not items:
            return
        
        # get data type
        data_type = items[0].Type
        
        # check same entity
        if any(d.Type.ID != data_type.ID for d in items):
            raise ValueError("All items must be of the same entity!")
        
        # retrieve all dirty properties
        if properties is None:
            props = (prop for item in items for prop in item.GetProperties())
            props = (prop for prop in props if (prop.Dirty() and not prop.Type.Virtual))
            properties = set(prop.Type.ColumnName for prop in props)
        
        # check properties
        for prop in properties:
            
            if not data_type.HasColumn(prop):
                raise ValueError("Unknown properties cannot be saved! -> '%s'" % (prop,))
            
            if data_type.GetColumn(prop).Virtual:
                raise ValueError("Custom properties cannot be saved! -> '%s'" % (prop,))
            
            if data_type.GetColumn(prop).IsInViewFile:
                raise ValueError("View file properties cannot be saved! -> '%s'" % (prop,))
        
        # no properties
        if not properties:
            return
        
        # update items
        self._update_items(items, properties)
        
        # commit changes
        if save:
            self._report.Save()
    
    
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
    
    
    def _get_column_names(self, *sources):
        """Creates a mapping between column display names and real column names."""
        
        names = {}
        ambiguous = False
        
        # use all sources
        for source in sources:
            for column in source.Columns:
                
                # already exists
                if column.ColumnName in names or column.DisplayName in names:
                    ambiguous = True
                
                # add column name
                names[column.ColumnName] = column.ColumnName
                
                # add display name
                if column.DisplayName and column.DisplayName not in names:
                    names[column.DisplayName] = column.ColumnName
        
        return names, ambiguous
    
    
    def _read_items(self, entity, query=None, columns=None, exclude=None, order=None, desc=False, limit=None, offset=0):
        """Reads items of given data type name."""
        
        # get data type
        data_type = self._report.GetDataType(entity)
        
        # get column names
        names, ambiguous = self._get_column_names(data_type)
        
        # init query
        sql = self._sql_initialize_select(data_type, columns, exclude, names)
        values = []
        
        # finalize query
        sql, values = self._sql_finalize_select(sql, values, names, query, order, desc, limit, offset)
        
        # execute query
        results = self._report.Execute(sql, values)
        
        # yield items
        for item_data in results:
            item = EntityItem(data_type)
            item.SetProperties(self._create_properties(data_type.Columns, exclude, **item_data))
            item.Lock()
            yield item
    
    
    def _read_connected(self, entity, parent, query=None, columns=None, exclude=None, order=None, desc=False, limit=None, offset=0):
        """Reads directly connected items of given data type name."""
        
        # get data type
        data_type = self._report.GetDataType(entity)
        
        # get connection
        connection = parent.Type.GetConnection(data_type.Name)
        
        # get column names
        names, ambiguous = self._get_column_names(data_type, connection)
        
        # init query
        excl = exclude if not ambiguous else []
        sql = self._sql_initialize_select(data_type, columns, excl, names)
        values = []
        
        # add link IDs
        buff = []
        for column in data_type.IDColumns:
            buff.append('"%s%s" = %s' % (data_type.TableName, column.ColumnName, column.ColumnName))
        sql += ' INNER JOIN "%s" ON %s' % (connection.TableName, ' AND '.join(buff))
        
        # add parent IDs
        buff = []
        for column in parent.Type.IDColumns:
            buff.append('"%s%s" = ?' % (parent.Type.TableName, column.ColumnName))
            values.append(parent.GetValue(column.ColumnName))
        sql += ' WHERE (%s)' % (' AND '.join(buff))
        
        # finalize query
        sql, values = self._sql_finalize_select(sql, values, names, query, order, desc, limit, offset)
        
        # execute query
        results = self._report.Execute(sql, values)
        
        # yield items
        for item_data in results:
            item = EntityItem(data_type, connection)
            item.SetProperties(self._create_properties(data_type.Columns, exclude, **item_data))
            item.SetProperties(self._create_properties(connection.Columns, exclude, **item_data))
            item.Lock()
            yield item
    
    
    def _read_hierarchy(self, path, parent, keep=(), queries={}, columns={}, excludes={}, orders={}, descs={}, limits={}, offsets={}):
        """Reads connected items along the given path."""
        
        # get path
        if parent is not None and parent.Type.Name == path[0]:
            path = path[1:]
        
        # get entity
        entity = path[0]
        
        # get specified settings
        query = queries.get(entity, None)
        cols = columns.get(entity, None)
        exclude = excludes.get(entity, None)
        order = orders.get(entity, None)
        desc = descs.get(entity, False)
        limit = limits.get(entity, None)
        offset = offsets.get(entity, 0)
        
        # use just ID columns if to keep
        if entity not in keep and cols is None and len(path) != 1:
            cols = []
        
        # read parents
        if parent is None:
            items = self._read_items(
                entity = entity,
                query = query,
                columns = cols,
                exclude = exclude,
                order = order,
                desc = desc,
                limit = limit,
                offset = offset)
        
        # read children of given parent
        else:
            items = self._read_connected(
                entity = entity,
                parent = parent,
                query = query,
                columns = cols,
                exclude = exclude,
                order = order,
                desc = desc,
                limit = limit,
                offset = offset)
        
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
                columns = columns,
                excludes = excludes,
                orders = orders,
                descs = descs,
                limits = limits,
                offsets = offsets)
            
            # keep this entity
            if entity in keep:
                item.AddChildren(children)
                yield item
            
            # keep children only
            else:
                for child in children:
                    yield child
    
    
    def _read_many(self, entity, ids, columns=None, exclude=None):
        """Reads items of given data type name for specified IDs."""
        
        # get data type
        data_type = self._report.GetDataType(entity)
        
        # get column names
        names, ambiguous = self._get_column_names(data_type)
        
        # init query
        sql = self._sql_initialize_select(data_type, columns, exclude, names)
        
        # add IDs
        buff = []
        for column in data_type.IDColumns:
            buff.append('"%s" = ?' % column.ColumnName)
        sql += ' WHERE (%s)' % (' AND '.join(buff))
        
        # read items
        for values in ids:
            
            # execute query
            results = self._report.Execute(sql, values)
            
            # yield items
            for item_data in results:
                item = EntityItem(data_type)
                item.SetProperties(self._create_properties(data_type.Columns, exclude, **item_data))
                item.Lock()
                yield item
    
    
    def _update_items(self, items, columns):
        """Updates specified properties of given items."""
        
        # get data type
        data_type = self._report.GetDataType(items[0].Type.Name)
        
        # get IDs
        id_columns = [c.ColumnName for c in data_type.IDColumns]
        
        # select columns
        names, ambiguous = self._get_column_names(data_type)
        columns = set(names[c] for c in columns)
        columns = list(columns.difference(id_columns))
        
        # finalize columns
        cols = ('"%s" = ?' % c for c in columns)
        cols = ", ".join(cols)
        
        # finalize IDs
        ids = ('"%s" = ?' % c for c in id_columns)
        ids = " AND ".join(ids)
        
        # make query
        sql = 'UPDATE "%s" SET %s WHERE %s' % (data_type.TableName, cols, ids)
        
        # get values
        values = []
        for item in items:
            values.append([item.GetProperty(c).RawValue for c in columns + id_columns])
        
        # execute query
        self._report.ExecuteMany(sql, values)
        
        # remove dirty flag
        for item in items:
            for prop in item.GetProperties():
                if prop.Type.ColumnName in columns:
                    prop.Dirty(False)
        
        # log change
        columns = [data_type.GetColumn(c) for c in columns]
        self._update_last_change("DataTypesColumns", columns)
    
    
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
        sql = 'UPDATE "%s" SET LastChange = ? WHERE ColumnId = ?' % (table_name, )
        
        # get values
        values = [(c.LastChange, c.ID) for c in columns]
        
        # execute query
        self._report.ExecuteMany(sql, values)
    
    
    def _sql_initialize_select(self, data_type, columns, exclude, names):
        """Initializes selection SQL query from data type and requested columns."""
        
        # get all columns
        if columns is None and not exclude:
            columns = "*"
        
        # get specified columns
        else:
            
            # get names
            if columns is None:
                columns = set(names.values())
            else:
                columns = set(names[c] for c in columns)
            
            # remove excluded
            if exclude:
                exclude = set(names[c] for c in exclude)
                columns = columns.difference(exclude)
            
            # ensure ID columns are present
            for column in data_type.IDColumns:
                columns.add(column.ColumnName)
            
            # make identifiers
            columns = ('"%s"' % c for c in columns)
            columns = ", ".join(columns)
        
        return 'SELECT %s FROM "%s"' % (columns, data_type.TableName)
    
    
    def _sql_finalize_select(self, sql, values, names, query=None, order=None, desc=False, limit=None, offset=0):
        """Finalizes SQL query by adding conditions, sorting and range."""
        
        # add query
        if query:
            
            qsql, qval = EDSQuery(query, names).sql()
            values += qval
            
            if " WHERE " not in sql:
                sql += ' WHERE %s' % qsql
            else:
                sql += ' AND (%s)' % qsql
        
        # add sorting if not in query
        if order and "ORDER BY " not in sql:
            sql += ' ORDER BY "%s"' % names[order]
            if desc:
                sql += ' DESC'
        
        # add limit if not in query
        if limit and "LIMIT " not in sql:
            sql += ' LIMIT %d' % limit
        
        # add offset if not in query
        if offset and "OFFSET " not in sql:
            sql += ' OFFSET %d' % offset
        
        return sql, values
    
    
    def _create_properties(self, columns, exclude, **data):
        """Creates property items from DB data."""
        
        items = []
        exclude = exclude or []
        
        for column in columns:
            if column.ColumnName in data and column.ColumnName not in exclude and column.DisplayName not in exclude:
                prop = PropertyValue(column, data[column.ColumnName])
                prop.Lock()
                items.append(prop)
        
        return items
