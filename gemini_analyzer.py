import os
import time
import glob
from datetime import datetime
import google.generativeai as genai

class GeminiAnalyzer:
    def __init__(self, api_key="AIzaSyDcbXxRHUgq7sr6XefRSmLNITaMihR-cTY", webhook_url="https://autopilot.aiwize.com/webhooks/flows/f5d38b8b-c6c3-4ba4-9ba6-34cab695bae8"):
        self.api_key = api_key
        self.webhook_url = webhook_url
        self.input_dir = "output_data/tavily"
        self.output_dir = "output_data/gemini_analysis"
        
        # 配置 Gemini API
        genai.configure(api_key=self.api_key)
        
        # 確保輸出目錄存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def analyze_with_gemini(self, text, borrower_name):
        """使用 Gemini 分析文本，提取信用評分特徵"""
        # 設定 Gemini 模型
        model = genai.GenerativeModel('gemini-1.5-pro')  # 更新為新版模型名稱
        
        # 設定參數，增加temperature使回應更有變化性
        generation_config = {
            "temperature": 0.2,
            "top_p": 0.9,
            "top_k": 40
        }
        
        # 構建評分提示詞
        prompt = f"""
        ## {borrower_name}新聞文章信用評分補充特徵分析

        請分析這篇關於{borrower_name}的新聞文章，提取以下可用於信用評分補充的特徵，並為每項提供量化評估。
        請只分析以下三個方面，其他方面請勿分析：

        **1. 曝光度分析：**
        * 借款者姓名出現頻率（具體次數）
        * 借款者是否出現在標題中（是/否）
        * 在文章中的突出程度（低/中/高）

        **2. 情感分析：**
        * 整體情感傾向評分（-5至+5，其中-5極度負面，+5極度正面）
        * 與借款者相關的正面詞彙數量
        * 與借款者相關的負面詞彙數量
        * 最顯著的3個正面關鍵詞
        * 最顯著的3個負面關鍵詞（如有）

        **3. 專業形象評估：**
        * 專業成就提及程度（0-5分）
        * 專業領域類別（例如：商業、科技、藝術等）
        * 專業穩定性暗示（如有，-3至+3分）

        最後，請提供一個-10至+10的總體評分，反映此新聞對借款者信用形象的整體影響，並簡要說明評分理由。

        輸出格式請完全按照以上格式，使用Markdown語法，只分析這三個方面。

        以下是需要分析的文章內容：
        {text}
        """
        
        try:
            # 發送到 Gemini API，加入generation_config參數
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            print(f"Gemini API 錯誤: {e}")
            return f"分析發生錯誤: {e}"
            
    def run_analysis(self, borrower_name):
        """分析所有文件"""
        # 獲取輸入目錄下所有txt檔案
        input_files = glob.glob(f"{self.input_dir}/*.txt")
        
        if not input_files:
            print(f"在 {self.input_dir} 目錄中找不到任何txt檔案")
            return False
        
        print(f"找到 {len(input_files)} 個檔案需要處理")
        
        # 處理每個檔案
        for index, file_path in enumerate(input_files):
            try:
                file_name = os.path.basename(file_path)
                print(f"處理檔案 {index+1}/{len(input_files)}: {file_name}")
                
                # 讀取檔案內容
                with open(file_path, 'r', encoding='utf-8') as file:
                    text_for_analysis = file.read()
                
                if not text_for_analysis.strip():
                    print(f"檔案 {file_name} 內容為空，跳過分析")
                    continue
                    
                file_size = len(text_for_analysis)
                print(f"成功讀取檔案內容，總計 {file_size} 字元")
                
                # 檢查內容是否過大
                if file_size > 100000:  # 約10萬字元限制
                    print(f"警告: 檔案 {file_name} 內容過大 ({file_size} 字元)，可能超出Gemini處理限制")
                    # 截斷過長內容以避免錯誤
                    text_for_analysis = text_for_analysis[:100000]
                    print(f"已截斷內容至10萬字元")
                
                # 使用 Gemini 分析文本
                print(f"正在使用 Gemini 分析關於 {borrower_name} 的內容...")
                analysis_result = self.analyze_with_gemini(text_for_analysis, borrower_name)
                
                # 生成帶時間戳的文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"{self.output_dir}/{borrower_name}_credit_analysis_{index+1}_{timestamp}.txt"
                
                # 保存分析結果
                with open(output_filename, "w", encoding="utf-8") as out_file:
                    out_file.write(analysis_result)
                
                print(f"分析完成！結果已保存到 {output_filename}")
                
                # 添加延遲以避免API限制
                if index < len(input_files) - 1:
                    delay = 2  # 2秒延遲
                    print(f"等待 {delay} 秒後繼續下一個檔案...")
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"處理檔案 {file_path} 時發生錯誤: {e}")
                continue
        
        print(f"所有 {len(input_files)} 個檔案處理完成！")
        return True