## autoleprabot ##

Бот для реддита, перекидывающий ссылки на видеорегистраторские ролики из тусиндо-постов из несуществующего бложика на реддит.

### Установка ###

Написан на среде с Python 2.7, работа с другими версиями не тестировалась.
Зависимости можно установить командой:

    $ pip install -r requirements.txt

### Настройка ###

Для создания базы необходимо запустить скрипт `models.py`, работающий пока как `initdb`:

    $ python models.py

Создаст SQLite-базу lepra.db в папке с ботом. В базе необходимо добавить связку между лепро- и реддито-постами:

    $ sqlite3 lepra.db
    sqlite> INSERT INTO posts (post_id, lepra_post_id, reddit_post_id) VALUES (100, 1709850, '236vkf');
    
Где, на примере выше, `100` - это номер поста ("странного хобби пост #100"), `1709850` - ID поста Тусинды #100 на Лепре, `236vkf` - ID поста на реддите, в котором будет жить бот.

Затем необходимо указать доступы к аккаунтам для лепры и реддита. Доступы указываются в файле `config.py`. Для лепры это сессия, сохранённая в `cookies` (можно выдрать из браузера), для реддита - обычные логин и пароль.

### Запуск ###

Всю остальную работу делает скрипт `parser.py`:

    $ python parser.py

