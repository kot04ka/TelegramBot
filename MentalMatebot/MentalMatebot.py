import telebot
import sqlite3
import openai
from telebot import types
import random
from bs4 import BeautifulSoup
import threading
import json
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from sqlite3 import Error
from queue import Queue
from threading import Thread, current_thread
import requests
from jokes import jokes_list
import base64
from io import BytesIO
from PIL import Image
# Your bot code here
# Declare the global variable
conversation_active = False



# Создаем новый экземпляр бота
bot = telebot.TeleBot('6166430773:AAHqpvwfB2eY7nJXUa4EdZ8kNDkr9zFrP8I')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    name = message.chat.first_name
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    existing_user = cursor.fetchone()
    if existing_user:
        bot.reply_to(message, "Welcome back., " + name + "!")
    else:
        cursor.execute("INSERT INTO users (user_id, name) VALUES (?, ?)", (user_id, name))
        conn.commit()
        bot.reply_to(message, "Hello " + name + ", I am your bot helper, type /help in the chatbox to learn my skills. be careful some commands require a  `/` and some do not, you can tell by looking at the tips")
    cursor.close()
    conn.close()

# Initialize database connection
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS mytable (id INTEGER PRIMARY KEY, wish TEXT)')

# Define a function to handle the wish command
@bot.message_handler(commands=['wish'])
def handle_wish_command(message):
    # Set the bot's state to "waiting_for_wish"
    bot.register_next_step_handler(message, handle_wish_response)
    bot.send_message(message.chat.id, "What is your wish?")

# Define a function to handle the user's response to the wish question
def handle_wish_response(message):
    # Get the user's chat ID and wish text
    user_id = message.chat.id
    text = message.text

    # Insert the wish into the database
    cursor.execute('INSERT INTO wishes (user_id, text) VALUES (?, ?)', (user_id, text))
    conn.commit()

    # Send a message to acknowledge the user's wish
    bot.reply_to(message, "Your wish has been added to the database.")

# Define a function to handle the showwishes command
@bot.message_handler(commands=['showwishes'])
def handle_show_wishes_command(message):
    try:
        cursor.execute('SELECT * FROM wishes')
        wishes = cursor.fetchall()
        if len(wishes) == 0:
            bot.send_message(message.chat.id, "No wishes found.")
        else:
            response = "Here are the wishes that have been made:\n\n"
            for wish in wishes:
                response += f"- {wish[2]}\n"
            bot.send_message(message.chat.id, response)
    except Exception as e:
        bot.send_message(message.chat.id, "Sorry, an error occurred while retrieving the wishes.")
        print(e)

def generate_joke(prompt):
    # Get your OpenAI API key from the Secret Manager
    assert "openai" in openai_secret_manager.get_services()
    secrets = openai_secret_manager.get_secret("openai")
    # Authenticate with the API
    openai.api_key = secrets["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"]

    # Generate joke with OpenAI's GPT-3 language model
    completions = openai.Completion.create(
        engine="text-ada-001",
        prompt=prompt,
        max_tokens=600,
        n=1,
        stop=None,
        temperature=0.5
    )

    # Format and return the joke
    joke = completions.choices[0].text.strip()
    return joke.capitalize()

# Define the 'poll' command handler
@bot.message_handler(commands=['poll'])
def poll_command_handler(message):
    # Create a keyboard with mood options
    mood_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    mood_keyboard.row(types.KeyboardButton('😀 Good'), types.KeyboardButton('😕 Not so good'))

    # Ask how the user is doing and prompt them to select their mood
    poll_message = bot.send_message(message.chat.id, "How are you doing today?", reply_markup=mood_keyboard)

    # Wait for the user's mood response
    bot.register_next_step_handler(poll_message, handle_mood_response)


# Define a function to handle the user's mood response
def handle_mood_response(message):
    # Get the user's mood from their response
    mood = message.text.lower()

    # Create a keyboard with activity options
    activity_keyboard = types.InlineKeyboardMarkup(row_width=2)

    # Suggest options based on the user's mood
    if 'good' in mood:
        game_button = types.InlineKeyboardButton('Play a game 🎮', callback_data='game')
        movie_button = types.InlineKeyboardButton('Watch a movie 🎬', callback_data='movie')
        activity_keyboard.add(game_button, movie_button)
        bot.send_message(message.chat.id, "That's great to hear! Here are a couple things you could do:", reply_markup=activity_keyboard)
    else:
        anime_button = types.InlineKeyboardButton('Watch anime 🐉', callback_data='anime')
        film_button = types.InlineKeyboardButton('Watch a movie 🍿', callback_data='film')
        activity_keyboard.add(anime_button, film_button)
        bot.send_message(message.chat.id, "I'm sorry to hear that. Here are a couple things that might help you feel better:", reply_markup=activity_keyboard)

@bot.callback_query_handler(func=lambda call: True)
def handle_activity_selection(call):
    if call.data == 'game':
        bot.send_message(call.message.chat.id, "How about trying a fun game? 🕹️")
        guess_number(call.message.chat.id)
    elif call.data == 'movie':
        movie_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        movie_keyboard.row(types.KeyboardButton('/anime'), types.KeyboardButton('/film'))
        bot.send_message(call.message.chat.id, "How about watching a movie? 🍿", reply_markup=movie_keyboard)
    elif call.data == 'anime':
        bot.send_message(call.message.chat.id, "Here are some anime recommendations 🐉")
        # code for suggesting anime options
    elif call.data == 'film':
        bot.send_message(call.message.chat.id, "Here are some movie recommendations 🎬")
        # code for suggesting movie options)

# Define a function for the game
def guess_number(chat_id):
    # Generate a random number between 1 and 10
    secret_number = random.randint(1, 10)
    # Set the number of attempts to 2
    attempts = 2

    # Ask the user to guess the number
    bot.send_message(chat_id, "I'm thinking of a number between 1 and 10. Can you guess what it is? You have two attempts.")

    # Define a function to handle the user's guess
    @bot.message_handler(func=lambda message: True)
    def handle_guess(message):
        nonlocal attempts

        # Check if the user's guess is correct
        try:
            guess = int(message.text)
        except ValueError:
            bot.send_message(chat_id, "Please enter a number between 1 and 10.")
            return

        if guess == secret_number:
            bot.send_message(chat_id, "Congratulations, you guessed the number! 🎉😃")
            # Ask the user if they want to play again
            bot.send_message(chat_id, "Do you want to play again?")
            bot.register_next_step_handler(message, play_again)
        elif attempts > 1:
            if guess < secret_number:
                bot.send_message(chat_id, "Sorry, your guess is too low. Try again. 😯")
            else:
                bot.send_message(chat_id, "Sorry, your guess is too high. Try again. 😰😢")
            attempts -= 1
            bot.send_message(chat_id, f"You have {attempts} attempts left.")
            bot.register_next_step_handler(message, handle_guess)
        else:
            bot.send_message(chat_id, f"Sorry, you lost! The secret number was {secret_number}. 😔")
            # Ask the user if they want to play again
            bot.send_message(chat_id, "Do you want to play again?")
            bot.register_next_step_handler(message, play_again)

    # Wait for the user's guess
    bot.register_next_step_handler(bot.send_message(chat_id, "Make a guess!"), handle_guess)


def play_again(message):
    if message.text.lower() == "yes":
        guess_number(message.chat.id)
    else:
        bot.send_message(message.chat.id, "Thank you for playing! How can I assist you further?")



openai.api_key = "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"
# Define a function to handle the user's response to the joke question
def handle_joke_response(message):
    if message.text.lower() == "yes":
        # Generate a joke using OpenAI
        response = openai.Completion.create(
            engine="text-ada-001",
            prompt="Tel me a joke",
            max_tokens=620,
            n=1,
            stop=None,
            temperature=0.5,
        )
        joke = response.choices[0].text.strip()
        bot.send_message(message.chat.id, joke)
    elif message.text.lower() == "no":
        # Apologize and ask what else the bot can do
        bot.send_message(message.chat.id, "Sorry to hear that. What else can I help you with?")
    else:
        # Invalid response, ask again
        joke_message = bot.send_message(message.chat.id, "Sorry, I didn't understand. Do you want to hear a joke? (Yes/No)")
        bot.register_next_step_handler(joke_message, handle_joke_response)

def handle_yes_message():
    joke = random.choice(jokes_list)
    return f"Joke's on you:\n{joke}"
help_keyboard = types.InlineKeyboardMarkup(row_width=1)
@bot.message_handler(commands=['joke'])
def joke_handler(message):
    response = requests.get('https://official-joke-api.appspot.com/random_joke')
    if response.status_code == 200:
        joke = response.json()
        bot.reply_to(message, f"{joke['setup']} \n\n {joke['punchline']}")
    else:
        bot.reply_to(message, "Oops! Something went wrong. I couldn't generate a joke.")
@bot.message_handler(commands=['help'])
def help_handler(message):
    # Текст для вывода в сообщении
    text = 'Commands: \n/music - random music Good songs from the spotify MentalMate_playlist \n/film - take name random film\n/anime - take name random anime serial\n/creators - Bot creator accounts\nsend me a photo - i`m give you random photo,\n/poll - survey how you`re doing\n/help - get a list of bot commands and their designations\n/joke - the bot will tell you a very funny joke,\n/wish to leave feedback or wish for improvement'
     # Отправляем сообщение с клавиатурой
    bot.send_message(message.chat.id, text, reply_markup=help_keyboard)
@bot.message_handler(func=lambda message: message.text == 'Tell me about yourself')
def about_handler(message):
    bot.send_message(message.chat.id, 'Im a MentalMate bot designed to help people with their emotional well-being \nMy main function is to provide tips on improving mood and dealing with fatigue, anxiety and depression \n I can also share with you resources and exercises to help you manage your emotions.', reply_markup=main_keyboard)
print(handle_yes_message())
@bot.message_handler(commands=['creators'])
def help_handler(message):
    # Текст для вывода в сообщении
    text = 'Main Creators:@Franktur\n testers:@Queen_of_memes_and_wine\n graphic designer:@Queen_of_memes_and_wine'
     # Отправляем сообщение с клавиатурой
    bot.send_message(message.chat.id, text, reply_markup=help_keyboard)

client_id = '6cf50693b6a94723b46e6f6fafbc9d4a'
client_secret = '881387b605d14977932999c8143d3163'

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def send_music(chat_id, language):
    # Generate a music genre prompt based on the requested language
    if language == 'english':
        prompt = 'Generate a random music genre (not sad) in English'
    else:
        prompt = 'Generate a random music genre (not sad) in Russian'
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.5,
    )
    genre = response.choices[0].text.strip()
    print(f"Generated genre: {genre}")

    # Search for playlists in the generated genre on Spotify
    search_results = sp.search(q=f'MentalMate_playlist"', type='playlist', market='US')
    playlists = search_results['playlists']['items']
    if playlists:
        # Choose a random playlist from the search results
        playlist = random.choice(playlists)
        playlist_name = playlist['name']
        playlist_link = playlist['external_urls']['spotify']
        message = f"Here's a {genre} playlist for you: {playlist_name}\n{playlist_link}"
    else:
        message = f"Sorry, no {genre} playlists were found."
    bot.send_message(chat_id, message)

played_songs = []

@bot.message_handler(commands=['music'])
def handle_music_command(message):
    # Define a list of genres and exclude sad songs
    genres = ['rock', 'pop', 'hip hop', 'country', 'reggae']
    prompt = "Generate a random upbeat song on Spotify"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    song_name = response.choices[0].text.strip().replace('\n', '').replace('"', '')

    try:
        # Search for the song on Spotify
        results = sp.search(q=song_name, limit=1, type='track')
        if results['tracks']['items']:
            song_uri = results['tracks']['items'][0]['uri']
            if 'open.spotify.com' in song_uri:
                song_url = song_uri
            else:
                song_url = f"https://open.spotify.com/track/{song_uri.split(':')[-1]}"
            
            # Check if the song has already been played
            if song_uri in played_songs:
                bot.send_message(message.chat.id, "Sorry, I couldn't find a new song. Please try again later.")
            else:
                played_songs.append(song_uri)
                bot.send_message(message.chat.id, song_url)
        else:
            bot.send_message(message.chat.id, "Sorry, I couldn't find a song. Please try again later.")
    except spotipy.exceptions.SpotifyException:
        bot.send_message(message.chat.id, "Sorry, there was an error searching for a song. Please try again later.")


# Define the /film command
@bot.message_handler(commands=['film'])
def handle_film_command(message):
    prompt = "Generate a random movie title"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        #temperature=0.5,
    )
    film_title = response.choices[0].text.strip()
    bot.reply_to(message, f"Random film: {film_title}")

    # Search for the film on IMDb
    search_url = f"https://www.imdb.com/find?q={film_title}&ref_=nv_sr_sm"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    result = soup.find(class_='result_text')
    if result:
        film_link = f"https://www.imdb.com{result.a['href']}"
        bot.send_message(message.chat.id, f"IMDb link for {film_title}: {film_link}")
    else:
        pass

# Define the /anime command
@bot.message_handler(commands=['anime'])
def handle_anime_command(message):
    prompt = "Generate a random anime title"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.5,
    )
    anime_title = response.choices[0].text.strip()
    bot.reply_to(message, f"Random anime: {anime_title}")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text.lower() == 'send me a photo':
        # Ask the user to enter a keyword for generating a photo
        bot.send_message(message.chat.id, "Please enter a keyword for the photo:")

        # Wait for the user's response
        bot.register_next_step_handler(message, generate_photo)

def generate_photo(message):
    # Use the user's keyword to generate a photo from Unsplash
    keyword = message.text
    response = requests.get(f'https://api.unsplash.com/photos/random?query={keyword}&orientation=landscape', headers={'Authorization': 'Client-ID BpO15_hO2JpDOcVfTV9hywhNHrkyt0MCKidLj2XBzSg'})

    if response.status_code == 200:
        # Download the photo to a file
        photo_url = response.json()['urls']['regular']
        photo_file = 'photo.jpg'
        with open(photo_file, 'wb') as f:
            f.write(requests.get(photo_url).content)

        # Send the photo to the user with the keyword as a caption
        with open(photo_file, 'rb') as f:
            bot.send_photo(message.chat.id, f, caption=f"Photo generated based on the keyword '{keyword}'")
    else:
        bot.send_message(message.chat.id, "Sorry, I couldn't find a photo for that keyword.")



# Define the reply keyboard
main_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(types.KeyboardButton('Tell me about yourself'))



def handle_text_message(message):
    bot.send_message(message.chat.id, 'I don`t understand what you`re saying. Try one of the available commands:', reply_markup=main_keyboard)

def handle_continue_conversation_request(message):
    if message.text.lower() == 'yes':
        bot.send_message(message.chat.id, 'Great!', reply_markup=main_keyboard)
    else:
        bot.send_message(message.chat.id, 'Too bad. If you need anything, I`m always here!', reply_markup=main_keyboard)

def sum_digits(n):
    """Returns the sum of digits of a non-negative integer n."""
    return sum(map(int, str(n)))



def is_happy_number(n):
    """
    Функция проверяет, является ли переданное число счастливым.
    """
    seen_numbers = set()  # Множество для хранения уже просмотренных чисел.
    while n != 1:  # Продолжаем, пока число не станет равным 1.
        if n in seen_numbers:  # Если число уже было просмотрено, то оно не счастливое.
            return False
        seen_numbers.add(n)  # Добавляем число в множество просмотренных.
        n = sum_digits(n ** 2)  # Считаем сумму квадратов цифр числа.
    return True  # Число счастливое, если мы добрались до 1.

# Примеры использования функций:
print(sum_digits(123))  # Выведет 6.
print(is_happy_number(19))  # Выведет True.
print(is_happy_number(123))  # Выведет False.


# Запускаем бота
bot.polling()