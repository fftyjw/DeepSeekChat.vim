# deepseek_chat.py
import requests
import vim
import json

def addColorLine(line, prefixLine=0, suffixLine=1):
    for _ in range(prefixLine):
        vim.current.buffer.append("")

    vim.current.buffer.append(line)
    for _ in range(suffixLine):
        vim.current.buffer.append("")


CstUrl = "https://api.deepseek.com/chat/completions"
CstTip="<!-- #user#---------------->"
CstHtmlSep1='<hr style="height: 2px; background: black; border: none;">'
CstHtmlSep2='***'
CstVarHistory="deepseek_history"
CstVarCfg="deepseek_chat_cfg"
CstCfgHtmlSepType="HtmlSepType"
CstCfgApiKey="ApiKey"
CstBufferName="deepseekchat"
gCfg = {}

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
        if buf.name and buf.name.endswith(CstBufferName):
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

def deepseek_chat_stream(q):
    conversation_history=vim.vars[CstVarHistory]
    conversation_history.append({"role": "user", "content": q})

    header = {
        "Authorization": f"Bearer {gCfg[CstCfgApiKey]}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user"}],
        "max_tokens": 2048,
    }
    data["messages"]=conversation_history
    data["stream"]=True
    with requests.post(CstUrl, headers=header, json=data, stream=True) as response:
        if response.status_code != 200:
            vim.command(f'echo "Status: {response.status_code}"')
            return
        assistant_reply = ""
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
        conversation_history.append({"role": "assistant", "content": assistant_reply})
        vim.vars[CstVarHistory]=conversation_history

def DeepSeekChatEnter():
    vim.command('highlight clear DeepseekHighlight')
    vim.command('highlight DeepseekHighlight guifg=#00d0ff')
    vim.command("match DeepseekHighlight /#deepseek#.*\\|#user#.*/")

def DeepSeekChatLeave():
    return

def setAutoCommand():
    buffer_name = vim.eval('bufname("%")')  # 获取当前缓冲区的名字
    vim.command(f'augroup BufferHighlight_{buffer_name}')  # 使用 buffer 名字作为 augroup 名称
    vim.command('autocmd!')
    vim.command(f'autocmd BufEnter <buffer={buffer_name}> py3 DeepSeekChatEnter()')
    vim.command(f'autocmd BufLeave <buffer={buffer_name}> py3 DeepSeekChatLeave()')
    vim.command('augroup END')

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
        vim.vars[CstVarHistory] = []
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

#        vim.command(f'echom "line: {line}, mode: {visualMode}"')
        putSep(moveCursor=False, htmlSep=True)
        deepseek_chat_stream(line)
        putSep("end", suffixLine=2)
        putTip()
    elif cmd == "new":
        vim.vars[CstVarHistory]=[]
        print("deepseeek session reset")
        if vim.current.buffer.name.endswith(CstBufferName):
            putSep("session reset", prefixLine=2, suffixLine=2)
            putTip()
            curserEnd()
    elif cmd == "open":
        openDeepSeek()
        setAutoCommand()
    elif cmd == "debug":
        debug={
            "cfg": gCfg,
            "history": vim.vars[CstVarHistory],
        }
        print(debug)
