import pymysql.cursors

class DataBase:
    def __init__(self):
        self.conn = pymysql.connect(
            host = 'localhost',
            user = 'root',
            password = '1234',
            db = 'test_db',
            charset = 'utf8'
        )

        self.cursor = self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


    def select_shop_count(self):
        return '''SELECT COUNT(shop_seq) FROM shop_info'''

    def select_shop(self, params=None):
        if not params:
            # select shop all
            return '''SELECT shop_seq, shop_name, shop_url, shop_cate, shop_list_position, shop_paging_position, shop_detail_content FROM shop_info WHERE shop_crawling = "false"'''
        elif len(params) == 1:
            # select shop one
            return '''SELECT shop_seq, shop_name, shop_url, shop_cate, shop_list_position, shop_paging_position, shop_detail_content FROM shop_info WHERE shop_seq = {}'''.format(params[0])
        elif len(params) == 2:
            # select shop list
            return '''SELECT shop_seq, shop_name, shop_url, DATE(shop_regdate) FROM shop_info ORDER BY shop_regdate DESC LIMIT {}, {}'''.format(params[0], params[1])
            

    def insert_shop(self, params):
        return '''INSERT INTO shop_info (shop_name, shop_url, shop_cate, shop_list_position, shop_paging_position, shop_detail_content) VALUES ("{}", "{}", "{}", "{}", "{}", "{}")'''.format(params[0], params[1], params[2], params[3], params[4], params[5])

    def update_shop(self, params):
        if len(params) == 1:
            return '''UPDATE shop_info SET shop_crawling="true" WHERE shop_seq in ({})'''.format(params[0])
        elif len(params) == 7:
            return '''UPDATE shop_info SET shop_name="{}", shop_url="{}", shop_cate="{}", shop_list_position="{}", shop_paging_position="{}", shop_detail_content="{}" WHERE shop_seq={}'''.format(params[0], params[1], params[2], params[3], params[4], params[5], params[6])

    def delete_shop(self, params):
        return '''DELETE FROM shop_info WHERE shop_seq IN ({})'''.format(params)


    def select_product_count(self):
        return '''SELECT COUNT(pro_seq) FROM product_info'''

    def select_product_count_keyword(self, params):
        return '''SELECT COUNT(pro_seq) FROM product_info WHERE pro_title LIKE "%{}%"'''.format(params)

    def select_product(self, params=None):
        if len(params) == 1:
            # select product one
            return '''SELECT s.shop_name, p.pro_seq, p.pro_url, p.pro_cate, p.pro_title, p.pro_price, p.pro_img, p.pro_activate FROM product_info p INNER JOIN shop_info s ON (s.shop_seq = p.shop_seq) WHERE p.pro_seq={}'''.format(params[0])
        elif len(params) == 2:
            # select product list
            return '''SELECT s.shop_name, p.pro_seq, p.pro_cate, p.pro_title, p.pro_price, p.pro_activate, DATE(p.pro_regdate) FROM product_info p INNER JOIN shop_info s ON (s.shop_seq = p.shop_seq) ORDER BY pro_regdate DESC LIMIT {}, {}'''.format(params[0], params[1])

    def select_product_keyword(self, params):
        return '''SELECT s.shop_name, p.pro_seq, p.pro_cate, p.pro_title, p.pro_price, p.pro_activate, DATE(p.pro_regdate) FROM product_info p INNER JOIN shop_info s ON (s.shop_seq = p.shop_seq) WHERE p.pro_title LIKE "%{}%" ORDER BY p.pro_regdate DESC LIMIT {}, {}'''.format(params[0], params[1], params[2])

    def insert_product(self, params):
        return '''INSERT INTO product_info (shop_seq, pro_url, pro_cate, pro_title, pro_price) VALUES ("{}", "{}", "{}", "{}", "{}")'''.format(params[0], params[1], params[2], params[3], params[4])

    def update_product(self, params):
        if len(params) == 2:
            # update product activate
            return '''UPDATE product_info SET pro_activate="{}" WHERE pro_seq={}'''.format(params[0], params[1])
        elif len(params) == 3:
            # update product img
            return '''UPDATE product_info SET pro_img="{}" WHERE pro_url="{}" AND pro_seq={}'''.format(params[0], params[1], params[2])
        elif len(params) == 6:
            # update product info
            return '''UPDATE product_info SET pro_url="{}", pro_cate="{}", pro_title="{}", pro_price="{}", pro_activate="{}" WHERE pro_seq={}'''.format(params[0], params[1], params[2], params[3], params[4], params[5])
        elif len(params) == 7:
            # update product all
            return '''UPDATE product_info SET pro_url="{}", pro_cate="{}", pro_title="{}", pro_price="{}", pro_activate="{}", pro_img="{}" WHERE pro_seq={}'''.format(params[0], params[1], params[2], params[3], params[4], params[5], params[6])
    
    def delete_product(self, params):
        return '''DELETE FROM product_info WHERE pro_seq IN ({})'''.format(params)


    def select_product_url(self):
        return '''SELECT s.shop_url, s.shop_detail_content, p.pro_seq, p.pro_url FROM product_info p LEFT JOIN shop_info s ON(p.shop_seq = s.shop_seq) ORDER BY pro_regdate DESC'''

    def select_img(self, params):
        return '''SELECT img_seq, img_data FROM product_img WHERE img_seq={}'''.format(params)

    def insert_img(self, params):
        return '''INSERT INTO product_img (pro_seq, img_data) VALUES ({}, "{}")'''.format(params[0], params[1])

    def delete_img(self, params):
        return '''DELETE FROM product_img WHERE img_seq={}'''.format(params)

    def select_last_id(self):
        return '''SELECT LAST_INSERT_ID()'''


    def execute(self, sql):
        self.cursor.execute(sql)

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()