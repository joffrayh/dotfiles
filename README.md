# dotfiles

My Arch + Hyprland setup, managed with [GNU Stow](https://www.gnu.org/software/stow/).

Each top-level folder (except `packages/` and `system/`) is a stow package laid out
like `$HOME`, e.g. `hypr/.config/hypr/hyprland.lua` → `~/.config/hypr/hyprland.lua`.
The files in `~` are symlinks into this repo, so editing a config edits the repo.

## New machine

```sh
sudo pacman -S --needed git stow
git clone git@github.com:<you>/dotfiles.git ~/dotfiles
~/dotfiles/install.sh
```

`install.sh` installs packages (official, AUR via paru, optional hardware set),
stows every package, optionally copies `system/` into `/etc`, symlinks the keyd
config into `/etc/keyd`, enables services, installs VS Code extensions and sets
zsh as the login shell. It asks before the hardware packages and `/etc` files.

## Day to day

| Task | Command |
|---|---|
| Save config changes | `cd ~/dotfiles && git add -A && git commit -m "..." && git push` |
| Refresh package lists | `./update-lists.sh`, then commit |
| Track a new app's config | `mkdir -p foo/.config && mv ~/.config/foo foo/.config/ && stow foo`, then add `foo` to `STOW_PACKAGES` in `install.sh` |
| Stop tracking one | `stow -D foo` (removes the symlinks; copy the files back first if you still want them) |

## Layout

| Folder | What |
|---|---|
| `hypr` | Hyprland (Lua config), hypridle, hyprlock, hyprpaper, wallpapers, lock-screen generator |
| `waybar` | Bar + themes in `configs/`. `chwaybar` switches theme by repointing `config` and `style.css` |
| `zsh`, `starship`, `foot`, `fuzzel`, `swaync`, `btop` | Shell, prompt, terminal, launcher, notifications, monitor |
| `keyd` | Caps Lock nav layer and bracket chords (linked into `/etc/keyd`) |
| `theme` | GTK 2/3/4, nwg-look, xsettingsd, Nerd Font |
| `scripts` | `~/.config/scripts` (extract, wallpaper switcher, paru cache cleaner, battery) |
| `nvim`, `zed`, `vscode` | Editors (VS Code extensions are in `packages/vscode-extensions.txt`) |
| `git`, `mime`, `neofetch`, `oculante` | Misc |
| `packages/` | `pacman.txt`, `aur.txt`, `hardware.txt` (Intel/ThinkPad only), `services.txt` |
| `system/` | Reference copies of edited `/etc` files: pacman, paru, reflector, TLP, GRUB, locale |

## Per-machine notes

- **Monitors** are hardcoded for a ThinkPad T470 + HP E232 in `hyprland.lua`.
- **TLP** charge thresholds in `system/etc/tlp.conf` assume a ThinkPad with BAT0/BAT1.
- **Lock screen** image is drawn for 1920x1080; regenerate with `make-lock.py WIDTH HEIGHT`.
- **PostgreSQL** isn't auto-enabled; run `initdb` first (see `packages/services.txt`).
- GTK bookmarks aren't tracked (they need absolute `file://` paths).
