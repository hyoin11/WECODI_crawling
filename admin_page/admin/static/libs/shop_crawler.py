import requests as req
from bs4 import BeautifulSoup
import re

# headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
headers = {'User-Agent': 'Mozilla/5.0'}

version = 1.0

# [ ShopCrawler 기본 로직 ] 
# 1. __init__        : 크롤링할 쇼핑몰 obj init 
# 2. set_pagination  : 해당 카테고리의 멀티 페이지 존재여부 판단 및 아이템 갯수 체크 
# 3. set_item_urls   : 아이템 URL 리스트 세팅 (DB데이터, 경우에 따라 조정 필요)
# 4. get_item_urls   : 아이템 URL 리스트 가져오기 
# 5. get_item_detail : 아이템 상세 페이지 크롤링 

class ShopCrawler:
    """
      [크롤링 쇼핑 콘텐츠]
      - param cate_url: 쇼핑몰링크(카테고리 지정된)
      - param item_container : 아이템 리스트를 포함하는 container
      - param pg_param : pagination 파라미터(사이트의 페이지이동 방식에 따라 수정 필요) 
      - param item_list_elem: 상품리스트 항목
      - param item_detail_elem: 상품상세 항목 
    """

    def __init__(self, shop_url, cate_url, item_container, pg_param, item_list_elem, item_detail_elem):
        self.shop_url = shop_url
        self.cate_url = shop_url + cate_url
        self.item_container = item_container
        self.pg_param = pg_param
        self.item_list_elem = item_list_elem
        self.item_detail_elem = item_detail_elem
        self.pg_urls = [] # 페이지 전체 리스트 
        self.item_count = 0 # 아이템 갯수
        self.item_urls = []

    def set_content(self, url):
        data = req.get(url, headers = headers)
        return BeautifulSoup(data.content, "html.parser")

    def set_pagination(self):
        pg_urls = []
        item_count = 0
        pg_index = 1
        while True:
            url = self.cate_url + self.pg_param + str(pg_index) # ex) 'https://www.choper.kr/product/list.html?cate_no=24' + '&page=' + '1'
            page_content = ShopCrawler.set_content(self, url)
            main_container = page_content.find(self.item_container[0][1], self.item_container[0][2])
            try: 
                lis = main_container.findAll(self.item_list_elem[0][1], self.item_list_elem[0][2]) 
                len_of_lis = len(lis)
                if len_of_lis>0:
                    pg_urls.append(url)
                    item_count += len_of_lis
                    pg_index += 1
                else:
                    break
            except:
                print("item container does not exist.")
                break
                
        self.pg_urls = pg_urls
        self.item_count = item_count

    def set_item_urls(self):
        item_urls = []
        for pg in self.pg_urls:
            page_content = ShopCrawler.set_content(self, pg)
            main_container  = page_content.find(self.item_container[0][1], self.item_container[0][2])
            lis = main_container.findAll(self.item_list_elem[0][1], self.item_list_elem[0][2])
            for item in lis:
                a = item.find("a")
                url = a.get('href')
                item_urls.append(url)

        self.item_urls = item_urls

    def get_item_urls(self):
        return self.item_urls

    def get_item_detail(self, item_url):
        # container = self.item_detail_elem['container']
        # main_img_area = self.item_detail_elem['main_img_area']
        # info_area = self.item_detail_elem['info_area']

        # page_content = ShopCrawler.set_content(self, item_url)
        # detail_container = page_content.find(container[0], container[1])

        # #image
        # dt_image = detail_container.find(main_img_area[0], main_img_area[1])
        # image = dt_image.find("img").get('src')

        # #product name
        # dt_info = detail_container.find(info_area[0], info_area[1])
        # name = dt_info.find(info_area[2]).getText()

        # return image, name


        name_elem = self.item_detail_elem['name_elem']
        price_elem = self.item_detail_elem['price_elem']
        img_elem = self.item_detail_elem['img_elem']

        page_content = ShopCrawler.set_content(self, item_url)

        try:
            # product_name
            for i, elem in enumerate(name_elem, start=0):
                if i == 0:
                    title = page_content.find(elem[1], elem[2])
                else:
                    title = title.find(elem[1], elem[2])


            for br in title.findAll('br'): br.extract()
            for i in title.findAll('i'): i.extract()
            for font in title.findAll('font'): font.extract()

            title = title.text.strip()
            title = re.sub('\(.*?\)', '', title)
            title = re.sub('\[.*?\]', '', title)

            # product_price
            for i, elem in enumerate(price_elem, start=0):
                if i == 0:
                    price = page_content.find(elem[1], elem[2])
                else:
                    price = price.find(elem[1], elem[2])
            price = price.text.strip()
            price = re.sub('₩', '', price)
            
            # product_img
            for i, elem in enumerate(img_elem, start=0):
                if i == 0:
                    img_area = page_content.find(elem[1], elem[2])
                else:
                    img_area = img_area.find(elem[1], elem[2])
            
            img_list = img_area.findAll('img')
            
            img_src_list = []
            for img in img_list:
                img_src = img.get('src')

                if not img_src:
                    img_src = img.get('ec-data-src')
                if not img_src:
                    img_src = img.get('data-src')
                
                try:
                    if img_src == '' or 'http' in img_src:
                        pass
                    elif img_src[0:2] == '//':
                        img_src = 'http:' + img_src
                    else:
                        img_src = self.shop_url + img_src
                    
                    img_src_list.append(img_src)
                except:
                    continue

            return item_url, title, price, img_src_list
        except:
            return False



if __name__ == '__main__':
    cate_url = []
    item_container = []
    pg_param = ''
    item_list_elem = []
    item_detail_elem = []
    ShopCrawler(cate_url, item_container, pg_param, item_list_elem, item_detail_elem)
