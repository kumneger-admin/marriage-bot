import telebot
from telebot import types
import sqlite3
import os

API_TOKEN = '8412575676:AAHEIv8Ao2qdMAPFi0uv3UObM5x2EwTarRU'
bot = telebot.TeleBot(API_TOKEN)
ADMIN_ID = '7014626219' 

def init_db():
    # በ Render ላይ ስህተት እንዳይፈጠር የድሮውን ዳታቤዝ ያጠፋል
    if os.path.exists('kumneger_database.db'):
        os.remove('kumneger_database.db')
    conn = sqlite3.connect('kumneger_database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE users 
                 (chat_id TEXT, name TEXT, gender TEXT, religion TEXT, age TEXT, 
                  address TEXT, service TEXT, phone TEXT, photo_id TEXT, id_photo_id TEXT)''')
    conn.commit()
    conn.close()

user_data = {}

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton('ተመዝገብ (Register)'), 
               types.KeyboardButton('ስለ ኤጀንሲው (About Us)'))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "እንኳን ወደ ቁምነገር ትዳር እና ከፋዮች አገናኛ ኤጀንሲ በሰላም መጡ!", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == 'ስለ ኤጀንሲው (About Us)')
def about_us(message):
    about_text = ("✅ቁምነገር ትዳር እና ከፋዮች አገናኛ ኤጀንሲ ለዘለቄታዊ የትዳር ግንኙነት የሚፈልጉ ግለሰቦችን በጥንቃቄ የሚያገናኝ መሪ ተቋም ነው።\n\n"
                  "ዛሬውኑ ያግኙን እና የትዳር አጋር ፍለጋ ጉዞዎን ይጀምሩ!")
    bot.send_message(message.chat.id, about_text)

@bot.message_handler(func=lambda m: m.text == 'ተመዝገብ (Register)')
def ask_name(message):
    msg = bot.send_message(message.chat.id, "1. ሙሉ ስምዎን ያስገቡ፡", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, process_name)

def process_name(message):
    user_data[message.chat.id] = {'name': message.text}
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('ወንድ', 'ሴት')
    msg = bot.send_message(message.chat.id, "2. ጾታዎን ይምረጡ፡", reply_markup=markup)
    bot.register_next_step_handler(msg, process_gender)

def process_gender(message):
    user_data[message.chat.id]['gender'] = message.text
    msg = bot.send_message(message.chat.id, "3. ሀይማኖትዎን ያስገቡ፡")
    bot.register_next_step_handler(msg, process_religion)

def process_religion(message):
    user_data[message.chat.id]['religion'] = message.text
    msg = bot.send_message(message.chat.id, "4. እድሜዎን ያስገቡ፡")
    bot.register_next_step_handler(msg, process_age)

def process_age(message):
    user_data[message.chat.id]['age'] = message.text
    msg = bot.send_message(message.chat.id, "5. አድራሻ ያስገቡ፡")
    bot.register_next_step_handler(msg, process_address)

def process_address(message):
    user_data[message.chat.id]['address'] = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('ትዳር', 'ሹገር')
    msg = bot.send_message(message.chat.id, "6. የአገልግሎት አይነት ይምረጡ፡", reply_markup=markup)
    bot.register_next_step_handler(msg, process_service)

def process_service(message):
    user_data[message.chat.id]['service'] = message.text
    msg = bot.send_message(message.chat.id, "7. ስልክ ቁጥርዎን ያስገቡ፡")
    bot.register_next_step_handler(msg, process_phone)

def process_phone(message):
    user_data[message.chat.id]['phone'] = message.text
    msg = bot.send_message(message.chat.id, "8. አንድ ጉርድ ፎቶ ይላኩ፡")
    bot.register_next_step_handler(msg, process_photo)

def process_photo(message):
    if message.content_type != 'photo':
        msg = bot.send_message(message.chat.id, "እባክዎ ፎቶ ይላኩ!")
        bot.register_next_step_handler(msg, process_photo)
        return
    user_data[message.chat.id]['photo'] = message.photo[-1].file_id
    msg = bot.send_message(message.chat.id, "9. የመታወቂያ ፎቶ ይላኩ፡")
    bot.register_next_step_handler(msg, process_id_photo)

def process_id_photo(message):
    if message.content_type != 'photo':
        msg = bot.send_message(message.chat.id, "እባክዎ የመታወቂያ ፎቶ ይላኩ!")
        bot.register_next_step_handler(msg, process_id_photo)
        return
    
    chat_id = message.chat.id
    user_data[chat_id]['id_photo'] = message.photo[-1].file_id
    d = user_data[chat_id]

    conn = sqlite3.connect('kumneger_database.db')
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?,?)", 
              (str(chat_id), d['name'], d['gender'], d['religion'], d['age'], d['address'], d['service'], d['phone'], d['photo'], d['id_photo']))
    conn.commit()
    conn.close()

    bot.send_message(chat_id, "ምዝገባውን ስለጨረሱ እናመሰግናለን🙏\n☎️0942176934\n☎️0936213634", reply_markup=main_menu())

    # መረጃውን ወደ አንተ መላክ
    admin_text = f"🚀 አዲስ ተመዝጋቢ!\nስም: {d['name']}\nስልክ: {d['phone']}\nአድራሻ: {d['address']}"
    bot.send_photo(ADMIN_ID, d['photo'], caption=admin_text)
    bot.send_photo(ADMIN_ID, d['id_photo'], caption=f"🪪 መታወቂያ ID: {chat_id}")

if __name__ == "__main__":
    init_db()
    bot.infinity_polling()
