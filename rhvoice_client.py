#!/usr/bin/env python3
# coding: utf8

"""
Модуль с клиентом для чтения 
и потоком для управления чтением
"""

import speechd      # speech-dispatcher
import threading    # для потоков
import time         # для задержек

class RHVoice_client():
    """
    Клиент speech-dispatcher для работы с RHVoice
    """
    def __init__(self, win):
        self._client = speechd.SSIPClient('bookreader')
        self._client.set_output_module('rhvoice')
        self._client.set_language('ru')
        # Здесь можно добавить выбор голоса
        # и прочие параметры воспроизведения

        self.win = win  # для связи с GUI классом

        # создаём событие сигнализирующие о завершении чтения
        # и поток для управления чтением
        self.event_idle_status = threading.Event()
        self.exit_signal = False
        self.thread_play = threading.Thread(target=self.play)
        self.thread_play.start()

        # флаги состояния клиента
        self.playing = False        # воспроизведение
        self.reading = False        # непосредственное чтение
        self.stoped = False         # остановлено (возможно возобновление)
        self.aborded = False        # прервано
        self.ended = False          # закончился текст

    def rh_speak(self, text):
        """ Чтение переданного текста """
        def callback_event(callback_type):  
            """ Обратная реакция от клиента """
            if callback_type == speechd.CallbackType.BEGIN:
                print("Воиспроизведение.")
                self.reading = True
            elif callback_type == speechd.CallbackType.END:
                print("Воспр. завершено.")
                self.reading = False
                self.event_idle_status.set()
            elif callback_type == speechd.CallbackType.CANCEL:
                print("Воспр. прервано.")
        self._client.speak(text, callback=callback_event,
                           event_types=(speechd.CallbackType.BEGIN,
                                        speechd.CallbackType.CANCEL,
                                        speechd.CallbackType.END)) 
    def play(self):
        """
        Запускается в отдельном потоке для воспроизведения.
        Для завершения потока, нужно установить события
        exit_signal и event_idle_status
        """
        while True: 
            # ловим событие о конце воспроизведения
            self.event_idle_status.wait()
            self.event_idle_status.clear()

            # Выходим, если есть сигнал об этом
            if self.exit_signal: break

            # сбрасываем флаги остановки
            self.aborded = False
            self.stoped = False

            txt = False
            if self.ended == False:
                txt = self.win.TTR.get_current_sentence()
                # Отмечаем текст, который читаем, если он есть
                if txt:
                    cur_sent_n = self.win.TTR.current_sentence_n
                    start, end = self.win.TTR.get_sentence_pos(cur_sent_n)
                    self.win.mark_readtext(start, end)
            else:
                self.playing = False

            # применяем задержки чтения между абзацами и предложениями
            if self.win.TTR.current_sentence_n == 0:
                delay = float(self.win.PBR_Pref.indent_delay)/1000
            else:
                delay = float(self.win.PBR_Pref.sentance_delay)/1000
            while delay > 0:
                time.sleep(0.001)
                if self.aborded: break   # выходим из задержки по указанию
                delay -= 0.001


            # добавляем текст в очередь на чтение
            # и переключаемся на новую строку
            if not (self.aborded or self.stoped):
                if txt: 
                    self.rh_speak(txt)  
                    self.win.TTR.get_next_sentence()
                else: 
                    if self.playing:
                        self.event_idle_status.set()
                        self.win.TTR.get_next_sentence()

    def abord(self):
        """ Прерывание чтения """
        self.aborded = True
        self._client.stop('self')
        if self.reading == True:
            self.reading = False
            if not self.win.TTR.get_prev_sentence():
                self.win.TTR.get_prev_text()

    def stop(self):
        """ Остановка чтения с возможностью восстановления"""
        self.playing = False
        self.reading = False
        self.stoped = True
        self._client.stop('self')
        # возвращаем указатель на предыдущее предложение или предыдущий абзац
        if not self.win.TTR.get_prev_sentence():
            self.win.TTR.get_prev_text()

    def resume(self):
        """ Продолжение чтения с начала предложения """
        self.playing = True
        self.event_idle_status.set()

    def get_voices_list(self):
        """ Получаем список доступных голосов """
        tmp = self._client.list_synthesis_voices() 
        voices = []
        for i in range(len(tmp)):
            voices.append(tmp[i][0])
        return voices

    def set_voice(self, voice):
        """ Установка голоса """
        self._client.set_synthesis_voice(voice, 'self')

    def set_rate(self, rate):
        """ Установка скорости чтения """
        self._client.set_rate(rate, 'self')
