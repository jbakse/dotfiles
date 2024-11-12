#/ brew - package manager
eval "$(/opt/homebrew/bin/brew shellenv)"

#/ devbox - nix frontend
eval "$(devbox global shellenv)"

#/ oh my zsh 
source ~/dotfiles/ohmyzsh.zsh

#/ exa - modern replacement for ls
alias ls='exa -alF --git'
alias lst='exa -lFT --git'

#/ zoxide - jump around directories
eval "$(zoxide init zsh)"

#/ bat
alias less='bat'
alias more='bat'

#/ fzf - fuzzy filter
# https://github.com/junegunn/fzf/wiki/examples#command-history

# fuzzy search history
fh() {
  print -z $( ([ -n "$ZSH_NAME" ] && fc -l 1 || history) | fzf +s --tac | sed -E 's/ *[0-9]*\*? *//' | sed -E 's/\\/\\\\/g')
}

#/ shell
alias reload!='. ~/.zshrc'

# add dotfiles/bin to front of path
export PATH="$HOME/dotfiles/bin:$PATH"

#/ welcome message
echo
echo -e "\033[1;37;40m Hello, .zshrc! \033[0m"
echo