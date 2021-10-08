import threading
import time

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject, GLib, Gio

print(str(Gtk.get_major_version()) + "." + str(Gtk.get_minor_version()) + "." + str(Gtk.get_micro_version()))
cards = 0


@Gtk.Template(filename="carditem_template.glade")
class CardItem(Gtk.Box):
    __gtype_name__ = "carditem"

    def __init__(self):
        Gtk.Box.__init__(self)

    carditemremove: Gtk.Button = Gtk.Template.Child()

    @Gtk.Template.Callback()
    def carditemremove_clicked_cb(self, button):
        global cards
        cards -= 1
        print("Removed card")
        print(str(cards))
        self.destroy()
        print(self.get_children())

    @Gtk.Template.Callback()
    def carditem_add_cb(self, button):
        global cards
        cards += 1
        print("Added card")
        print(str(cards))


class Handler:
    def on_window1_destroy(self, object, data=None):
        print("Quit with cancel")
        Gtk.main_quit()

    def on_gtk_quit_activate(self, menuitem, data=None):
        print("Quit from menu")
        Gtk.main_quit()

    def on_findbutton_clicked(self, data=None):
        pass
    #     print("Find")
    #     self.timer = threading.Thread(target=self.update_window_title)
    #     self.event = threading.Event()
    #     self.timer.daemon = True
    #     self.timer.start()
    #
    # def on_yourcardsadd_clicked(self, data=None):
    #     print("Stop")
    #     self.event.set()
    #     self.timer = None
    def on_yourcardsadd_clicked(self, data=None):
        # self.builder.extend_with_template(self.gladefile, "carditem")
        # self.carditem = self.builder.get_object("carditem")
        # self.carditem.unparent()
        self.newcard = CardItem()
        self.yourcardlist.pack_end(self.newcard, False, True, 0)

    #
    # def update_window_title(self):
    #     i = 0
    #     while not self.event.is_set():
    #         i += 1
    #         self.window.set_title(str(i))
    #         time.sleep(2)

    def __init__(self):
        self.gladefile = "neonmobmatcher.glade"
        self.builder = Gtk.Builder()
        # self.repeatbuilder = Gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        # self.repeatbuilder.add_objects_from_file(self.gladefile, "carditem")
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("window1")
        self.window.show()
        self.yourcardlist = self.builder.get_object("yourcardlist")


if __name__ == '__main__':
    main = Handler()
    Gtk.main()
