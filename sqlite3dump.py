import os
# Mimic the sqlite3 console shell's .dump and .mode csv command for single or all tables
# Author: Paul Kippes & ZQZ44

class Dumper():
    def __init__(self, sqlite_connection):
        self.connection = sqlite_connection
    
    # dump a table to dir_path with the specific format(sql or csv)
    def dump(self, dir_path, table_name, output_format):
        if output_format.casefold() == "csv".casefold():
            result = self._iterdumpCSV(table_name)
        elif output_format.casefold() == "sql".casefold():
            result = self._iterdump(table_name)
        else:
            print("Unknown format")
        path = os.path.join(dir_path,table_name+".{0}".format(output_format.lower()))
        with open(path,'w') as f:
            for line in result:
                f.write("{0}\n".format(line))
    
    # dump all the table in the database to dir_path
    def dump_all(self, dir_path, output_format):
        result = self.connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        for name in result:
            self.dump(dir_path, name[0], output_format)
    
    # internal function to translate the result to csv
    def _iterdumpCSV(self, table_name):
        result = self.connection.execute("SELECT * from {0}".format(table_name)) 
        result_data = result.fetchall()
        if len(result_data) !=0:
            yield(','.join(str(header[0]) for header in result.description))
            for row in result_data:
                yield(','.join(str(value) if str(value) and str(value).isascii() and not " " in str(value) and value is not None else '"{0}"'.format(value) if value is not None else "" for value in row))
   
    # internal function to translate the result to sql
    def _iterdump(self, table_name):
        """
        Returns an iterator to the dump of the database in an SQL text format.
        Used to produce an SQL dump of the database.  Useful to save an in-memory
        database for later restoration.  This function should not be called
        directly but instead called from the Connection method, iterdump().
        """
        
        cu = self.connection.cursor()
        table_name = table_name

        yield('PRAGMA foreign_keys=OFF;')
        # add this pragma turns off checking of foreign keys as tables would be inconsistent while restoring.  It was introduced in SQLite 3.6.19.
        
        yield('BEGIN TRANSACTION;')
        # sqlite_master table contains the SQL CREATE statements for the database.
        
        q = """
           SELECT "name", "type", "sql"
            FROM "sqlite_master"
                WHERE "sql" NOT NULL AND
                "type" == 'table' AND
                "name" == '{0}'
            """
        schema_res = cu.execute(q.format(table_name))
        for table_name, type, sql in schema_res.fetchall():
            if table_name == 'sqlite_sequence':
                yield('DELETE FROM "sqlite_sequence";')
            elif table_name == 'sqlite_stat1':
                yield('ANALYZE "sqlite_master";')
            elif table_name.startswith('sqlite_'):
                continue
            else:
                yield('{0};'.format(sql.replace("CREATE TABLE","CREATE TABLE IF NOT EXISTS"))) 
                # add a checking for table exist(same as sqlite3 .dump)

            # Build the insert statement for each row of the current table
            table_name_ident = table_name.replace('"','""')
            res = cu.execute('PRAGMA table_info("{0}")'.format(table_name_ident))
            column_names = [str(table_info[1]) for table_info in res.fetchall()]
            q = """SELECT 'INSERT INTO {0} VALUES({1})' FROM "{0}";""".format(table_name_ident,",".join("""'||quote("{0}")||'""".format(col.replace('"', '""')) for col in column_names))
            query_res = cu.execute(q)
            for row in query_res:
                yield("{0};".format(row[0]))

        # Now when the type is 'index', 'trigger', or 'view'
        q = """
            SELECT "name", "type", "sql"
            FROM "sqlite_master"
                WHERE "sql" NOT NULL AND
                "type" IN ('index', 'trigger', 'view')
            """
        schema_res = cu.execute(q)
        for name, type, sql in schema_res.fetchall():
            yield('{0};'.format(sql))

        yield('COMMIT;')
