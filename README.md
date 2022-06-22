# contents_crawling
Crawling shopping website

# 모듈
### 모듈추가
####  - 2021.08.04
######   1. 크롤러: libs/shop_crawler.py
######   2. DB:   libs/db_connect.py

### 모듈수정
####  - 2021.08.05
######   1. DB:   libs/db_connect.py

### 모듈 ref 수정 
####  - 2021.08.06 by Breana
#####    1. DB:   libs/db_connect.py 
#####       - insert id, join table 추가 
#####       - join table 사용예시: 
<pre><code>
        DBConnect = DBConnect()
        DBConnect.set_table('user', 'U')
        DBConnect.join_table('user_status', 'US', 'LEFT', 'U.user_seq = US.user_seq')
        DBConnect.join_table('user_clothes', 'UC', 'LEFT', 'US.user_seq = UC.user_seq')
        DBConnect.get_join_table_sql()
        DBConnect.findAllFromJoinTable('U.user_seq > 0', 'U.user_id, US.user_clothes_count, UC.user_clothe_title', 'ORDER BY U.user_seq')
        
</code></pre>

### 모듈추가
####  - 2021.08.13
######   1. element: libs/elem.py

### 모듈수정
####  - 2021.09.09
######   1. 크롤러:   libs/shop_crawler.py


# admin_page
### admin_page수정
####  - 2021.08.05
######   1. templates/index.html
######   2. templates/shop_list.html
######   3. templates/shop_form.html

### admin_page수정
####  - 2021.08.10
######   1. templates/shop_list.html
######   2. templates/shop_form.html
######   3. templates/product_list.html

### admin_page수정
####  - 2021.08.13
######   1. templates/shop_form.html

### admin_page수정
####  - 2021.08.19
######   1. templates/shop_form.html
######   2. templates/product_list.html
######   3. templates/product_view.html

### admin_page수정
####  - 2021.09.09
######   1. templates/shop_form.html
######   2. templates/product_list.html
######   3. templates/product_view.html


# webview
### webview_page
####  - 2021.09.06
######   1. search_list.html
######   2. search_product.html

### webview_page 수정
####  - 2021.09.07
######   1. search_list.html
######   2. search_product.html