import os
from selenium.webdriver import Chrome, ChromeOptions
import time
import pandas as pd
import datetime
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

# Chromeを起動する関数
LOG_FILE_PATH = "./log/log_{datetime}.log"
EXP_CSV_PATH = "./exp_list_{search_keyword}_{datetime}.csv"
log_file_path = LOG_FILE_PATH.format(datetime=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))

def set_driver(driver_path, headless_flg):
    # Chromeドライバーの読み込み
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    driver_path = ChromeDriverManager().install()
    return Chrome(driver_path,options=options)
    
def log(txt):
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    logStr = '[%s: %s] %s' % ('log',now, txt)
    # ログ出力
    with open(log_file_path,'a',encoding='utf-8')as f:
        f.write(logStr + '\n')
    print(logStr)

def find_table_target_word(th_elms, td_elms, target:str):
    for th,td in zip(th_elms, td_elms):
        if th.text == target:
            return td.text


def main():
    log("処理開始")
    search_keyword = input('キーワードを入力して下さい>')
    log("検索キーワード:{}".format(search_keyword))
    # driverを起動
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", False)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", False)
    # Webサイトを開く
    driver.get("https://tenshoku.mynavi.jp/")
    time.sleep(1)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')
    time.sleep(1)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')

    # 検索窓に入力
    driver.find_element_by_class_name(
        "topSearch__text").send_keys(search_keyword)
    # 検索ボタンクリック
    driver.find_element_by_class_name("topSearch__button").click()
    #空のデータフレームを作成
    df = pd.DataFrame()
    count = 0
    success = 0
    fail = 0

    while True:
        # ページ終了まで繰り返し取得
        # 会社名、特徴、役職を取得してリストにまとめる
        names_list = []
        copys_list = []
        status_list = []
        first_salary_list = []

        names = driver.find_elements_by_class_name("cassetteRecruit__name") #会社名を取り出す
        copys = driver.find_elements_by_class_name("cassetteRecruit__copy") #キャッチコピーを取り出す
        status = driver.find_elements_by_class_name("labelEmploymentStatus") #ステータスを取り出す
        tables = driver.find_elements_by_class_name("tableCondition")
        
        for name,copy,st,table in zip(names,copys,status,tables):
            try:
                names_list.append(name.text)
                copys_list.append(copy.text)
                status_list.append(st.text)
                first_year_fee = find_table_target_word(table.find_elements_by_class_name("tableCondition__head"),table.find_elements_by_class_name("tableCondition__body"),"初年度年収")
                first_salary_list.append(first_year_fee)
                log(f"{count}件目成功 : {name.text}")
                success += 1
            except Exception as e:
                log(f"{count}件目失敗 : {name.text}")
                log(f"{e}")
                fail += 1
            finally:
                count += 1
        for n,c,s,f in zip(names_list,copys_list,status_list,first_salary_list):
            df = df.append(
                {"会社名":n,
                "魅力":c,
                "地位":s,
                "初年度年収":f},
                ignore_index=True)
            print(df)
        
        link_page = driver.find_elements_by_class_name("iconFont--arrowLeft")
        print(len(link_page))
        if len(link_page) >= 1:
            link_url = link_page[0].get_attribute("href")
            driver.get(link_url)
        else:
            log('最終ページです、終了します')
            break
    
    df.to_csv(EXP_CSV_PATH.format(datetime=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),search_keyword=search_keyword),encoding='utf-8')

    

    
    # 1ページ分繰り返し
    # print(len(name_list))
    # for name in name_list:
    #     print(name.text)
    #     # DataFrameに対して辞書形式でデータを追加する
    #     df = df.append(
    #         {"会社名": name.text, 
    #          "項目B": "",
    #          "項目C": ""}, 
    #         ignore_index=True)
        
        


# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()