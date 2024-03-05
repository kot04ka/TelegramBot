# Импорт необходимых библиотек
import telebot
import mysql.connector
from threading import Timer
import threading
import schedule
import time
from telebot import types
from datetime import datetime, timedelta
from dateutil.parser import parse
from apscheduler.schedulers.background import BackgroundScheduler
import random
from advice_lists import advice_start, advice_action, advice_end
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
# Токен бота 
bot = telebot.TeleBot('6166430773:AAGUFrcEN1Mkx4QYMU7Xx8fPwHUU0Sga3do')


# Подключение к базе данных MySQL
db = mysql.connector.connect(
    host="localhost",
    user="kot04ka",
    password="1111",
    database="users"
)
cursor = db.cursor()


#================================Базовые Функции========================================
#================================Базовые Функции========================================
def start_test(message):
    print("Start test function called")
    bot.reply_to(message,"Выберете тест который вы хотите пройти ")
    

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    # Запрос к базе данных для получения имени пользователя
    cursor.execute("SELECT fullname FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    # Если пользователь найден в базе данных, приветствуем его по имени
    if user is not None:
        bot.reply_to(message, f"Привет, {user[0]}! Чем я могу помочь вам сегодня?")
    # Если пользователь не найден в базе данных, приветствуем его и просим ввести ФИО
    else:
        bot.reply_to(message, "Привет! Я ваш виртуальный психолог. Чем я могу помочь вам сегодня?")
        bot.send_message(message.chat.id, "Пожалуйста, введите ваше ФИО:")
        bot.register_next_step_handler(message, save_fullname)

# Функция для сохранения ФИО пользователя в базе данных
def save_fullname(message):
    user_id = message.from_user.id
    fullname = message.text
    # Запрос на вставку данных пользователя в базу данных
    sql = "INSERT INTO users (user_id, fullname) VALUES (%s, %s)"
    val = (user_id, fullname)
    cursor.execute(sql, val)
    db.commit()
    # После сохранения ФИО пользователя, просим его ввести номер телефона
    bot.send_message(message.chat.id, f"Спасибо, {fullname}! Теперь введите ваш номер телефона или напишите 'нет', если не хотите указывать:")
    bot.register_next_step_handler(message, save_phone)
    
# Функция для сохранения номера телефона пользователя в базе данных
def save_phone(message):
    user_id = message.from_user.id
    phone = message.text
    # Если пользователь не хочет указывать номер телефона, сохраняем вместо него '#'
    if phone.lower() == 'нет':
        phone = '#'
    # Запрос на обновление номера телефона пользователя в базе данных
    sql = "UPDATE users SET phone = %s WHERE user_id = %s"
    val = (phone, user_id)
    cursor.execute(sql, val)
    db.commit()
    # После сохранения номера телефона пользователя, благодарим его
    bot.send_message(message.chat.id, "Спасибо! Ваш номер телефона сохранен." if phone != '#' else "Спасибо! Выбор без указания номера телефона сохранен.")
    bot.send_message(message.chat.id, "Благодарим за регистрацию! Чтобы узнать доступные команды, напишите /help.")



#================================ Конец Базовым Функциям ========================================
#================================ Конец Базовым Функциям ========================================
    

# Создаем внешний словарь для хранения информации о активном тесте пользователями
active_tests = {}

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def send_help(message):
    # Создаем кнопки для выбора действия
    markup = types.InlineKeyboardMarkup()
    tests_button = types.InlineKeyboardButton('Посмотреть все тесты', callback_data='tests')
    sleep_button = types.InlineKeyboardButton('Получить совет по сну', callback_data='sleep_tip')
    remind_button = types.InlineKeyboardButton('Установить напоминание', callback_data='remind')
    markup.add(tests_button)
    markup.add(sleep_button)
    markup.add(remind_button)
    # Отправляем сообщение с кнопками
    bot.send_message(message.chat.id, "То что я умею:", reply_markup=markup)

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    # Проверяем, есть ли у пользователя активный тест
    if call.message.chat.id in active_tests:
        bot.answer_callback_query(call.id, "У вас уже есть активный тест.")
        return

    # Запускаем соответствующий тест в зависимости от выбора пользователя
    if call.data == 'tests':
        send_tests(call.message)
    elif call.data == 'sleep_tip':
        handle_sleep_tip(call.message)
    elif call.data == 'remind':
        bot.send_message(call.message.chat.id, 'Введите данные для напоминания в формате: /remind [текст напоминания] [дата и время] [интервал]')
    elif call.data == 'test-1':
        start_anxiety_test(call.message)
        active_tests[call.message.chat.id] = 'test-1'
        
    elif call.data == 'test-2':
        start_yesno_test(call.message)
        active_tests[call.message.chat.id] = 'test-2'
#================================ Конец Базовым Функциям ========================================
#================================ Конец Базовым Функциям ========================================




#================================ Тестирование ========================================
#================================ Тестирование ========================================

# Обработчик команды для начала тестирования
def start_test(message):
    bot.reply_to(message,"Выберете тест который вы хотите пройти ")

# Обработчик команды для прохождения теста на уровень тревожности
@bot.message_handler(commands=['test-1'])
def start_anxiety_test(message):
    # Создаем словарь для данного пользователя
    user_data[message.from_user.id] = {}
    bot.reply_to(message, "Давайте проверим ваш уровень тревожности. Пожалуйста, ответьте на следующие вопросы числами от 1 до 5, где 1 - совсем не так, а 5 - очень сильно.")
    bot.send_message(message.chat.id, "1. Чувствуете ли вы постоянное беспокойство и нервозность?")
    bot.register_next_step_handler(message, question_2)

# Функция для обработки второго вопроса теста
def question_2(message):
    try:
        response = int(message.text)
        # Если ответ не в диапазоне от 1 до 5, вызываем исключение
        if response < 1 or response > 5:
            raise ValueError
        
        # Проверяем, есть ли уже словарь для этого пользователя
        if message.from_user.id not in user_data:
            user_data[message.from_user.id] = {}
            
        # Сохраняем ответ пользователя
        user_data[message.from_user.id]['Вопрос 1'] = response

        # Подключаемся к базе данных
        db = mysql.connector.connect(
            host="localhost",
            user="kot04ka",
            password="1111",
            database="users"
        )
        cursor = db.cursor()

        # Получаем ФИО и номер телефона пользователя из базы данных
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

        # Вставляем данные в таблицу testresults
        query = "INSERT INTO testresults (fullname, phone_number, answers, test_date) VALUES (%s, %s, %s, %s)"
        values = (fullname, phone_number, answers, test_date)

        cursor.execute(query, values)

        # Подтверждаем транзакцию
        db.commit()

        # Если уровень тревожности высокий, рекомендуем обратиться к специалисту
        if response >= 4:
            bot.send_message(message.chat.id, "Ваш уровень тревожности высокий. Рекомендуется обратиться к специалисту.")
        else:
            bot.send_message(message.chat.id, "Ваш уровень тревожности находится в пределах нормы.")
        del active_tests[message.chat.id]
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

# Функция для обработки второго вопроса теста
def yesno_question_2(message):
    try:
        response = message.text.lower()
        # Если ответ не 'да' или 'нет', вызываем исключение
        if response not in ['да', 'нет']:
            raise ValueError

        # Сохраняем ответ пользователя
        user_data[message.from_user.id]['Вопрос 1'] = response

        # Продолжаем с следующим вопросом
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

        # Продолжаем с следующим вопросом
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

        # Подключаемся к базе данных
        db = mysql.connector.connect(
            host="localhost",
            user="kot04ka",
            password="1111",
            database="users"
        )
        cursor = db.cursor()


        # Получаем ФИО и номер телефона пользователя из базы данных
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

        # Вставляем данные в таблицу test2results
        query = "INSERT INTO test2results (fullname, phone_number, answers, test_date) VALUES (%s, %s, %s, %s)"
        values = (fullname, phone_number, answers, test_date)

        cursor.execute(query, values)

        # Подтверждаем транзакцию
        db.commit()

        # Завершаем тест
        bot.send_message(message.chat.id, "Спасибо за прохождение теста!")
        del active_tests[message.chat.id]
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, ответьте 'да' или 'нет'.")
        bot.register_next_step_handler(message, yesno_question_4)



#================================ Конец Тестирование ========================================
#================================ Конец Тестирование ========================================


#================================ Трекер напоминаний ========================================
#================================ Трекер напоминаний ========================================
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
    if interval in [1]:  # одноразовое напоминание
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
    
    # Преобразуем интервал в число
    try:
        interval = int(parts[-1])
    except ValueError:
        bot.reply_to(message, 'Интервал должен быть числом.')
        return

    # Устанавливаем напоминание
    set_reminder(chat_id, text, datetime_str, interval)
    bot.reply_to(message, 'Напоминание установлено!')

#================================ Конец Трекер напоминаний ========================================
#================================ Конец Трекер напоминаний ========================================

#================================ Функция Советы по сну ========================================
#================================ Функция Советы по сну ========================================

# Функция для получения совета по сну
def get_sleep_tip():
    # Выбираем случайный совет из списка
    advice = random.choice(advice_start) + ' ' + random.choice(advice_action) + ' ' + random.choice(advice_end)
    return advice

# Обработчик команды для получения совета по сну
@bot.message_handler(commands=['sleep_tip'])
def handle_sleep_tip(message):
    chat_id = message.chat.id
    # Получаем совет и отправляем его пользователю
    sleep_tip = get_sleep_tip()
    bot.send_message(chat_id, sleep_tip)

#================================ Конец Функция Советы по сну ========================================
#================================ Конец Функция Советы по сну ========================================


#================================  Дневник настроения========================================
#================================ Дневник настроения ========================================

# Создание подключение к базе данных
db = mysql.connector.connect(
    host="localhost",
    user="kot04ka",
    password="1111",
    database="users"
)


# Создание курсора для выполнения запросов в БД
cursor = db.cursor()

# Обработчик команды /mood
@bot.message_handler(commands=['mood'])
def mood(message):
    # Отправление пользователю сообщения с просьбой ввести свое настроение
    msg = bot.send_message(message.chat.id, "Введите ваше настроение")
    # Регистрируем следующий шаг
    bot.register_next_step_handler(msg, save_mood)

# Функция для сохранения настроения пользователя в базе данных
def save_mood(message):
    # Получаем настроение пользователя
    mood = message.text
    # Получаем id пользователя
    user_id = message.from_user.id
    # Получаем полное имя пользователя
    full_name = message.from_user.full_name
    # Получаем текущую дату
    date = datetime.now()
    # Вставляем данные пользователя в базу данных
    sql = "INSERT INTO mood (user_id, FullName, date, mood) VALUES (%s, %s, %s, %s)"
    val = (user_id, full_name, date, mood)
    # Выполняем запрос
    cursor.execute("ALTER TABLE mood ALTER COLUMN ID SET DEFAULT 0;")
    # Выполняем запрос с параметрами и сохраняем изменения
    cursor.execute(sql, val)
    db.commit()
    # Отправляем сообщение пользователю с подтверждением сохранения настроения
    bot.send_message(message.chat.id, "Ваше настроение сохранено")


#================================ Дневник настроения========================================
#================================  Дневник настроения========================================

#================================  ========================================
#================================ ========================================
# Обработчик команды /tests
@bot.message_handler(commands=['tests'])
def send_tests(message):
    # Создаем кнопки для выбора теста
    markup = types.InlineKeyboardMarkup()
    test1_button = types.InlineKeyboardButton('Тест 1', callback_data='test-1')
    test2_button = types.InlineKeyboardButton('Тест 2', callback_data='test-2')
    markup.add(test1_button, test2_button)
    # Отправляем сообщение с кнопками
    bot.send_message(message.chat.id, "Выберите тест:", reply_markup=markup)
# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    # Запускаем соответствующий тест в зависимости от выбора пользователя
    if call.data == 'test-1':
        start_anxiety_test(call.message)
    elif call.data == 'test-2':
        start_yesno_test(call.message)
        
#================================ конец Обработoк всех кнопок ========================================
#================================ конец Обработoк всех кнопок ===================================



#================================ Функция для запуска бота ========================================
#================================ Функция для запуска бота ========================================

# Функция для запуска планировщика заданий
def run_schedule():
    while True:
        # Запускаем все запланированные задания
        schedule.run_pending()
        time.sleep(1)

# Запуск цикла в отдельном потоке
schedule_thread = threading.Thread(target=run_schedule)
schedule_thread.start()

# Обработчик для других сообщений
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    # Если бот не понял сообщение пользователя, он просит пользователя ввести команду /help
    bot.reply_to(message, "Извините, я не понял вашего сообщения. Если вам нужна помощь, введите /help.")

# Запуск бота
bot.polling()

#================================ Функция для запуска бота ========================================
#================================ Функция для запуска бота ========================================

