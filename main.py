
import telebot
import mysql.connector
from threading import Timer
import threading
import schedule
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

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
    bot.reply_to(message, "Давайте проверим ваш уровень тревожности. Пожалуйста, ответьте на следующие вопросы числами от 1 до 5, где 1 - совсем не так, а 5 - очень сильно.")
    bot.send_message(message.chat.id, "1. Чувствуете ли вы постоянное беспокойство и нервозность?")
    bot.register_next_step_handler(message, question_2)

def question_2(message):
    try:
        response = int(message.text)
        if response < 1 or response > 5:
            raise ValueError

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

        # Insert the data into the testresults table
        query = "INSERT INTO testresults (fullname, phone_number, answers) VALUES (%s, %s, %s)"
        values = (fullname, phone_number, str(response))

        cursor.execute(query, values)

        # Commit the transaction
        db.commit()

        if response >= 4:
            bot.send_message(message.chat.id, "Ваш уровень тревожности высокий. Рекомендуется обратиться к специалисту.")
        else:
            bot.send_message(message.chat.id, "Ваш уровень тревожности находится в пределах нормы.")
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите числа от 1 до 5.")

# Обработчик команды для прохождения нового теста
@bot.message_handler(commands=['test-2'])
def start_yesno_test(message):
    bot.reply_to(message, "Давайте пройдем новый тест. Пожалуйста, ответьте 'да' или 'нет' на следующие вопросы.")
    bot.send_message(message.chat.id, "1. Вопрос 1?")
    bot.register_next_step_handler(message, yesno_question_2)

def yesno_question_2(message):
    try:
        response = message.text.lower()
        if response not in ['да', 'нет']:
            raise ValueError

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

        # Insert the data into the test2results table
        query = "INSERT INTO test2results (fullname, phone_number, answers) VALUES (%s, %s, %s)"
        values = (fullname, phone_number, response)

        cursor.execute(query, values)

        # Commit the transaction
        db.commit()

        # Continue with the next question
        bot.send_message(message.chat.id, "2. Вопрос 2?")
        bot.register_next_step_handler(message, yesno_question_3)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, ответьте 'да' или 'нет'.")

def yesno_question_3(message):
    try:
        response = message.text.lower()
        if response not in ['да', 'нет']:
            raise ValueError

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

        # Insert the data into the test2results table
        query = "INSERT INTO test2results (fullname, phone_number, answers) VALUES (%s, %s, %s)"
        values = (fullname, phone_number, response)

        cursor.execute(query, values)

        # Commit the transaction
        db.commit()

        # Continue with the next question
        bot.send_message(message.chat.id, "3. Вопрос 3?")
        bot.register_next_step_handler(message, yesno_question_4)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, ответьте 'да' или 'нет'.")

def yesno_question_4(message):
    try:
        response = message.text.lower()
        if response not in ['да', 'нет']:
            raise ValueError

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

        # Insert the data into the test2results table
        query = "INSERT INTO test2results (fullname, phone_number, answers) VALUES (%s, %s, %s)"
        values = (fullname, phone_number, response)

        cursor.execute(query, values)

        # Commit the transaction
        db.commit()

        # Finish the test
        bot.send_message(message.chat.id, "Спасибо за прохождение теста!")
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, ответьте 'да' или 'нет'.")







#Трекер 
reminders = {}

scheduler = BackgroundScheduler()
scheduler.start()

def send_reminder(chat_id, text):
    bot.send_message(chat_id, text)

def set_reminder(chat_id, text, datetime_str, interval):
    try:
        remind_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
    except ValueError:
        bot.send_message(chat_id, 'Invalid datetime format. Use YYYY-MM-DD HH:MM.')
        return

    if interval == 'once':  # one-time reminder
        scheduler.add_job(send_reminder, 'date', run_date=remind_datetime, args=[chat_id, text])
    elif interval.isdigit() and int(interval) >= 1:  # recurring reminder
        scheduler.add_job(send_reminder, 'interval', days=int(interval), start_date=remind_datetime, args=[chat_id, text])
    else:
        bot.send_message(chat_id, 'Invalid interval. Use "once" for one-time reminders and 1 or more for recurring reminders.')
        return

@bot.message_handler(commands=['remind'])
def handle_remind(message):
    chat_id = message.chat.id
    parts = message.text.split()

    if len(parts) < 4:
        bot.reply_to(message, 'Invalid command format. Use: /remind [text] [datetime] [interval]')
        return

    text = ' '.join(parts[1:-3])
    datetime_str = ' '.join(parts[-3:-1])

    try:
        interval = int(parts[-1])
    except ValueError:
        bot.reply_to(message, 'Interval must be a number.')
        return

    set_reminder(chat_id, text, datetime_str, interval)
    bot.reply_to(message, 'Reminder set!')



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

