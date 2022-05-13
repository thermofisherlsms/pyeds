#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
from .grammar import Grammar

# create basic query grammar
_GRAMMAR = Grammar(
    
    log = 'AND | OR',
    op = '<= | >= | != | = | < | > | LIKE',
    null = 'IS NULL | IS NOT NULL',
    
    column = '[A-Za-z0-9_]+',
    name = '\" [A-Za-z0-9-_\.\s\[\]\+\-]+ \" | \' [A-Za-z0-9-_\.\s\[\]\+\-]+ \'',
    val = '[A-Za-z0-9-_%\.]+',
    quote = '\" [A-Za-z0-9-_%\.\s\[\]\+\-]* \" | \' [A-Za-z0-9-_%\.\s\[\]\+\-]* \'',
    
    seq = 'val , seq | quote , seq | val , val | val , quote | val , | val | quote , val | quote , quote | quote , | quote',
    inside = 'IN \( seq \) | NOT IN \( seq \)',
    
    state = 'column op val | column op quote | column inside | column null | name op val | name op quote | name inside | name null',
    group = '\( expr \)',
    
    expr = 'group log expr | state log expr | group | state',
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
        self._tree = _GRAMMAR.parse(query, 'expr')
        
        # check query
        if query and (self._tree is None or len(self._tree) != 1):
            message = "Query syntax error! --> %s" % query
            raise ValueError(message)
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return Grammar.visualize(self.tree) if self.tree is not None else ""
    
    
    @property
    def raw_query(self):
        """
        Gets original query.
        
        Returns:
            str
                Query string.
        """
        
        return self._query
    
    
    @property
    def query(self):
        """
        Gets parsed query string.
        
        Returns:
            str
                Query string.
        """
        
        if not self._tree:
            return ""
        
        return self._to_str(self._tree[0])
    
    
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
    
    
    def _to_str(self, tree):
        """Converts query into text."""
        
        text = ""
        
        if type(tree) != list:
            return " %s" % tree
        
        if tree[0] == 'quote':
            return " \"%s\"" % tree[2]
        
        for item in tree[1:]:
            text += self._to_str(item)
        
        return text


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
        
        super().__init__(query)
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
        
        # make sqls and values from tree
        if self._tree:
            sqls, values = self._parse_expr(self._tree[0])
            sql = " ".join(sqls)
        
        return sql, values
    
    
    def _parse_expr(self, expr):
        """Parses expr into SQL conditions."""
        
        sqls = []
        values = []
        
        # parse expression
        for item in expr[1:]:
            name = item[0]
            
            # parse inner expression
            if name == 'expr':
                parsed = self._parse_expr(item)
            
            # parse group
            elif name == 'group':
                parsed = self._parse_group(item)
            
            # parse statement
            elif name == 'state':
                parsed = self._parse_state(item)
            
            # get logical operand
            elif name == 'log':
                parsed = [item[1]], []
            
            # unknown rule
            else:
                raise KeyError("Unknown rule! --> '%s" % name)
            
            # update SQL and values
            sqls += parsed[0]
            values += parsed[1]
        
        return sqls, values
    
    
    def _parse_group(self, item):
        """Parses group into SQL conditions."""
        
        sqls, values = self._parse_expr(item[2])
        sqls = ["("] + sqls + [")"]
        
        return sqls, values
    
    
    def _parse_state(self, item):
        """Parses element into SQL conditions."""
        
        column = ""
        value = ""
        
        # get column name
        if item[1][0] == 'column':
            column = item[1][1]
        
        elif item[1][0] == 'name':
            column = item[1][2]
        
        # ensure real column name
        if self._names is not None:
            column = self._names[column]
        
        # IN sequence
        if item[2][0] == 'inside':
            
            if item[2][1] == 'NOT':
                values = self._parse_seq(item[2][4])
                sql = '"%s" NOT IN (%s)' % (column, ", ".join("?"*len(values)))
            else:
                values = self._parse_seq(item[2][3])
                sql = '"%s" IN (%s)' % (column, ", ".join("?"*len(values)))
            
            return [sql], values
        
        # NULL comparison
        if item[2][0] == 'null':
            sql = '"%s" %s' % (column, " ".join(item[2][1:]))
            return [sql], []
        
        # make SQL from column and operand
        sql = '"%s" %s ?' % (column, item[2][1])
        
        # get value
        if item[3][0] == 'val':
            value = item[3][1]
        
        elif item[3][0] == 'quote':
            value = item[3][2]
        
        return [sql], [value]
    
    
    def _parse_seq(self, item):
        """Parses sequence of values."""
        
        values = []
        
        # get 1st value
        if item[1][0] == 'val':
            values.append(item[1][1])
        
        elif item[1][0] == 'quote':
            values.append(item[1][2])
        
        elif item[1][0] == 'seq':
            values += self._parse_seq(item[1])
        
        # check other values
        if len(item) != 4:
            return values
        
        # get other values
        if item[3][0] == 'val':
            values.append(item[3][1])
        
        elif item[3][0] == 'quote':
            values.append(item[3][2])
        
        elif item[3][0] == 'seq':
            values += self._parse_seq(item[3])
        
        return values
