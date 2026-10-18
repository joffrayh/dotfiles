----------------------------------
-- MONITORS
----------------------------------
-- mirror any external to laptop
hl.monitor({ output = "HDMI-A-2", mode = "highres", position = "0x0", scale = 1, mirror = "eDP-1" })
-- laptop screen
hl.monitor({ output = "desc:Chimei Innolux Corporation 0x14C9", mode = "1920x1080@60", position = "0x0", scale = 1 })
-- extend home monitor
hl.monitor({ output = "desc:Hewlett Packard HP E232 3CQ61417SX", mode = "1920x1080@60", position = "0x-1080", scale = 1, transform = 0 })
-- hl.monitor({ output = "desc:Hewlett Packard HP E232 3CQ61417SX", mode = "1920x1080@60", position = "0x0", scale = 1, mirror = "eDP-1" })

----------------------------------
-- AUTOSTART & ENVIRONMENT
----------------------------------
hl.env("XCURSOR_SIZE", "24")

hl.on("hyprland.start", function()
    hl.exec_cmd("foot --server")
    hl.exec_cmd("hypridle")
    hl.exec_cmd("/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1")
    hl.exec_cmd("waybar")
    hl.exec_cmd("hyprpaper")
    hl.exec_cmd("swaync")
end)

----------------------------------
-- VARIABLES / CONFIGURATION
----------------------------------
hl.config({
    input = {
        kb_layout = "gb",
        kb_variant = "",
        kb_model = "",
        kb_options = "", -- "caps:swapescape"
        kb_rules = "",
        follow_mouse = 1,
        touchpad = {
            natural_scroll = true,
        },
        sensitivity = 0,
    },
    general = {
        gaps_in = 3,
        gaps_out = 6,
        border_size = 3,
        ["col.inactive_border"] = "rgba(000000dd)",
        ["col.active_border"] = "rgba(595959aa)",
        layout = "dwindle",
    },
    decoration = {
        rounding = 5,
        blur = {
            enabled = false,
        },
    },
    -- Animations are disabled, so no beziers/animation curves are needed.
    -- (In the new Lua API these are set via hl.curve()/hl.animation() anyway,
    -- not as tables inside hl.config — this is what was throwing errors before.)
    animations = {
        enabled = false,
    },
    dwindle = {
        preserve_split = false,
        force_split = 2,
    },
    gestures = {
        workspace_swipe_cancel_ratio = 0.2,
    },
    misc = {
        disable_hyprland_logo = true,
    },
})

-- Swipe gesture definition now has its own function
hl.gesture({
    fingers = 3,
    direction = "horizontal",
    action = "workspace",
})

----------------------------------
-- KEYBINDS
----------------------------------
local mainMod = "SUPER"

-- Mouse bind (disable middle-click paste)
hl.bind("mouse:274", hl.dsp.exec_cmd(";"))

-- System & Application Binds
hl.bind(mainMod .. " + Return", hl.dsp.exec_cmd("foot"))
hl.bind(mainMod .. " + space", hl.dsp.exec_cmd("pkill -x fuzzel || fuzzel"))
hl.bind(mainMod .. " + B", hl.dsp.exec_cmd("pkill -x waybar || waybar"))
hl.bind(mainMod .. " + W", hl.dsp.window.close())
hl.bind(mainMod .. " + V", hl.dsp.window.float({ action = "toggle" }))
hl.bind(mainMod .. " + P", hl.dsp.window.pseudo())
hl.bind(mainMod .. " + R", hl.dsp.layout("togglesplit")) -- dwindle only
hl.bind(mainMod .. " + F", hl.dsp.exec_cmd("nemo"))

-- Move focus (h, j, k, l)
hl.bind(mainMod .. " + h", hl.dsp.focus({ direction = "l" }))
hl.bind(mainMod .. " + l", hl.dsp.focus({ direction = "r" }))
hl.bind(mainMod .. " + k", hl.dsp.focus({ direction = "u" }))
hl.bind(mainMod .. " + j", hl.dsp.focus({ direction = "d" }))

-- Move active window (Shift + h, j, k, l)
hl.bind(mainMod .. " + SHIFT + h", hl.dsp.window.move({ direction = "l" }))
hl.bind(mainMod .. " + SHIFT + l", hl.dsp.window.move({ direction = "r" }))
hl.bind(mainMod .. " + SHIFT + k", hl.dsp.window.move({ direction = "u" }))
hl.bind(mainMod .. " + SHIFT + j", hl.dsp.window.move({ direction = "d" }))

-- Workspaces 1-10
local workspaces = { "1", "2", "3", "4", "5", "6", "7", "8", "9", "0" }
for i, key in ipairs(workspaces) do
    hl.bind(mainMod .. " + " .. key, hl.dsp.focus({ workspace = i }))
    hl.bind(mainMod .. " + SHIFT + " .. key, hl.dsp.window.move({ workspace = i }))
end

-- Mouse scroll workspaces & Window dragging
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up", hl.dsp.focus({ workspace = "e-1" }))
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- Media & System control keys
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+"), { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"), { locked = true, repeating = true })
hl.bind("XF86AudioMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"), { locked = true })
hl.bind("XF86AudioMicMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_SOURCE@ toggle"), { locked = true })
hl.bind("XF86AudioPlay", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioNext", hl.dsp.exec_cmd("playerctl next"), { locked = true })
hl.bind("XF86AudioPrev", hl.dsp.exec_cmd("playerctl previous"), { locked = true })
hl.bind("XF86MonBrightnessUp", hl.dsp.exec_cmd("brightnessctl s +5% -q"), { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("brightnessctl s 5%- -q"), { locked = true, repeating = true })

-- Screenshots
hl.bind("Print", hl.dsp.exec_cmd("grimblast save area - | wl-copy"))
hl.bind(mainMod .. " + Print", hl.dsp.exec_cmd("grimblast save active - | wl-copy"))

-- Notifications
hl.bind(mainMod .. " + M", hl.dsp.exec_cmd("swaync-client -t"))

-- Lock & Sleep
hl.bind(mainMod .. " + Escape", hl.dsp.exec_cmd("loginctl lock-session"))
hl.bind(mainMod .. " + S", hl.dsp.exec_cmd("systemctl suspend"))