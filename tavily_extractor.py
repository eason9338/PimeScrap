import os
import time
import json
import requests

class TavilyExtractor:
    def __init__(self, api_key="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", webhook_url="https://autopilot.aiwize.com/webhooks/flows/f5d38b8b-c6c3-4ba4-9ba6-34cab695bae8"):
        self.api_key = api_key
        self.webhook_url = webhook_url
        self.input_file = "output_data/pimeyes/pimeyes_results.txt"
        self.output_dir = "output_data/tavily"
        
        # 確保輸出目錄存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def extract_content(self):
        """從URL列表中提取內容"""
        # 讀取URL列表
        try:
            with open(self.input_file, "r") as file:
                urls = [line.strip() for line in file if line.strip()]
            
            print(f"從 {self.input_file} 讀取了 {len(urls)} 個URL")
        except FileNotFoundError:
            print(f"錯誤: 找不到 {self.input_file} 檔案")
            return False
        except Exception as e:
            print(f"讀取URL檔案時發生錯誤: {e}")
            return False
            
        # 用於追蹤成功處理的URL數量
        successful_count = 0
        skipped_count = 0
        
        # 逐一處理每個URL
        for index, target_web in enumerate(urls):
            try:
                print(f"處理 URL {index+1}/{len(urls)}: {target_web}")
                
                # 準備API請求
                payload = {
                    "urls": target_web,
                    "include_images": True,
                    "extract_depth": "basic"
                }
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                # 發送請求到Tavily API
                url = "https://api.tavily.com/extract"
                response = requests.request("POST", url, json=payload, headers=headers)
                
                # 檢查API回應狀態
                if response.status_code != 200:
                    print(f"警告: URL {target_web} 的API請求失敗，狀態碼: {response.status_code}")
                    print(f"回應內容: {response.text}")
                    skipped_count += 1
                    continue
                
                try:
                    json_data = response.json()
                    
                    # 檢查是否有結果以及是否有內容
                    has_content = False
                    for result in json_data.get("results", []):
                        if result.get("raw_content") and len(result.get("raw_content").strip()) > 0:
                            has_content = True
                            break
                    
                    if not has_content:
                        print(f"跳過 URL {target_web}: 沒有獲取到內容")
                        skipped_count += 1
                        continue
                    
                    # 發送到webhook (只有在有內容時才發送)
                    try:
                        webhook_response = requests.post(
                            self.webhook_url,
                            json=json_data,
                            headers={"Content-Type": "application/json"}
                        )
                        print(f"Webhook回應狀態: {webhook_response.status_code}")
                    except Exception as webhook_error:
                        print(f"發送到webhook時發生錯誤: {webhook_error}")
                    
                    # 儲存回應資料到檔案 (序號從1開始)
                    successful_count += 1
                    output_filename = f"{self.output_dir}/tavily_response_{successful_count}.txt"
                    
                    with open(output_filename, "w", encoding="utf-8") as file:
                        for i, result in enumerate(json_data.get("results", [])):
                            file.write(f"URL: {result.get('url', 'N/A')}\n")
                            
                            if "raw_content" in result:
                                file.write("內容:\n")
                                file.write(result.get("raw_content", ""))
                                file.write("\n\n")
        
                            file.write("=" * 50 + "\n\n")
                        
                        print(f"已將結果儲存到 {output_filename}")
                        
                except json.JSONDecodeError:
                    print(f"警告: 無法解析URL {target_web} 的API回應為JSON格式")
                    skipped_count += 1
                    continue
                
                # 添加延遲避免API限制
                if index < len(urls) - 1:  # 不在最後一個URL後延遲
                    time.sleep(1)  # 每次請求間隔1秒
                    
            except Exception as e:
                print(f"處理URL {target_web} 時發生錯誤: {e}")
                skipped_count += 1
                continue
                
        print(f"處理完成：成功 {successful_count} 個URL，跳過 {skipped_count} 個URL，共 {len(urls)} 個URL")
        return successful_count > 0