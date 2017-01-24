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
        self.voices = self.config['Voices']
        # считываем значения в переменные
        self.parse()

    def parse(self):
        """ Чтение настроек из файла """
        # название синтезатора
        self.name = self.s_opt.get('name')
        # основная команда синтезатора
        self.synth_cmd = self.s_opt.get('synth_cmd')
        # скорость чтения
        self.set_rate = self.s_opt.get('set_rate')
        self.speech_rate = self.s_opt.getint('speech_rate')
        # список доступных голосов
        self.voices_list = []
        for option in self.config['Voices']:
            self.voices_list.append(self.voices.get(option))
        # текущий голос
        self.current_voice = self.s_opt.get('current_voice')
        self.set_voice = self.s_opt.get('set_voice')

    def get_name(self):
        return self.name

    def save_curret_voice(self):
        """ Сохранение настроек текущего голоса в файл """
        self.config['Synth Options']['current_voice'] = self.current_voice
        with open(self.conf_file, 'w') as configfile:
            self.config.write(configfile)

    def save_rate(self):
        """ Установка скорости чтения и сохранение значения """
        self.config['Synth Options']['speech_rate'] = str(self.speech_rate)
        with open(self.conf_file, 'w') as configfile:
            self.config.write(configfile)
