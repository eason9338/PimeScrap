from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from selenium import webdriver
import requests
from selenium.webdriver.chrome.service import Service as ChromeService
import pickle  # 新增用於讀取cookie檔案
import math  # 用於計算座標點擊


image = "/Users/akiraeason/Desktop/PimeScrap/meA.png"
cookie_file = "/Users/akiraeason/Desktop/PimeScrap/pimeyes_cookies.pkl"  # 新增cookie檔案路徑


driver = webdriver.Chrome()
print(driver.capabilities['browserVersion'])  # 瀏覽器版本
print(driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0])  # ChromeDriver 版本

# 設定 Mozilla User-Agent 這個是不會被擋的agent
user_agent = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36"
ua = UserAgent()

print("current user-agent:", user_agent)
print("--------------------------------")
chrome_options = Options()
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors")

driver = webdriver.Chrome(options=chrome_options)

def load_cookies(driver, cookie_file):
    try:
        cookies = pickle.load(open(cookie_file, "rb"))
        for cookie in cookies:
            # 處理可能導致錯誤的cookie屬性
            if 'expiry' in cookie:
                del cookie['expiry']
            driver.add_cookie(cookie)
        print("Cookies載入成功")
    except Exception as e:
        print(f"載入Cookies時發生錯誤: {e}")

def scroll_to_element(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
    time.sleep(random.uniform(1, 3))

def js_click(driver, element):
    driver.execute_script("arguments[0].click();", element)

def random_sleep(min_time=2, max_time=6):
    time.sleep(random.uniform(min_time, max_time))

def simulate_mouse(driver, element):
    action = ActionChains(driver)
    action.move_to_element(element).pause(random.uniform(0.5, 2)).click().perform()

try:
    # 設定固定的瀏覽器視窗大小，確保座標點擊一致性
    driver.set_window_size(1366, 768)
    
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # 新增：先打開網站，再載入cookie
    driver.get("https://pimeyes.com/en")
    random_sleep(1, 2)
    load_cookies(driver, cookie_file)
    
    # 重新載入頁面以應用cookie
    driver.get("https://pimeyes.com/en")
    random_sleep(3, 7)

    # 檢查是否需要處理Cookie對話框
    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
        )
        simulate_mouse(driver, cookie_button)
        random_sleep(2, 5)
    except:
        print("沒有找到Cookie對話框或已透過cookie自動登入")

    # 點擊上傳圖片按鈕
    upload_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="hero-section"]/div/div[1]/div/div/div[1]/button[2]'))
    )
    simulate_mouse(driver, upload_button)
    random_sleep(3, 6)

    # 上傳圖片
    file_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type=file]'))
    )
    file_input.send_keys(image)

    random_sleep(3, 6)

    # 滾動頁面
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    random_sleep(1, 3)
    driver.execute_script("window.scrollTo(0, 0);")

    time.sleep(3)

    print("----------------Buckle up----------------")

    # 定位所有勾選框
    checkboxes = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, "//label[@class='checkbox']/input[@type='checkbox']"))
    )

    
    # 點擊每一個勾選框
    for checkbox in checkboxes[:3]:
        checkbox.click()
        print("checkbox clicked")
        random_sleep(1, 5)
        

    random_sleep(3, 6)  # 等待畫面穩定
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print("----------------Move on----------------")
    random_sleep(1, 5)


    # 重新定位並使用 JavaScript 點擊提交按鈕
    submit_button = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div/div/div/div[1]/div/div[1]/button/span"))
    )
    print(driver.execute_script("return window.getComputedStyle(arguments[0]).display;", submit_button))
    print("----------------Click----------------")
    driver.execute_script("arguments[0].click();", submit_button)
    random_sleep(5, 8)

    # 等待結果頁面加載完成
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print("----------------Results Loaded----------------")
    random_sleep(3, 6)
    
    try:
        # 嘗試使用 XPath 定位第一張圖片
        first_image = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/div/div[3]/div/div[4]/div/div[1]/div[1]"))
        )
        print("找到第一張圖片，準備點擊")
        
        driver.execute_script("arguments[0].click();", first_image)
        print("已點擊第一張圖片")
        
        # 等待圖片詳情頁面加載
        random_sleep(3, 6)
        print("圖片詳情頁面已加載")
        
        
    except Exception as e:
        print(f"點擊圖片時發生錯誤: {e}")
    
    # 保持瀏覽器視窗開啟
    print("程式執行完畢，保持瀏覽器視窗開啟")
    print("請手動按 Ctrl+C 來結束程式")
    
    # 使用無限循環來保持程式執行，同時不佔用太多CPU資源
    while True:
        time.sleep(10)

except Exception as e:
    print(f"發生錯誤: {e}")
    # 不關閉瀏覽器視窗
    print("發生錯誤，但保持瀏覽器視窗開啟")
    print("請手動按 Ctrl+C 來結束程式")
    while True:
        time.sleep(10)

# 移除 finally 區塊，不自動關閉瀏覽器
# 使用者需要手動關閉或按 Ctrl+C 結束程式