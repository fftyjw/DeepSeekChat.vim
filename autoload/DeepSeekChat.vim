python3 import sys, vim
python3 if vim.eval('expand("<sfile>:p:h")') not in sys.path: sys.path.append(vim.eval('expand("<sfile>:p:h")'))
python3 from DeepSeekChat import DeepSeekChatCommand, DeepSeekChatEnter, DeepSeekChatLeave

function! deepseekchat#map()
    if g:deepseek_chat_automap == 0
        return
    endif
    if bufname('%') == 'deepseekchat'
        nnoremap <buffer> <c-s> :<C-u>call deepseekchat#cmd('chat')<CR>
        inoremap <buffer> <c-s> <esc>:call deepseekchat#cmd('chat')<CR>
        vnoremap <buffer> <c-s> <esc>:call deepseekchat#cmd_v('chat')<CR>
        noremap <buffer> <c-n> :<C-u>call deepseekchat#cmd('new')<CR>
        inoremap <buffer> <c-n> <esc>:call deepseekchat#cmd('new')<CR>
        noremap <buffer> <c-d> :<C-u>call deepseekchat#cmd('debug')<CR>
        inoremap <buffer> <c-d> <esc>:call deepseekchat#cmd('debug')<CR>
    endif
endfunction

fun! deepseekchat#cmd_v(cmd) range
    call deepseekchat#cmdImp(a:cmd, 1)
endfun

fun! deepseekchat#cmd(cmd)
    call deepseekchat#cmdImp(a:cmd, 0)
endfun

fun! deepseekchat#cmdImp(cmd, visualMode) range
python3 << EOF
cmd = vim.eval('a:cmd')
visualMode = int(vim.eval('a:visualMode'))
DeepSeekChatCommand(cmd, visualMode)
EOF
endfun
fun! deepseekchat#open() range
    call deepseekchat#cmd("open")
endfun
autocmd BufEnter * call deepseekchat#map()
