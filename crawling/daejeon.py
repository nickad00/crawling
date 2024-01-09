from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import datetime
from pymongo import MongoClient


client = MongoClient("******")
db = client.dhub


def saving(category: str, pageIndex):
    # 브라우저 생성
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    browser = webdriver.Chrome("C:/chromedriver.exe", options=chrome_options)

    # 웹 사이트 열기
    browser.get(
        f"http://bigdata.daejeon.go.kr/data/set/list/pageLoad.do?searchKeywordR=&ctgSmry={category}&mainSearchOrignlFileExt=&mainSearchGnrtnCycle=&stDt=&edDt=&datasetSn=&datasetSe=#"
    )
    browser.implicitly_wait(10)

    # 카테고리별 페이지 수 만큼 반복
    doc = []
    i = 0
    while i < pageIndex:
        i += 1
        try:
            # 페이지 버튼 클릭
            if i != 1 and (i - 1) % 5 == 0:
                browser.find_element(By.CSS_SELECTOR, f"#paging > li.next > a").click()
                time.sleep(1)
            else:
                browser.find_element(
                    By.XPATH, f'//*[@id="paging"]/li/a[contains(text(), "{i}")]'
                ).click()
                time.sleep(1)

            # 제목, 내용, 분류, 수정일자, 제공기관, 제공부서 dictionary에 저장
            for li in browser.find_elements(
                By.CSS_SELECTOR, "#data_content > div > dl"
            ):
                dict = {}

                title = li.find_element(By.CSS_SELECTOR, "dt").text
                dict["제목"] = title
                content = li.find_element(By.CSS_SELECTOR, "dd.info-text01").text
                dict["내용"] = content
                cate = li.find_element(
                    By.XPATH, '//*[@id="data_content"]/div[2]/div[1]'
                ).text
                dict["분류"] = cate

                for span in li.find_elements(By.CSS_SELECTOR, "dd.info-text02 > span"):
                    span_text = span.text.split(" ")
                    dict[span_text[0]] = span_text[-1]

                # url 저장
                txt03 = li.find_element(By.CSS_SELECTOR, "dd.info-text03").text

                if txt03 == "url":
                    link = li.find_element(By.CSS_SELECTOR, "dd.info-text04 > button")
                    link.click()

                    time.sleep(1)

                    new_window = browser.window_handles[1]
                    browser.switch_to.window(new_window)
                    url = browser.current_url

                    dict["url"] = url

                    browser.close()
                    time.sleep(1)

                    new_window = browser.window_handles[-1]
                    browser.switch_to.window(new_window)

                # url 없는 경우 pass
                else:
                    pass

                doc.append(dict)

        # 페이지가 없으면 반복문 종료
        except:
            break

    # MongoDB Insert
    col = "Daejeon_{0}".format(datetime.datetime.today().strftime("%Y%m%d"))
    db[col].insert_many(doc)


# 찾고 싶은 분류 키워드와 페이지 인덱스 값 전달
# 교통 CT, 도시 HU
if __name__ == "__main__":
    result = saving("HU", 20)
