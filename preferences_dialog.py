#!/usr/bin/env python3
# coding: utf8

"""
Модуль диалога настроек и работа с файлом настроек
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class PreferencesDialog(Gtk.Window):
    """
    Диалог настроек
    """
    def __init__(self, parent, PBR_Pref, SD_client):
        self.PBR_Pref = PBR_Pref
        self.SD_client = SD_client
        self.main_win = parent
        Gtk.Window.__init__(self, title = "Настройки")
        self.connect("destroy", self.exit_pref_win)

        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        # Вкладка с настройками внешнего вида
        #=====================================================================
        self.page_view = Gtk.Grid()
        self.page_view.set_border_width(10)
        label_view_pref = Gtk.Label('Настройка интерфейса:')
        self.page_view.add(label_view_pref)
        check_tool_text = Gtk.CheckButton("Подписать кнопки управления")
        check_tool_text.set_active(True)
        check_tool_text.connect("toggled", self.on_check_tool_text_toggled)
        self.page_view.attach_next_to(check_tool_text,label_view_pref,
                                      Gtk.PositionType.BOTTOM,1,1)
        self.notebook.append_page(self.page_view, Gtk.Label('Внешний вид'))
        #=====================================================================

        # Вкладка с настройками параметров чтения
        #=====================================================================
        self.page_voice = Gtk.Grid()
        self.page_voice.set_border_width(10)

        label_voice_pref = Gtk.Label('Настройка параметров чтения:')
        self.page_voice.add(label_voice_pref)

        label_choose_voice = Gtk.Label('Голос для чтения:')
        self.page_voice.attach_next_to(label_choose_voice, label_voice_pref,
                                       Gtk.PositionType.BOTTOM, 1, 1)
        combo_voice = Gtk.ComboBoxText()
        # заполняем комбобокс и устанавливаем текущий голос в нём
        i = 0
        for voice in self.PBR_Pref.list_of_voices:
            combo_voice.append(str(i), voice)
            if voice == self.PBR_Pref.current_voice:
                combo_voice.set_active(i)
            i +=1
        self.page_voice.attach_next_to(combo_voice, label_choose_voice,
                                       Gtk.PositionType.RIGHT, 1, 1)
        combo_voice.connect("changed", self.on_combo_voice_changed)

        label_indent_delay = Gtk.Label('Задержка между абзацами, мс:')
        self.page_voice.attach_next_to(label_indent_delay,
                                       label_choose_voice,
                                       Gtk.PositionType.BOTTOM, 1, 1)
        spin_indent_delay = Gtk.SpinButton.new_with_range(0, 2000, 1)
        spin_indent_delay.set_value(self.PBR_Pref.indent_delay)
        self.page_voice.attach_next_to(spin_indent_delay,
                                       label_indent_delay,
                                       Gtk.PositionType.RIGHT, 1, 1)
        spin_indent_delay.connect("changed",
                                  self.on_spin_indent_delay_changed)

        label_sentance_delay = Gtk.Label('Задержка между предложениями, мс:')
        self.page_voice.attach_next_to(label_sentance_delay,
                                       label_indent_delay,
                                       Gtk.PositionType.BOTTOM, 1, 1)
        spin_sentance_delay = Gtk.SpinButton.new_with_range(0, 2000, 1)
        spin_sentance_delay.set_value(self.PBR_Pref.sentance_delay)
        self.page_voice.attach_next_to(spin_sentance_delay,
                                       label_sentance_delay,
                                       Gtk.PositionType.RIGHT, 1, 1)
        spin_sentance_delay.connect("changed",
                                    self.on_spin_sentance_delay_changed)

        self.notebook.append_page(self.page_voice, Gtk.Label('Синтезатор'))
        #=====================================================================

        # Вкладка с настройками гарячих клавиш
        #=====================================================================
        # TODO: добавить таблицу со списком действий
        self.page_keys = Gtk.Box()
        self.page_keys.set_border_width(10)
        self.page_keys.add(Gtk.Label('Настройка горячих клавиш:'))
        self.notebook.append_page(self.page_keys,
                                  Gtk.Label('Сочетания клавиш'))
        #=====================================================================

        self.show_all()

    def exit_pref_win(self, data=None):
        """ Выход из диалога """
        self.destroy()

    def on_combo_voice_changed(self, combo):
        """ Изменение голоса """
        combo_text = combo.get_active_text()
        if combo_text != None:
            self.SD_client.set_voice(combo_text)

    def on_check_tool_text_toggled(self, widget):
        """ Включение / отключение подписывания кнопок в панели управления """
        # получаем ссылку на панель управления
        toolbar = self.main_win.grid.get_child_at(0,1)
        # включаем или отключаем текс у значков
        if widget.get_active() == True and toolbar != None:
            toolbar.set_style(2)
        else:
            toolbar.set_style(0)

    def on_spin_indent_delay_changed(self, widget):
        """ Изменение задержки для абзаца """
        self.PBR_Pref.indent_delay = widget.get_value_as_int()

    def on_spin_sentance_delay_changed(self, widget):
        """ Изменение задержки для предложения """
        self.PBR_Pref.sentance_delay = widget.get_value_as_int()

class Preferences():
    """
    Обработка настроек (хранение, чтение, запись)
    TODO: добавить работу с файлом настроек
    """
    def __init__(self, SD_client):
        """ Инициализация настроек """
        # клиент speech-dispatcher для получения списка голосов
        self.SD_client = SD_client
        self.list_of_voices = self.SD_client.get_voices_list()
        self.current_voice = self.get_current_voice()
        # значения задержек для абзаца и предложения
        self.indent_delay = self.get_indent_delay()
        self.sentance_delay = self.get_sentance_delay()

        # Устанавливаем текущий голос
        self.SD_client.set_voice(self.current_voice)

    def  get_current_voice(self):
        """ Получаем текущий голос из conf файла """
        voice = 'Aleksandr+Alan'
        return voice

    def  get_indent_delay(self):
        """ Получаем задержку чтения между абзацами из conf файла"""
        return 400

    def  get_sentance_delay(self):
        """ Получаем задержку чтения между предложениями из conf файла """
        return 200
