
import telebot
import mysql.connector
from threading import Timer
import threading
import schedule
import time

from datetime import datetime, timedelta
from dateutil.parser import parse
from apscheduler.schedulers.background import BackgroundScheduler
import random
from advice_lists import advice_start, advice_action, advice_end
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

#Token бота 
bot = telebot.TeleBot('6166430773:AAHqpvwfB2eY7nJXUa4EdZ8kNDkr9zFrP8I')

# Подключение к базе данных MySQL
db = mysql.connector.connect(
    host="localhost",
    user="kot04ka",
    password="1111",
    database="users"
)
cursor = db.cursor()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    cursor.execute("SELECT fullname FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    if user is not None:
        bot.reply_to(message, f"Привет, {user[0]}! Чем я могу помочь вам сегодня?")
    else:
        bot.reply_to(message, "Привет! Я ваш виртуальный психолог. Чем я могу помочь вам сегодня?")
        bot.send_message(message.chat.id, "Пожалуйста, введите ваше ФИО:")
        bot.register_next_step_handler(message, save_fullname)
def save_fullname(message):
    user_id = message.from_user.id
    fullname = message.text
    sql = "INSERT INTO users (user_id, fullname) VALUES (%s, %s)"
    val = (user_id, fullname)
    cursor.execute(sql, val)
    db.commit()
    bot.send_message(message.chat.id, f"Спасибо, {fullname}! Теперь введите ваш номер телефона или напишите 'нет', если не хотите указывать:")
    bot.register_next_step_handler(message, save_phone)

def save_phone(message):
    user_id = message.from_user.id
    phone = message.text
    if phone.lower() == 'нет':
        phone = '#'
    sql = "UPDATE users SET phone = %s WHERE user_id = %s"
    val = (phone, user_id)
    cursor.execute(sql, val)
    db.commit()
    bot.send_message(message.chat.id, "Спасибо! Ваш номер телефона сохранен." if phone != '#' else "Спасибо! Выбор без указания номера телефона сохранен.")

#Обработка команды тесты
def start_test(message):
    bot.reply_to(message,"Выберете тест который вы хотите пройти ")


#test

# Обработчик команды для прохождения теста на уровень тревожности
@bot.message_handler(commands=['test-1'])
def start_anxiety_test(message):
    # Создаем словарь для данного пользователя
    user_data[message.from_user.id] = {}
    bot.reply_to(message, "Давайте проверим ваш уровень тревожности. Пожалуйста, ответьте на следующие вопросы числами от 1 до 5, где 1 - совсем не так, а 5 - очень сильно.")
    bot.send_message(message.chat.id, "1. Чувствуете ли вы постоянное беспокойство и нервозность?")
    bot.register_next_step_handler(message, question_2)

def question_2(message):
    try:
        response = int(message.text)
        if response < 1 or response > 5:
            raise ValueError

        # Сохраняем ответ пользователя
        user_data[message.from_user.id]['Вопрос 1'] = response

        # Connect to the database
        db = mysql.connector.connect(
            host="localhost",
            user="kot04ka",
            password="1111",
            database="users"
        )
        cursor = db.cursor()

        # Get the user's fullname and phone_number from the database
        user_id = message.from_user.id
        cursor.execute("SELECT fullname, phone FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if user is not None:
            fullname, phone_number = user
        else:
            fullname, phone_number = "Unknown", "Unknown"

        # Преобразуем словарь с ответами пользователя в строку
        answers = str(user_data[message.from_user.id])

        # Получаем текущую дату и время
        test_date = datetime.now()

        # Insert the data into the testresults table
        query = "INSERT INTO testresults (fullname, phone_number, answers, test_date) VALUES (%s, %s, %s, %s)"
        values = (fullname, phone_number, answers, test_date)

        cursor.execute(query, values)

        # Commit the transaction
        db.commit()

        if response >= 4:
            bot.send_message(message.chat.id, "Ваш уровень тревожности высокий. Рекомендуется обратиться к специалисту.")
        else:
            bot.send_message(message.chat.id, "Ваш уровень тревожности находится в пределах нормы.")
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите числа от 1 до 5.")
        bot.register_next_step_handler(message, question_2)


# Создаем глобальный словарь для хранения ответов пользователя
user_data = {}

# Обработчик команды для прохождения нового теста
@bot.message_handler(commands=['test-2'])
def start_yesno_test(message):
    # Создаем словарь для данного пользователя
    user_data[message.from_user.id] = {}
    bot.reply_to(message, "Давайте пройдем новый тест. Пожалуйста, ответьте 'да' или 'нет' на следующие вопросы.")
    bot.send_message(message.chat.id, "1. Вопрос 1?")
    bot.register_next_step_handler(message, yesno_question_2)

def yesno_question_2(message):
    try:
        response = message.text.lower()
        if response not in ['да', 'нет']:
            raise ValueError

        # Сохраняем ответ пользователя
        user_data[message.from_user.id]['Вопрос 1'] = response

        # Continue with the next question
        bot.send_message(message.chat.id, "2. Вопрос 2?")
        bot.register_next_step_handler(message, yesno_question_3)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, ответьте 'да' или 'нет'.")
        bot.register_next_step_handler(message, yesno_question_2)

# Аналогично для остальных вопросов...
def yesno_question_3(message):
    try:
        response = message.text.lower()
        if response not in ['да', 'нет']:
            raise ValueError

        # Сохраняем ответ пользователя
        user_data[message.from_user.id]['Вопрос 2'] = response

        # Continue with the next question
        bot.send_message(message.chat.id, "3. Вопрос 3?")
        bot.register_next_step_handler(message, yesno_question_4)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, ответьте 'да' или 'нет'.")
        bot.register_next_step_handler(message, yesno_question_3)
        
def yesno_question_4(message):
    try:
        response = message.text.lower()
        if response not in ['да', 'нет']:
            raise ValueError

        # Сохраняем ответ пользователя
        user_data[message.from_user.id]['Вопрос 3'] = response

        # Connect to the database
        db = mysql.connector.connect(
            host="localhost",
            user="kot04ka",
            password="1111",
            database="users"
        )
        cursor = db.cursor()

        # Get the user's fullname and phone_number from the database
        user_id = message.from_user.id
        cursor.execute("SELECT fullname, phone FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if user is not None:
            fullname, phone_number = user
        else:
            fullname, phone_number = "Unknown", "Unknown"

        # Преобразуем словарь с ответами пользователя в строку
        answers = str(user_data[message.from_user.id])

        # Получаем текущую дату и время
        test_date = datetime.now()

        # Insert the data into the test2results table
        query = "INSERT INTO test2results (fullname, phone_number, answers, test_date) VALUES (%s, %s, %s, %s)"
        values = (fullname, phone_number, answers, test_date)

        cursor.execute(query, values)

        # Commit the transaction
        db.commit()

        # Finish the test
        bot.send_message(message.chat.id, "Спасибо за прохождение теста!")
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, ответьте 'да' или 'нет'.")
        bot.register_next_step_handler(message, yesno_question_4)



# Трекер напоминаний
reminders = {}

# Создаем планировщик заданий, который будет управлять напоминаниями
scheduler = BackgroundScheduler()
scheduler.start()

# Функция для отправки напоминания
def send_reminder(chat_id, text):
    bot.send_message(chat_id, text)

# Функция для установки напоминания
def set_reminder(chat_id, text, datetime_str, interval):
    # Преобразуем строку даты и времени в объект datetime
    try:
        remind_datetime = parse(datetime_str)
    except ValueError:
        bot.send_message(chat_id, 'Неверный формат времени даты. Используйте YYYY-MM-DD HH:MM.')
        return

    # Преобразуем интервал в число
    try:
        interval = int(interval)
    except ValueError:
        bot.send_message(chat_id, 'Интервал должен быть числом.')
        return

    # Устанавливаем напоминание в планировщике заданий
    if interval in [1, 2]:  # одноразовое напоминание
        scheduler.add_job(send_reminder, 'date', run_date=remind_datetime, args=[chat_id, text])
    elif interval > 2:  # повторяющееся напоминание
        scheduler.add_job(send_reminder, 'interval', days=interval, start_date=remind_datetime, args=[chat_id, text])
    else:
        bot.send_message(chat_id, 'Неверный интервал. Используйте "1" или "2" для одноразовых напоминаний и числа больше 2 для повторяющихся напоминаний.')

# Обработчик команды /remind
@bot.message_handler(commands=['remind'])
def handle_remind(message):
    chat_id = message.chat.id
    parts = message.text.split()

    # Проверяем, что команда введена правильно
    if len(parts) < 4:
        bot.reply_to(message, 'Неверный формат команды. Используйте: /remind [текст напоминания] [дата и время] [интервал]')
        return

    # Извлекаем текст напоминания, дату и время, и интервал из команды
    text = ' '.join(parts[1:-3])
    datetime_str = ' '.join(parts[-3:-1])
    interval = parts[-1]-9

    # Устанавливаем напоминание
    set_reminder(chat_id, text, datetime_str, interval)
    bot.reply_to(message, 'Напоминание установлено!')





#Советы по сну 
def get_sleep_tip():
    advice = random.choice(advice_start) + ' ' + random.choice(advice_action) + ' ' + random.choice(advice_end)
    return advice

# Обработчик команды для получения совета по сну
@bot.message_handler(commands=['sleep_tip'])
def handle_sleep_tip(message):
    chat_id = message.chat.id
    sleep_tip = get_sleep_tip()
    bot.send_message(chat_id, sleep_tip)



#Кнопки












# Обработчик для других сообщений
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Извините, я не понял вашего сообщения. Если вам нужна помощь, введите /help.")


# Обработчик команды для отображения информации о помощи
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
    Добро пожаловать
    Вы можете использовать следующие команды:
    /start - Начать взаимодействие с психологом
    /tests - Посмотреть все тесты :
    /help - Получить информацию о командах бота
    """
    bot.reply_to(message, help_text)



def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Запуск цикла в отдельном потоке
schedule_thread = threading.Thread(target=run_schedule)
schedule_thread.start()
bot.polling()

