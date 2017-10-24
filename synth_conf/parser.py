#!/usr/bin/env python3
# coding: utf8

import configparser

class SynthConfParser():
    """
    Обработка настроек синтезатора
    """
    def __init__(self, conf_file):
        """ Инициализация настроек """
        # открываем файл конфигурации
        self.conf_file = conf_file
        self.config = configparser.ConfigParser()
        self.config.read(conf_file)
        self.s_opt = self.config['Synth Options']
        self.player_conf = self.config['Player_conf']
        try:
            self.voices = self.config['Voices']
        except:
            self.voices = None

        # считываем значения в переменные
        self.parse()

    def parse(self):
        """ Чтение настроек из файла """

        # название синтезатора (обязательный параметр)
        self.name = self.s_opt.get('name')

        # основная команда синтезатора (обязательный параметр)
        self.synth_cmd = self.s_opt.get('synth_cmd')

        # кодировка текста (обязательный параметр)
        self.text_coding = self.s_opt.get('text_coding')

        # скорость чтения
        try:
            self.set_rate = self.s_opt.get('set_rate')
            self.speech_rate = self.s_opt.getint('speech_rate')
        except:
            self.set_rate = None
            self.speech_rate = None

        # список доступных голосов
        try:
            self.voices_list = []
            for option in self.config['Voices']:
                self.voices_list.append(self.voices.get(option))
        except:
            if len(self.voices_list) < 1:
                self.voices_list = None

        # текущий голос
        try:
            self.current_voice = self.s_opt.get('current_voice')
            self.set_voice = self.s_opt.get('set_voice')
        except:
            self.current_voice = None
            self.set_voice = None

        # дополнительная информация
        try:
            self.note = self.s_opt.get('note')
        except:
            self.note = ''

        # команда для воспроизведения аудио данных
        try:
            self.play_cmd = []
            self.play_cmd.append(self.player_conf.get('player_cmd'))
            for option in self.config['Player_conf']:
                if option != 'player_cmd':
                    self.play_cmd.append(self.player_conf.get(option))
        except:
            if len(self.play_cmd) < 1:
                self.play_cmd = ['aplay', '-q']

    def change_conf_file(self, conf_file):
        # открываем файл конфигурации
        self.conf_file = conf_file
        self.config = configparser.ConfigParser()
        self.config.read(conf_file)
        self.s_opt = self.config['Synth Options']
        self.player_conf = self.config['Player_conf']
        try:
            self.voices = self.config['Voices']
        except:
            self.voices = None

        self.parse()

    def get_name(self):
        """ Передача имени синтезатора внешнему потребителю """
        return self.name

    def get_play_cmd(self):
        """ Возвращает собранную команду для плеера внешнему потребителю """
        return self.play_cmd

    def get_text_coding(self):
        """ Возвращает кодировку текста внешнему потребителю """
        return self.text_coding

    def save_curret_voice(self):
        """ Сохранение настроек текущего голоса в файл """
        if self.current_voice != None:
            self.config['Synth Options']['current_voice'] = self.current_voice
            with open(self.conf_file, 'w') as configfile:
                self.config.write(configfile)

    def save_rate(self):
        """ Сохранение значения скорости чтения """
        if self.speech_rate != None:
            self.config['Synth Options']['speech_rate'] = str(self.speech_rate)
            with open(self.conf_file, 'w') as configfile:
                self.config.write(configfile)
