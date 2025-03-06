import cv2
import os
from pathlib import Path

def extract_faces_from_id_cards(input_folder, output_folder, min_face_size=(50, 50), min_neighbors=8, scale_factor=1.1, confidence_threshold=0.6):
    """
    從身分證照片中擷取人臉區域並儲存
    
    參數:
        input_folder: 存放身分證照片的資料夾路徑
        output_folder: 儲存擷取出的人臉照片的資料夾路徑
    """
    # 確保輸出資料夾存在
    os.makedirs(output_folder, exist_ok=True)
    
    # 載入預訓練的人臉檢測器
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # 取得所有圖片檔案
    extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    image_files = []
    for ext in extensions:
        image_files.extend(list(Path(input_folder).glob(f'*{ext}')))
    
    print(f"找到 {len(image_files)} 張圖片")
    
    # 處理每張圖片
    for img_path in image_files:
        print(f"處理: {img_path}")
        
        # 讀取圖片
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"無法讀取圖片: {img_path}")
            continue
            
        # 裁剪圖片，只保留右邊一半
        height, width = img.shape[:2]
        half_width = width // 2
        img = img[:, half_width:width]  # 保留右半部
        
        # 轉換為灰階以加速處理
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 使用Haar Cascade分類器檢測人臉
        # 使用函數參數控制檢測參數
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            minSize=min_face_size
        )
        
        # 儲存檢測到的人臉
        if len(faces) > 0:
            print(f"在 {img_path} 中檢測到 {len(faces)} 個人臉")
            
            # 如果檢測到多個人臉，只保留最大的一個（因為每個身分證應該只有一個人臉）
            if len(faces) > 1:
                max_area = 0
                max_face_idx = 0
                for i, (x, y, w, h) in enumerate(faces):
                    area = w * h
                    if area > max_area:
                        max_area = area
                        max_face_idx = i
                # 只保留面積最大的人臉
                faces = [faces[max_face_idx]]
                print(f"只保留最大的人臉")
            
            for i, (x, y, w, h) in enumerate(faces):
                # 增加臉部周圍的邊界 - 增加更大的邊界以確保包含頭髮和下巴
                padding_top = int(h * 0.4)      # 頭部需要更多空間
                padding_bottom = int(h * 0.3)    # 下巴也需要一些空間
                padding_sides = int(w * 0.3)     # 兩側適當留白
                
                # 計算新的邊界，同時確保不超出圖片範圍
                new_x = max(0, x - padding_sides)
                new_y = max(0, y - padding_top)
                new_w = min(img.shape[1] - new_x, w + 2 * padding_sides)
                new_h = min(img.shape[0] - new_y, h + padding_top + padding_bottom)
                
                # 擷取人臉區域
                face_img = img[new_y:new_y+new_h, new_x:new_x+new_w]
                
                # 儲存人臉圖片
                output_filename = os.path.join(output_folder, f"{img_path.stem}_face_{i}.jpg")
                cv2.imwrite(output_filename, face_img)
                print(f"已儲存: {output_filename}")
        else:
            print(f"在 {img_path} 中沒有檢測到人臉")

if __name__ == "__main__":
    # 指定輸入和輸出資料夾
    input_folder = "IDCard"  # 存放身分證照片的資料夾
    output_folder = "extracted_faces"  # 儲存擷取出的人臉照片的資料夾
    
    # 執行人臉擷取 - 可調整這些參數以提高準確性
    extract_faces_from_id_cards(
        input_folder, 
        output_folder,
        min_face_size=(50, 50),  # 最小人臉尺寸
        min_neighbors=8,         # 檢測所需的鄰近區域數量
        scale_factor=1.1,        # 圖像縮放因子
        confidence_threshold=0.6  # 信心閾值
    )
    
    print("處理完成!")