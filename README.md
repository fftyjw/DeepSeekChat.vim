# DeepSeekChat for Neovim

![record](https://github.com/user-attachments/assets/f90a6eb2-f693-45c8-96ae-c481e88e09d7)

# Requirements

- [Neovim 0.10.2+](https://neovim.io/) or [vim 9.1.0+](https://vim.org/). Both editor need python3 support.
- Python3 with requests installed.
```
     'pip3 install requests'
```

# Installation

### [Vim-Plug](https://github.com/junegunn/vim-plug)

```vim
call plug#begin()
Plug 'fftyjw/DeepSeekChat.vim'
call plug#end()

"ApiKey must set.
let g:deepseek_chat_cfg = {
    \ "ApiKey": "<your api key>",
    \ }
```

# Usage

## Commands

- `:DeepSeekChatOpen` - Open chat window.
- `:DeepSeekChat` - Ask a question using the text you input in the chat buffer. If there is any text visually selected, the selected text will be used. Otherwise, it will use all the text from the current line up to the separator line or the tip line (If generated by the plugin itself).
- `:DeepSeekChatNew` - Start a new chat session. This will clear the chat history.
- `:DeepSeekChatDebug` - Print debug info, include config and chat history.

## Mappings
   In the chat buffer, these mappings are set by default. You can disable it by set `g:deepseek_chat_automap` to `0`
   
- `<C-s>` - Command DeepSeekChat
- `<C-n>` - Command DeepSeekChatNew
- `<C-d>` - Command DeepSeekChatDebug
 
  You can define your own mapings like this:
  ```vim
    let g:deepseek_chat_automap=0
    function! MyDeepSeekChatMap()
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
    autocmd BufEnter * call MyDeepSeekChatMap()
    noremap <leader>ss :DeepSeekChatOpen<CR>
  ```

## Config
- `g:deepseek_chat_cfg` Basic configs. Example:
```vim
    let g:deepseek_chat_cfg = {
        \ "ApiKey": "xxxxxxx", "Put your api key here. This is required.
        \ "The chat buffer's filetype is 'markdown'. To render it nicely, the plugin offers 2 types of separator lines:
        \ "  1: A black 2-pixel-high separator line. 
        \ "  2: Normal separator line.(Markdown code: ***). 
        \ "If this config is set to 0, there will be no separator lines.
        \ "HtmlSepType": 0, 
        \ }
```
- `g:deepseek_chat_automap` 0: Disable auto mapping. 1: Enable auto mapping. Default 1.
