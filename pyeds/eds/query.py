#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
from .grammar import Grammar

# create basic query grammar
_GRAMMAR = Grammar(
    
    # define keywords
    log = 'AND | OR',
    op = '<= | >= | != | = | < | > | LIKE',
    null = 'IS NULL | IS NOT NULL',
    desc = 'DESC | ASC',
    
    # define columns
    column = '[A-Za-z0-9_]+ | \' [A-Za-z0-9-_\.\s\(\)\[\]\+\-]+ \' | \" [A-Za-z0-9-_\.\s\(\)\[\]\+\-]+ \"',
    
    # define values
    value = '[A-Za-z0-9-_%\.]+ | \' [A-Za-z0-9-_%\.\s\(\)\[\]\+\-]* \' | \" [A-Za-z0-9-_%\.\s\(\)\[\]\+\-]* \"',
    sequence = 'value , sequence | value , | value',
    
    # define IN
    inside = 'IN \( sequence \) | NOT IN \( sequence \)',
    
    # define constraint
    statement = 'column op value | column inside | column null',
    group = '\( constraint \)',
    constraint = 'group log constraint | statement log constraint | group | statement',
    
    # define ORDER BY
    order = 'column desc | column',
    orders = 'order , orders | order , | order',
    orderby = 'ORDER BY orders',
    
    # define LIMIT
    limit = 'LIMIT [0-9]+ OFFSET [0-9]+ | LIMIT [0-9]+ | OFFSET [0-9]+ ',
    
    # define full expression
    expression = 'constraint orderby limit | constraint orderby | constraint limit | orderby | limit | constraint',
)


class Query(object):
    """
    Represents a query definition and provides functionality to parse it.
    """
    
    
    def __init__(self, query):
        """
        Initializes a new instance of Query.
        
        Args:
            query: str
                Query string.
        """
        
        self._query = query
        self._tree = _GRAMMAR.parse(query, 'expression')
        
        # check query
        if query and (self._tree is None or len(self._tree) != 1):
            message = "Query syntax error! --> %s" % query
            raise ValueError(message)
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return Grammar.visualize(self.tree) if self.tree is not None else ""
    
    
    @property
    def query(self):
        """
        Gets original query.
        
        Returns:
            str
                Query string.
        """
        
        return self._query
    
    
    @property
    def tree(self):
        """
        Gets parsed query tree.
        
        Returns:
            hierarchical list
                Parsed query tree.
        """
        
        return self._tree
    
    
    def extract(self, rule):
        """
        Extracts values for given rule.
        
        Args:
            rule: str
                Rule name to be extracted.
        
        Returns:
            hierarchical list
                Rule values.
        """
        
        values = []
        
        # check tree
        if not self._tree:
            return values
        
        # search tree
        return Grammar.extract(self._tree, rule)


class EDSQuery(Query):
    """
    Represents a specific type of query definition providing functionality to
    convert it into SQLite query and list of values.
    """
    
    
    def __init__(self, query, names=None):
        """
        Initializes a new instance of EDSQuery.
        
        Args:
            query: str
                Query string.
            
            names: {str:str} or None
                Mapping of names to real column names.
        """
        
        super().__init__(query.strip())
        self._names = names
    
    
    def sql(self):
        """
        Parses query into SQL conditions and list of values.
        
        Returns:
            (sql, [?,])
                Tuple of SQL query and values.
        """
        
        sql = ""
        values = []
        
        # extract SQL and values from tree
        if self._tree:
            sqls, values = self._parse_expression(self._tree[0])
            sql = " ".join(sqls)
        
        return sql, values
    
    
    def _parse_expression(self, expr_elm):
        """Parses expression into SQL."""
        
        sqls = []
        values = []
        
        # check element
        if expr_elm[0] != 'expression':
            raise KeyError("Incorrect element! --> '%s" % expr_elm[0])
        
        # parse elements
        for elm in expr_elm[1:]:
            
            # get element name
            elm_name = elm[0]
            
            # parse constraint
            if elm_name == 'constraint':
                sqls, values = self._parse_constraint(elm)
            
            # parse ORDER BY
            elif elm_name == 'orderby':
                sqls.append(self._parse_orderby(elm))
            
            # parse LIMIT
            elif elm_name == 'limit':
                sqls.append(self._parse_limit(elm))
            
            # unknown rule
            else:
                raise KeyError("Unknown rule! --> '%s" % elm_name)
        
        return sqls, values
    
    
    def _parse_column(self, col_elm):
        """Parses column name."""
        
        column = ""
        
        # check element
        if col_elm[0] != 'column':
            raise KeyError("Incorrect element! --> '%s" % col_elm[0])
        
        # get simple column name
        if len(col_elm) == 2:
            column = col_elm[1]
        
        # get extended column name
        elif len(col_elm) == 4:
            column = col_elm[2]
        
        # ensure real column name
        if self._names is not None:
            column = self._names[column]
        
        return column
    
    
    def _parse_value(self, val_elm):
        """Parses value."""
        
        value = ""
        
        # check element
        if val_elm[0] != 'value':
            raise KeyError("Incorrect element! --> '%s" % val_elm[0])
        
        # get simple value
        if len(val_elm) == 2:
            value = val_elm[1]
        
        # get extended value
        elif len(val_elm) == 4:
            value = val_elm[2]
        
        return value
    
    
    def _parse_sequence(self, seq_elm):
        """Parses sequence of values."""
        
        values = []
        
        # check element
        if seq_elm[0] != 'sequence':
            raise KeyError("Incorrect element! --> '%s" % seq_elm[0])
        
        # parse elements
        for elm in seq_elm[1:]:
            
            # get element name
            elm_name = elm[0]
            
            # parse sequence
            if elm_name == 'sequence':
                values += self._parse_sequence(elm)
            
            # parse value
            elif elm_name == 'value':
                values.append(self._parse_value(elm))
        
        return values
    
    
    def _parse_constraint(self, con_elm):
        """Parses constraint into SQL."""
        
        sqls = []
        values = []
        
        # check element
        if con_elm[0] != 'constraint':
            raise KeyError("Incorrect element! --> '%s" % con_elm[0])
        
        # parse elements
        for elm in con_elm[1:]:
            
            # get element name
            elm_name = elm[0]
            
            # parse inner constraint
            if elm_name == 'constraint':
                parsed = self._parse_constraint(elm)
            
            # parse statement
            elif elm_name == 'statement':
                parsed = self._parse_statement(elm)
            
            # parse operand
            elif elm_name == 'log':
                parsed = [elm[1]], []
            
            # parse group
            elif elm_name == 'group':
                parsed = self._parse_group(elm)
            
            # unknown rule
            else:
                raise KeyError("Unknown rule! --> '%s" % elm_name)
            
            # update SQL and values
            sqls += parsed[0]
            values += parsed[1]
        
        return sqls, values
    
    
    def _parse_statement(self, state_elm):
        """Parses single constraint statement into SQL."""
        
        column = ""
        sql = ""
        values = []
        
        # check element
        if state_elm[0] != 'statement':
            raise KeyError("Incorrect element! --> '%s" % state_elm[0])
        
        # parse elements
        for elm in state_elm[1:]:
            
            # get element name
            elm_name = elm[0]
            
            # parse column
            if elm_name == 'column':
                column = self._parse_column(elm)
            
            # parse operand
            elif elm_name == 'op':
                sql = self._parse_op(elm)
            
            # parse value
            elif elm_name == 'value':
                values = [self._parse_value(elm)]
            
            # parse IN statement
            elif elm_name == 'inside':
                sql, values = self._parse_inside(elm)
            
            # parse NULL statement
            elif elm_name == 'null':
                sql = self._parse_null(elm)
            
            # unknown rule
            else:
                raise KeyError("Unknown rule! --> '%s" % elm_name)
        
        # finalize SQL
        sql = "%s %s" % (column, sql)
        
        return [sql], values
    
    
    def _parse_op(self, op_elm):
        """Parses statement operand into SQL."""
        
        # check element
        if op_elm[0] != 'op':
            raise KeyError("Incorrect element! --> '%s" % op_elm[0])
        
        # parse operand
        return '%s ?' % op_elm[1]
    
    
    def _parse_inside(self, in_elm):
        """Parses IN statement into SQL."""
        
        sql = ""
        values = []
        
        # check element
        if in_elm[0] != 'inside':
            raise KeyError("Incorrect element! --> '%s" % in_elm[0])
        
        # parse IN
        if in_elm[1] == 'IN':
            values = self._parse_sequence(in_elm[3])
            sql = 'IN (%s)' % (", ".join("?"*len(values)),)
        
        # parse NOT IN
        elif in_elm[1] == 'NOT':
            values = self._parse_sequence(in_elm[4])
            sql = 'NOT IN (%s)' % (", ".join("?"*len(values)),)
        
        return sql, values
    
    
    def _parse_null(self, null_elm):
        """Parses NULL statement into SQL."""
        
        # check element
        if null_elm[0] != 'null':
            raise KeyError("Incorrect element! --> '%s" % null_elm[0])
        
        # parse IS NULL
        if null_elm[2] == 'NULL':
            return 'IS NULL'
        
        # parse IS NOT NULL
        elif null_elm[1] == 'NOT':
            return 'IS NOT NULL'
    
    
    def _parse_group(self, group_elm):
        """Parses constraint group into SQL."""
        
        # check element
        if group_elm[0] != 'group':
            raise KeyError("Incorrect element! --> '%s" % group_elm[0])
        
        # parse inner constraint
        sqls, values = self._parse_constraint(group_elm[2])
        sqls = ["("] + sqls + [")"]
        
        return sqls, values
    
    
    def _parse_orderby(self, ord_elm):
        """Parses ORDER BY into SQL."""
        
        # check element
        if ord_elm[0] != 'orderby':
            raise KeyError("Incorrect element! --> '%s" % ord_elm[0])
        
        # parse orders
        sqls = self._parse_orders(ord_elm[3])
        
        # finalize SQL
        sql = "ORDER BY %s" % (", ".join(sqls))
        
        return sql
    
    
    def _parse_orders(self, ord_elm):
        """Parses sequence of orders into SQL."""
        
        sqls = []
        
        # check element
        if ord_elm[0] != 'orders':
            raise KeyError("Incorrect element! --> '%s" % ord_elm[0])
        
        # parse elements
        for elm in ord_elm[1:]:
            
            # get element name
            elm_name = elm[0]
            
            # parse orders
            if elm_name == 'orders':
                sqls += self._parse_orders(elm)
            
            # parse order
            elif elm_name == 'order':
                sqls.append(self._parse_order(elm))
        
        return sqls
    
    
    def _parse_order(self, ord_elm):
        """Parses single order statement into SQL."""
        
        column = ""
        desc = ""
        
        # check element
        if ord_elm[0] != 'order':
            raise KeyError("Incorrect element! --> '%s" % ord_elm[0])
        
        # parse elements
        for elm in ord_elm[1:]:
            
            # get element name
            elm_name = elm[0]
            
            # parse column
            if elm_name == 'column':
                column = self._parse_column(elm)
            
            # parse DESC or ASC
            elif elm_name == 'desc':
                desc = self._parse_desc(elm)
            
            # unknown rule
            else:
                raise KeyError("Unknown rule! --> '%s" % elm_name)
        
        # finalize SQL
        sql = "%s %s" % (column, desc) if desc else column
        
        return sql
    
    
    def _parse_desc(self, desc_elm):
        """Parses DESC or ASC into SQL."""
        
        # check element
        if desc_elm[0] != 'desc':
            raise KeyError("Incorrect element! --> '%s" % desc_elm[0])
        
        # parse DESC
        if desc_elm[1] == 'DESC':
            return 'DESC'
        
        # parse ASC
        elif desc_elm[1] == 'ASC':
            return 'ASC'
    
    
    def _parse_limit(self, lim_elm):
        """Parses LIMIT and OFFSET into SQL."""
        
        # check element
        if lim_elm[0] != 'limit':
            raise KeyError("Incorrect element! --> '%s" % lim_elm[0])
        
        # finalize sql
        return " ".join(lim_elm[1:])
