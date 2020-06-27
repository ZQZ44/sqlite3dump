# sqlite3dump

This file provides an class Dumper works for  [Python's sqlite3](https://github.com/python/cpython/blob/3.8/Lib/sqlite3). 

It is used to dump the specific table or separately dump all the tables to csv or sql file(s). 

It is functionally equivalent to console shell `sqlite3 DATABASE ".dump table_name" > table_name.sql` or `sqlite3 DATABASE -header -csv "select * from table_name" > table_name.csv`

For common cases, it should provided compeletely same result with sqlite console shell(using version SQLite 3.31.1)

# Usage
```python
import sqlite3
from sqlite3dump import Dumper
connection = sqlite3.connect("sample.db")
dumper = Dumper(connection)
dumper.dump('target_dir_path','table_name','csv or sql')
dumper.dump_all('target_dir_path','csv or sql')
```
