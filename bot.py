from sqlalchemy.testing.suite.test_reflection import users
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram import Update
import  translations
import API
from telegram import ReplyKeyboardMarkup
import Users
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    filters,
)

# Состояния диалога
ASK_CODE = 1
ASK_WORD= 2
# Старт — запускает диалог
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! У тебя есть код? Введи его:")
    return ASK_CODE  # переходим в состояние "ожидание кода"

# Обработка введённого кода
async def get_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text
    context.user_data["code"] = code  # сохраняем код в память пользователя
    await update.message.reply_text(f"Спасибо! Ты ввёл код: {code}")
    user_id = int(update.effective_user.id)
    first_name = update.effective_user.first_name
    if code == "112233":

        if Users.User.search_user(user_id) is None:
            Users.User.create_user(user_id, first_name)
            await update.message.reply_text(f"Welcome {first_name}")
            print(f" User with ID {user_id} and name {first_name} is created")
        else:
            await update.message.reply_text(f"User {first_name} already created")
        return ConversationHandler.END

    else:
        await update.message.reply_text(f"Код неверный")

        # Отмена (если нужно)
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Диалог отменён.")
    return ConversationHandler.END

async def word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите слово, которое нужно добавить в словарь:")
    return ASK_WORD

async def translation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = Users.User.search_user(user_id)  # получаем объект пользователя

    if user is None:
        await update.message.reply_text("Сначала зарегистрируйтесь через /start")
        return ConversationHandler.END

    word = update.message.text

    await update.message.reply_text(f"Ты ввел слово '{word}', перевожу...")

    meaning = translations.Translator.transl(word)
    if meaning.lower() == word.lower():
        await update.message.reply_text(f"Перевод не найден")
    else:
        await update.message.reply_text(f"Перевод : {meaning}")

        user.add_word(word, meaning)
        print(f"Word   '{word}'  added by {update.effective_user.name}")
        await update.message.reply_text(f"слово '{word}', значение '{meaning}' добавлено в словарь ")

async def show_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = Users.User.search_user(user_id)

    if user is None:
        await update.message.reply_text("Сначала зарегистрируйтесь через /start")
        return

    vocab = translations.Translator.show_vocabular(user)
    await update.message.reply_text(vocab)

async def show_today_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = Users.User.search_user(user_id)

    if user is None:
        await update.message.reply_text("Сначала зарегистрируйтесь через /start")
        return

    vocab = translations.Translator.show_todays_vocabular(user)
    await update.message.reply_text(vocab)

async def delete_last_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = Users.User.search_user(user_id)

    if not user:
        await update.message.reply_text("Сначала зарегистрируйтесь через /start")
        return

    deleted = user.delete_last_word()
    if deleted:
        await update.message.reply_text(f"Слово '{deleted}' удалено ✅")
    else:
        await update.message.reply_text("В словаре нет слов для удаления ❌")



async def export_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = Users.User.search_user(user_id)
    if not user:
        await update.message.reply_text("Сначала зарегистрируйтесь через /start")
        return
    else:
        qq= translations.Translator.export_vocabular_to_docx(user)
        await update.message.reply_document(qq)


if __name__ == "__main__":
    TOKEN = API.bot

    app = ApplicationBuilder().token(TOKEN).build()

    # Диалоговый обработчик
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_code)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    word_handler = ConversationHandler(
        entry_points=[CommandHandler("word", word)],
        states={
            ASK_WORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, translation)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )



    app.add_handler(conv_handler)
    app.add_handler(word_handler)
    app.add_handler(CommandHandler("allwords", show_words))
    app.add_handler(CommandHandler("today", show_today_words))
    app.add_handler(CommandHandler("delete_last_word", delete_last_word))
    app.add_handler(CommandHandler("export_words", export_words))
    print("Бот запущен...")
    app.run_polling()
