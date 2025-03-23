from pimeyes_scraper import PimeyesScraper
from tavily_extractor import TavilyExtractor
from gemini_analyzer import GeminiAnalyzer
from url_retrieve import UrlRetrieve

def main():
    # 取得使用者輸入
    borrower_name = input("請輸入借款人姓名 (預設: 黃煒傑): ").strip() or "黃煒傑"
    
    # 設定查詢 URL（可以根據實際情況調整）
    search_url = "https://pimeyes.com/en/results/O9y_2502230jp5ugwnws8htmh9c1365a4?query=040007079f6fe7fb0000032f7fefe7ef"
    image_url = '/Users/akiraeason/Desktop/PimeScrap/meB.png'
    # 取得處理的圖片數量限制
    try:
        image_limit = int(input("請輸入要處理的圖片數量 (預設: 10): ").strip() or "10")
    except ValueError:
        image_limit = 10
        print("輸入無效，使用預設值 10")
    
    # 創建類別實例
    pimeyes_scraper = PimeyesScraper()
    tavily_extractor = TavilyExtractor()
    gemini_analyzer = GeminiAnalyzer()
    url_retrieve = UrlRetrieve()
    
    print(f"開始為借款人 {borrower_name} -- 執行信用評分分析流程")
    print("=" * 50)
    
    print("\n🔍 階段 0: 上傳圖片至 Pimeyes 圖像搜尋...")
    search_url = url_retrieve.run(image_url)

    # 第一階段：Pimeyes 圖像搜尋
    print(f"\n🔍 階段 1: 執行 Pimeyes 圖像搜尋..., URL: {search_url}")
    scraping_success = pimeyes_scraper.run(search_url, image_limit)
    
    if not scraping_success:
        print("❌ Pimeyes 搜尋失敗，無法繼續後續流程")
        return
        
    print("✅ Pimeyes 搜尋完成")
    print("=" * 50)
    
    # 第二階段：Tavily 內容提取
    print("\n📄 階段 2: 使用 Tavily 提取網頁內容...")
    extraction_success = tavily_extractor.extract_content()
    
    if not extraction_success:
        print("❌ Tavily 提取失敗，無法繼續後續流程")
        return
        
    print("✅ Tavily 內容提取完成")
    print("=" * 50)
    
    # 第三階段：Gemini 分析
    print("\n🧠 階段 3: 使用 Gemini 分析內容...")
    analysis_success = gemini_analyzer.run_analysis(borrower_name)
    
    if not analysis_success:
        print("❌ Gemini 分析失敗")
        return
        
    print("✅ Gemini 分析完成")
    print("=" * 50)
    
    print(f"\n🎉 {borrower_name} 的信用評分分析流程全部完成!")


if __name__ == "__main__":
    main()