#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import codecs
import os.path
import sqlite3 as sqlite


class Database(object):
    """
    Database is a wrapper around SQLite database providing convenient functions
    to open and close connections etc.
    
    Attributes:
    
        path: str
            Database file path.
        
        conn: sqlite3.Connection or None
            Current SQLite connection.
    """
    
    
    def __init__(self, path, new=False, delete_old=False):
        """
        Initializes a new instance of Database.
        
        Args:
            path: str
                Path to an existing or new SQLite database file. You can also
                use in-memory database by providing ':memory:' as a path. In
                that case, each time you open a new connection, new database
                will be created. Therefore you should open a connection before
                you provide the database into any tool.
            
            new: bool
                If set to True, new database will be created. If the file
                already exists it will be deleted or exception raises depending
                on the 'delete_old' parameter.
            
            delete_old: bool
                If set to True and a new file should be created an existing file
                (if any) will be deleted.
        """
        
        self._path = path.strip()
        self._conn = None
        self._refs = 0
        
        # use in-memory database
        if path == ':memory:':
            return
        
        # check existing database
        file_exists = os.path.exists(path)
        
        # remove old database
        if file_exists and new and delete_old:
            os.remove(path)
        
        # existing database
        elif file_exists and new:
            message = "Specified database already exists! --> '%s'" % path
            raise IOError(message)
        
        # no database found
        elif not file_exists and not new:
            message = "Specified database does not exist! --> '%s'" % path
            raise IOError(message)
        
        # ensure database file exists
        self.connect()
        self.close()
        
        # check format of existing file
        if not new:
            self._check_db_format()
    
    
    def __enter__(self):
        """Opens a database connection within 'with' statement."""
        
        self.connect()
        return self
    
    
    def __exit__(self, exc_ty, exc_val, tb):
        """Closes database connection within 'with' statement ended."""
        
        self.close()
    
    
    @property
    def path(self):
        """
        Gets database path.
        
        Returns:
            str
                Database file path.
        """
        
        return self._path
    
    
    @property
    def conn(self):
        """
        Gets database connection.
        
        Returns:
            sqlite3.Connection or None
                SQLite connection.
        """
        
        return self._conn
    
    
    def connect(self, row_factory=sqlite.Row, foreign_keys=True):
        """
        Increase reference counter and opens a database connection if necessary.
        
        Internally the database retains number of opened connections and closes
        the connection only when the reference count is back to zero. See the
        'close' method.
        
        Args:
            row_factory: callable
                A callable that accepts the cursor and the original row as a
                tuple and returns the real result row.
            
            foreign_keys: bool
                Specifies whether foreign keys support should be ON.
        """
        
        # increase counter
        self._refs += 1
        
        # establish new connection if necessary
        if self._conn is None:
            
            # create connection
            self._conn = sqlite.connect(self._path)
            self._conn.row_factory = row_factory
            
            # set foreign keys
            cur = self._conn.cursor()
            if foreign_keys:
                cur.execute("PRAGMA foreign_keys = ON")
            else:
                cur.execute("PRAGMA foreign_keys = OFF")
    
    
    def close(self, force=False):
        """
        Decrease reference counter and closes database connection if no
        references found.
        
        Args:
            force: bool
                If set to True current reference counter is ignored and
                connection is always closed. Otherwise the connection is only
                closed if the reference counter is zero.
        """
        
        # decrease counter
        self._refs = 0 if force else max(0, self._refs - 1)
        
        # close connection
        if self._refs == 0 and self._conn is not None:
            self._conn.close()
            self._conn = None
    
    
    def execute(self, sql, values=()):
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
        return self._conn.execute(sql, values)
    
    
    def executemany(self, sql, values=()):
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
        return self._conn.executemany(sql, values)
    
    
    def executescript(self, sql):
        """
        Executes given SQL script and returns new cursor.
        
        Args:
            sql: str
                SQL script.
        
        Return:
            sqlite.Cursor
                Cursor pointing to query results.
        """
        
        # assert connection
        self._assert_connection()
        
        # execute sql query
        return self._conn.executescript(sql)
    
    
    def commit(self):
        """Commits changes made during current transaction."""
        
        # assert connection
        self._assert_connection()
        
        # commit changes
        self._conn.commit()
    
    
    def table_exists(self, table):
        """
        Returns True if table exists, False otherwise.
        
        Args:
            table: str
                Table name to check.
        
        Returns:
            bool
                True if table exists, False otherwise.
        """
        
        # assert connection
        self._assert_connection()
        
        # execute sql query
        sql = f"SELECT count(0) FROM sqlite_master WHERE type='table' AND name='{table}'"
        cur = self._conn.execute(sql)
        
        return bool(cur.fetchone()[0])
    
    
    def _assert_connection(self):
        """Asserts database connection."""
        
        if self._conn is None:
            raise ValueError("Database connection is not opened!")
    
    
    def _check_db_format(self):
        """Checks whether database file is valid SQLite database."""
        
        with open(self._path, "r", encoding="Latin1") as f:
            ima = codecs.encode(str.encode(f.read(16)),'hex_codec')
        
        if ima and ima != b"53514c69746520666f726d6174203300":
            message = "Specified file is not a valid SQLite database."
            raise sqlite.Error(message)
