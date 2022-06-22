from ast import Index
from requests.api import get
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException

from bs4 import BeautifulSoup, Comment

import time
import requests
import re
import json
import ast

import data
from static.libs.db_connect import DBConnect
from static.libs.shop_crawler import ShopCrawler
import static.libs.elem as elem

def get_shop_info():
    crawling_DB = DBConnect()
    column = 'shop_idx, shop_name, shop_url, shop_cate_url, pg_param, item_container, item_list_elem, item_detail_elem'
    shop_info_list = crawling_DB.findAll('shop_info', column)

    if shop_info_list:
        return shop_info_list
    else:
        return False

def check_product(url):
    crawling_DB = DBConnect()
    column = 'pro_idx'
    where = f'WHERE pro_url="{url}"'
    pro_idx = crawling_DB.find('product_info', column, where)

    return pro_idx

def get_category(pro_cate, title):
    category = {
        "OUTER" : {
            "자켓":["자켓", "쟈켓", "셔켓", "jk", "jacket"],
            "코트":["코트", "바바리", "트렌치", "ct"],
            "점퍼":["점퍼", "집업", "야상", "바람막이", "패딩", "다운", "jp", "jumper"],
            "가디건":["가디건", "로브", "숄", "cardigan", "robe", "gown", "gardigan"],
            "베스트":["베스트", "vest"],
        },
        "TOP" : {
            "니트":["니트", "knit", "cd"],
            "블라우스":["블라우스", "셔츠", "남방", "셔켓", "shirt", "nb", "bl", "blouse"],
            "슬리브리스":["나시", "탑", "슬리브리스", "조끼", "top", "cami", "sleeve"],
            "티셔츠":["티셔츠", "맨투맨", "후드", "mtm", "tee", "hoody"],
        },
        "PANTS" : {
            "청바지":["데님", "진", "청바지", "jean", "jeans", "denim", "dn"],
            "반바지":["반바지", "숏츠", "쇼츠", "숏팬츠", "하프팬츠", "2부", "3부", "4부", "5부", "short", "shorts", "hp"],
            "슬랙스":["슬랙스", "sl"],
            "이지팬츠":["와이드", "조거", "밴딩", "밴드", "배기", "면팬츠", "통", "플리츠", "트레이닝", "wide", "jogger", "banding", "baggy"],
            "레깅스":["레깅스"],
        },
        "SKIRT" : {
            "치마":["치마", "스커트", "skirt", "sk"],
        },
        "DRESS" : {
            "원피스":["원피스", "dress", "ops", "op", 'onepiece'],
            "점프수트":["점프", "오버롤", "jump", "js"]
        }
    }

    cate = {}
    cate_text = False
    
    cate_keys = category.keys()
    for cate1 in cate_keys:
        set = ["set", "세트", "셋업", "&", "+"]
        for s in set:
            if cate1 == pro_cate:
                cate_text = pro_cate
    
    if cate_text:
        # pro_cate가 ETC가 아닌경우
        for cate2 in category[cate_text]:
            for value in category[cate_text][cate2]:
                if value in title:
                    if cate1 in cate:
                        # cate안에 cate1 있을 경우
                        values = []
                        is_value = False
                        for c in cate[cate_text]:
                            values.append(c)
                            if c == cate2:
                                is_value = True
                        if not is_value:
                            values.append(cate2)
                        cate[cate_text] = values
                    else:
                        cate[cate_text] = [cate2]
                        
    if not cate:
        # 넘어온 pro_cate가 ETC일 경우
        # 일치하는 카테고리가 없을 경우
        for cate1 in category:
            for cate2 in category[cate1]:
                for value in category[cate1][cate2]:
                    if value in title:
                        if cate1 in cate:
                            # cate안에 cate1 있을 경우
                            values = []
                            is_value = False
                            for c in cate[cate1]:
                                values.append(c)
                                if c == cate2:
                                    is_value = True
                            if not is_value:
                                values.append(cate2)
                            cate[cate1] = values
                        else:
                            cate[cate1] = [cate2]
        if not cate:
            t_shirt = ["티", "t_", "반팔", "-t", "t"]
            top = ["-n"]
            pants = ["팬츠", "pants", "pt"]
            
            for p in pants:
                if p in title:
                    cate["PANTS"] = ["팬츠"]
            
            if pro_cate == "TOP":
                for t in t_shirt:
                    if t in title:
                        cate["TOP"] = ["티셔츠"]
                for t in top:
                    if t in title:
                        cate["TOP"] = ["슬리브리스"]
    # 카테고리 걸러내기
    if "TOP" in cate and "DRESS" in cate:
        del cate["TOP"]
    if ("PANTS" in cate and "OUTER" in cate) or ("PANTS" in cate and "TOP" in cate) or ("PANTS" in cate and "SKIRT" in cate) or ("PANTS" in cate and "DRESS" in cate):
        del cate["PANTS"]
    if "SKIRT" in cate and "DRESS" in cate:
        del cate["DRESS"]
    if "OUTER" in cate and "DRESS" in cate:
        del cate["OUTER"]
        
    for key in cate:
        if key == "PANTS":
            if ("슬랙스" in cate["PANTS"]) and ("청바지" in cate["PANTS"]):
                cate["PANTS"].remove("슬랙스")
            elif ("슬랙스" in cate["PANTS"]) and ("이지팬츠" in cate["PANTS"]):
                cate["PANTS"].remove("이지팬츠")
    
    return json.dumps(cate, ensure_ascii=False)

def save_product_info(shop_idx, pro_url, pro_cate, pro_title, pro_price, pro_img):
    crawling_DB = DBConnect()
    insert_data = {
        'shop_idx' : str(shop_idx),
        'pro_url' : pro_url,
        'pro_cate' : str(pro_cate),
        'pro_title' : pro_title,
        'pro_price' : pro_price,
        'pro_img' : pro_img
    }
    crawling_DB.insert('product_info', insert_data)

def get_product():
    shop_info_list = get_shop_info()

    if shop_info_list:
        for info in shop_info_list:
            shop_idx = info['shop_idx']
            shop_url = info['shop_url']
            pg_param = '&' + info['pg_param'] + '='
            item_container = elem.get_elem(info['item_container'])
            item_list_elem = elem.get_elem(info['item_list_elem'])
            item_detail_elem = ast.literal_eval(info['item_detail_elem'])
            item_detail_elem['name_elem'] = elem.get_elem(item_detail_elem['name_elem'])
            item_detail_elem['price_elem'] = elem.get_elem(item_detail_elem['price_elem'])
            item_detail_elem['img_elem'] = elem.get_elem(item_detail_elem['img_elem'])

            shop_cate_url_list = ast.literal_eval(info['shop_cate_url'])

            for cate in shop_cate_url_list.keys():
                for cate_url in shop_cate_url_list[cate]:
                    new_crawling = ShopCrawler(shop_url, cate_url, item_container, pg_param, item_list_elem, item_detail_elem)
                    new_crawling.set_pagination()
                    new_crawling.set_item_urls()
                    item_urls = new_crawling.get_item_urls()

                    for item_url in item_urls:
                        if check_product(shop_url+item_url):
                            continue
                        else:
                            get_product_detail = new_crawling.get_item_detail(shop_url+item_url)

                            if get_product_detail:
                                pro_url = get_product_detail[0]
                                pro_cate = get_category(cate, get_product_detail[1])
                                pro_title = get_product_detail[1]
                                pro_price = get_product_detail[2]
                                pro_img = save_img(get_product_detail[3])

                                save_product_info(shop_idx, pro_url, pro_cate, pro_title, pro_price, pro_img)
                            else:
                                print('false')
                                continue
        
        return True
    else:
        return False

def get_product_url():
    db_class = data.DataBase()

    sql = db_class.select_product_url()
    db_class.execute(sql)
    pro_url_list = db_class.fetchall()
    db_class.close()

    return pro_url_list

def save_img(img_src_list):
    img_seq_list = ''
    for img_src in img_src_list:
        insert_data = {
            "img_data" : img_src
        }
        crawling_DB = DBConnect()
        crawling_DB.insert('product_img', insert_data)
        img_seq = crawling_DB.get_inserted_id()
        img_seq_list += ('' if img_seq_list == '' else '; ') + str(img_seq)
    
    return img_seq_list

def update_product_img(info):
    db_class = data.DataBase()

    sql = db_class.update_product(info)
    db_class.execute(sql)
    db_class.commit()
    db_class.close()

def get_product_img():
    pro_info_list = get_product_url()

    for pro_info in pro_info_list:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(pro_info[3], headers = headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        img_list = soup.select(pro_info[1] + ' img')

        img_seq_list = ''
        for img in img_list:
            try:
                if img['src'] == '':
                    pass
                elif img['src'][0:2] == '//':
                    img_src = 'http:' + img['src']
                elif 'http' in img['src']:
                    img_src = img['src']
                else:
                    img_src = pro_info[0][:-1] + img['src']
                
                img_seq = save_img([pro_info[2], img_src])
                img_seq_list += str(img_seq) if img_seq_list == '' else '; ' + str(img_seq)
            except:
                continue
        
        update_product_img([img_seq_list, pro_info[3], pro_info[2]])
