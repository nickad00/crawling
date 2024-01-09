from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import requests
import json
import datetime
from pymongo import MongoClient

client = MongoClient("******")
db = client.dhub


def saving():
    # 브라우저 생성
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    browser = webdriver.Chrome("C:/chromedriver.exe", options=chrome_options)

    # 사이트 접속
    browser.get(f"http://data.uri.re.kr/share/List.do")
    browser.implicitly_wait(10)
    time.sleep(1)

    # 국토관리, 교통물류 카테고리 클릭
    browser.find_element(By.XPATH, f' //*[@id="dataCategory"]/dd[5]').click()
    time.sleep(1)
    browser.find_element(By.XPATH, f' //*[@id="dataCategory"]/dd[6]').click()
    time.sleep(1.5)

    # 카테고리별 자료 수
    data_count = browser.find_element(By.CSS_SELECTOR, "#listResult").text

    # post 요청
    url = "http://data.uri.re.kr/share/List.do"

    data = {
        "task": "select",
        "mode": "list",
        "SEARCH_TYPE": "TITLE",
        "page": 1,
        "size": data_count,
        "DATA_CATEGORY": "'CODE-0004', 'CODE-0005'",
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
    }

    res = requests.post(url, data=data, headers=headers)
    data = json.loads(res.text)

    # response json데이터 dictionary에 저장
    doc = []

    for i in range(int(data_count)):
        dict = {}

        dict["제목"] = data["data"][i]["TITLE"]
        dict["내용"] = data["data"][i]["CONTENTS"]
        dict["수정일"] = data["data"][i]["UPDATE_DTM"].split(" ")[0]
        dict["유형"] = data["data"][i]["FILE_EXTENSION"]
        dict["분류"] = data["data"][i]["DATA_CATEGORY_NM"]

        seq = data["data"][i]["DOC_SEQ"]
        dict["url"] = data["filesList"][seq][0]["FILE_PATH"]
        file_ext = data["filesList"][seq][0]["FILE_EXT_NM"]

        # 다운로드 파일이 있는 경우
        if data["filesList"][seq][0]["FILE_NM_STORED"] and file_ext:
            dict["파일명"] = data["filesList"][seq][0]["FILE_NM_STORED"] + f".{file_ext}"
        else:
            pass

        doc.append(dict)

    # MongoDB Insert
    col = "Ulsan_{0}".format(datetime.datetime.today().strftime("%Y%m%d"))
    db[col].insert_many(doc)


if __name__ == "__main__":
    result = saving()
