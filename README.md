# PyBookReaderTTS
Читалка для книг на Gtk с помощью TTS движков (RHvoice, Festival, ru_tts и др.).

## Файлы настроек
### Общие настройки
Общие настройки расположены в "pbr.conf".

### Настройки синтезаторов
Настройки синтезаторов расположены в "synth_conf" и имеют расшерение "conf".
В них должна быть указана основная команда запуска, параметры проигрывателя, список поддерживаемых голосов и другие параметры. На данный момент представлено 3 варианта:

#### RHVoice
Файл настроек: "synth_conf/rhvoice.conf".
Синтез голоса производится через "RHVoice-client".
Для его использования необходимо запустить "RHVoice-service".

#### Festival
Файл настроек: "synth_conf/festival.conf".
Синтез голоса производится через "text2wave".

#### Ru_tts
Файл настроек: "synth_conf/ru_tts.conf".
Синтез голоса производится через "ru_tts".
Для работы необходима сгенерированная локаль "koi8-r". И утилита "play" из состава "sox".

## Внешний вид
(зависит от установленной темы Gtk):
![Внешний вид](https://github.com/vantu5z/PyBookReaderTTS/raw/master/screenshot.png)
