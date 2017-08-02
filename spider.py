from selenium import webdriver
from time import sleep
from lxml import etree
from openpyxl import Workbook

# 初始化
keys = ['名称', '月租金', '地址', '出租形式', '户型', '面积', '楼层', '朝向', '装修程度', '支付方式', '地铁', '品牌', '发布时间']

# 初始化浏览器
url = 'http://www.aizuna.com'
driver = webdriver.PhantomJS()

# 初始化excel表
file = 'e:/aizuna.xlsx'
wb = Workbook()
ws = wb.active
ws.append(keys)


def get_info_links(page):
    """
    获得详情页地址
    
    :param page: 页码 
    :return: links 由详情页的地址组成的list
    """

    # 打开每一页
    driver.get(f'{url}/rentlist/itemname-_comefrom-1_p-{page}')
    # sleep(1)
    r = driver.page_source

    # 通过xpath获得每条房源的信息页面地址
    tree = etree.HTML(r)
    return tree.xpath("//span[@class='fl']/a/@href")


def get_info(html):
    tree = etree.HTML(html)
    item = dict()

    # 名称
    name = tree.xpath("//h3[@class='tit']/span/text()")
    if name:
        item['名称'] = name[0]

    # 月租金
    price = tree.xpath("//div[@class='price r_bg_01']/span/text()")
    if price:
        item['月租金'] = price[0]

    # 地址
    li = tree.xpath("//div[@class='mdb-l']/div[1]/a/text()")
    item['地址'] = '/'.join(each for each in li)

    # 表格内8项信息
    li = tree.xpath("//li[@class='mes-li']/text()")
    # 定义两个列表用于替换指定关键词和存入对应item中
    key = keys[3:-2]
    # 迭代
    for i, each in enumerate(li):
        # 去除空格空行等，并替换关键词为空
        info = ''.join(each.split())
        info = info.replace(f'{key[i]}：', '')
        # 存入字典
        item[key[i]] = info

    # 品牌
    banner = tree.xpath("//div[@class='tit_'][1]/text()")
    if banner:
        item['品牌'] = banner[0]

    # 发布时间
    time = tree.xpath("//div[@class='spans']/text()")
    if time:
        time = time[0]
        item['发布时间'] = time.strip().replace('发布时间：', '')

    return item


def store(result):
    """存储"""
    line = list(result[key] for key in keys)
    ws.append(line)
    print('>>> success! ')
    return None


if __name__ == '__main__':
    for i in range(1, 483):
        # 每一页中的links
        print(f'>>> page: {i}')
        links = get_info_links(i)

        try:
            # 每条链接
            for each in links:
                # 打开页面
                driver.get(f'{url}{each}')
                # sleep(1)
                # 爬取信息
                result = get_info(driver.page_source)
                # 储存结果
                store(result)
        except:
            print('>>> something wrong')

        wb.save(file)
