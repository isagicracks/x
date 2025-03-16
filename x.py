import os
import subprocess
import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "7606853839:AAE0WbYLjgkCcvwB5-f6F3xndE-MpL7e_ag"
OWNER_ID = 6353114118  # Change this to the actual owner ID
admins = set()
allowed_users = {}
bot = telebot.TeleBot(TOKEN)

BASE_DIR = "binary_files"
C_FILES_DIR = os.path.join(BASE_DIR, "c_files")
BINARIES_DIR = os.path.join(BASE_DIR, "binaries")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(C_FILES_DIR, exist_ok=True)
os.makedirs(BINARIES_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

@bot.message_handler(commands=['command'])
def gcc_help(message: Message):
    guide_text = (
        "💻 **GCC Compilation Guide** 💻\n\n"
        "📌 **Basic Compilation:**\n`gcc -o binary_name input_name.c -lpthread -lz -static`\n\n"
        "📌 **Debug Mode:**\n`gcc -g input_name.c -o binary_name`\n\n"
        "📌 **Optimization Mode:**\n`gcc -O3 input_name.c -o binary_name`\n\n"
        "📌 **Multi-File Compilation:**\n`gcc file1.c file2.c -o binary_name`\n\n"
        "📌 **Static Compilation:**\n`gcc -static input_name.c -o binary_name`\n\n"
        "📌 **Windows EXE:**\n`x86_64-w64-mingw32-gcc input_name.c -o output.exe`\n\n"
        "🚀 Use the **best-suited** command for your needs!"
    )
    bot.reply_to(message, guide_text, parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    if message.from_user.id not in allowed_users and message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ You don't have access. Contact the admin for access.")
        return
    intro_text = (
        "🔥 **WELCOME TO THE ULTIMATE C COMPILATION BOT** 🔥\n\n"
        "🚀 **POWERED BY TELEGRAM BOT** 🚀\n\n"
        "💻 Upload a `.c` file, and I'll compile it into a binary! 💻\n\n"
        "📜 **HOW TO USE:**\n"
        "1️⃣ Upload your C file 📂\n"
        "2️⃣ Select Compile (Auto) or send GCC command ⚙️\n"
        "3️⃣ Receive your compiled binary instantly! 🎯\n\n"
        "⚡ **FAST, RELIABLE, AND SECURE!** ⚡"
    )
    bot.reply_to(message, intro_text)

@bot.message_handler(content_types=['document'])
def handle_c_file(message: Message):
    if message.from_user.id not in allowed_users and message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ You don't have access. Contact the admin.")
        return
    
    doc = message.document
    if not doc.file_name.endswith(".c"):
        bot.reply_to(message, "❌ Invalid file! Please upload a C source file (.c).")
        return
    
    file_info = bot.get_file(doc.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    local_c_file = os.path.join(C_FILES_DIR, doc.file_name)
    with open(local_c_file, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("✅ Compile (Auto)", callback_data=f"compile_auto:{doc.file_name}"),
               InlineKeyboardButton("⚙️ Custom Command", callback_data=f"compile_manual:{doc.file_name}"))
    
    bot.reply_to(message, f"✅ File received: {doc.file_name}\nChoose an option:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("compile_auto") or call.data.startswith("compile_manual"))
def compile_callback(call):
    _, filename = call.data.split(":")
    local_c_file = os.path.join(C_FILES_DIR, filename)
    
    if "compile_auto" in call.data:
        compile_c_file_auto(call.message, local_c_file, filename)
    else:
        bot.reply_to(call.message, "⚙️ Send the GCC compile command (or type `/command` for help).")
        bot.register_next_step_handler(call.message, compile_c_file_manual, local_c_file, filename)

def compile_c_file_auto(message: Message, local_c_file: str, c_filename: str):
    binary_name = c_filename.replace(".c", "")
    binary_path = os.path.join(BINARIES_DIR, binary_name)
    compile_command = f"gcc -o {binary_path} {local_c_file} -lpthread -lz -static"
    execute_compilation(message, compile_command, binary_path)

def compile_c_file_manual(message: Message, local_c_file: str, c_filename: str):
    gcc_command = message.text.strip()
    binary_path = os.path.join(BINARIES_DIR, "custom_binary")
    compile_command = gcc_command.replace(c_filename, local_c_file).replace("-o", f"-o {binary_path}")
    execute_compilation(message, compile_command, binary_path)

def execute_compilation(message: Message, compile_command: str, binary_path: str):
    process = subprocess.run(compile_command, shell=True, capture_output=True, text=True)
    if process.returncode == 0:
        bot.reply_to(message, "✅ **Compilation Successful!** Sending binary...")
        with open(binary_path, "rb") as binary_file:
            bot.send_document(message.chat.id, binary_file, caption="🔥 Your compiled binary 🔥")
    else:
        bot.reply_to(message, f"❌ **Compilation Failed:**\n```{process.stderr}```", parse_mode="Markdown")

bot.polling()
