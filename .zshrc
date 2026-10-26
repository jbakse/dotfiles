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

#/ git shortcuts
alias glog='git-l'
alias gclean='git-clean-branches'

#/ shell
alias reload!='. ~/.zshrc'

#/ ai
alias bf='butterfish shell -m gpt-6.1-sol'

#/ PATH
export PATH="$HOME/dotfiles/bin:$PATH"
export PATH="$HOME/.npm/bin:$PATH"
export PATH="$HOME/.deno/bin:$PATH"
export PATH="$HOME/.cache/lm-studio/bin:$PATH"
export PATH="/Applications/Aseprite.app/Contents/MacOS:$PATH"
export PATH="$HOME/.local/bin:$PATH"

#/ welcome message
echo
echo -e "\033[30m\033[48;5;217m H\033[48;5;223me\033[48;5;229ml\033[48;5;229ml\033[48;5;194mo\033[48;5;194m,\033[48;5;159m T\033[48;5;159me\033[48;5;183mr\033[48;5;183mm\033[48;5;218mi\033[48;5;218mn\033[48;5;223ma\033[48;5;229ml\033[48;5;229m!\033[48;5;194m \033[0m"
echo
echo -e " \033[1;36mkeybindings\033[0m"
echo -e " \033[33mctrl-r\033[0m         fuzzy search command history"
echo -e " \033[33mctrl-t\033[0m         fuzzy find files"
echo
echo -e " \033[1;36maliases\033[0m"
echo -e " \033[33mls\033[0m             eza with details and git status"
echo -e " \033[33mlst\033[0m            eza tree view"
echo -e " \033[33mless\033[0m / \033[33mmore\033[0m    bat (syntax-highlighted pager)"
echo -e " \033[33mman\033[0m            bat-powered man pages"
echo -e " \033[33mbrowse\033[0m         fuzzy find files with bat preview"
echo -e " \033[33mbig\033[0m            show 10 largest files in current tree"
echo -e " \033[33mz <dir>\033[0m        jump to a directory (zoxide)"
echo -e " \033[33mreload!\033[0m        re-source .zshrc"
echo -e " \033[33mbf\033[0m             butterfish AI shell (gpt-6.1-sol)"
echo
echo -e " \033[1;36mscripts\033[0m"
echo -e " \033[33mglog\033[0m           interactive git log with fzf"
echo -e " \033[33mgclean\033[0m         delete branches merged into main"
echo -e " \033[33mshrink-grab\033[0m         re-encode .mov screen recordings to .mp4"
echo -e " \033[33mscreenshot-watch\033[0m on|off|status|log [-f] — auto-compress ~/Screenshots videos"
echo
echo -e " \033[1;36mtools\033[0m"
echo -e " \033[33mtldr\033[0m           simplified man pages"
echo -e " \033[33mfd\033[0m             modern find"
echo -e " \033[33mncdu\033[0m           interactive disk usage"
echo -e " \033[33magentsview\033[0m     review coding agent activity"
# Added by LM Studio CLI (lms)
export PATH="$PATH:/Users/jbakse/.cache/lm-studio/bin"
# End of LM Studio CLI section

