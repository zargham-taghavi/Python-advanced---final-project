import time
import re
from datetime import datetime
import mysql.connector
from mysql.connector import errorcode
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


my_host = "127.0.0.1"
my_user = "root"
my_pass = ""
my_db = "python_test"
my_tb = "vehicleprice2"
# must have 6 column, first and second text, and next 3 are int and last one Date
# (name, detial, model, mileage, price, date)

scroll_count = 100
all_cars_list = []
scroll_pause_time = 1  # You can set your own pause time by sec.


def format_html_result():
    # options = webdriver.ChromeOptions()
    # options.add_argument('--ignore-certificate-errors')
    # options.add_argument('--ignore-ssl-errors')
    # browser_driver = webdriver.Chrome(chrome_options=options)
    browser_driver = webdriver.Chrome(
        "C:/Users/zargham/.cache/selenium/chromedriver/win32/109.0.5414.74/chromedriver.exe")

    # browser_driver.get("https://divar.ir/s/tehran/car?non-negotiable=true")
    browser_driver.get("https://bama.ir/car?mileage=1&priced=1")

    screen_height = browser_driver.execute_script(
        "return window.screen.height;")   # get the screen height of the web
    all_result = []


# method 1, first scroll until scroll_count finish, then find elements

    for i in range(scroll_count):
        browser_driver.execute_script(
            "window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i+1))
        time.sleep(scroll_pause_time)
        WebDriverWait(browser_driver, 20).until(EC.visibility_of_all_elements_located(
            (By.CLASS_NAME, 'bama-ad-holder')))   # for 'Divar.ir' website   post-card-item-af972
    try:
        elements = WebDriverWait(browser_driver, 50).until(EC.visibility_of_all_elements_located(
            (By.CLASS_NAME, 'bama-adlist-container')))  # for 'Divar.ir' website  post-list-grid-eef81
        # for 'Divar.ir' website   post-card-item-af972
        all_result = elements[0].find_elements(By.CLASS_NAME, 'bama-ad-holder')
        time.sleep(scroll_pause_time)
    except errorcode:
        print(errorcode)


# method 2, in each scroll find elements, and extend it to final result

    # for i in range(scroll_count):
    #     # scroll one screen height each time
    #     browser_driver.execute_script(
    #         "window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i+1))
    #     try:
    #         elements = WebDriverWait(browser_driver, 20).until(EC.visibility_of_all_elements_located(
    #             (By.CLASS_NAME, 'bama-ad-holder')))  # for 'Divar.ir' website    post-card-item-af972
    #     #     print(len(elements))
    #     #     print('elements[0].text: ',elements[0].text)
    #         all_result.extend(elements)
    #         time.sleep(scroll_pause_time)
    #     except errorcode:
    #         print(errorcode)

    print('------------ len(all_result) -----------', len(all_result))
    faile_with_price = 0
    faile_with_milage = 0
    for car in all_result:
        try:
            # print('car_index start: ',car_index)
            car_dict = {}
            car_dict['right format'] = True
            # for divar.ir website
            # post['title'] = element.find_element(By.CLASS_NAME,'kt-post-card__title')
            # post['description'] = element.find_elements(By.CLASS_NAME,'kt-post-card__description')
            # post['bottom'] = element.find_element(By.CLASS_NAME,'kt-post-card__bottom-description')

            # for bama.ir website
            # print('car_index start: ',car_index,' - name')
            car_dict['name'] = car.find_element(
                By.CLASS_NAME, 'bama-ad__title').text
            # print('car_index start: ',car_index,' - model')
            car_dict['model'] = int(car.find_element(
                By.CSS_SELECTOR, '.bama-ad__detail-row>span:nth-child(1)').text)
            # print('car_index start: ',car_index,' - mileage')
            car_dict['mileage'] = car.find_element(
                By.CSS_SELECTOR, '.bama-ad__detail-row>span:nth-child(3)').text
            car_dict['mileage'] = re.sub(
                r'(\d+),*(\d*).*', '\g<1>\g<2>', car_dict['mileage'])
            if (car_dict['mileage'].isnumeric()):
                car_dict['mileage'] = int(car_dict['mileage'])
            else:
                faile_with_milage += 1
                # it doesn't have mileage so dont save this car
                car_dict['right format'] = False
            # print('car_index start: ',car_index,' - price')
            car_price = car.find_element(By.CLASS_NAME, 'bama-ad__price')
            if car_price == None:
                faile_with_price += 1
                # it doesn't have price so dont save this car
                car_dict['right format'] = False
            else:
                car_dict['price'] = int(re.sub(
                    r'(\d+),*(\d*),*(\d*),*(\d*)?', '\g<1>\g<2>\g<3>\g<4>', car_price.text))
            # print('car_index start: ',car_index,' - detail')
            car_detail = car.find_element(
                By.CLASS_NAME, 'bama-ad__detail-trim')
            if car_detail != None:  # it has detial
                car_dict['detail'] = car_detail.text
            else:
                car_dict['detail'] = 'no detail'
            if car_dict['right format']:
                all_cars_list.append(car_dict)
            # print('car_index finish: ',car_index)
        except Exception as e:
            print('----Exception-------', str(e))

        # print('----------------- new item: ---')
        # for key, value in list(car_dict.items()):
        #     print(key+": ", value)
    print('----len(all_cars_list)----', len(all_cars_list), '----len(all_result)----', len(all_result),
          '--faile_with_price--', faile_with_price, '---faile_with_milage---', faile_with_milage)
    # for car in all_cars_list:
    #     print(
    #         f"the car {car['name']} model {car['model']} + {all_result[car_index].setdefault('detail')} with {car['mileage']} mileage is {car['price']} Toman on Date: {datetime.today().date()}")
    #         # The setdefault() method returns the value associated with the key searched if the key exists. If the key does not exist, it will insert the key in the dictionary with a provided value (which, by default, is None) and returns that value.


# connect to database and save Data
def save_to_database():
    try:
        cnx = mysql.connector.connect(user=my_user, password=my_pass,
                                      host=my_host,
                                      database=my_db)
        # print('connected successfully')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:  # else will run if try part execute successfully.
        cursor = cnx.cursor()

    for car in all_cars_list:
        query = f"INSERT INTO {my_tb} VALUES (\'{car['name']}\', \'{car['detail']}\', {car['model']}, {car['mileage']}, {car['price']}, \'{datetime.today().date()}\')"
        # print(query)
        cursor.execute(query)
        cnx.commit()
    # cnx.commit()
    print('your search has saved to database!')


def read_from_database():
    try:
        cnx = mysql.connector.connect(user=my_user, password=my_pass,
                                      host=my_host,
                                      database=my_db)
        # print('connected successfully')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:  # else will run if try part execute successfully.
        cursor = cnx.cursor()

    # query = f"SELECT * FROM {my_tb}"
    query = f"SELECT DISTINCT name, detail, model, mileage, price, date FROM {my_tb}"
    cursor.execute(query)

    i = 1
    all_cars=[]
    x=[]
    y=[]
    for name, detail, model, mileage, price, date in cursor:
        new_car = {}
        new_car_input = []
        # print(f"{i}: the car {name +' - '+detail} model {model} +  with {mileage} mileage is {price} Toman on Date: {date}")
        new_car['name']=name
        new_car['detail'] =detail
        new_car['model']=model
        new_car['mileage']=mileage
        new_car['price']=price
        # new_car['date']=date
        # print(new_car)
        all_cars.append(new_car)
        new_car_input=[name,detail,model,mileage]
        x.append(new_car_input)
        y.append(price)
        i += 1
    import numpy as np
    import pandas as pd
    from sklearn import tree
    from sklearn.linear_model import LinearRegression
    all_cars_df = pd.DataFrame(all_cars)
    all_cars_df.rename(index=all_cars_df.name,inplace=True)
    print (all_cars_df[0:5])
    print(all_cars_df.describe())
    # print(x)
    # print(y)
    clf = tree.DecisionTreeClassifier()
    reg = LinearRegression()
    # reg.fit(x,y)
    # clf = clf.fit(x,y)
    # new_data = ['پژو 206','تیپ 2','1399']
    # answer = reg.predict(new_data)
    # print(f'i predict that price is {answer} toman')

# format_html_result()
# save_to_database()
read_from_database()
