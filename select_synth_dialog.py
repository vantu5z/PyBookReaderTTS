#!/usr/bin/env python3
# coding: utf8

"""
Модуль диалога выбора синтезатора
Выводится, если не выбран текущий синтезатор
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class SelectSynthDialog(Gtk.Dialog):
    def __init__(self, PBR_Pref):
        Gtk.Dialog.__init__(self, "Выбор синтезатора", None,
                            Gtk.DialogFlags.MODAL, buttons=(
                            Gtk.STOCK_OK, Gtk.ResponseType.OK,
                            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))

        box = self.get_content_area()

        label = Gtk.Label("Для продолжения необходимо выбрать синтезатор")
        box.add(label)

        self.combo_synth = Gtk.ComboBoxText()
        # заполняем комбобокс и устанавливаем текущий синтезатор в нём
        i = 0
        for synth in PBR_Pref.list_of_synth:
            self.combo_synth.append(str(i), synth[1])
            i +=1
        box.add(self.combo_synth)

        self.show_all()

    def get_synth(self):
        """ Возвращает название выбранного синтезатора потребителю """
        synth = self.combo_synth.get_active_text()
        return synth
