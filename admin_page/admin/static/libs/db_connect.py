import pymysql


class DBConnect:
    
    host = 'localhost'
    # db   = 'shop_crawling'
    db   = 'crawling_test'
    user = 'root'
    password = '1234'
    charset  = 'utf8'

    def __init__(self):
        self.conn = pymysql.connect(host=DBConnect.host, 
                                    user=DBConnect.user, 
                                    db=DBConnect.db, 
                                    password=DBConnect.password, 
                                    charset=DBConnect.charset) 
        self.cursor = self.conn.cursor()
        self.get_id = 0
        self.table = ''
        self.table_as = ''
        self.join = ''
        self.join_table_sql = ''

    def execute(self, sql, insert=False):
        try:
            self.cursor.execute(sql)
            if insert:
                self.cursor.execute('SELECT @@IDENTITY AS ID;')
                self.get_id = self.cursor.fetchone()[0]
            self.conn.commit()
            self.conn.close() 
        except pymysql.Error as e:
            print(f"SQL ERROR: {e}")
            self.conn.close()

    def close(self):
        self.conn.close()

    def get_inserted_id(self):
        return self.get_id

    def insert(self, table, values):
        column = '('+','.join(values.keys())+')'
        value  = "('"+"','".join(values.values())+"')"

        sql = "INSERT INTO " + DBConnect.db + '.' + table + ' ' + column + " VALUES " + value
        DBConnect.execute(self, sql, True)

    def update(self, table, values, where):
        set_value = ''
        set_value += ', '.join("{}='{}'".format(key,val) for key,val in values.items())
        sql = "UPDATE " + DBConnect.db + '.' + table + ' SET ' + set_value + ' ' + where
        DBConnect.execute(self, sql)

    def delete(self, table, where):
        sql = "DELETE FROM " + DBConnect.db + '.' + table + ' ' + where
        DBConnect.execute(self, sql)

    def findAll(self, table, column, where='', orderby='', limit=''):
        sql = "SELECT " + column + " FROM " + DBConnect.db + '.' + table + ' ' + where + ' ' + orderby + ' ' + limit
        try:
            self.cursor.execute(sql)
            rows = self.cursor.fetchall() 
            self.conn.close() 
        except pymysql.Error as e:
            print(f"SQL ERROR: {e}")
            self.conn.close()

        column_keys = column.split(', ')
        
        result = []
        for i, row in enumerate(rows):
            dict = {}
            for j, _r in enumerate(row):
                dict[column_keys[j]] = _r
            result.append(dict)

        return result

    def findAllFromJoinTable(self, column, where='', orderby='', limit=''):
        sql = 'SELECT ' + column + ' FROM ' + DBConnect.db + '.' + self.table + self.join_table_sql + ' ' + where + ' ' + orderby + ' ' + limit

        try:
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            self.conn.close()
        except pymysql.Error as e:
            print(f'SQL ERROR: {e}')
            self.conn.close()

        result = []
        if rows:
            column_keys = column.split(', ')
            for i, row in enumerate(rows):
                dict = {}
                for j, _r in enumerate(row):
                    dict[column_keys[j].split('.')[1].lstrip().split(' ')[0].replace(')', '')] = _r
                result.append(dict)

        return result

    def find(self, table, column, where=''):
        sql = "SELECT " + column + " FROM " + DBConnect.db + '.' + table + ' ' + where + ' LIMIT 0,1'

        try:
            self.cursor.execute(sql)
            row = self.cursor.fetchone() 
            self.conn.close() 
        except pymysql.Error as e:
            print(f"SQL ERROR: {e}")
            self.conn.close()
        
        column_keys = column.split(', ')
        result = {}

        try:
            if row:
                for j, _r in enumerate(row):
                    result[column_keys[j]] = _r
        except:
            return result

        return result

    def set_table(self, table, table_as):
        self.table = table + ' ' + table_as

    def join_table(self, table, table_as, join_direction, join_on):
        self.join += ' ' + join_direction + ' JOIN ' + table + ' ' + table_as + ' ON ' + join_on

    def get_join_table_sql(self):
        self.join_table_sql = self.join