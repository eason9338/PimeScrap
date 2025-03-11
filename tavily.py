import requests
import json

target_web = 'https://news.ltn.com.tw/news/life/breakingnews/3961691'
url = "https://api.tavily.com/extract"
WEBHOOK_URL = "https://autopilot.aiwize.com/webhooks/flows/f5d38b8b-c6c3-4ba4-9ba6-34cab695bae8"

payload = {
    "urls": target_web,
    "include_images": True,
    "extract_depth": "basic"
}
headers = {
    "Authorization": "Bearer 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",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers)

webhook_response = requests.post(
    WEBHOOK_URL,
    json=response.json(),
    headers={"Content-Type": "application/json"}
)

with open("output_data/tavily_response.txt", "w", encoding="utf-8") as file:
    json_data = json.loads(response.text)
    
    for i, result in enumerate(json_data.get("results", [])):
        file.write(f"===== 結果 {i+1} =====\n")
        file.write(f"URL: {result.get('url', 'N/A')}\n")
        file.write(f"標題: {result.get('title', 'N/A')}\n\n")
        
        if "raw_content" in result:
            file.write("內容:\n")
            file.write(result.get("raw_content", ""))
            file.write("\n\n")
        
        if "images" in result and result["images"]:
            file.write("圖片:\n")
            for img in result["images"]:
                file.write(f"- {img.get('url', 'N/A')}\n")
            file.write("\n")
        
        file.write("=" * 50 + "\n\n")

print("Tavily API 回應已儲存到 tavily_response.txt 檔案")