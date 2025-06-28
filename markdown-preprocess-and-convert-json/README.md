# Markdown Preprocess and Convert to JSON

本工具提供一套將 Markdown 內容結構化為 JSON 的 Python 函數，並可根據自訂正則表達式過濾不支援的 Markdown 語法。適用於將條列、說明、參數等資訊轉換為易於處理的結構化資料，特別適合需進一步分析、展示或轉換 Markdown 的場合。

## 功能說明

- **不支援語法檢查**：可透過外部正則表達式清單（`unsupported_patterns.txt`）動態管理不支援的 Markdown 語法，避免處理特殊區塊或標籤。
- **Markdown 結構化轉換**：將 Markdown 檔案轉換為 JSON，支援巢狀條列結構。提供 `default` 及 `prompt` 兩種模式，`prompt` 模式下可將標題（如說明、參數、細則）自動對應為 JSON key。
- **自訂縮排層級**：可設定條列縮排的空白數，正確解析巢狀結構。

## 主要函數

- `load_unsupported_patterns(filepath)`  
  讀取外部正則表達式清單，每行一條，忽略空行與井字註解。
- `is_supported_markdown(md: str, patterns=None)`  
  判斷 Markdown 文字是否僅包含支援的語法。
- `markdown_to_json(markdown_text: str, mode: str = "default", indent_size: int = 2) -> dict`  
  轉換 Markdown 為 JSON，支援巢狀條列與 prompt 結構。

## 使用方法

1. **建立正則表達式過濾清單**  
   於專案目錄下新增 `unsupported_patterns.txt`，每行一個正則表達式，用以過濾不支援的 Markdown 語法。例如：

   ```
   # HTML標籤
   <\/?(div|span|script|iframe|table|form|input|button)[^>]*>
   # 特殊程式區塊
   ```(mermaid|plantuml|flowchart|dot|sequence|graphviz)
   # 數學公式
   \$\$[^$]+\$\$
   ```

   - 井字（`#`）開頭表示註解。
   - 空行會被忽略。

2. **準備 Markdown 檔案**

   將要轉換的 Markdown 內容存為檔案（如 `test.md`）。

3. **執行主程式**

   ```bash
   python markdown_preprocess_and_to_json.py
   ```

   程式會自動讀取 `unsupported_patterns.txt` 作為過濾條件，並根據 `test.md` 內容進行支援性檢查與轉換。

4. **查看結果**

   若 Markdown 不包含不支援語法，將輸出結構化 JSON；否則會顯示「此檔案包含不支援的Markdown語法，無法解析。」。

## 管理正則過濾清單

- **新增規則**：直接於 `unsupported_patterns.txt` 新增新行，每行一個正則。
- **移除規則**：刪除或註解（加 `#`）對應行即可。
- **調整規則**：直接修改相應行的正則表達式內容，儲存檔案即可生效。

**注意事項：**
- 請確保每條正則的語法正確，避免誤過濾正常內容。
- 修改 `unsupported_patterns.txt` 無需重啟程式，下次執行會自動套用新規則。

## 範例

假設 `test.md` 內容如下：

```
### 查詢功能

#### 說明
本 API 用於查詢使用者資料。

#### 參數
- 使用者ID：必填
- 權限類別：選填

#### 細則
1. 僅限管理員可查詢。
2. 查詢結果含隱私資訊。
```

執行後會得到類似以下的 JSON 輸出：

```json
{
  "Prompts": {
    "查詢功能": {
      "description": "本 API 用於查詢使用者資料。",
      "parameters": [
        {"type": "listItem", "text": "使用者ID：必填"},
        {"type": "listItem", "text": "權限類別：選填"}
      ],
      "instructions": [
        {"type": "listItem", "text": "僅限管理員可查詢。"},
        {"type": "listItem", "text": "查詢結果含隱私資訊。"}
      ]
    }
  }
}
```

## 依賴

- Python 3.x
- 標準函式庫：`re`, `json`

---

如有更多自訂需求，請依據原始碼進行調整。
