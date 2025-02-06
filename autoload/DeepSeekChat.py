# deepseek_chat.py
import requests
import vim
import json
import os
import sys

def addColorLine(line, prefixLine=0, suffixLine=1):
    for _ in range(prefixLine):
        vim.current.buffer.append("")

    vim.current.buffer.append(line)
    for _ in range(suffixLine):
        vim.current.buffer.append("")


CstUrl = "https://api.deepseek.com/chat/completions"
CstOllamaUrl= "http://127.0.0.1:11434/api/chat"
CstTip="<!-- #user#---------------->"
CstHtmlSep1='<hr style="height: 2px; background: black; border: none;">'
CstHtmlSep2='***'
CstVarHistory="deepseek_history"
CstVarCfg="deepseek_chat_cfg"
CstCfgHtmlSepType="HtmlSepType"
CstCfgApiKey="ApiKey"
CstCfgAIServerUrl="AIServerUrl"
CstCfgAIServerType="AIServerType"
CstCfgModel="Model"
CstCfgHideThink="HideThink"

CstBufferName="deepseekchat"

CstServerTypeDeepSeek="deepseek"
CstServerTypeOllama="ollama"

gCfg = {}
gNvim = -1

def putTip():
    addColorLine(CstTip, suffixLine=0)
    putHtmlSep(suffixLine=1)
    curserEnd()

def putSep(txt="", prefixLine=0, suffixLine=1, moveCursor=True, htmlSep=False):
    line=f"<!-- #deepseek#--{txt}-------------->"
    if htmlSep:
        addColorLine(line, prefixLine=prefixLine, suffixLine=0)
        putHtmlSep(suffixLine=suffixLine)
    else:
        addColorLine(line, prefixLine=prefixLine, suffixLine=suffixLine)
    if moveCursor:
        curserEnd()

def putHtmlSep(suffixLine=0):
    if gCfg[CstCfgHtmlSepType] != 0:
        sep=CstHtmlSep1
        if gCfg[CstCfgHtmlSepType]==2:
            sep=CstHtmlSep2
        addColorLine(sep, suffixLine=suffixLine)
    else:
        for _ in range(suffixLine):
            vim.current.buffer.append("")

def curserEnd():
    last_line = len(vim.current.buffer)
    vim.current.window.cursor = (last_line, 0)

def openDeepSeek():
    for tab in vim.tabpages:
        for win in tab.windows:
            if win.buffer.name.endswith(CstBufferName):
                # 切换到对应的标签页和窗口
                vim.current.tabpage = tab
                vim.current.window = win
                return

    target_buffer = None
    for buf in vim.buffers:
        is_listed = vim.eval(f'buflisted({buf.number})') == '1'
        if is_listed and buf.name and buf.name.endswith(CstBufferName):
            target_buffer = buf
            break
    # 如果未找到缓冲区，则垂直拆分窗口并创建新缓冲区
    if target_buffer:
        vim.command('vsplit')  # 垂直拆分窗口
        vim.command(f"buffer {target_buffer.number}")  # 垂直拆分窗口
        return
    vim.command(f'vnew {CstBufferName}')  # 创建新缓冲区
    vim.command('set filetype=markdown')  # 设置文件类型为 "vimwiki"
    vim.command('set hidden')  # 设置文件类型为 "vimwiki"
    vim.command('setlocal buftype=nofile')
    vim.command('set wrap')
    DeepSeekChatEnter()
    if gCfg[CstCfgHtmlSepType] == 0:
        vim.current.buffer[:]=[CstTip, ""]
    elif gCfg[CstCfgHtmlSepType] == 1:
        vim.current.buffer[:]=[CstTip, CstHtmlSep1, ""]
    else:
        vim.current.buffer[:]=[CstTip, CstHtmlSep2, ""]
    curserEnd()

def find_question():
    # 获取当前行号
    current_line_num = int(vim.eval('line(".")'))
    
    # 用于存储符合条件的行
    matching_lines = []
    
    # 从当前行开始往前遍历
    for line_num in range(current_line_num, 0, -1):
        # 获取当前行的内容
        line_content = vim.eval(f'getline({line_num})')
        if line_content.startswith(("<!-- #deepseek#", "<!-- #user#")):
            break
        if line_content==CstHtmlSep1 or line_content==CstHtmlSep2:
            break
        # 检查是否为空行
        if line_content.strip():
            matching_lines.append(line_content)
    
    # 输出所有符合条件的行
    if len(matching_lines) > 0:
        return "\n".join(matching_lines[::-1])
    
    return ""

def historyFromVim():
    return vim.vars[CstVarHistory]

def historyToVim(history=None):
    if None == history:
        if isNvim():
            history=[]
        else:
            history=([], {})
    vim.vars[CstVarHistory] = history

def addHistory(history, *items):
    if isNvim():
        for item in items:
            history.append(item)
    else:
        for item in items:
            key=f"{len(history[0])}"
            history[1].update({key: item})
            history[0].extend(key)

def serializableHistory(history, extra=None):
    def convItem(item):
#        print(item, isinstance(item, dict))
        if isinstance(item, dict) or isinstance(item, vim.Dictionary):
            role=item["role"]
            if not isNvim():
                role=item[b"role"]
            if isinstance(role, bytes):
                role=role.decode()
            content=item["content"]
            if not isNvim():
                content=item[b"content"]
            if isinstance(content, bytes):
                content=content.decode()
            if role and content:
#                print(role, content)
                return {"role": role, "content": content}
        return None

    ret=[]
    if isNvim():
        for item in history:
            item=convItem(item)
            if item:
                ret.append(item)
    else:
        for key in history[0]:
            item=history[1][key]
            item=convItem(item)
            if item:
                ret.append(item)
    if extra:
        ret.append(extra)
#    print(ret)
    return ret

def isNvim():
    global gNvim
    if gNvim < 0:
        if 'NVIM' in os.environ:
#            print("Running in Neovim")
            gNvim=1
        else:
#            print("Running in Vim")
            gNvim=0
    if 0 == gNvim:
        return False
    else:
        return True

def getCfgWithDefault(key, default):
    ret=default
    if key in gCfg:
        ret=gCfg[key]
        if type(ret) is bytes:
            ret=ret.decode('utf-8')
#    vim.command(f'echom "getCfgWithDefault, key: {key}, ret: {ret}, default: {default}"')
    return ret

def ollama_chat_stream(q):
    conversation_history=historyFromVim()
    url=getCfgWithDefault(CstCfgAIServerUrl, CstOllamaUrl)
    model=getCfgWithDefault(CstCfgModel, "")
#    vim.command(f'echom "ollama, history: {conversation_history}"')
    header = {
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": [{"role": "user"}],
    }
    hisReq={"role": "user", "content": q}
    data["messages"]=serializableHistory(conversation_history, hisReq)
    data["stream"]=True
    with requests.post(url, headers=header, json=data, stream=True) as response:
        if response.status_code != 200:
            vim.command(f'echo "Status: {response.status_code}"')
            return False
        assistant_reply = ""
        putSep(moveCursor=False, htmlSep=True)
        thinking=False
        hideThink=getCfgWithDefault(CstCfgHideThink, 1)
        for chunk in response.iter_lines():
            if chunk:
                chunk_str=chunk.decode("utf-8").strip()
                try:
                    json_data = json.loads(chunk_str)  # 解析 JSON
                    if "message" in json_data:
                        text = json_data["message"]["content"]
                        if text:
                            if hideThink:
                                if text=="<think>":
                                    thinking=True
                                    continue
                                elif text=="</think>":
                                    thinking=False
                                    continue
                                elif thinking:
                                    continue
                            assistant_reply += text
                            buf = vim.current.buffer
                            lines = text.split('\n')
                            firstLine=True
                            for line in lines:
                                if firstLine:
                                    firstLine = False
                                    last_line = len(buf) - 1
                                    buf[last_line] += line  # 直接修改最后一行的内容
                                else:
                                    buf.append(line)  # 将每一行添加到缓冲区末尾
                                    curserEnd()
                            vim.command("redraw")  # 刷新界面 
                    if "done" in json_data and json_data["done"]:
                        continue
                except json.JSONDecodeError:
                    print(f"Invalid JSON chunk: {chunk_str}", file=sys.stderr)
        if assistant_reply:
            addHistory(conversation_history, hisReq, {"role": "assistant", "content": assistant_reply})
            historyToVim(conversation_history)
    return True

def deepseek_chat_stream(q):
    conversation_history=historyFromVim()
    apiKey=getCfgWithDefault(CstCfgApiKey, "")
#    vim.command(f'echom "key: {apiKey}, history: {conversation_history}"')
    header = {
        "Authorization": f"Bearer {apiKey}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user"}],
        "max_tokens": 2048,
    }
    hisReq={"role": "user", "content": q}
    data["messages"]=serializableHistory(conversation_history, hisReq)
    data["stream"]=True
    with requests.post(CstUrl, headers=header, json=data, stream=True) as response:
        if response.status_code != 200:
            vim.command(f'echo "Status: {response.status_code}"')
            return False
        assistant_reply = ""
        putSep(moveCursor=False, htmlSep=True)
        for chunk in response.iter_lines():
            if chunk:
                chunk_str=chunk.decode("utf-8").strip()
                if chunk_str.startswith("data:"):  # 假设返回的数据格式是 "data: {...}"
                    json_str = chunk_str[5:].strip()  # 去掉 "data:" 前缀
                    if json_str == "[DONE]":
                        continue
                    try:
                        json_data = json.loads(json_str)  # 解析 JSON
                        if "choices" in json_data:
                            delta = json_data["choices"][0]["delta"]
                            if "content" in delta:
                                text= delta["content"]
                                assistant_reply += text
                                if text:
                                    buf = vim.current.buffer
                                    lines = text.split('\n')
                                    firstLine=True
                                    for line in lines:
                                        if firstLine:
                                            firstLine = False
                                            last_line = len(buf) - 1
                                            buf[last_line] += line  # 直接修改最后一行的内容
                                        else:
                                            buf.append(line)  # 将每一行添加到缓冲区末尾
                                            curserEnd()
                                    vim.command("redraw")  # 刷新界面
                    except json.JSONDecodeError:
                        print(f"Invalid JSON chunk: {chunk_str}", file=sys.stderr)
        if assistant_reply:
            addHistory(conversation_history, hisReq, {"role": "assistant", "content": assistant_reply})
            historyToVim(conversation_history)
    return True

def DeepSeekChatEnter():
    vim.command('highlight clear DeepseekHighlight')
    vim.command('highlight DeepseekHighlight guifg=#00d0ff')
    vim.command("match DeepseekHighlight /#deepseek#.*\\|#user#.*/")

def DeepSeekChatLeave():
    return

def getLinePart(line, start=0, end=-1):
    byte_data = line.encode('utf-8')
    if end==-1:
        end=len(byte_data)
    else:
        char_index = len(byte_data[:end].decode('utf-8', errors='ignore'))
        char_byte_length = len(line[char_index].encode('utf-8'))
        end+=char_byte_length
    sliced_bytes = byte_data[start:end]
    try:
        return sliced_bytes.decode('utf-8')
    except UnicodeDecodeError:
        return sliced_bytes.decode('utf-8', errors='ignore')

def DeepSeekChatCommand(cmd, visualMode=0):
    if CstVarHistory not in vim.vars:
        historyToVim()
    if CstVarCfg not in vim.vars:
        print(f"please set g:{CstVarCfg}")
        return
    global gCfg
    gCfg=vim.vars[CstVarCfg]

    if not CstCfgHtmlSepType in gCfg:
        gCfg[CstCfgHtmlSepType] = 2
    if cmd=="chat":
        if not CstCfgApiKey in gCfg:
            print(f"please set g:{CstVarCfg}.{CstCfgApiKey}")
            return
        line=""
        if 0 != visualMode:
            start_pos=vim.eval("getpos(\"'<\")")
            end_pos=vim.eval("getpos(\"'>\")")
#            vim.command(f'echom "{start_pos}, {end_pos}"')
            start_line, start_col = start_pos[1:3]
            end_line, end_col = end_pos[1:3]
            endCol=int(end_col)
            if endCol == 0x7FFFFFFF:
                endCol = -1
            else:
                endCol -= 1
            selected_lines = vim.current.buffer[int(start_line) - 1:int(end_line)]
            if selected_lines:
                if len(selected_lines) == 1:
                    # 单行选中
                    line=getLinePart(selected_lines[0], int(start_col)-1, endCol)
                else:
                    # 多行选中
                    selected_lines[0] = getLinePart(selected_lines[0], int(start_col)-1)
                    selected_lines[-1] = getLinePart(selected_lines[-1], end=endCol)
                    line="\n".join(selected_lines)

        if "" == line:
            line=find_question()

        if "" == line:
            print("empty question")
            return

        aiType=getCfgWithDefault(CstCfgAIServerType, CstServerTypeDeepSeek)
#        vim.command(f'echom "line: {line}, mode: {visualMode}, aiType: {aiType}"')
        if aiType==CstServerTypeOllama:
            ret=ollama_chat_stream(line)
        else:
            ret=deepseek_chat_stream(line)
        if ret:
            putSep("end", suffixLine=2)
            putTip()
    elif cmd == "new":
        historyToVim()
        print("deepseeek session reset")
        if vim.current.buffer.name.endswith(CstBufferName):
            putSep("session reset", prefixLine=2, suffixLine=2)
            putTip()
            curserEnd()
    elif cmd == "open":
        openDeepSeek()
    elif cmd == "debug":
        debug={
            "cfg": dict(gCfg),
            "history": serializableHistory(historyFromVim()),
        }
        print(debug)
