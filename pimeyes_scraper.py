import os
import time
import random
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class PimeyesScraper:
    def __init__(self, cookies_path='/Users/akiraeason/Desktop/PimeScrap/cookies.pkl'):
        self.cookies_path = cookies_path
        self.output_file = 'output_data/pimeyes/pimeyes_results.txt'
        self.driver = None
        
        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
    def setup_driver(self):
        """設定 Chrome WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-software-rasterizer")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
    def login(self):
        """登入 Pimeyes 網站"""
        url = "https://pimeyes.com/en/"
        self.driver.get(url)
        
        # 點擊 Cookie 按鈕
        cookie_button = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
        )
        action = ActionChains(self.driver)
        action.move_to_element(cookie_button).pause(random.uniform(0.5, 2)).click().perform()
        time.sleep(2.5)
        
        # 載入 Cookie
        try:
            with open(self.cookies_path, "rb") as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)

            # 重新整理頁面
            self.driver.refresh()

            # 驗證登入是否成功
            if "login" in self.driver.current_url:
                print("Cookie 失效，請重新登入！")
                self.driver.quit()
                return False
            else:
                print("成功使用 Cookie 自動登入！")
                return True
        except:
            print("無法載入 Cookie，請先手動登入一次！")
            self.driver.quit()
            return False
            
    def scrape_search_results(self, search_url, limit=10):
        """抓取搜尋結果的網址"""
        self.driver.get(search_url)
        time.sleep(3)  # 確保網頁完全載入
        print('網頁載入完成')
        # 找到所有搜尋結果的圖片
        images = self.driver.find_elements(By.XPATH, '//div[contains(@class, "thumbnail")]//img')
        print(f"找到 {len(images)} 張圖片")
        
        # 限制處理數量
        images = images[:limit]
        print(f"將處理前 {limit} 張圖片")
        
        result_links = []
        
        for index, img in enumerate(images):
            try:
                print(f"點擊圖片 {index + 1}/{len(images)}")
                
                # 滾動到圖片，確保它可見
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", img)
                time.sleep(random.uniform(1, 2))
                
                # 點擊圖片
                img.click()
                time.sleep(1)  # 等待載入
                
                # 檢查是否出現多張圖片
                try:
                    inner_images = self.driver.find_elements(By.XPATH, '//div[contains(@class, "sub-grid")]//div[contains(@class, "result")]')
                    if inner_images:
                        print(f"縮圖包含 {len(inner_images)} 張內部圖片，點擊第一張")
                        inner_images[1].click()
                        time.sleep(1)  # 等待 Modal 開啟
                except:
                    print("直接進入 Modal，沒有內部圖片")
                
                # 等待 Modal 出現
                WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "wrapper mobile-fullscreen-mode")]'))
                )
                
                # 記住原始 Pimeyes 分頁
                original_window = self.driver.current_window_handle
                original_window_url = self.driver.current_url
                
                # 點擊「Open website」按鈕
                open_website_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "action-item")]//p[contains(text(), "Open website")]'))
                )
                open_website_btn.click()
                
                # 等待新分頁開啟
                WebDriverWait(self.driver, 1).until(EC.number_of_windows_to_be(2))
                
                # 切換到新分頁
                new_window = [window for window in self.driver.window_handles if window != original_window][0]
                self.driver.switch_to.window(new_window)
                
                # 等待網址變更，否則直接使用 `current_url`
                try:
                    WebDriverWait(self.driver, 5).until(lambda d: d.current_url != original_window_url)
                    website_link = self.driver.current_url
                except:
                    print("⚠️ 網頁加載超時，直接使用當前網址")
                    website_link = self.driver.current_url  # 直接使用當前網址
                
                # 將網址添加到結果列表
                result_links.append(website_link)
                
                print(f"✅ 擷取到新分頁網址: {website_link}")
                
                # 關閉新分頁，回到 Pimeyes
                self.driver.close()
                self.driver.switch_to.window(original_window)
                time.sleep(1)
                
                # 關閉 modal
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(1)
                
            except Exception as e:
                print(f"無法處理圖片 {index + 1}: {e}")
                continue
                
        return result_links
        
    def save_results(self, result_links):
        """將結果保存到文件"""
        with open(self.output_file, 'w') as f:
            for link in result_links:
                f.write(f"{link}\n")
                
        print(f"已將 {len(result_links)} 個網址輸出至 {self.output_file}")
        
    def run(self, search_url, limit=10):
        """運行完整的抓取流程"""
        try:
            self.setup_driver()
            if not self.login():
                return False
                
            result_links = self.scrape_search_results(search_url, limit)
            self.save_results(result_links)
            
            print("擷取的網址：")
            for link in result_links:
                print(link)
                
            return True
        finally:
            if self.driver:
                self.driver.quit()
                
        return False