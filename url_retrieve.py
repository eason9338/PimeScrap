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
import requests
from selenium.webdriver.chrome.service import Service as ChromeService
import pickle
import math


class UrlRetrieve:
    def __init__(self, image_path=None, cookie_file="/Users/akiraeason/Desktop/PimeScrap/cookies.pkl"):
        """初始化 PimEyes 爬蟲"""
        self.image_path = image_path
        self.cookie_file = cookie_file
        self.driver = None
        
        # 設定 Mozilla User-Agent 這個是不會被擋的agent
        self.user_agent = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36"
        
    def setup_driver(self):
        """設定 Chrome WebDriver"""
        # 初始化 Chrome Driver
        driver = webdriver.Chrome()
        print(driver.capabilities['browserVersion'])  # 瀏覽器版本
        print(driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0])  # ChromeDriver 版本
        
        # 設定 Chrome Options
        ua = UserAgent()
        print("current user-agent:", self.user_agent)
        print("--------------------------------")
        chrome_options = Options()
        chrome_options.add_argument(f"user-agent={self.user_agent}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        
        # 初始化 WebDriver
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # 設定固定的瀏覽器視窗大小，確保座標點擊一致性
        self.driver.set_window_size(1366, 768)
        
        # 隱藏 webdriver 特徵
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def load_cookies(self):
        """載入 cookies 檔案"""
        try:
            cookies = pickle.load(open(self.cookie_file, "rb"))
            for cookie in cookies:
                # 處理可能導致錯誤的cookie屬性
                if 'expiry' in cookie:
                    del cookie['expiry']
                self.driver.add_cookie(cookie)
            print("Cookies載入成功")
        except Exception as e:
            print(f"載入Cookies時發生錯誤: {e}")
            
    def scroll_to_element(self, element):
        """滾動到元素位置"""
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(random.uniform(1, 3))
        
    def js_click(self, element):
        """使用 JavaScript 點擊元素"""
        self.driver.execute_script("arguments[0].click();", element)
        
    def random_sleep(self, min_time=2, max_time=6):
        """隨機睡眠一段時間"""
        time.sleep(random.uniform(min_time, max_time))
        
    def simulate_mouse(self, element):
        """模擬滑鼠移動和點擊"""
        action = ActionChains(self.driver)
        action.move_to_element(element).pause(random.uniform(0.5, 2)).click().perform()
        
    def initialize_session(self):
        """初始化會話，載入網站和cookies"""
        # 先打開網站，再載入cookie
        self.driver.get("https://pimeyes.com/en")
        self.random_sleep(1, 2)
        self.load_cookies()
        
        # 重新載入頁面以應用cookie
        self.driver.get("https://pimeyes.com/en")
        self.random_sleep(3, 7)
        
        # 檢查是否需要處理Cookie對話框
        try:
            cookie_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
            )
            self.simulate_mouse(cookie_button)
            self.random_sleep(2, 5)
        except:
            print("沒有找到Cookie對話框或已透過cookie自動登入")
            
    def upload_image(self):
        """上傳圖片並處理確認對話框"""
        # 點擊上傳圖片按鈕
        upload_button = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="hero-section"]/div/div[1]/div/div/div[1]/button[2]'))
        )
        self.simulate_mouse(upload_button)
        self.random_sleep(3, 6)
        
        # 上傳圖片
        file_input = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type=file]'))
        )
        file_input.send_keys(self.image_path)
        self.random_sleep(3, 6)
        
        # 滾動頁面
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.random_sleep(1, 3)
        self.driver.execute_script("window.scrollTo(0, 0);")
        
        time.sleep(3)
        
    def handle_checkboxes(self):
        """處理勾選框"""
        print("----------------Buckle up----------------")
        
        # 定位所有勾選框
        checkboxes = WebDriverWait(self.driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, "//label[@class='checkbox']/input[@type='checkbox']"))
        )
        
        # 點擊每一個勾選框
        for checkbox in checkboxes[:3]:
            checkbox.click()
            print("checkbox clicked")
            self.random_sleep(1, 5)
            
        self.random_sleep(3, 6)  # 等待畫面穩定
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("----------------Move on----------------")
        self.random_sleep(1, 5)
        
    def submit_search(self):
        """提交搜尋"""
        # 重新定位並使用 JavaScript 點擊提交按鈕
        submit_button = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div/div/div/div[1]/div/div[1]/button/span"))
        )
        print(self.driver.execute_script("return window.getComputedStyle(arguments[0]).display;", submit_button))
        print("----------------Click----------------")
        self.js_click(submit_button)
        self.random_sleep(5, 8)
        
        # 等待結果頁面加載完成
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("----------------Results Loaded----------------")
        self.random_sleep(3, 6)
        
        # 獲取當前URL
        current_url = self.driver.current_url
        print(f"搜尋結果URL: {current_url}")
        return current_url
        
    def keep_browser_open(self):
        """保持瀏覽器視窗開啟"""
        print("程式執行完畢，保持瀏覽器視窗開啟")
        print("請手動按 Ctrl+C 來結束程式")
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("程式已手動終止")
            
    def run(self, image_path=None):
        """運行完整的爬蟲流程，只返回搜尋URL而不關閉瀏覽器
        
        Args:
            image_path: 可選的圖片路徑，如果在初始化時已提供則可忽略
            
        Returns:
            str: 搜尋結果的URL
        """
        if image_path:
            self.image_path = image_path
            
        if not self.image_path:
            raise ValueError("必須提供圖片路徑")
            
        try:
            # 設定 WebDriver
            self.setup_driver()
            
            # 初始化會話
            self.initialize_session()
            
            # 上傳圖片
            self.upload_image()
            
            # 處理勾選框
            self.handle_checkboxes()
            
            # 提交搜尋
            search_url = self.submit_search()
            
            return search_url
            
        except Exception as e:
            print(f"PimEyesScraper發生錯誤: {e}")
            return None


# 使用範例
if __name__ == "__main__":
    image_path = "/Users/akiraeason/Desktop/PimeScrap/meA.png"
    cookie_file = "/Users/akiraeason/Desktop/PimeScrap/cookies.pkl"
    
    # 創建爬蟲實例並執行
    scraper = PimEyesScraper(image_path=image_path, cookie_file=cookie_file)
    search_url = scraper.run()
    
    print(f"獲取到搜尋結果URL: {search_url}")
    
    # 這裡可以繼續執行其他操作，比如將URL傳遞給其他函數或類別
    # next_step(search_url)
    
    # 如果需要在整個程式結束時關閉瀏覽器，可以手動調用quit
    # scraper.driver.quit()