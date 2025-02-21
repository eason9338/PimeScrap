from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
from fake_useragent import UserAgent

from selenium import webdriver

driver = webdriver.Chrome()
print(driver.capabilities['browserVersion'])  # 瀏覽器版本
print(driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0])  # ChromeDriver 版本

# 設定 Mozilla User-Agent 這個是不會被擋的agent
user_agent = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36"
ua = UserAgent()

# 使用隨機的 User-Agent
# user_agent = ua.random

print("current user-agent:", user_agent)
print("--------------------------------")
chrome_options = Options()
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")


# 初始化 WebDriver
driver = webdriver.Chrome(options=chrome_options)

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
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.get("https://pimeyes.com/en")
    random_sleep(3, 7)

    # 點擊 Cookie 按鈕
    cookie_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
    )
    simulate_mouse(driver, cookie_button)
    random_sleep(2, 5)

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
    file_input.send_keys("D:/D-Coding/Grad/PimeScrap/meA.png")
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
    for checkbox in checkboxes:
        checkbox.click()
        print("checkbox clicked")
        random_sleep(1, 5)

    random_sleep(3, 6)  # 等待畫面穩定
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print("----------------Move on----------------")
    random_sleep(1, 5)


    # 重新定位並使用 JavaScript 點擊提交按鈕
    submit_button = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[5]/div/div/div/div[1]/div/div[1]/button"))
    )
    print(driver.execute_script("return window.getComputedStyle(arguments[0]).display;", submit_button))
    print("----------------Click----------------")
    driver.execute_script("arguments[0].click();", submit_button)
    random_sleep(5, 8)

    # 取得結果 ------Steven的原始碼，曾經可以執行
    currenturl = driver.current_url
    resultsXPATH = '//*[@id="results"]/div/div/div[3]/div/div/div[1]/div/div[1]/button/div/span/span'
    results = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, resultsXPATH))
    ).text

    print("Results:", results)
    print("URL:", currenturl)

except Exception as e:
    print(f"發生錯誤: {e}")
    driver.quit()

finally:
    driver.quit()
