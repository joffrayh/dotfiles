#!/usr/bin/env python3
"""Windows 2000 style calendar popup for the taskbar clock.

Run once to open it above the clock on the monitor under the cursor;
run again (click the clock again) to close it. Esc or OK also close it.
Scroll over the calendar to flip months.
"""
import calendar as cal
import datetime
import json
import os
import signal
import subprocess
import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gdk, GLib, Gtk, GtkLayerShell  # noqa: E402

PIDFILE = os.path.join(os.environ.get("XDG_RUNTIME_DIR", "/tmp"), "waybar-calpopup.pid")

# How far you have to scroll to flip one month. A mouse wheel notch is 1.0;
# raise these to make scrolling less sensitive.
SCROLL_PER_MONTH = 1.0
TOUCHPAD_SCROLL_PER_MONTH = 6.0

CSS = b"""
* {
    font-family: "Liberation Sans", sans-serif;
    font-size: 18px;
    color: #000000;
    border-radius: 0;
    text-shadow: none;
    -gtk-icon-shadow: none;
    box-shadow: none;
}

/* Raised window frame */
#frame {
    background: #d4d0c8;
    border-style: solid;
    border-width: 1px;
    border-color: #d4d0c8 #404040 #404040 #d4d0c8;
    box-shadow: inset 1px 1px #ffffff, inset -1px -1px #808080;
    padding: 3px;
}

/* Active title bar gradient */
#titlebar {
    background-image: linear-gradient(to right, #0a246a, #a6caf0);
    padding: 2px 2px 2px 6px;
}
#titlebar label {
    color: #ffffff;
    font-weight: bold;
}

/* Raised push buttons */
button {
    background: #d4d0c8;
    background-image: none;
    border-style: solid;
    border-width: 1px;
    border-color: #ffffff #404040 #404040 #ffffff;
    box-shadow: inset -1px -1px #808080;
    padding: 2px 14px;
    min-height: 0;
    outline: none;
}
button:hover {
    background: #d4d0c8;
}
button:active, button:checked {
    border-color: #404040 #ffffff #ffffff #404040;
    box-shadow: inset 1px 1px #808080;
}
#close {
    padding: 0 5px;
    min-width: 0;
}
#close label {
    font-size: 14px;
    font-weight: bold;
}

/* "Date" group box */
frame > border {
    border-style: solid;
    border-width: 1px;
    border-color: #808080 #ffffff #ffffff #808080;
}
frame > label {
    padding: 0 3px;
}

/* Sunken fields: month combo, year spin, calendar */
combobox button, spinbutton {
    background: #ffffff;
    border-style: solid;
    border-width: 1px;
    border-color: #808080 #ffffff #ffffff #808080;
    box-shadow: inset 1px 1px #404040;
}
combobox button {
    padding: 1px 4px;
}
spinbutton entry, spinbutton text {
    background: #ffffff;
    border: none;
    box-shadow: none;
    padding: 1px 4px;
    min-height: 0;
}
spinbutton button {
    background: #d4d0c8;
    border-color: #ffffff #404040 #404040 #ffffff;
    box-shadow: inset -1px -1px #808080;
    padding: 0 4px;
    min-width: 0;
}
menu, .menu, menuitem {
    background: #ffffff;
    padding: 1px 6px;
}
menuitem:hover {
    background: #0a246a;
}
menuitem:hover label {
    color: #ffffff;
}

#calwell {
    background: #ffffff;
    border-style: solid;
    border-width: 1px;
    border-color: #808080 #ffffff #ffffff #808080;
    box-shadow: inset 1px 1px #404040;
    padding: 2px;
}
calendar {
    background: #ffffff;
    border: none;
    padding: 2px;
}
calendar.header {
    border: none;
}
calendar.highlight {
    /* weekday names row */
    background: #808080;
    color: #ffffff;
    font-weight: bold;
}
calendar:selected {
    background: #0a246a;
    color: #ffffff;
}
calendar:indeterminate {
    color: #a0a0a0;
}

#clock {
    padding: 2px 0;
}
"""


def toggle_existing():
    """If a popup is already open, close it and return True."""
    try:
        with open(PIDFILE) as f:
            pid = int(f.read().strip())
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            if b"calpopup.py" not in f.read():
                return False
        os.kill(pid, signal.SIGTERM)
        return True
    except (OSError, ValueError):
        return False


def cursor_monitor():
    """Return the Gdk.Monitor under the mouse pointer (where the clock was clicked)."""
    display = Gdk.Display.get_default()
    try:
        pos = subprocess.run(["hyprctl", "cursorpos", "-j"], capture_output=True, text=True, timeout=1)
        p = json.loads(pos.stdout)
        x, y = p["x"], p["y"]
    except Exception:
        return None
    for i in range(display.get_n_monitors()):
        m = display.get_monitor(i)
        g = m.get_geometry()
        if g.x <= x < g.x + g.width and g.y <= y < g.y + g.height:
            return m
    return None


class CalendarPopup(Gtk.Window):
    def __init__(self):
        super().__init__(title="Date/Time Properties")
        self.today = datetime.date.today()

        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_namespace(self, "waybar-calendar")
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, 2)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT, 2)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)
        monitor = cursor_monitor()
        if monitor is not None:
            GtkLayerShell.set_monitor(self, monitor)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, name="frame")
        self.add(outer)

        # Title bar
        titlebar = Gtk.Box(spacing=4, name="titlebar")
        titlebar.pack_start(Gtk.Label(label="Date/Time Properties", xalign=0), True, True, 0)
        close = Gtk.Button(label="✕", name="close")
        close.connect("clicked", lambda *_: self.close())
        titlebar.pack_end(close, False, False, 0)
        outer.pack_start(titlebar, False, False, 0)

        # "Date" group box
        group = Gtk.Frame(label="Date")
        group.set_margin_start(6)
        group.set_margin_end(6)
        outer.pack_start(group, False, False, 0)

        inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        inner.set_border_width(10)
        group.add(inner)

        # Month combo + year spinner
        pickers = Gtk.Box(spacing=8)
        self.month = Gtk.ComboBoxText()
        for name in cal.month_name[1:]:
            self.month.append_text(name)
        self.year = Gtk.SpinButton.new_with_range(1900, 2999, 1)
        self.year.set_numeric(True)
        self.year.set_width_chars(4)
        pickers.pack_start(self.month, True, True, 0)
        pickers.pack_start(self.year, False, False, 0)
        inner.pack_start(pickers, False, False, 0)

        # Calendar grid in a sunken white well
        well = Gtk.EventBox(name="calwell")
        self.calendar = Gtk.Calendar()
        self.calendar.set_display_options(Gtk.CalendarDisplayOptions.SHOW_DAY_NAMES)
        well.add(self.calendar)
        inner.pack_start(well, False, False, 0)

        self.clock = Gtk.Label(name="clock")
        inner.pack_start(self.clock, False, False, 0)

        # Bottom buttons
        buttons = Gtk.Box(spacing=6)
        buttons.set_margin_start(6)
        buttons.set_margin_end(6)
        buttons.set_margin_bottom(4)
        ok = Gtk.Button(label="OK")
        ok.connect("clicked", lambda *_: self.close())
        today = Gtk.Button(label="Today")
        today.connect("clicked", lambda *_: self.go_to(self.today.year, self.today.month, self.today.day))
        buttons.pack_end(ok, False, False, 0)
        buttons.pack_end(today, False, False, 0)
        outer.pack_start(buttons, False, False, 0)

        self._syncing = False
        self._scroll_acc = 0.0
        self.month.connect("changed", self.on_picker_changed)
        self.year.connect("value-changed", self.on_picker_changed)
        self.calendar.connect("month-changed", self.on_calendar_changed)
        self.calendar.add_events(Gdk.EventMask.SCROLL_MASK | Gdk.EventMask.SMOOTH_SCROLL_MASK)
        self.calendar.connect("scroll-event", self.on_scroll)
        self.connect("key-press-event", self.on_key)
        self.connect("destroy", Gtk.main_quit)

        self.go_to(self.today.year, self.today.month, self.today.day)
        self.tick()
        GLib.timeout_add_seconds(1, self.tick)

    def go_to(self, year, month, day=None):
        if day is None:
            day = min(self.calendar.get_date().day, cal.monthrange(year, month)[1])
        self.calendar.select_month(month - 1, year)
        self.calendar.select_day(day)
        self.on_calendar_changed()

    def on_calendar_changed(self, *_):
        y, m, _d = self.calendar.get_date()
        self._syncing = True
        self.month.set_active(m)
        self.year.set_value(y)
        self._syncing = False
        # Bold today's date while it's on screen
        self.calendar.clear_marks()
        if (y, m + 1) == (self.today.year, self.today.month):
            self.calendar.mark_day(self.today.day)

    def on_picker_changed(self, *_):
        if self._syncing or self.month.get_active() < 0:
            return
        self.go_to(self.year.get_value_as_int(), self.month.get_active() + 1)

    def on_scroll(self, _widget, event):
        if event.direction == Gdk.ScrollDirection.SMOOTH:
            if event.is_stop:
                self._scroll_acc = 0.0
                return True
            device = event.get_source_device()
            touchpad = device is not None and device.get_source() == Gdk.InputSource.TOUCHPAD
            threshold = TOUCHPAD_SCROLL_PER_MONTH if touchpad else SCROLL_PER_MONTH
            # Start fresh when the scroll direction reverses
            if self._scroll_acc * event.delta_y < 0:
                self._scroll_acc = 0.0
            self._scroll_acc += event.delta_y
            step = int(self._scroll_acc / threshold)
            self._scroll_acc -= step * threshold
        else:
            step = {Gdk.ScrollDirection.DOWN: 1, Gdk.ScrollDirection.UP: -1}.get(event.direction, 0)
        if step:
            y, m, _d = self.calendar.get_date()
            total = y * 12 + m + step
            self.go_to(total // 12, total % 12 + 1)
        return True

    def on_key(self, _widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()
            return True
        return False

    def tick(self):
        now = datetime.datetime.now()
        if now.date() != self.today:
            self.today = now.date()
            self.on_calendar_changed()
        ampm = "AM" if now.hour < 12 else "PM"
        self.clock.set_text(now.strftime(f"%A, %-d %B %Y   %-I:%M:%S {ampm}"))
        return True


def main():
    if toggle_existing():
        return
    with open(PIDFILE, "w") as f:
        f.write(str(os.getpid()))

    try:
        gi.require_version("GLibUnix", "2.0")
        from gi.repository import GLibUnix
        GLibUnix.signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, Gtk.main_quit)
    except (ImportError, ValueError):
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, Gtk.main_quit)

    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
    )

    win = CalendarPopup()
    win.show_all()
    try:
        Gtk.main()
    finally:
        try:
            os.remove(PIDFILE)
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())
