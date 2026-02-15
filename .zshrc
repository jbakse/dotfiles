#/ brew - package manager
eval "$(/opt/homebrew/bin/brew shellenv)"

#/ devbox - nix frontend
eval "$(devbox global shellenv)"

#/ oh my zsh 
source ~/dotfiles/ohmyzsh.zsh

#/ eza - modern replacement for ls
alias ls='eza -alF --git'
alias lst='eza -lFT --git'

#/ zoxide - jump around directories
eval "$(zoxide init zsh)"

#/ bat
alias less='bat'
alias more='bat'
export MANPAGER="sh -c 'col -bx | bat -l man -p'"

#/ fzf - fuzzy filter
source <(fzf --zsh)

alias browse='fzf --preview "bat --style=numbers --color=always --line-range :500 {}"'

#/ fd

alias big='fd --type f -0 | xargs -0 du -h | sort -rh | head -n 10'

#/ shell
alias reload!='. ~/.zshrc'

#/ PATH
export PATH="$HOME/dotfiles/bin:$PATH"
export PATH="$HOME/.npm/bin:$PATH"
export PATH="$HOME/.deno/bin:$PATH"
export PATH="$HOME/.cache/lm-studio/bin:$PATH"
export PATH="/Applications/Aseprite.app/Contents/MacOS:$PATH"

#/ welcome message
echo
echo -e "\033[1;37;40m Hello, .zshrc! \033[0m"
echo "hints: ctrl-t, ctrl-r, fd, browse, reload!"