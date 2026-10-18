# Lines configured by zsh-newuser-install
HISTFILE=~/.histfile
HISTSIZE=1000
SAVEHIST=1000
bindkey -e
# End of lines configured by zsh-newuser-install
# The following lines were added by compinstall
zstyle :compinstall filename '/home/joffray/.zshrc'

autoload -Uz compinit
compinit
# End of lines added by compinstall


# navigation
eval "$(zoxide init --cmd cd zsh)"
source /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'

# listing
alias l='exa --icons -l --group-directories-first'
alias ls='exa --icons --group-directories-first'
alias la='exa --icons -al --group-directories-first'
alias lt='exa --icons -T -L 2 --group-directories-first'
alias ldu='sudo du -hxd 1 ./ | sort -rh'


# file/folder management
alias rm='trash-put'
alias n="nvim" 
cc() { cd "$1" && code ./ }
alias imv='chafa'
alias extract='~/.config/scripts/extract.sh'


# git
alias g='git'
alias gst='git status'
alias ga='git add'
alias gaa='git add --all'
alias gp='git push'
alias gpl='git pull'
alias gc='git commit -m'
alias gco='git checkout'
alias gl='git log --oneline --graph --decorate'


# bluetooth
alias bt='bluetoothctl'
alias bts='bluetoothctl connect F8:DF:15:63:51:EB'
alias btsl='bluetoothctl connect AB:CD:EF:00:E7:A2'
alias btd='bluetoothctl disconnect'
alias bth='bluetoothctl connect 80:C3:BA:98:18:95'
alias bthk='bluetoothctl connect AC:80:0A:E7:58:5C'
alias btsr='bluetoothctl connect 17:1A:C1:88:ED:62'


# waybar and hyprland
alias chwaybar='~/.config/waybar/scripts/switch-waybar-config.sh'
alias chwall='~/.config/scripts/change-wallpaper.sh'
alias h='start-hyprland'


# vpn
alias vpnc='sudo openfortivpn remoteaccess.shef.ac.uk:443 --username=acd22jh'
alias vpnd='fortivpn disconnect'


# package management
remove() { paru -Rns "$@" && ~/.config/scripts/paru_cache_cleaner.sh; }
alias update='paru -Syu && ~/.config/scripts/paru_cache_cleaner.sh'
alias cleanall='sudo pacman -Scc --noconfirm && ~/.config/scripts/paru_cache_cleaner.sh' # full cache clean


#  monitoring
alias b='btop'
alias lb='~/.config/scripts/check_battery.sh'


# ssh connctions
alias sshup='ssh joffray@100.91.63.89'

# prettification
eval "$(starship init zsh)"
source /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
ZSH_HIGHLIGHT_STYLES[suffix-alias]=fg=#909CB0,bold
ZSH_HIGHLIGHT_STYLES[precommand]=fg=#909CB0,bold
ZSH_HIGHLIGHT_STYLES[arg0]=fg=#909CB0,bold
ZSH_HIGHLIGHT_STYLES[unknown-token]=fg=#f4a261,bold

# --- Key bindings (Home/End/Delete/Ctrl+arrows/Ctrl+Backspace/Ctrl+Delete) ---
typeset -g -A key
key[Home]="${terminfo[khome]}"
key[End]="${terminfo[kend]}"
key[Delete]="${terminfo[kdch1]}"
key[Control-Left]="${terminfo[kLFT5]}"
key[Control-Right]="${terminfo[kRIT5]}"

[[ -n "${key[Home]}"          ]] && bindkey -- "${key[Home]}"          beginning-of-line
[[ -n "${key[End]}"           ]] && bindkey -- "${key[End]}"           end-of-line
[[ -n "${key[Delete]}"        ]] && bindkey -- "${key[Delete]}"        delete-char
[[ -n "${key[Control-Left]}"  ]] && bindkey -- "${key[Control-Left]}"  backward-word
[[ -n "${key[Control-Right]}" ]] && bindkey -- "${key[Control-Right]}" forward-word
bindkey '^H'      backward-kill-word   # Ctrl+Backspace
bindkey '^[[3;5~' kill-word            # Ctrl+Delete

if (( ${+terminfo[smkx]} && ${+terminfo[rmkx]} )); then
  autoload -Uz add-zle-hook-widget
  function zle_application_mode_start { echoti smkx }
  function zle_application_mode_stop  { echoti rmkx }
  add-zle-hook-widget -Uz zle-line-init   zle_application_mode_start
  add-zle-hook-widget -Uz zle-line-finish zle_application_mode_stop
fi
