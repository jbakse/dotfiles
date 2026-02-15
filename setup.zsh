# this isn't intended to be run as a script. 
exit

# this is intended as notes for steps to run on the command line

# install Xcode command line tools 
# trying to run any tool in the cli tools will trigger install
git 
    
# install Nix with Determinate
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
    
# install Devbox
curl -fsSL https://get.jetify.com/devbox | bash
    
#  install Oh My Zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

# set up sym links
ln -sf ~/dotfiles/devbox.json ~/.local/share/devbox/global/default/devbox.json
ln -sf ~/dotfiles/.zshrc ~/.zshrc
ln -sf ~/dotfiles/.gitconfig ~/.gitconfig

# install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
# install Apps with Homebrew
cd dotfiles
brew bundle install 



