# Телеграм бот Маяк

## Описание 
Бот дает возможность добавить новые сайты для парсинга. Для этого необходимо прикрепить документ .csv с полями `'NAME'`, `'URL'`, `'XPATH'`. Для тестерования бота можно воспользовать файлом [`Document_TEST.csv`](https://github.com/afivan20/Mayak/blob/main/Document_TEST.csv)
Бот выполнит парсинг и вернет полученный ответ пользователю ввиде файла.
https://t.me/upload_xpath_bot

### Как развернуть бота

- склонировать проект
```
git clone https://github.com/afivan20/Mayak
```

- установить все необходимые зависимости
```
pip install -r requirements.txt
```

- указать `TOKEN` для бота в <b>.env</b>

- запустить бота
```
python3 bot.py
```




