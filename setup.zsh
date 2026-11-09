# this isn't intended to be run as a script. 
exit

# this is intended as notes for steps to run on the command line

# install Xcode command line tools 
# trying to run any tool in the cli tools will trigger install
git 
    
# install Nix with Determinate
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
    
# install Devbox (no Homebrew package; needs Nix from above)
# update later with: devbox version update
curl -fsSL https://get.jetify.com/devbox | bash
    
#  install Oh My Zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

# set up sym links
mkdir -p ~/.local/share/devbox/global/default
ln -sf ~/dotfiles/devbox.json ~/.local/share/devbox/global/default/devbox.json
ln -sf ~/dotfiles/.zshrc ~/.zshrc
ln -sf ~/dotfiles/.gitconfig ~/.gitconfig
ln -sf ~/dotfiles/finicky.js ~/.finicky.js
# ~/.npmrc is NOT linked: it holds the npm auth token and must stay out of this
# public repo. `npm login` creates it. The npm prefix is set in .zshrc instead.

# install devbox global packages (no lock in dotfiles; gets latest)
devbox global install

# install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
# install Apps with Homebrew
cd dotfiles
brew bundle install

# install global npm tools (node comes from devbox; prefix set by NPM_CONFIG_PREFIX in .zshrc)
# claude code lives here instead of devbox so it can auto-update
npm install -g @anthropic-ai/claude-code



