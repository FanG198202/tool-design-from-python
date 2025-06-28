import re

def markdown_to_json(markdown_text: str, mode: str = "default", indent_size: int = 2) -> dict:
    """
    將Markdown轉換為結構化JSON，支援巢狀條列(根據indent_size判斷階層)。
    mode: "default"普通結構化，"prompt"則自動將說明、參數、細則等mapping為對應key。
    indent_size: 條列每層縮進空白數。
    """
    lines = markdown_text.split('\n')
    root = {'type': 'document', 'content': []}
    stack = [{'node': root, 'level': 0}]
    result = {}

    # Prompt模式下的標題對映
    mapping = {
        'description': ['說明', '描述', '描述：', '說明：', 'Description', 'Desc', 'Overview'],
        'parameters': ['參數', '參數：', '條件', '條件：', 'Parameters', 'Params'],
        'instructions': ['細則', '條件細則', '規則', '規則：', 'Instructions', 'Instruction', 'Guidelines'],
    }
    key_title_map = {}
    for k, vlist in mapping.items():
        for v in vlist:
            key_title_map[v.strip('：').lower()] = k

    current_key = None
    buffer = []
    current_prompt = None

    heading_regex = re.compile(r'^(#{1,6})\s*(.*)$')
    list_item_regex = re.compile(r'^(\s*)([-*+]|(\d+)\.)\s+(.*)$')

    # 巢狀條列輔助
    def parse_nested_list(start_idx):
        items_stack = []
        last_level = None
        parent_items = []
        cur_items = parent_items

        i = start_idx
        while i < len(lines):
            line = lines[i].rstrip('\n')
            list_match = list_item_regex.match(line)
            if not list_match:
                break  # 條列結束

            indent = len(list_match.group(1).replace('\t', ' ' * indent_size))
            level = indent // indent_size
            text = list_match.group(4).strip()

            node = {'type': 'listItem', 'text': text}
            if not items_stack or level == 0:
                cur_items.append(node)
                items_stack = [(level, cur_items)]
            else:
                # find parent
                while items_stack and items_stack[-1][0] >= level:
                    items_stack.pop()
                if not items_stack:
                    cur_items.append(node)
                    items_stack = [(level, cur_items)]
                else:
                    parent = items_stack[-1][1][-1]
                    if 'children' not in parent:
                        parent['children'] = []
                    parent['children'].append(node)
                    items_stack.append((level, parent['children']))
            i += 1
        return parent_items, i - start_idx

    def flush_buffer_to_key():
        nonlocal buffer, current_key, result
        if current_key and buffer:
            if current_key in ['parameters', 'instructions']:
                # 處理巢狀條列
                buf = '\n'.join(buffer)
                buf_lines = buf.split('\n')
                items = []
                idx = 0
                while idx < len(buf_lines):
                    if list_item_regex.match(buf_lines[idx]):
                        nested, consumed = parse_nested_list_from_lines(buf_lines, idx)
                        items.extend(nested)
                        idx += consumed
                    else:
                        val = buf_lines[idx].lstrip('-*+ ').lstrip('0123456789. ').strip()
                        if val:
                            items.append(val)
                        idx += 1
                result.setdefault(current_prompt, {})[current_key] = items
            else:
                desc = '\n'.join(buffer).strip()
                result.setdefault(current_prompt, {})[current_key] = desc
        buffer = []

    def parse_nested_list_from_lines(buf_lines, start_idx):
        # 與上面parse_nested_list類似但針對任意行陣列
        items_stack = []
        parent_items = []
        cur_items = parent_items

        i = start_idx
        while i < len(buf_lines):
            line = buf_lines[i].rstrip('\n')
            list_match = list_item_regex.match(line)
            if not list_match:
                break
            indent = len(list_match.group(1).replace('\t', ' ' * indent_size))
            level = indent // indent_size
            text = list_match.group(4).strip()
            node = {'type': 'listItem', 'text': text}
            if not items_stack or level == 0:
                cur_items.append(node)
                items_stack = [(level, cur_items)]
            else:
                while items_stack and items_stack[-1][0] >= level:
                    items_stack.pop()
                if not items_stack:
                    cur_items.append(node)
                    items_stack = [(level, cur_items)]
                else:
                    parent = items_stack[-1][1][-1]
                    if 'children' not in parent:
                        parent['children'] = []
                    parent['children'].append(node)
                    items_stack.append((level, parent['children']))
            i += 1
        return parent_items, i - start_idx

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue

        heading_match = heading_regex.match(line)
        if heading_match:
            flush_buffer_to_key()
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            low_title = title.strip('：').lower()
            if level == 3:
                current_prompt = title
                current_key = None
                i += 1
                continue
            if low_title in key_title_map:
                current_key = key_title_map[low_title]
                i += 1
                continue
            current_key = None
            i += 1
            continue

        # 巢狀條列（prompt模式下進入buffer，default模式下直接插入）
        list_match = list_item_regex.match(line)
        if list_match:
            if mode == "prompt" and current_key in ['parameters', 'instructions']:
                buffer.append(line)
                i += 1
                continue
            else:
                # default模式下直接處理巢狀條列
                items, consumed = parse_nested_list(i)
                stack[-1]['node']['content'].append({
                    'type': 'list',
                    'ordered': bool(list_match.group(3)),
                    'items': items
                })
                i += consumed
                continue

        # 段落
        if mode == "prompt" and current_key:
            buffer.append(line.strip())
        else:
            stack[-1]['node']['content'].append({'type': 'paragraph', 'text': line.strip()})
        i += 1

    flush_buffer_to_key()

    if mode == "prompt" and result:
        return {"Prompts": result}
    else:
        return root

# 測試範例
if __name__ == "__main__":
    md = '''
### 測試巢狀條列

#### 參數
- 第一層A
  - 第二層A1
  - 第二層A2
    - 第三層A2-1
- 第一層B
    '''
    import json
    print(json.dumps(markdown_to_json(md, mode="prompt", indent_size=2), ensure_ascii=False, indent=2))