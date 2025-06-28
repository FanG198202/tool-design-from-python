# markdown_nested_list_to_json

將 Markdown 文件轉換為結構化 JSON，支援巢狀條列、標題等格式，並可依需求自動將常見說明、參數、規則等區塊對應為指定 key，適合工具設計、API 文件解析與 Prompt 工程等需求。

## 特色

- 支援多層巢狀條列（可設定縮排空格數）
- 支援標題識別（各階層標題自動對應）
- 提供 `default` 與 `prompt` 兩種解析模式
    - `default`：原始結構化輸出，適用各類 Markdown
    - `prompt`：自動將「說明」、「參數」、「規則」等對應為 JSON key，方便生成 API or Prompt 結構
- 純 Python 實作，無外部依賴

## 安裝與使用

將 `markdown_nested_list_to_json.py` 放入專案目錄，即可直接匯入使用：

```python
from markdown_nested_list_to_json import markdown_to_json

# 讀取 Markdown 內容
md = """
### 測試範例

#### 說明
這是說明段落。

#### 參數
- 參數A
  - 子參數A1
  - 子參數A2
    - 子參數A2-1
- 參數B

#### 細則
1. 規則1
2. 規則2
"""

# 轉換為 JSON
json_obj = markdown_to_json(md, mode="prompt", indent_size=2)
import json
print(json.dumps(json_obj, ensure_ascii=False, indent=2))
```

## 解析模式說明

### 1. default 模式

- 還原 Markdown 結構，所有段落、條列、標題皆以結構化 JSON 表示

#### 範例 Markdown

```markdown
# API 文件

說明段落。

- 條列一
  - 子條列一
- 條列二
```

#### 轉換結果（片段）

```json
{
  "type": "document",
  "content": [
    {
      "type": "paragraph",
      "text": "說明段落。"
    },
    {
      "type": "list",
      "ordered": false,
      "items": [
        {
          "type": "listItem",
          "text": "條列一",
          "children": [
            {
              "type": "listItem",
              "text": "子條列一"
            }
          ]
        },
        {
          "type": "listItem",
          "text": "條列二"
        }
      ]
    }
  ]
}
```

### 2. prompt 模式

- 常見區塊（說明、參數、細則等）自動對應為 JSON key，方便用於 Prompt、API 文件結構
- 支援標題多語（如「說明」、「Description」、「參數」、「Parameters」等皆可自動辨識）

#### 範例 Markdown

```markdown
### 查詢用戶

#### 說明
查詢系統內指定用戶資料。

#### 參數
- user_id: 用戶唯一識別碼
- include_history: 是否包含歷史紀錄

#### 細則
1. 僅管理員可查詢
2. 查詢結果以 JSON 回傳
```

#### 轉換結果

```json
{
  "Prompts": {
    "查詢用戶": {
      "description": "查詢系統內指定用戶資料。",
      "parameters": [
        {
          "type": "listItem",
          "text": "user_id: 用戶唯一識別碼"
        },
        {
          "type": "listItem",
          "text": "include_history: 是否包含歷史紀錄"
        }
      ],
      "instructions": [
        {
          "type": "listItem",
          "text": "僅管理員可查詢"
        },
        {
          "type": "listItem",
          "text": "查詢結果以 JSON 回傳"
        }
      ]
    }
  }
}
```

## 參數說明

- `markdown_text`：原始 Markdown 內容（str）
- `mode`：解析模式，"default" 或 "prompt"（預設 "default"）
- `indent_size`：條列每層縮排空白數，預設 2

## 進階應用

- 可用於自動化文件生成、API 文件解析、Prompt 模板結構化等場合
- 支援中文及英文多語標題辨識

## 範例：常見 Markdown 文檔轉換

### Markdown 範例

```markdown
### 建立任務

#### 說明
建立一個新任務，並指派負責人。

#### 參數
- task_name: 任務名稱
- assignee: 負責人
  - 可多選
- due_date: 截止日期

#### 細則
1. 任務名稱不可重複
2. 截止日期不可早於今日
```

### 轉換結果

```json
{
  "Prompts": {
    "建立任務": {
      "description": "建立一個新任務，並指派負責人。",
      "parameters": [
        {
          "type": "listItem",
          "text": "task_name: 任務名稱"
        },
        {
          "type": "listItem",
          "text": "assignee: 負責人",
          "children": [
            {
              "type": "listItem",
              "text": "可多選"
            }
          ]
        },
        {
          "type": "listItem",
          "text": "due_date: 截止日期"
        }
      ],
      "instructions": [
        {
          "type": "listItem",
          "text": "任務名稱不可重複"
        },
        {
          "type": "listItem",
          "text": "截止日期不可早於今日"
        }
      ]
    }
  }
}
```

---

## License

MIT
