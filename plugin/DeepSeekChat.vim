if !exists("g:deepseek_chat_automap")
    let g:deepseek_chat_automap= 1
endif

command! DeepSeekChatOpen call deepseekchat#open()
command! DeepSeekChatNew call deepseekchat#cmd("new")
command! DeepSeekChatDebug call deepseekchat#cmd("debug")
command! DeepSeekChat call deepseekchat#cmd("chat")

let s:scriptPath=expand("<sfile>:p:h")."/.."
fun deepseekchat#reload()
    execute 'source' s:scriptPath."/autoload/DeepSeekChat.vim"
python3 << EOF
import importlib
import sys
if 'DeepSeekChat' in sys.modules:
    m = sys.modules['DeepSeekChat']
    importlib.reload(m)
EOF
    echo "reloaded!"
endfun
