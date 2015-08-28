import ctypes
import os
import tempfile
import threading
import wx
from PIL import Image, ImageFont, ImageDraw
from time import sleep, strftime

TRAY_TOOLTIP = 'Hexclock'
TRAY_ICON = 'assets/icon.png'
BRIGHT_COLORS = True

###############################################################################


def hexclock():
    global BRIGHT_COLORS
    tmpdir = tempfile.gettempdir()
    filename = "hexclock.jpg"
    full_path = os.path.join(tmpdir, filename)
    user32 = ctypes.windll.user32
    desktop_res = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    # desktop_res = (1920, 1080)

    while True:
        try:
            timestr = strftime("%H%M%S")
            if BRIGHT_COLORS:
                hours = int(float(timestr[:2])*10.625)
                mins = int(float(timestr[2:4])*4.25)
                secs = int(float(timestr[4:6])*4.25)
            else:
                hours = int(timestr[:2], 16)
                mins = int(timestr[2:4], 16)
                secs = int(timestr[4:6], 16)

            color = (hours, mins, secs, 255)
            print "[%s]" % strftime("%H:%M:%S"), color, BRIGHT_COLORS

            img = Image.new(mode="RGBA", size=desktop_res, color=color)
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("assets/Lato-Thin.ttf", 68)
            # font =  ImageFont.truetype("Roboto-Thin.ttf", 70)
            # draw.text((818, 450), "#"+timestr, (255, 255, 255), font=font)

            w, h = draw.textsize("#"+timestr, font=font)
            vert_offset = 50  # text looks too far down without offset

            text_pos = ((desktop_res[0]-w)/2, ((desktop_res[1]-h)/2)-vert_offset)
            draw.text(text_pos, "#"+timestr, (255, 255, 255), font=font)
            img.save(full_path, "JPEG", quality=100)

            SPI_SETDESKWALLPAPER = 20
            ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, full_path, 0)

            while timestr == strftime("%H%M%S"):
                sleep(0.1)

        except KeyboardInterrupt:
            print "Exiting.."
            break

###############################################################################


class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self):
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def create_menu_item(self, menu, label, func):
        item = wx.MenuItem(menu, -1, label)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        menu.AppendItem(item)
        return item

    def CreatePopupMenu(self):
        menu = wx.Menu()
        self.create_menu_item(menu, 'Bright colors', self.bright_colors)
        self.create_menu_item(menu, 'Literal colors', self.literal_colors)
        menu.AppendSeparator()
        self.create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_left_down(self, event):
        print 'Tray icon was left-clicked.'

    def bright_colors(self, event):
        global BRIGHT_COLORS
        print 'Switching to bright colors'
        BRIGHT_COLORS = True

    def literal_colors(self, event):
        global BRIGHT_COLORS
        print 'Switching to literal colors'
        BRIGHT_COLORS = False

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)

###############################################################################


def main():
    app = wx.App()
    TaskBarIcon()

    t = threading.Thread(target=hexclock)
    t.setDaemon(1)
    t.start()

    app.MainLoop()

###############################################################################

if __name__ == '__main__':
    main()
