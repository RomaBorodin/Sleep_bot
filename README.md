# Telegram-бот для отслеживания сна  

## Описание проекта  
Этот Telegram-бот позволяет пользователям отслеживать длительность сна, оценивать его качество и оставлять заметки.  
Бот сохраняет историю сна каждого пользователя в **БД** (`sleep.db`), что позволяет не терять данные после перезапуска  

---

## Команды  
- `/sleep` — фиксирует время начала сна  
- `/wake` — фиксирует время пробуждения и рассчитывает длительность сна  
- `/quality X` — позволяет оценить качество сна (где `X` — число от 1 до 10)  
- `/notes ТЕКСТ` — добавляет заметку к последнему завершённому сну  
- `/show_notes` — выводит сохранённые заметки  

---

## Техническая реализация  
- Python + `telebot`
- Данные хранятся в базе данных `sleep.db`, загружаются при запуске и сохраняются после каждой операции  
- Обработаны возможные ошибки (`KeyError`, `ValueError`), чтобы предотвратить сбои  
- Идентификация пользователей по `user_id`, каждый пользователь имеет свою историю сна  
