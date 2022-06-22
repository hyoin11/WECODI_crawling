from flask import Flask, render_template, request, redirect

import json
import os

from flask.helpers import url_for

import data
import crawling
from static.libs.db_connect import DBConnect
import static.libs.elem as elem

app = Flask(__name__)

@app.route('/')
def index():
    crawling_DB = DBConnect()
    column = 'COUNT(shop_idx)'
    result = crawling_DB.find('shop_info', column)
    shop_count = result[column]

    crawling_DB = DBConnect()
    column = 'COUNT(pro_idx)'
    result = crawling_DB.find('product_info', column)
    product_count = result[column]

    return render_template('index.html', shop_count=shop_count, product_count=product_count)

@app.route('/shop_list')
def shop_list():
    current_page = request.args.get('page')
    if(current_page == None):
        current_page = 1
    else:
        current_page = int(current_page)

    crawling_DB = DBConnect()
    column = 'COUNT(shop_idx)'
    result = crawling_DB.find('shop_info', column)
    shop_count = int(result[column])

    # 전체 페이지
    if shop_count % 20 == 0:
        total_page = int(shop_count / 20)
    else:
        total_page = int(shop_count / 20) + 1

    if current_page % 10 == 0:
        start_paging = current_page - 9
    else:
        start_paging = (int(current_page / 10) * 10) + 1
    end_paging = start_paging + 9
    if total_page < end_paging:
        end_paging = total_page

    start = (current_page - 1) * 20
    get_list_count = 20

    crawling_DB = DBConnect()
    where = ''
    column2 = 'shop_idx, shop_name, shop_url, DATE(shop_regdate)'
    orderby = 'ORDER BY shop_idx DESC'
    limit = f'LIMIT {start}, {get_list_count}'
    shop_list = crawling_DB.findAll('shop_info', column2, where, orderby, limit)

    return render_template('shop_list.html', shop_list = shop_list, start_paging = start_paging, end_paging = end_paging, total_page = total_page, current_page = current_page, shop_count = shop_count)

@app.route('/shop_check', methods=['POST'])
def shop_check():
    url = request.form['url']

    crawling_DB = DBConnect()
    where = f'WHERE shop_url="{url}"'
    column = 'shop_idx'
    shop_info = crawling_DB.find('shop_info', column, where)
    if shop_info:
        return json.dumps(False)
    else:
        return json.dumps(True)

    

@app.route('/shop_add', methods=['GET', 'POST'])
def shop_add():
    if request.method == 'GET':
        return render_template('shop_form.html')
    elif request.method == 'POST':
        shop_name = request.form['input_shop_name']
        shop_url = request.form['input_shop_url']
        cateURL_count = int(request.form['cateURL_count'])
        shop_cate_url = {}
        for i in range(1, cateURL_count + 1):
            if request.form['input_cate_{}'.format(i)] in shop_cate_url:
                values = []
                for url in shop_cate_url[request.form['input_cate_{}'.format(i)]]:
                    values.append(url)
                values.append(request.form['input_cateURL_{}'.format(i)])

                shop_cate_url[request.form['input_cate_{}'.format(i)]] = values
            else:
                shop_cate_url[request.form['input_cate_{}'.format(i)]] = [request.form['input_cateURL_{}'.format(i)]]
        shop_cate_url = json.dumps(shop_cate_url, ensure_ascii=False)
            
        pg_param = request.form['input_pg_param']
        item_container = elem.insert_elem(request.form['input_container'])
        item_list_elem = elem.insert_elem(request.form['input_list_elem'])
        name_elem = elem.insert_elem(request.form['input_name_elem'])
        price_elem = elem.insert_elem(request.form['input_price_elem'])
        img_elem = elem.insert_elem(request.form['input_img_elem'])

        item_detail_elem = {
            'name_elem': name_elem,
            'price_elem': price_elem,
            'img_elem': img_elem
        }
        item_detail_elem = json.dumps(item_detail_elem, ensure_ascii=False)

        crawling_DB = DBConnect()
        insert_data = {
            'shop_name' : shop_name,
            'shop_url' : shop_url,
            'shop_cate_url' : str(shop_cate_url),
            'pg_param' : pg_param,
            'item_container' : item_container,
            'item_list_elem' : item_list_elem,
            'item_detail_elem' : str(item_detail_elem)
        }
        crawling_DB.insert('shop_info', insert_data)

        return redirect('/shop_list')

@app.route('/shop_modify', methods=['GET', 'POST'])
def shop_modify():
    if request.method == 'GET':
        shop_idx = request.args.get('shop_idx')

        crawling_DB = DBConnect()
        where = f'WHERE shop_idx={shop_idx}'
        column = 'shop_name, shop_url, shop_cate_url, pg_param, item_container, item_list_elem, item_detail_elem'
        shop_info = crawling_DB.find('shop_info', column, where)

        shop_cate_url = json.loads(shop_info['shop_cate_url'].replace("'", "\""))
        item_container = elem.get_elem(shop_info['item_container'], True)
        item_list_elem = elem.get_elem(shop_info['item_list_elem'], True)
        item_detail_elem = json.loads(shop_info['item_detail_elem'].replace("'", "\""))
        item_detail_elem['name_elem'] = elem.get_elem(item_detail_elem['name_elem'], True)
        item_detail_elem['price_elem'] = elem.get_elem(item_detail_elem['price_elem'], True)
        item_detail_elem['img_elem'] = elem.get_elem(item_detail_elem['img_elem'], True)
        
        return render_template('shop_form.html', shop_modify=True, shop_info=shop_info, shop_idx=shop_idx, shop_cate_url=shop_cate_url, item_container=item_container, item_list_elem=item_list_elem, item_detail_elem=item_detail_elem)

    elif request.method == 'POST':
        shop_idx = request.form['input_shop_idx']
        shop_name = request.form['input_shop_name']
        shop_url = request.form['input_shop_url']
        cateURL_count = int(request.form['cateURL_count'])
        shop_cate_url = {}
        for i in range(1, cateURL_count + 1):
            if request.form['input_cate_{}'.format(i)] in shop_cate_url:
                values = []
                for url in shop_cate_url[request.form['input_cate_{}'.format(i)]]:
                    values.append(url)
                values.append(request.form['input_cateURL_{}'.format(i)])

                shop_cate_url[request.form['input_cate_{}'.format(i)]] = values
            else:
                shop_cate_url[request.form['input_cate_{}'.format(i)]] = [request.form['input_cateURL_{}'.format(i)]]
        shop_cate_url = json.dumps(shop_cate_url, ensure_ascii=False)
        
        pg_param = request.form['input_pg_param']
        container_idx = request.form['input_container_idx']
        container = request.form['input_container']
        item_container_elem = elem.update_elem(container_idx, container)
        list_elem_idx = request.form['input_list_elem_idx']
        list_elem = request.form['input_list_elem']
        item_list_elem = elem.update_elem(list_elem_idx, list_elem)
        name_elem_idx = request.form['input_name_elem_idx']
        name_elem = request.form['input_name_elem']
        name_elem = elem.update_elem(name_elem_idx, name_elem)
        price_elem_idx = request.form['input_price_elem_idx']
        price_elem = request.form['input_price_elem']
        price_elem = elem.update_elem(price_elem_idx, price_elem)
        img_elem_idx = request.form['input_img_elem_idx']
        img_elem = request.form['input_img_elem']
        img_elem = elem.update_elem(img_elem_idx, img_elem)

        crawling_DB = DBConnect()

        item_detail_elem = {
            'name_elem': name_elem,
            'price_elem': price_elem,
            'img_elem': img_elem
        }
        item_detail_elem = json.dumps(item_detail_elem, ensure_ascii=False)

        update_data = {
            'shop_name' : shop_name,
            'shop_url' : shop_url,
            'shop_cate_url' : shop_cate_url,
            'pg_param' : pg_param,
            'item_container' : item_container_elem,
            'item_list_elem' : item_list_elem,
            'item_detail_elem' : item_detail_elem
        }
        where = f'WHERE shop_idx={shop_idx}'
        crawling_DB.update('shop_info', update_data, where)

        return redirect('/shop_list')

@app.route('/shop_delete', methods=['POST'])
def shop_delete():
    shop_idx = request.form['shop_idx']

    crawling_DB = DBConnect()
    where = f'WHERE shop_idx IN ({shop_idx})'
    crawling_DB.delete('shop_info', where)

    return json.dumps(True)


@app.route('/product_list')
def product_list():
    keyword = request.args.get('find_keyword')
    current_page = request.args.get('page')

    if current_page == None: current_page = 1
    current_page = int(current_page)

    if keyword == None:
        crawling_DB = DBConnect()
        column = 'COUNT(pro_idx)'
        result = crawling_DB.find('product_info', column)
        product_count = int(result[column])
    else:
        crawling_DB = DBConnect()
        column = 'COUNT(pro_idx)'
        where = f'WHERE pro_title LIKE "%{keyword}%"'
        result = crawling_DB.find('product_info', column, where)
        product_count = int(result[column])

    if product_count % 20 == 0:
        total_page = int(product_count / 20)
    else:
        total_page = int(product_count / 20) + 1

    if current_page % 10 == 0:
        start_paging = current_page - 9
    else:
        start_paging = (int(current_page / 10) * 10) + 1
    end_paging = start_paging + 9
    if total_page < end_paging:
        end_paging = total_page

    start = (current_page - 1) * 20
    get_list_count = 20

    if keyword == None:
        crawling_DB = DBConnect()
        column = 's.shop_name, p.pro_idx, p.pro_cate, p.pro_title, p.pro_price, p.pro_activate, DATE(p.pro_regdate)'
        where = ''
        orderby = 'ORDER BY pro_regdate DESC'
        limit = f'LIMIT {start}, {get_list_count}'

        crawling_DB.set_table('product_info', 'p')
        crawling_DB.join_table('shop_info', 's', 'INNER', 's.shop_idx = p.shop_idx')
        crawling_DB.get_join_table_sql()
        pro_list = crawling_DB.findAllFromJoinTable(column, where, orderby, limit)

        pro_cate = []
        for product in pro_list:
            pro_cate.append(json.loads(product['pro_cate'].replace("'", "\"")))

        return render_template('product_list.html', pro_list=pro_list, pro_cate=pro_cate, start_paging=start_paging, end_paging=end_paging, total_page=total_page, current_page=current_page, product_count=product_count)
    else:
        crawling_DB = DBConnect()
        column = 's.shop_name, p.pro_idx, p.pro_cate, p.pro_title, p.pro_price, p.pro_activate, DATE(p.pro_regdate)'
        where = f'WHERE p.pro_title LIKE "%{keyword}%"'
        orderby = 'ORDER BY pro_regdate DESC'
        limit =f'LIMIT {start}, {get_list_count}'

        crawling_DB.set_table('product_info', 'p')
        crawling_DB.join_table('shop_info', 's', 'INNER', 's.shop_idx = p.shop_idx')
        crawling_DB.get_join_table_sql()
        pro_list = crawling_DB.findAllFromJoinTable(column, where, orderby, limit)
        
        return render_template('product_list.html', pro_list=pro_list, start_paging = start_paging, end_paging = end_paging, total_page = total_page, current_page = current_page, product_count = product_count, keyword = keyword)

@app.route('/product_view')
def product_view():
    pro_idx = request.args.get('pro_idx')

    crawling_DB = DBConnect()
    column = 's.shop_name, p.pro_idx, p.pro_url, p.pro_cate, p.pro_title, p.pro_price, p.pro_img, p.pro_activate'
    where = f'WHERE pro_idx = {pro_idx}'
    orderby = ''
    limit = f'LIMIT 0,1'

    crawling_DB.set_table('product_info', 'p')
    crawling_DB.join_table('shop_info', 's', 'INNER', 's.shop_idx = p.shop_idx')
    crawling_DB.get_join_table_sql()
    pro_info = crawling_DB.findAllFromJoinTable(column, where, orderby, limit)[0]

    pro_img_list = []
    pro_img_seq_list = pro_info['pro_img'].split('; ')

    for pro_img_seq in pro_img_seq_list:
        if pro_img_seq:
            crawling_DB = DBConnect()
            column = 'img_idx, img_data'
            where = f'WHERE img_idx = {pro_img_seq}'

            img_data = crawling_DB.find('product_img', column, where)
            pro_img_list.append((img_data['img_idx'], img_data['img_data']))

    cate_list = json.loads(pro_info['pro_cate'].replace("'", "\""))

    img_count = len(pro_img_list)

    return render_template('product_view.html', pro_info = pro_info, pro_img_list = json.dumps(pro_img_list), img_count = img_count, cate_list = cate_list)

@app.route('/product_modify', methods=['POST'])
def product_modify():
    crawling_DB = DBConnect()

    mod = request.form['mod']
    pro_idx = request.form['pro_idx']

    if mod == 'get':
        column = 's.shop_name, p.pro_idx, p.pro_url, p.pro_cate, p.pro_title, p.pro_price, p.pro_activate'
        where = f'WHERE pro_idx = {pro_idx}'
        orderby = ''
        limit = f'LIMIT 0,1'

        crawling_DB.set_table('product_info', 'p')
        crawling_DB.join_table('shop_info', 's', 'INNER', 's.shop_idx = p.shop_idx')
        crawling_DB.get_join_table_sql()
        pro_info = crawling_DB.findAllFromJoinTable(column, where, orderby, limit)[0]

        return pro_info

    elif mod == 'activate':
        pro_activate = request.form['pro_activate']

        crawling_DB = DBConnect()
        update_data = {
            'pro_activate' : pro_activate
        }
        where = f'WHERE pro_idx = {pro_idx}'
        crawling_DB.update('product_info', update_data, where)

        return json.dumps(True)

    elif mod == 'info':
        pro_url = request.form['input_pro_url']
        cate_count = request.form['cate_count']
        pro_cate = {}
        for i in range(1, int(cate_count)+1):
            cate = request.form['cate_{}'.format(i)].split('-')

            if cate[0] in pro_cate:
                values = []
                for value in pro_cate[cate[0]]:
                    values.append(value)
                values.append(cate[1])

                pro_cate[cate[0]] = values
            else:
                pro_cate[cate[0]] = [cate[1]]
        pro_cate = json.dumps(pro_cate, ensure_ascii=False)

        pro_title = request.form['input_pro_title']
        pro_price = request.form['input_pro_price']
        pro_activate = request.form['input_pro_activate']

        crawling_DB = DBConnect()
        update_data = {
            'pro_url' : pro_url,
            'pro_cate' : str(pro_cate),
            'pro_title' : pro_title,
            'pro_price' : pro_price,
            'pro_activate' : pro_activate
        }
        where = f'WHERE pro_idx = {pro_idx}'
        crawling_DB.update('product_info', update_data, where)

        return redirect('/product_list')
    
    elif mod == 'all':
        pro_url = request.form['input_pro_url']
        cate_count = int(request.form['cate_count'])
        pro_cate = {}
        for i in range(1, cate_count + 1):
            cate_text = request.form['cate_{}'.format(i)].split('-')
            if cate_text[0] in pro_cate:
                values = []
                is_value = False
                for c in pro_cate[cate_text[0]]:
                    values.append(c)
                    if c == cate_text[1]:
                        is_value = True
                if not is_value:
                    values.append(cate_text[1])
                pro_cate[cate_text[0]] = values
            else:
                pro_cate[cate_text[0]] = [cate_text[1]]
        pro_cate = json.dumps(pro_cate, ensure_ascii=False)
        pro_title = request.form['input_pro_title']
        pro_price = request.form['input_pro_price']
        pro_activate = request.form['input_pro_activate']

        img_count = int(request.form['img_count'])
        img_seq_list = ''
        for i in range(1, img_count + 1):
            img_seq_list += ('' if i == 1 else '; ') + request.form['img_idx_{}'.format(i)]
        
        update_data = {
            'pro_url' : pro_url,
            'pro_cate' : str(pro_cate),
            'pro_title' : pro_title,
            'pro_price' : pro_price,
            'pro_img' : img_seq_list,
            'pro_activate' : pro_activate,
        }
        where = f'WHERE pro_idx = {pro_idx}'
        crawling_DB.update('product_info', update_data, where)
        
        return redirect('/product_list')

@app.route('/product_delete', methods=['POST'])
def product_delete():
    pro_idx = request.form['pro_idx']

    crawling_DB = DBConnect()
    where = f'WHERE pro_idx IN ({pro_idx})'
    crawling_DB.delete('product_info', where)

    return json.dumps(True)

@app.route('/get_product', methods=['POST'])
def product_crawling():
    mod = request.form['mod']

    if mod == 'product':
        return json.dumps(crawling.get_product())

@app.route('/img_delete', methods=['GET', 'POST'])
def img_modify():
    mod = request.form['mod']

    if mod == 'insert_cancel':
        img_idx = request.form['img_idx']

        crawling_DB = DBConnect()
        column = 'img_data'
        where = f'WHERE img_idx = {img_idx}'
        result = crawling_DB.find('product_img', column, where)
        img_data = result[column]

        os.remove(img_data)

        crawling_DB = DBConnect()
        crawling_DB.delete('product_img', where)

    return json.dumps(True)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    pro_idx = request.args.get('pro_idx')

    if request.method == 'GET':
        print('get')
    else:
        print('POST')

        file = request.files['file']

        app_root = os.path.dirname(os.path.abspath(__file__).replace('\\', '/'))
        target = os.path.join(app_root + '/', 'static/uploads/')
        filename = file.filename
        destination = ''.join([target, filename])

        file.save(destination)

        crawling_DB = DBConnect()
        insert_data = {
            'img_data' : destination
        }
        crawling_DB.insert('product_img', insert_data)
        img_idx = crawling_DB.get_inserted_id()

        return json.dumps(img_idx)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')

