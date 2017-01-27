#!/usr/bin/env python3
# coding: utf8

"""
Модуль с клиентом для чтения 
и необходимыми потоками для управления чтением
"""

import threading    # для организации потоков
import time         # для задержек

import subprocess   # для выполнения консольных команд

# модули программы
# для чтения настроек синтезаторов
import synth_conf.parser as SCP

class SynthClient(object):
    """
    Клиент для работы с синтезатором
    """
    def __init__(self, win):
        self.win = win  # для связи с главным окном программы

        self.synth_conf = SCP.SynthConfParser('synth_conf/' +
                            self.win.PBR_Pref.get_synth_filename(self.win.PBR_Pref.current_synth))

        # создаём событие по которому разрешается чтение
        # и поток для управления чтением
        self.say = threading.Event()
        self.exit_signal = False
        self.thread_play = threading.Thread(target=self.play)
        self.thread_play.start()

        # флаги состояния клиента
        self.playing = False        # воспроизведение
        self.stoped = False         # остановлено (возможно возобновление)
        self.aborded = False        # прервано
        self.ended = False          # закончился текст

        # плеер для воспроизведения аудио
        self.player = PlayAudio()

        # генератор команды для синтеза речи
        self.s_cmd = SynthCMD(self.synth_conf)

        # преобразователи текста в аудио
        # текущий - из него берутся данные для чтения
        self.curent_data = TextToAudio(self.s_cmd)
        self.curent_data.start()

        # следующий - пока идёт чтение в другом потоке подготавливаются данные
        self.next_data = TextToAudio(self.s_cmd)
        self.next_data.start()

    def play(self):
        """
        Запускается в отдельном потоке для воспроизведения.
        Завершение потока производится через self.exit()
        """
        while True:
          # завершаем поток, если есть сигнал об этом
          if self.exit_signal: break  
          while True:
            # ловим событие о разрешении чтения
            self.say.wait()
            self.say.clear()

            # завершаем поток, если есть сигнал об этом
            if self.exit_signal: break

            self.aborded = False
            self.stoped = False

            # небольшая задержка для устранения рассинхрона потоков
            time.sleep(0.005)
            # ожидание окончания преобразования
            while not self.next_data.state:
                time.sleep(0.001)
                # прекращаем ожидание преобразования
                # из-за остановки или конца текста
                if self.aborded or self.ended: break

            if self.aborded or self.ended: break

            self.curent_data.data = self.next_data.data
            self.curent_data.state = True

            txt = None
            cur_sent_n = None

            if self.ended == False and self.aborded == False:
                txt = self.win.TTR.get_current_sentence()
                # Отмечаем текст, который читаем, если он есть
                if txt != None:
                    cur_sent_n = self.win.TTR.current_sentence_n
                    start, end = self.win.TTR.get_sentence_pos(cur_sent_n)
                    self.win.mark_readtext(start, end)

                    self.next_data.get(self.win.TTR.get_next_sentence())
            else:
                self.playing = False
                self.win.clear_selections()

            # применяем задержки чтения между абзацами и предложениями
            if cur_sent_n != None:
                if cur_sent_n == 0:
                    delay = float(self.win.PBR_Pref.indent_delay)/1000
                else:
                    delay = float(self.win.PBR_Pref.sentance_delay)/1000
                while delay > 0:
                    time.sleep(0.001)
                    if not self.playing: break   # выходим из задержки по указанию
                    delay -= 0.001

            if not self.playing: break

            # читаем текущий текст, если не было команд на остановку
            if not (self.aborded or self.stoped):
                if (txt != None) and (self.curent_data.data != None):
                    self.player.play(self.curent_data.data)
                    # продолжаем чтение, если небыло остановок
                    if not (self.aborded or self.stoped): self.say_allow()
                else:
                    if self.playing: self.say_allow()

    def say_allow(self):
        """ Разрешение чтения """
        self.say.set()

    def start_play(self):
        """ Начало воспроизведения """
        self.playing = True
        self.ended = False
        self.next_data.get(self.win.TTR.get_current_sentence())
        self.say_allow()

    def abord(self):
        """ Прерывание чтения """
        self.playing = False
        self.aborded = True
        self.stoped = False
        # останавливаем чтение
        # возвращаем указатель на предыдущее предложение
        if self.player.state == 'read':
            self.player.stop()
            self.win.TTR.get_prev_sentence()

    def stop(self):
        """ Остановка чтения с возможностью восстановления"""
        self.playing = False
        self.stoped = True
        # возвращаем указатель на предыдущее предложение
        if self.player.state == "read":
            self.player.stop()
            self.win.TTR.get_prev_sentence()
        # сбрасываем данные следующего текста на текущий
        # для возобновления чтения
        self.next_data.abord()
        self.next_data.data = self.curent_data.data
        self.next_data.state = True

    def resume(self):
        """ Продолжение чтения с начала предложения """
        self.playing = True
        self.say_allow()

    def get_current_voice(self):
        """ Получение текущего голоса """
        voice = self.synth_conf.current_voice
        return voice

    def set_voice(self, voice):
        """ Установка голоса """
        self.synth_conf.current_voice = voice
        self.s_cmd.generate(self.synth_conf)
        # обновляем команды в преобразователях
        self.curent_data.update_cmd()
        self.next_data.update_cmd()

    def save_curret_voice(self):
        """ Сохранение настроек текущего голоса в файл """
        self.synth_conf.save_curret_voice()

    def get_voices_list(self):
        """ Получение списока доступных голосов """
        voices = self.synth_conf.voices_list
        return voices

    def get_rate(self):
        """ Получение значение скорости чтения """
        rate = self.synth_conf.speech_rate
        if rate != None: int(rate)
        return rate

    def set_rate(self, rate):
        """ Установка скорости чтения и сохранение значения """
        self.synth_conf.speech_rate = rate
        self.s_cmd.generate(self.synth_conf)
        self.curent_data.update_cmd()
        self.next_data.update_cmd()

    def get_synth_note(self):
        """ Получение примечания по синтезатору """
        note = self.synth_conf.note
        if note == None: note = ''
        return note

    def save_rate(self):
        """ Сохранение скорости чтения """
        self.synth_conf.save_rate()

    def set_text_ending(self):
        """ Установка метки о завершении текста """
        self.ended = True

    def change_synth_conf(self, synth):
        """ Переключение на другой синтезатор """
        self.synth_conf = SCP.SynthConfParser('synth_conf/' + synth)
        # обновляем команды в преобразователях
        self.curent_data.update_cmd()
        self.next_data.update_cmd()

    def exit(self):
        """ Завершение потоков клиента для выхода из программы """
        self.abord()
        self.exit_signal = True
        self.say_allow()
        self.thread_play.join(1)

        self.curent_data.exit()
        self.curent_data.join(1)

        self.next_data.exit()
        self.next_data.join(1)

class PlayAudio(object):
    """
    Воспроизведение переданных аудио данных
    TODO: команда для воспроизведения из файла конфигурации, пока используется "aplay"
    """
    def __init__(self):
        # команда для воспроизведения
        self.play_cmd = ['aplay', '-q']
        # статус (свободен - idle, чтение - read)
        self.state = 'idle'

    def play(self, data):
        """ Воспроизведение переданных аудио данных """
        if data:
            self.state = 'read'
            self.p = subprocess.Popen(self.play_cmd, 
                                      stdin=subprocess.PIPE)
            self.p.communicate(data)
            self.state = 'idle'

    def stop(self):
        """ Остановка процесса, если он существует """
        if self.state == 'read':
            try:
                self.p.kill()
                self.state = 'idle'
            except:
                pass

class TextToAudio(threading.Thread):
    """
    Перевод текста в аудио данные с помощью синтезатора
    Действия производятся в отдельном потоке
    """
    def __init__(self, s_cmd):
        threading.Thread.__init__(self)
        self.get_value = threading.Event()
        self.s_cmd = s_cmd
        # команда для синтезатора
        self.synth_cmd = self.s_cmd.get()
        # состояние
        self.state = True
        # аудио данные
        self.data = None
        # текст для чтения
        self.text = ''
        # флаги управления
        self.aborded = False
        self.exit_signal = False

    def run(self):
        """ Ожидание события с запросом на преобразование """
        while True:
            self.get_value.wait()
            self.get_value.clear()

            # завершаем поток для выхода из программы
            if self.exit_signal: break

            self.aborded = False
            self.state = False
            if self.text:
                self.data = self.txt2audio(self.text)
                if not self.aborded:
                    self.state = True

    def get(self, text):
        """ Запрос на преобразование """
        # сначала остановим незаконченное преобразование
        if not self.state: self.abord()
        else: self.state = False
        self.text = text
        # разрешаем преобразование
        self.get_value.set()

    def abord(self):
        """ Остановка преобразования """
        try:
            self.p.kill()
            self.aborded = True
            self.state = False
        except:
            pass

    def txt2audio(self, text):
        """ Перевод текста в аудио данные """
        self.p = subprocess.Popen(self.synth_cmd, 
                                  stdin = subprocess.PIPE,
                                  stdout = subprocess.PIPE,
                                  stderr = subprocess.PIPE)
        stdout, stderr = self.p.communicate(text.encode('utf-8'))
        return stdout

    def update_cmd(self):
        """ Обновление команды синтезатора 
            (требуется для изменения голоса и других параметров) """
        self.synth_cmd = self.s_cmd.get()

    def exit(self):
        """ Завершение потока для выхода из программы """
        self.exit_signal = True
        self.get('stop thread')

class SynthCMD(object):
    """
    Команда для перевода текста в аудио данные
    """
    def __init__(self, synth_conf):
        self.synth_cmd = None
        # собираем команду
        self.generate(synth_conf)

    def generate(self, synth_conf):
        """ Составление команды с параметрами """
        self.synth_cmd = []

        # основная команда синтезатора
        self.synth_cmd.append(synth_conf.synth_cmd)

        # голос
        self.synth_cmd.append(synth_conf.set_voice)
        self.synth_cmd.append(synth_conf.current_voice)

        # скорость чтения
        if synth_conf.set_rate != None:
            self.synth_cmd.append(synth_conf.set_rate)
            self.synth_cmd.append(str(synth_conf.speech_rate/100))

    def get(self):
        """ Возвращает собранную команду внешнему потребителю """
        return self.synth_cmd
