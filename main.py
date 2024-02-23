
import telebot
import mysql.connector
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
        if response >= 4:
            bot.send_message(message.chat.id, "Ваш уровень тревожности высокий. Рекомендуется обратиться к специалисту.")
        else:
            bot.send_message(message.chat.id, "Ваш уровень тревожности находится в пределах нормы.")
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите числа от 1 до 5.")



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

bot.polling()