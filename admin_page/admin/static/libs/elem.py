# from db_connect import DBConnect

from static.libs.db_connect import DBConnect

# db_connect.DBConnect()

def slice_elem(str):
    if '.' in str:
        el = str.split('.')
        tag = el[0]
        attr = 'class'
        attr_value = el[1]
    elif '#' in str:
        el = str.split('#')
        tag = el[0]
        attr = 'id'
        attr_value = el[1]
    else:
        tag = str
        attr = ''
        attr_value = ''

    return tag, attr, attr_value

def insert_elem(elem):
    elem_arr = elem.split(' ')

    elem_idx_list = ''
    for el in elem_arr:
        result = slice_elem(el)

        crawling_DB = DBConnect()
        insert_data = {
            "elem_tag" : result[0],
            "elem_attr" : result[1],
            "elem_attr_value" : result[2],
        }
        crawling_DB.insert('elem_info', insert_data)
        elem_idx = str(crawling_DB.get_inserted_id())
        elem_idx_list += ('' if elem_idx_list == '' else ', ') + elem_idx

    return elem_idx_list

def update_elem_db(elem_idx, elem):
    el = slice_elem(elem)
    crawling_DB = DBConnect()
    update_data = {
        'elem_tag' : el[0],
        'elem_attr' : el[1],
        'elem_attr_value' : el[2],
    }
    where = f'WHERE elem_idx={elem_idx}'
    crawling_DB.update('elem_info', update_data, where)

def delete_elem(elem_idx):
    crawling_DB = DBConnect()
    where = f'WHERE elem_idx={elem_idx}'
    crawling_DB.delete('elem_info', where)

def update_elem(elem_idx_list, elem_info):
    elem_idx_arr = elem_idx_list.split(', ')
    len_elem_idx_arr = len(elem_idx_arr)
    elem_arr = elem_info.split(' ')
    len_elem_arr = len(elem_arr)

    elem_idx_list = ''
    if len_elem_idx_arr == len_elem_arr:
        # 수정
        for i in range(len_elem_idx_arr):
            update_elem_db(elem_idx_arr[i], elem_arr[i])
            elem_idx_list += ('' if elem_idx_list == '' else ', ') + elem_idx_arr[i]

    elif len_elem_idx_arr > len_elem_arr:
        # 삭제
        for i in range(len_elem_idx_arr-len_elem_arr):
            delete_elem(elem_idx_arr[len_elem_idx_arr-i-1])
        # 수정
        for i in range(len_elem_arr):
            update_elem_db(elem_idx_arr[i], elem_arr[i])
            elem_idx_list += ('' if elem_idx_list == '' else ', ') + elem_idx_arr[i]

    elif len_elem_idx_arr < len_elem_arr:
        # 수정
        for i in range(len_elem_idx_arr):
            update_elem_db(elem_idx_arr[i], elem_arr[i])
            elem_idx_list += ('' if elem_idx_list == '' else ', ') + elem_idx_arr[i]
        # 삽입
        for i in range(len_elem_arr-len_elem_idx_arr):
            elem_idx = insert_elem(elem_arr[len_elem_arr-i-1])
            elem_idx_list += ('' if elem_idx_list == '' else ', ') + elem_idx

    return elem_idx_list

def get_elem(elem_idx_list, concat=False):
    elem_idx_arr = elem_idx_list.split(', ')

    elem_list = []
    for elem_idx in elem_idx_arr:
        crawling_DB = DBConnect()
        where = f'WHERE elem_idx={elem_idx}'
        column = 'elem_tag, elem_attr, elem_attr_value'
        result = crawling_DB.find('elem_info', column, where)
        elem_list.append([elem_idx, result['elem_tag'], {result['elem_attr']:result['elem_attr_value']}])

    if not concat:
        return elem_list
    else:
        el = ''
        for elem in elem_list:
            if 'class' in elem[2]:
                el += ('' if el == '' else ' ') + elem[1] + '.' + elem[2]['class']
            elif 'id' in elem[2]:
                el += ('' if el == '' else ' ') + elem[1] + '#' + elem[2]['id']
            else:
                el += ('' if el == '' else ' ') + elem[1]
        return [elem_idx_list, el]