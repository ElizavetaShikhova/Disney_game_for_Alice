# Навык-игра для Алисы  
![alt text](https://ia.wampi.ru/2022/05/04/1b67ed9e6cb518be6.jpg)
## Суть игры
+ Игрок должен угадать название фильма или имя героя по картинке (2 режима игры). Угадывать можно по 3-м категориям: фильмы, короткие фильмы и тв-шоу.  
+ В игре будут присутствовать 3 подсказки (открытие первых 3-х букв в названии)  
+ Если игрок угадал без подсказки, то ему начисляется 10 балов, с 1 подсказкой - 8 баллов, с 2 подсказками - 6 баллов, с 3 подсказками - 4 балла.   
+ Баллы будут сохраняться, чтобы сформировать лидерборд.

Используется api https://disneyapi.dev  
  
    
    ТЗ
    в translated.bd хранятся переводы названий фильмов и имен, а также картинки из яндекс.диалогов
    в users.json хранятся данные об игроках(id,name,played,guessed,point)
    в numbers.json хранятся номера для рандомного выбора вопроса
    в phrases.json хранятся фразы для Алисы (возможность добавить разные языки в игру)
