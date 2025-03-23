from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import random
import pickle

# 設定 Chrome 選項
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-software-rasterizer")

# 初始化 WebDriver
driver = webdriver.Chrome(options=chrome_options)

# **1. 進入 Pimeyes**
url = "https://pimeyes.com/en/"
driver.get(url)
wait = WebDriverWait(driver, 3)

# 點擊 Cookie 按鈕
cookie_button = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
)
action = ActionChains(driver)
action.move_to_element(cookie_button).pause(random.uniform(0.5, 2)).click().perform()
time.sleep(2.5)

# **2. 載入 Cookie**
try:
    with open("cookies.pkl", "rb") as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)

    # **3. 重新整理頁面**
    driver.refresh()
    # time.sleep(3)  # 確保 Pimeyes 內容加載完成

    # **4. 驗證登入是否成功**
    if "login" in driver.current_url:
        print("Cookie 失效，請重新登入！")
        driver.quit()
        exit()
    else:
        print("成功使用 Cookie 自動登入！")
except:
    print("無法載入 Cookie，請先手動登入一次！")
    driver.quit()
    exit()

# **5. 跳轉到搜尋結果頁面**
search_url = "https://pimeyes.com/en/results/O9y_2502230jp5ugwnws8htmh9c1365a4?query=040007079f6fe7fb0000032f7fefe7ef"
driver.get(search_url)
time.sleep(3)  # **確保網頁完全載入**

# **6. 找到所有搜尋結果的圖片**
images = driver.find_elements(By.XPATH, '//div[contains(@class, "thumbnail")]//img')
print(f"找到 {len(images)} 張圖片")

# **7. 依序點擊圖片並擷取「Open website」對應網址**
result_links = []


for index, img in enumerate(images):
    try:
        print(f"點擊圖片 {index + 1}/{len(images)}")

        # **滾動到圖片，確保它可見**
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", img)
        time.sleep(random.uniform(1, 2))

        # **點擊圖片**
        img.click()
        time.sleep(1)  # 等待載入

        # 檢查是否出現多張圖片
        try:
            inner_images = driver.find_elements(By.XPATH, '//div[contains(@class, "sub-grid")]//div[contains(@class, "result")]')
            if inner_images:
                print(f"縮圖包含 {len(inner_images)} 張內部圖片，點擊第一張")
                inner_images[1].click()
                time.sleep(1)  # 等待 Modal 開啟
        except:
            print("直接進入 Modal，沒有內部圖片")

        # **等待 Modal 出現**
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "wrapper mobile-fullscreen-mode")]'))
        )

        # **記住原始 Pimeyes 分頁**
        original_window = driver.current_window_handle
        original_window_url = driver.current_url

        # **點擊「Open website」按鈕**
        open_website_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "action-item")]//p[contains(text(), "Open website")]'))
        )
        open_website_btn.click()
        
     

        # **記住原始 Pimeyes 分頁**
        original_window = driver.current_window_handle

        # **等待新分頁開啟**
        WebDriverWait(driver, 1).until(EC.number_of_windows_to_be(2))

        # **切換到新分頁**
        new_window = [window for window in driver.window_handles if window != original_window][0]
        driver.switch_to.window(new_window)


         # **等待網址變更，否則直接使用 `current_url`**
        try:
            WebDriverWait(driver, 5).until(lambda d: d.current_url != original_window_url)
            website_link = driver.current_url
        except:
            print("⚠️ 網頁加載超時，直接使用當前網址")
            website_link = driver.current_url  # **直接使用當前網址**


        print(f"✅ 擷取到新分頁網址: {website_link}")
        
        # **關閉新分頁，回到 Pimeyes**
        driver.close()
        driver.switch_to.window(original_window)
        time.sleep(1)

        # 關閉 modal
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(1)

        

    except Exception as e:
        print(f"無法處理圖片 {index + 1}: {e}")
        continue

# **8. 關閉瀏覽器**
driver.quit()

# **9. 輸出所有擷取的網址**
print("擷取的網址：")
for link in result_links:
    print(link)