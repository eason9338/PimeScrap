from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 連接到已開啟的Chrome瀏覽器
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)

print(f"已連接到瀏覽器，目前URL: {driver.current_url}")

try:
    # 嘗試使用XPath點擊第一張圖片
    xpath = "/html/body/div[1]/div[2]/div/div[3]/div/div[3]/div[1]/div[1]/div[1]"
    print(f"嘗試使用XPath定位元素: {xpath}")
    
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    print("元素已找到，嘗試點擊...")
    
    # 使用JavaScript點擊
    driver.execute_script("arguments[0].click();", element)
    print("點擊成功")
    
    # 保持程式運行，以便查看結果
    print("程式執行完畢，但保持瀏覽器開啟")
    print("請按Ctrl+C來結束程式")
    
    while True:
        time.sleep(10)
        
except Exception as e:
    print(f"出現錯誤: {e}")
    print("程式繼續執行，保持瀏覽器開啟")
    
    while True:
        time.sleep(10)