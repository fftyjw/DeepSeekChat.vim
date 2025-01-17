if !exists("g:deepseek_chat_automap")
    let g:deepseek_chat_automap= 1
endif

command! -range DeepSeekChatOpen call deepseekchat#open()
command! -range DeepSeekChatNew call deepseekchat#cmd("new")
command! -range DeepSeekChatDebug call deepseekchat#cmd("debug")
command! -range DeepSeekChat call deepseekchat#cmd("chat")

let s:scriptPath=expand("<sfile>:p:h")."/.."
execute 'py3file' s:scriptPath.'/autoload/DeepSeekChat.py'
augroup BufferHighlight_deepseekchat
autocmd!
autocmd BufEnter * if bufname("%") == "deepseekchat" | execute "py3 DeepSeekChatEnter()" | endif
autocmd BufLeave * if bufname("%") == "deepseekchat" | execute "py3 DeepSeekChatLeave()" | endif
augroup END

fun! deepseekchat#reload()
    execute 'source' s:scriptPath."/autoload/DeepSeekChat.vim"
    execute 'py3file' s:scriptPath.'/autoload/DeepSeekChat.py'
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
