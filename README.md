# Конфигурационное управление дз №1
## Общее описание
Разработка эмулятора для языка оболочки ОС. Эмулятор запускается из реальной командной строки, 
а файл с виртуальной файловой системой не нужно распаковывать у пользователя. 
Эмулятор принимает образ виртуальной файловой системы в виде файла формата 
zip. Эмулятор работает в режиме CLI. 

Ключами командной строки задаются:
- Путь к архиву виртуальной файловой системы.
- Путь к лог-файлу.
- Путь к стартовому скрипту.

Лог-файл имеет формат csv и содержит все действия во время последнего 
сеанса работы с эмулятором.
Стартовый скрипт служит для начального выполнения заданного списка 
команд из файла.

Необходимо поддержать в эмуляторе команды ls, cd и exit, а также 
следующие команды:
1. pwd.
2. history.
3. uptime.

Все функции эмулятора должны быть покрыты тестами, а для каждой из 
поддерживаемых команд необходимо написать 3 теста.
##  Описание всех функций и настроек

1. pwd
   - вывод текущей дирректории
2. history
     - вывод истории введенных команд
4. uptime
     - выводит в одну строку информацию о работе системы: текущее время, общее время, в течение которого система работала, количество пользователей (количество зарегистрированных пользователей)
##  Описание команд для сборки проекта.
1. Клонирование репозитория 

```git clone https://github.com/ValeriaKhomutova/Homework_config.git```

2. Переход в директорию Homework_config

```cd Homework_config/cli```

3. Запуск скрипта для демонстрации возможностей Cli

```python .\var28.py .\config.toml```

4. Запуск тестов
   
```pytest test.py```

## Примеры использования
![Screen](https://github.com/ValeriaKhomutova/Homework_config/blob/main/image.png)

## Результаты прогона тестов
![Screen](https://github.com/ValeriaKhomutova/Homework_config/blob/main/img.png)

<!--описание коммитов-->
## Описание коммитов
| Название | Описание                                                                             |
|------------------|----------------------------------------------------------------------------- |
| First step	     | Эмулятор командной строки с базовыми командами, запускаемые из файла-скрипта |
| second step      | Добавлены собственные команды, описанные в варианте                          |
| third step tests | Реализация тестов, отладка варианта                                          |
| Prod_version	   | Готовый проект                                                               |
