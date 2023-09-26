import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from retrying import retry

@retry(stop_max_attempt_number=3, wait_fixed=2000)
def get_list_page_url(city, year):
    start_url = "https://mfang.58.com/{}/xinfang/fangjia-{}/?PGTID=0d000000-0000-0088-499c-defca7a3c558&ClickID=1".format(city, year)
    # start_url = "https://mfang.58.com/hrb/xinfang/fangjia-{}-{}/?PGTID=0d000000-0000-06c8-1d79-123413748be9&ClickID=1".format(city, year)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }
    # 这里我们不用try的方式去执行，因为一旦执行中出现错误就会导致整个代码运行结束
    response = requests.get(start_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    # print(soup)
    houses = soup.select('tbody')
    house_avg = soup.select('.title-desc>em')
    # print("====================")
    # print(house_avg[0].text.strip())
    # 获取房屋均价，当数据是暂无时使用
    house_avg = float(house_avg[0].text.strip()[:-4])
    house_detail = houses[0].select('tr')
    # print(house_detail)
    title = []
    price = []
    for house in house_detail:
        title.append(house.select('tr>td')[0].text.strip())
        # print(house.select('tr>td')[1].text.strip()[2:-4])
        # 如果数据是暂无
        # 注意，需要手动去除2023.10、2023.11、2023.12的数据
        if house.select('tr>td')[1].text.strip() == "暂无":
            price.append(int(float(house_avg)))
            continue
        price.append(int(house.select('tr>td')[1].text.strip()[2:-4]))
    print(title)
    print(price)
    print()
    return title, price
    # except requests.exceptions.RequestException as s:
    #     print(s)
    #     print("获取总套数出错,请确认起始URL是否正确")

def toCsv(city, year, title_list, price_list):
    if (city == "bj") & (year == 2015):
        data_dict = {'city_name': city, 'title': title_list, 'price': price_list}
        df = pd.DataFrame(data_dict)
        df.to_csv('./AllCityData.csv', index=False)
    else:
        data_dict = {'city_name': city, 'title': title_list, 'price': price_list}
        df = pd.DataFrame(data_dict)
        df.to_csv('./AllCityData.csv', mode='a', index=False, header=False)  # 如果不是bj、2015就是对表格数据进行追加
def toLasaCsv(city, year, title_list, price_list):
    data_dict = {'city_name': city, 'title': title_list, 'price': price_list}
    df = pd.DataFrame(data_dict)
    df.to_csv('./cqData.csv', mode='a', index=False, header=False)
if __name__ == '__main__':
    old = time.time()
    # area_list_3 = ["bj", "hrb", "cn", "gz", "sz", "jl", "sy", "bt", "sjz", "xj",
    #                "lz", "xn", "xa", "ty", "tj", "jn", "zz", "cd", "lasa", "cq", "wh",
    #                "hf", "nj", "hz", "nc", "cs", "gy", "km", "nn", "fz", "haikou"]
    # area_list_3 = ["cq", "wh","hf", "nj", "hz", "nc", "cs", "gy", "km", "nn", "fz", "haikou"]
    lasa = ["cq"]  # 因为拉萨的数据在2018年一条也没有，所以导致报错，在这里单独对拉萨数据进行爬取
    # year_list = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
    lasa_year = [2015, 2016, 2017, 2018, 2019]
    for i in lasa:
        for j in lasa_year:
            time.sleep(5)
            title, price = get_list_page_url(i, j)
            toLasaCsv(i, j, title, price)
    new = time.time()
    delta_time = new - old
    print("程序共运行{}s".format(delta_time))
