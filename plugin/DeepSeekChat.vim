if !exists("g:deepseek_chat_automap")
    let g:deepseek_chat_automap= 1
endif

command! -range DeepSeekChatOpen call deepseekchat#open()
command! -range DeepSeekChatNew call deepseekchat#cmd("new")
command! -range DeepSeekChatDebug call deepseekchat#cmd("debug")
command! -range DeepSeekChat call deepseekchat#cmd("chat")

let s:scriptPath=expand("<sfile>:p:h")."/.."
fun! deepseekchat#reload()
    execute 'source' s:scriptPath."/autoload/DeepSeekChat.vim"
python3 << EOF
import importlib
import sys
import vim
if 'DeepSeekChat' in sys.modules:
    m = sys.modules['DeepSeekChat']
    importlib.reload(m)
EOF
    python3 from DeepSeekChat import DeepSeekChatCommand, DeepSeekChatEnter, DeepSeekChatLeave
    echom "reloaded!"
endfun
