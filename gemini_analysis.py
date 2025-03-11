import requests
import json
import google.generativeai as genai
import os
from datetime import datetime

# 禁止 gRPC 警告
os.environ['GRPC_VERBOSITY'] = 'ERROR'

# API 金鑰設定
TAVILY_API_KEY = "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"
GEMINI_API_KEY = "AIzaSyDcbXxRHUgq7sr6XefRSmLNITaMihR-cTY"
WEBHOOK_URL = "https://autopilot.aiwize.com/webhooks/flows/f5d38b8b-c6c3-4ba4-9ba6-34cab695bae8"

genai.configure(api_key=GEMINI_API_KEY)

def get_web_content(urls):
    url = "https://api.tavily.com/extract"
    
    payload = {
        "urls": urls,
        "include_images": True,
        "extract_depth": "basic"
    }
    
    headers = {
        "Authorization": f"Bearer {TAVILY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.request("POST", url, json=payload, headers=headers)
    
    if response.status_code == 200:
        webhook_response = requests.post(
            WEBHOOK_URL,
            json=response.json(),
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    else:
        print(f"Tavily API 錯誤: {response.status_code}")
        return None

def analyze_with_gemini(text, borrower_name):
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
    
    # 發送到 Gemini API，加入generation_config參數
    response = model.generate_content(
        prompt,
        generation_config=generation_config
    )
    
    return response.text

def main():
    # 獲取用戶輸入
    borrower_name = '黃煒傑'
    
    try:
        with open('tavily_response.txt', 'r', encoding='utf-8') as file:
            text_for_analysis = file.read()
        print(f"成功讀取內容，總計 {len(text_for_analysis)} 字元")
    except FileNotFoundError:
        print("找不到文件，請確保文件存在於正確路徑")
        return
    except Exception as e:
        print(f"讀取文件時發生錯誤: {e}")
        return
    
    # 使用 Gemini 分析文本
    print(f"正在使用 Gemini 分析關於 {borrower_name} 的內容...")
    analysis_result = analyze_with_gemini(text_for_analysis, borrower_name)
    
    # 生成帶時間戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"output_data/{borrower_name}_credit_analysis_{timestamp}.txt"
    
    # 保存分析結果
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(analysis_result)
    
    print(f"分析完成！結果已保存到 {output_filename}")

if __name__ == "__main__":
    main()