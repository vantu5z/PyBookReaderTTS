#!/usr/bin/env python3
# coding: utf8

"""
Модуль диалога поиска
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class SearchDialog(Gtk.Dialog):
    """
    Диалог поиска
    TODO: добавить функциональности
    """
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Поиск", parent,
                            Gtk.DialogFlags.MODAL, buttons=(
                            Gtk.STOCK_FIND, Gtk.ResponseType.OK,
                            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))

        box = self.get_content_area()

        label = Gtk.Label("Введите текст для поиска:")
        box.add(label)

        self.entry = Gtk.Entry()
        box.add(self.entry)

        self.show_all()
    
    def get_search_text(self):
        """ Текст для поиска """
        return self.entry.get_text()
