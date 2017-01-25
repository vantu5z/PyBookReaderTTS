#!/usr/bin/env python3
# coding: utf8

"""
Модуль диалога настроек и работа с файлом настроек
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import configparser
import os

# модули программы
# для чтения настроек синтезаторов
import synth_conf.conf_parse as CP

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
        # начальное значение
        check_tool_text.set_active(self.PBR_Pref.labels_for_toolbuttons)
        check_tool_text.connect("toggled", self.on_check_tool_text_toggled)
        self.page_view.attach_next_to(check_tool_text,label_view_pref,
                                      Gtk.PositionType.BOTTOM,1,1)
        self.notebook.append_page(self.page_view, Gtk.Label('Внешний вид'))
        # показываем или прячем текст (взависимости от настройки)
        self.on_check_tool_text_toggled(check_tool_text)
        #=====================================================================

        # Вкладка с выбором синтезатора и настройками параметров чтения
        #=====================================================================
        self.page_voice = Gtk.Grid()
        self.page_voice.set_border_width(10)

        label_choose_synth = Gtk.Label('Синтезатор:')
        self.page_voice.add(label_choose_synth)
        combo_synth = Gtk.ComboBoxText()
        # заполняем комбобокс и устанавливаем текущий синтезатор в нём
        i = 0
        for synth in self.PBR_Pref.list_of_synth:
            combo_synth.append(str(i), synth[1])
            if synth[1] == self.PBR_Pref.current_synth:
                combo_synth.set_active(i)
            i +=1
        self.page_voice.attach_next_to(combo_synth, label_choose_synth,
                                       Gtk.PositionType.RIGHT, 1, 1)
        combo_synth.connect("changed", self.on_combo_synth_changed)

        self.note = Gtk.Label('Примечание: ' + self.SD_client.get_synth_note())
        self.page_voice.attach_next_to(self.note, label_choose_synth,
                                       Gtk.PositionType.BOTTOM, 1, 1)

        separator = Gtk.Separator.new(0)
        self.page_voice.attach_next_to(separator, self.note,
                                       Gtk.PositionType.BOTTOM, 2, 1)

        label_voice_pref = Gtk.Label('Настройка параметров чтения:')
        self.page_voice.attach_next_to(label_voice_pref, separator,
                                       Gtk.PositionType.BOTTOM, 1, 1)

        label_choose_voice = Gtk.Label('Голос для чтения:')
        self.page_voice.attach_next_to(label_choose_voice, label_voice_pref,
                                       Gtk.PositionType.BOTTOM, 1, 1)
        self.combo_voice = Gtk.ComboBoxText()
        self.page_voice.attach_next_to(self.combo_voice, label_choose_voice,
                                       Gtk.PositionType.RIGHT, 1, 1)
        self.combo_voice.connect("changed", self.on_combo_voice_changed)
        # заполняем комбобокс и устанавливаем текущий голос в нём
        self.upd_voices_combo()

        label_indent_delay = Gtk.Label('Задержка между абзацами, мс:')
        self.page_voice.attach_next_to(label_indent_delay,
                                       label_choose_voice,
                                       Gtk.PositionType.BOTTOM, 1, 1)
        spin_indent_delay = Gtk.SpinButton.new_with_range(0, 2000, 1)
        spin_indent_delay.set_value(self.PBR_Pref.indent_delay)
        self.page_voice.attach_next_to(spin_indent_delay,
                                       label_indent_delay,
                                       Gtk.PositionType.RIGHT, 1, 1)
        spin_indent_delay.set_tooltip_markup('Задержка перед абзацем в миллисекундах')
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
        spin_sentance_delay.set_tooltip_markup('Задержка перед предложением в миллисекундах')
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

    def on_combo_synth_changed(self, combo):
        """ Переключение синтезатора """
        self.SD_client.change_synth_conf(
                    self.PBR_Pref.get_synth_filename(combo.get_active_text()))
        self.PBR_Pref.current_synth = combo.get_active_text()
        self.upd_voices_combo()
        self.update_note()

    def on_combo_voice_changed(self, combo):
        """ Изменение голоса """
        combo_text = combo.get_active_text()
        if combo_text != None:
            self.SD_client.set_voice(combo_text)

    def on_check_tool_text_toggled(self, widget):
        """ Включение / отключение подписывания кнопок в панели управления """
        if widget.get_active() == True and self.main_win.toolbar != None:
            self.main_win.toolbar.set_style(2)
            self.PBR_Pref.labels_for_toolbuttons = True
        else:
            self.main_win.toolbar.set_style(0)
            self.PBR_Pref.labels_for_toolbuttons = False

    def on_spin_indent_delay_changed(self, widget):
        """ Изменение задержки для абзаца """
        self.PBR_Pref.indent_delay = widget.get_value_as_int()

    def on_spin_sentance_delay_changed(self, widget):
        """ Изменение задержки для предложения """
        self.PBR_Pref.sentance_delay = widget.get_value_as_int()

    def upd_voices_combo(self):
        """ Заполнение выпадающего меню голосами """
        i = 0
        self.combo_voice.remove_all()
        for voice in self.SD_client.get_voices_list():
            self.combo_voice.append(str(i), voice)
            if voice == self.SD_client.get_current_voice():
                self.combo_voice.set_active(i)
            i +=1

    def update_note(self):
        """ Обновление примечания """
        if self.SD_client.get_synth_note() != '':
            self.note.set_text("Примечание: " + self.SD_client.get_synth_note())
            self.note.show()
        else:
            self.note.hide()

    def exit_pref_win(self, data=None):
        """ Выход из диалога настроек """
        # сохраняем настройки и выходим
        self.PBR_Pref.save_settings()
        self.destroy()

class Preferences(object):
    """
    Обработка настроек (хранение, чтение, запись)
    """
    def __init__(self):
        """ Инициализация настроек """
        # открываем файл конфигурации или создаём новый, если его нет
        self.config = configparser.ConfigParser()
        if not os.path.exists('pbr.conf'):
            self.set_default_conf()
        self.config.read('pbr.conf')
        self.settings = self.config['Settings']

        # значения задержек для абзаца и предложения
        self.indent_delay = self.get_indent_delay()
        self.sentance_delay = self.get_sentance_delay()
        # показывать ли текст у кнопок на панели
        self.labels_for_toolbuttons = self.get_labels_for_toolbuttons()

        # список доступных синтезаторов
        self.list_of_synth = self.get_list_of_synth()
        # текущий синтезатор
        self.current_synth = self.get_current_synth()

    def set_default_conf(self):
        """ Установка настроек по умолчанию """
        self.config['Settings'] = {'indent_delay': '400',
                                   'sentance_delay': '200', 
                                   'labels_for_toolbuttons': 'True', 
                                   'current_synth': ''}
        with open('pbr.conf', 'w') as configfile:
            self.config.write(configfile)

    def save_settings(self):
        """ Сохранение настроек в файл """
        self.config['Settings'] = {'indent_delay': self.indent_delay,
                                   'sentance_delay': self.sentance_delay,
                                   'labels_for_toolbuttons': self.labels_for_toolbuttons,
                                    'current_synth': self.current_synth}
        with open('pbr.conf', 'w') as configfile:
            self.config.write(configfile)

    def  get_indent_delay(self):
        """ Получаем задержку чтения между абзацами из conf файла"""
        delay = self.settings.getint('indent_delay')
        return delay

    def  get_sentance_delay(self):
        """ Получаем задержку чтения между предложениями из conf файла """
        delay = self.settings.getint('sentance_delay')
        return delay

    def get_labels_for_toolbuttons(self):
        """ Получаем из conf файла - подписывать ли кнопки на панели (да/нет) """
        labels = self.settings.getboolean('labels_for_toolbuttons')
        return labels

    def get_current_synth(self):
        """ Получаем текущий синтезатор из conf файла"""
        synth = self.settings.get('current_synth')
        # TODO: если ещё не выбран синтезатор, предложить выбор
        return synth

    def get_list_of_synth(self):
        """ Создание списка доступных файлов конфигурации для синтезаторов """
        files = os.listdir('synth_conf')
        # фильтруем по расширению ".conf"
        list_of_synth_files = filter(lambda x: x.endswith('.conf'), files)
        list_of_synth = []
        for synth_file in list_of_synth_files:
            synth_conf = CP.SynthConfParser('synth_conf/' + synth_file)
            list_of_synth.append([synth_file, synth_conf.get_name()])
        return list_of_synth

    def get_synth_filename(self, synth_name):
        """ Вычисление имени файла настроек по имени синтезатора """
        for synth_record in self.list_of_synth:
            if synth_name == synth_record[1]:
                return synth_record[0]
        return False
