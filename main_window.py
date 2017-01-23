#!/usr/bin/env python3
# coding: utf8

"""
Модуль главного окна программы.
Также содержит класс для выбора и переключения
по читаемому тексту.
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

# для работы с регулярными выражениями
import re

# модули программы
import preferences_dialog as PD
import search_dialog as SD
import synth_client as SC

class MainWindow(Gtk.Window):
    """
    Основное окно программы
    """
    def __init__(self):
        Gtk.Window.__init__(self, title="PyBookReaderTTS")

        self.set_default_size(600, 400)

        # сетка для размещения элементов окна
        self.grid = Gtk.Grid()
        self.add(self.grid)

        # флаг занятости при переходе между абзацами
        self.progress = False

        # клиент для чтения
        self.synth_client = SC.SynthClient(self)

        # установка настроек
        self.PBR_Pref = PD.Preferences(self.synth_client)

        # создание группы для горячих клавиш
        self.accel_group = Gtk.AccelGroup()
        self.add_accel_group(self.accel_group)

        # создание управляеющих элементов
        self.create_mainmenu()
        self.create_textview()
        self.create_toolbar()
        self.create_buttons()

        # для разделения на участки и получения текста из GUI
        self.TTR = TextToRead(self)

    def create_mainmenu(self):
        """ Создание главного меню """
        mainmenu = Gtk.MenuBar.new()
        self.grid.attach(mainmenu, 0, 0, 3, 1)
        for label in ["Файл", "Правка", "Чтение", "Справка"]:
            mi=Gtk.MenuItem(label)
            mainmenu.add(mi)
            if label == "Файл":
                mi2=Gtk.Menu()
                m_item=Gtk.MenuItem("Открыть")
                m_item.connect("activate", self.open_book_file)
                mi2.add(m_item)
                # сочетание ctrl+O
                m_item.add_accelerator("activate", self.accel_group, ord('O'),
                                        Gdk.ModifierType.CONTROL_MASK,
                                        Gtk.AccelFlags.VISIBLE)

                m_item=Gtk.MenuItem("Выйти")
                m_item.connect("activate", self.close_app)
                mi2.add(m_item)
                # сочетание ctrl+Q
                m_item.add_accelerator("activate", self.accel_group, ord('Q'),
                                        Gdk.ModifierType.CONTROL_MASK,
                                        Gtk.AccelFlags.VISIBLE)
                mi.set_submenu(mi2)

            if label == "Правка":
                mi2=Gtk.Menu()
                m_item=Gtk.MenuItem("Параметры")
                m_item.connect("activate", self.on_preferences_clicked)
                mi2.add(m_item)
                mi.set_submenu(mi2)
                # сочетание ctrl+P
                m_item.add_accelerator("activate", self.accel_group, ord('P'),
                                        Gdk.ModifierType.CONTROL_MASK,
                                        Gtk.AccelFlags.VISIBLE)
            if label == "Чтение":
                mi2=Gtk.Menu()
                m_item=Gtk.MenuItem("Читать")
                m_item.connect("activate", self.on_play_button_clicked)
                mi2.add(m_item)
                # сочетание ctrl+enter
                m_item.add_accelerator("activate", self.accel_group, 65293,
                                        Gdk.ModifierType.CONTROL_MASK,
                                        Gtk.AccelFlags.VISIBLE)

                m_item=Gtk.MenuItem("Вперёд")
                m_item.connect("activate", self.on_next_button_clicked)
                mi2.add(m_item)
                # сочетание ctrl+right
                m_item.add_accelerator("activate", self.accel_group, 65363,
                                        Gdk.ModifierType.CONTROL_MASK,
                                        Gtk.AccelFlags.VISIBLE)

                m_item=Gtk.MenuItem("Назад")
                m_item.connect("activate", self.on_prev_button_clicked)
                mi2.add(m_item)
                # сочетание ctrl+left
                m_item.add_accelerator("activate", self.accel_group, 65361,
                                        Gdk.ModifierType.CONTROL_MASK,
                                        Gtk.AccelFlags.VISIBLE)

                m_item=Gtk.MenuItem("Стоп")
                m_item.connect("activate", self.on_stop_button_clicked)
                mi2.add(m_item)
                # сочетание ctrl+space
                m_item.add_accelerator("activate", self.accel_group, 32,
                                        Gdk.ModifierType.CONTROL_MASK,
                                        Gtk.AccelFlags.VISIBLE)
                mi.set_submenu(mi2)

    def create_toolbar(self):
        """Создание панели иструментов с кнопками управления"""
        toolbar = Gtk.Toolbar()
        # устанавливаем начальный стиль для кнопок (с текстом или без)
        if self.PBR_Pref.labels_for_toolbuttons:
            toolbar.set_style(2)
        else:
            toolbar.set_style(0)
        self.grid.attach(toolbar, 0, 1, 3, 1)

        button_prev = Gtk.ToolButton()
        button_prev.set_label('Назад')
        button_prev.set_icon_name("stock_media-prev")
        toolbar.insert(button_prev, 0)

        button_stop = Gtk.ToolButton()
        button_stop.set_label('Стоп')
        button_stop.set_icon_name("media-playback-stop")
        toolbar.insert(button_stop, 1)

        button_play = Gtk.ToolButton()
        button_play.set_label('Читать')
        button_play.set_icon_name("media-playback-start")
        toolbar.insert(button_play, 2)

        button_next = Gtk.ToolButton()
        button_next.set_label('Вперёд')
        button_next.set_icon_name("stock_media-next")
        toolbar.insert(button_next, 3)

        # подключаем события к кнопкам
        button_prev.connect("clicked", self.on_prev_button_clicked)
        button_stop.connect("clicked", self.on_stop_button_clicked)
        button_play.connect("clicked", self.on_play_button_clicked)
        button_next.connect("clicked", self.on_next_button_clicked)

        toolbar.insert(Gtk.SeparatorToolItem(), 4)

        button_search = Gtk.ToolButton()
        button_search.set_label('Поиск')
        button_search.set_icon_name("system-search")
        button_search.connect("clicked", self.on_search_clicked)
        toolbar.insert(button_search, 5)

        toolbar.insert(Gtk.SeparatorToolItem(), 6)

        button_preferences = Gtk.ToolButton()
        button_preferences.set_label('Настройки')
        button_preferences.set_icon_name("preferences-system")
        button_preferences.connect("clicked", self.on_preferences_clicked)
        toolbar.insert(button_preferences, 7)

    def create_textview(self):
        """Создание текстового окна с прокруткой"""
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        self.grid.attach(scrolledwindow, 0, 2, 3, 1)

        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        # подгужаем текст приветствия из файла
        self.textbuffer.set_text(self.get_welcome_text())
        scrolledwindow.add(self.textview)

        # отступ слева для абзацев
        self.textview.set_indent(20)

        # формат выделения найденного текста
        self.tag_found = self.textbuffer.create_tag("found",
                                    background = "yellow",
                                    foreground = "black")
        # формат выделения текста для чтения
        self.tag_readtext = self.textbuffer.create_tag("readtext",
                                    background = "blue",
                                    foreground = "white")

    def create_buttons(self):
        """Создание кнопок настройки и регулировки скорости"""
        check_readonly = Gtk.CheckButton("Только чтение")
        check_readonly.set_active(True)
        check_readonly.connect("toggled", self.on_readonly_toggled)
        self.grid.attach(check_readonly, 0, 3, 1, 1)
        self.on_readonly_toggled(check_readonly)

        check_wordwrap = Gtk.CheckButton("Переносить текст по словам")
        check_wordwrap.set_active(True)
        check_wordwrap.connect("toggled", self.on_wordwrap_toggled)
        self.grid.attach_next_to(check_wordwrap, check_readonly,
                                 Gtk.PositionType.RIGHT, 1, 1)
        self.on_wordwrap_toggled(check_wordwrap)

        # ползунок для настройки скорости чтения
        speech_rate = Gtk.HScale.new_with_range(-100, 100, 1)
        # начальное значение
        speech_rate.set_value(self.synth_client.get_rate())
        speech_rate.set_hexpand(True)
        speech_rate.set_tooltip_markup('Скорость чтения от -100 до 100')
        speech_rate.connect("value-changed", self.speech_rate_changed)
        self.grid.attach_next_to(speech_rate, check_wordwrap,
                                 Gtk.PositionType.RIGHT, 1, 1)
        # применяем изменения
        self.speech_rate_changed(speech_rate)

    # обработка нажатия на кнопки управления
    #=========================================================

    def on_prev_button_clicked(self, widget):
        """ Переключение на предыдущий абзац текста """
        if self.progress == False:
            self.progress = True
            if self.synth_client.playing:
                # переключаем чтение на предыдущий абзац
                self.synth_client.abord()
                self.TTR.get_prev_indent()
                self.mark_readtext(self.TTR.indent_pos[0], self.TTR.indent_pos[1])
                self.on_play_button_clicked(widget)
            else:
                # просто переключаемся на предыдущий абзац
                self.synth_client.stoped = False
                self.TTR.get_prev_indent()
                self.mark_readtext(self.TTR.indent_pos[0], self.TTR.indent_pos[1])
            self.progress = False

    def on_stop_button_clicked(self, widget):
        """ Остановка воспроизведения """
        self.synth_client.stop()

    def on_play_button_clicked(self, widget):
        """" Обработка нажатия кнопки начала чтения """
        if self.synth_client.stoped == True:
            # восстанавливаем чтение, если оно было остановлено
            self.synth_client.resume()
        elif self.synth_client.playing:
            # если идёт чтение - не реагируем на нажатие
            pass
        else:
            # начинаем чтение, если есть что читать
            if self.TTR.get_current_indent():
                self.synth_client.start_play()
            elif self.TTR.get_next_indent():
                self.synth_client.start_play()

    def on_next_button_clicked(self, widget):
        """ Переключение на следующий абзац текста """
        if self.progress == False:
            self.progress = True
            if self.synth_client.playing:
                # переключаем чтение на следующий абзац, если идёт чтение
                self.synth_client.abord()
                self.synth_client.stoped = False
                if self.TTR.get_next_indent():
                    self.mark_readtext(self.TTR.indent_pos[0],
                                       self.TTR.indent_pos[1])
                    self.on_play_button_clicked(widget)
                else:
                    self.synth_client.set_text_ending()
                    self.clear_selections()
            else:
                # просто переключаемся на следующий абзац
                self.synth_client.stoped = False
                self.TTR.get_next_indent()
                self.mark_readtext(self.TTR.indent_pos[0],
                                   self.TTR.indent_pos[1])
            self.progress = False

    #==========================================================

    def open_book_file(self, widget):
        """ Диалог выбора файла книги для чтения"""
        dialog = Gtk.FileChooserDialog("Выберите книгу", self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL,
                                       Gtk.ResponseType.CANCEL,
                                       Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            # открываем файл и подгружаем текст
            f = open(dialog.get_filename(), 'r')
            self.textbuffer.set_text(f.read())

        dialog.destroy()

    def speech_rate_changed(self, widget):
        """ Обработка изменения скорости чтения """
        rate = widget.get_value()
        if rate != None:
            rate = int(rate)
            self.synth_client.set_rate(rate)

    def on_preferences_clicked(self, widget):
        """ Вызов диалога настройки """
        PD.PreferencesDialog(self, self.PBR_Pref,
                             self.synth_client)

    def clear_selections(self):
        """ Очистка всех отметок в тексте """
        start = self.textbuffer.get_start_iter()
        end = self.textbuffer.get_end_iter()
        self.textbuffer.remove_all_tags(start, end)

    def on_readonly_toggled(self, widget):
        """ Переключение режима редактирования текста """
        self.textview.set_editable(not widget.get_active())

    def on_wordwrap_toggled(self, widget):
        """" Переключение режима переноса строк """
        if widget.get_active() == True:
            self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        else:
            self.textview.set_wrap_mode(Gtk.WrapMode.NONE)

    def on_search_clicked(self, widget):
        """ Обработка диалога поиска """
        dialog = SD.SearchDialog(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.clear_selections()
            cursor_mark = self.textbuffer.get_insert()
            start = self.textbuffer.get_iter_at_mark(cursor_mark)
            if start.get_offset() == self.textbuffer.get_char_count():
                start = self.textbuffer.get_start_iter()
            # получаем текст для поиска, ищем его и отмечаем
            self.search_and_mark(dialog.get_search_text(), start)

        dialog.destroy()

    def search_and_mark(self, text, start):
        """" Рекурсивно ищем и отмечаем найденный текст """
        end = self.textbuffer.get_end_iter()
        match = start.forward_search(text, 0, end)

        if match != None:
            match_start, match_end = match
            self.textbuffer.apply_tag(self.tag_found, 
                                      match_start, match_end)
            self.search_and_mark(text, match_end)

    def mark_readtext(self, start, end):
        """ Выделение текста для чтения """
        self.clear_selections()
        self.textbuffer.apply_tag(self.tag_readtext, start, end)

    def get_welcome_text(self):
        """ Получение текста приветствия из файла """
        f = open('welcome.txt', 'r')
        txt = f.read()
        return txt

    def close_app(self, widget):
        """ Закрытие окна программы с последующим выходом """
        self.close()

class TextToRead(object):
    """
    Управление текстом для чтения.
    Получение текста и переход по абзаца и предложениям.
    """
    def __init__(self, win):
        # для доступа к главному окну и функциям клиента чтения
        self.win = win
        # для доступа к данным в текстовом окне
        self.textbuffer = win.textbuffer
        # номер абзаца для чтения
        self.indent_num = -1
        # позиция участка текста для чтения x,y : iter
        self.indent_pos = None
        # абзац разбитый на предложения
        self.indent_sentences = None
        # номер текущего предложения
        self.current_sentence_n = 0

        # установка переменных по первому абзацу текста
        self.get_next_indent()

    def get_sentence_pos(self, nomber):
        """ Получаем координаты указанного (nomber) предложения,
            если такого предложения нет, то возвращаем False """
        if self.indent_sentences is not None:
            if nomber < len(self.indent_sentences):
                start = self.indent_pos[0].copy()
                i = 0
                while i < nomber:
                    start.forward_chars(len(self.indent_sentences[i]))
                    i += 1
                end = start.copy()
                end.forward_chars(len(self.indent_sentences[nomber]))
                return start.copy(), end.copy()
            else:
                return False, False
        else:
            return False, False

    def get_current_sentence(self):
        """ Считываем текущее предложение """
        if self.indent_sentences is not None:
            txt = self.indent_sentences[self.current_sentence_n]
            return txt
        else:
            return False

    def get_next_sentence(self):
        """ Переходим к следующему предложению,
            если его нет, то переходим на следующий абзац """
        if self.indent_sentences is not None:
            self.current_sentence_n += 1
            if self.current_sentence_n < len(self.indent_sentences):
                txt = self.get_current_sentence()
                return txt
            else:
                if self.get_next_indent():
                    if len(self.indent_sentences) > 0:
                        txt = self.get_current_sentence()
                        return txt
                    else:
                        return False
        else: 
            return False

    def get_prev_sentence(self):
        """ Переходим к предыдущему предложению, если его нет,
            то переходим на последнее предложение предыдущего абзаца """
        if self.indent_sentences is not None:
            self.current_sentence_n -= 1
            if (self.current_sentence_n < len(self.indent_sentences)
                                   and self.current_sentence_n >= 0):
                txt = self.get_current_sentence()
                return txt
            else:
                self.get_prev_indent()
                if len(self.indent_sentences) > 0:
                    self.current_sentence_n = len(self.indent_sentences)-1
                    txt = self.get_current_sentence()
                    return txt
                else:
                    return False
        else:
            return False

    def split_to_sentences(self, text):
        """ Разбиение абзаца на предложения """
        tmp_list = []
        text = text.replace('\n','')

        # FIXME: изменить регулярное выражение, чтобы определять имена и сокращения
        # разбиваем абзац на список предложений
        tmp_list = re.split(r'([.!?]+ )', text)

        # объединяем короткие предложения с предыдущими
        i = 1
        while i < len(tmp_list):
            if len(tmp_list[i]) < 10:
                tmp_list[i-1] = tmp_list[i-1] + tmp_list[i]
                tmp_list.pop(i)
                i -= 1
            i += 1

        return tmp_list

    def get_current_indent(self):
        """
        Получаем координаты текущего абзаца, возвращаем его текст
        и разбиваем на предложения (пропуская пустые строки)
        """
        if self.textbuffer.get_line_count() > self.indent_num+1:
            start = self.textbuffer.get_iter_at_line(self.indent_num)
            end = self.textbuffer.get_iter_at_line(self.indent_num+1)

        elif self.textbuffer.get_line_count() == self.indent_num+1:
            start = self.textbuffer.get_iter_at_line(self.indent_num)
            end = self.textbuffer.get_end_iter()

        else:
            # сообщаем, что дошли до конца текста
            self.win.synth_client.set_text_ending()
            start = self.textbuffer.get_end_iter()
            end = start

        self.indent_pos = start, end
        txt = self.textbuffer.get_text(start, end, False)

        # удаляем символ новой строки
        txt = txt.replace('\n','')
        # удаляем лишние пробелы для проверки пустой строки
        txt_skip = re.sub(r'\s+', ' ', txt)

        if txt_skip == '' or txt_skip ==' ':
            # пропускаем пустые строки
            txt = False
            self.indent_sentences = None
        else:
            # разбиваем текст на предложения
            self.indent_sentences = self.split_to_sentences(txt)
            # переводим указатель на первое предложение абзаца
            self.current_sentence_n = 0
        return txt

    def get_next_indent(self):
        """ Переход к следующему абзацу """
        txt = False
        while self.textbuffer.get_line_count() > self.indent_num:
            self.indent_num += 1
            txt = self.get_current_indent()
            if txt: break
        return txt

    def get_prev_indent(self):
        """ Переход к предыдущему абзацу """
        txt = False
        while self.indent_num > 0:
            self.indent_num -= 1
            txt = self.get_current_indent()
            if txt: break
        return txt

def exit_app(self, widget):
    """
    Выход из программы с сохранением настроек,
    остановкой чтения и завершением всех запущенных потоков
    """
    self.synth_client.save_rate()
    self.PBR_Pref.save_settings()
    self.synth_client.exit()
    Gtk.main_quit()

def main():
    """ Старт программы """
    win = MainWindow()
    win.connect("delete-event", exit_app)
    win.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()
