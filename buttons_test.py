from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
import Users
import translations

# === КНОПКИ ===
ASK_WORD= 2
def get_start_keyboard():
    """Кнопки для незарегистрированных"""
    return ReplyKeyboardMarkup(
        [["Регистрация"]],
        resize_keyboard=True
    )

def get_main_keyboard():
    """Кнопки для зарегистрированных"""
    return ReplyKeyboardMarkup(
        [["Добавить слово", "Показать слова"],
         ["Слова за сегодня", "Удалить последнее"],["еще"]],
        resize_keyboard=True
    )

# === ОБРАБОТЧИКИ ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = Users.User.search_user(user_id)

    if user:
        await update.message.reply_text(
            f"С возвращением, {user.name}!",
            reply_markup=get_main_keyboard()
        )
    else:
        await update.message.reply_text(
            "Привет! Чтобы пользоваться ботом — зарегистрируйся.",
            reply_markup=get_start_keyboard()
        )
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
        await update.message.reply_text(f"слово '{word}', значение '{meaning}' добавлено в словарь ",
        reply_markup = get_main_keyboard())
    context.user_data.pop("awaiting_word", None)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    user = Users.User.search_user(user_id)

    if context.user_data.get("awaiting_word"):
        await translation(update, context)
        return

    if text == "Регистрация":
        if user:
            await update.message.reply_text(
                "Ты уже зарегистрирован!",
                reply_markup=get_main_keyboard()
            )
        else:
            name = update.effective_user.first_name
            Users.User.create_user(user_id, name)
            await update.message.reply_text(
                f"Добро пожаловать, {name}! 🎉",
                reply_markup=get_main_keyboard()
            )

    elif not user:
        await update.message.reply_text(
            "Пожалуйста, зарегистрируйтесь через кнопку 'Регистрация'.",
            reply_markup=get_start_keyboard()
        )

    if text == "Добавить слово":

        await update.message.reply_text("Введите слово для перевода:")

        context.user_data["awaiting_word"] = True

        return

    elif text == "Показать слова":
        vocab = translations.Translator.show_vocabular(user)
        await update.message.reply_text(vocab)

    elif text == "Слова за сегодня":
        vocab = translations.Translator.show_todays_vocabular(user)
        await update.message.reply_text(vocab)

    elif text == "Удалить последнее":
        deleted = user.delete_last_word()
        await update.message.reply_text(f"Удалено слово: {deleted}")


    elif text == "еще":
        return ReplyKeyboardMarkup(
            [["Добавить слово", "Показать слова"],
             ["Слова за сегодня", "Удалить последнее"], ["еще"]],
            resize_keyboard=True
        )

    else:
        await update.message.reply_text("Неизвестная команда.")


# === ЗАПУСК ===
if __name__ == "__main__":
    TOKEN = "8482723120:AAEF2EoJilWLMwqyHrLTjdAc6II7Lv5ntMc"

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling()
