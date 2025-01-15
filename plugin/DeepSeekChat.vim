command! DeepSeekChatOpen call deepseekchat#open()
command! DeepSeekChatNew call deepseekchat#cmd("new")
command! DeepSeekChatDebug call deepseekchat#cmd("debug")
command! DeepSeekChat call deepseekchat#cmd("chat")

let s:scriptPath=expand("<sfile>:p:h")."/.."
fun deepseekchat#reload()
    execute 'source' s:scriptPath."/autoload/DeepSeekChat.vim"
    echo "reloaded!"
endfun
