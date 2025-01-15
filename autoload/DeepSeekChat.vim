python3 << EOF
import importlib
import sys

if 'DeepSeekChat' in sys.modules:
    m = sys.modules['DeepSeekChat']
    importlib.reload(m)
EOF

python3 import sys, vim
python3 if vim.eval('expand("<sfile>:p:h")') not in sys.path: sys.path.append(vim.eval('expand("<sfile>:p:h")'))
python3 from DeepSeekChat import DeepSeekChatCommand, DeepSeekChatEnter, DeepSeekChatLeave

function! deepseekchat#map()
    if g:deepseek_chat_automap == 0
        return
    endif
    if bufname('%') == 'deepseek'
        noremap <buffer> <c-s> :call deepseekchat#cmd('chat')<CR>
        inoremap <buffer> <c-s> <esc>:call deepseekchat#cmd('chat')<CR>
        noremap <buffer> <c-n> :call deepseekchat#cmd('new')<CR>
        inoremap <buffer> <c-n> <esc>:call deepseekchat#cmd('new')<CR>
        noremap <buffer> <c-d> :call deepseekchat#cmd('debug')<CR>
        inoremap <buffer> <c-d> <esc>:call deepseekchat#cmd('debug')<CR>
    endif
endfunction

fun! deepseekchat#cmd(cmd) range
python3 << EOF
cmd = vim.eval('a:cmd')
DeepSeekChatCommand(cmd)
EOF
endfun
fun! deepseekchat#open() range
    autocmd BufEnter * call deepseekchat#map()
    call deepseekchat#cmd("open")
    call deepseekchat#map()
endfun
