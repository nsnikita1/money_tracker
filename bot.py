import os
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from utils import parse_amount, parse_date, format_money

load_dotenv()

from db import init_db, add_expense, get_month_total, get_history, count_today

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.INFO)
logging.getLogger('httpx').setLevel(logging.WARNING)

TOKEN = os.getenv('BOT_TOKEN')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Я бот для учёта трат.')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Команды:\n'
        '/add 500 еда обед — записать трату\n'
        '/history 2026-10-07 — траты за день\n'
        '/month — сумма за месяц'
    )


async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Твой ID: {update.effective_user.id}')


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if count_today(user_id) >= 50:
        await update.message.reply_text('Лимит трат на сегодня исчерпан (50)')
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text('Формат: /add 500 еда обед')
        return
    try:
        amount = parse_amount(args[0])
    except ValueError as error:
        await update.message.reply_text(str(error))
        return
    category = args[1].lower()
    comment = ' '.join(args[2:])
    add_expense(user_id, amount, category, comment)
    await update.message.reply_text(f'Записано: {format_money(amount)} ({category})')


async def month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = get_month_total(update.effective_user.id)
    await update.message.reply_text(f'Расходы за этот месяц: {format_money(total)}')


async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.args:
        try:
            date_str = parse_date(context.args[0])
        except ValueError as error:
            await update.message.reply_text(str(error))
            return
    else:
        date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    rows = get_history(user_id, date_str)
    if not rows:
        await update.message.reply_text(f'За {date_str} трат нет')
        return

    lines = []
    for amount, category, comment, created_at in rows:
        time_str = created_at.astimezone(timezone.utc).strftime('%H:%M')
        line = f'{time_str} — {format_money(amount)} {category}'
        if comment:
            line += f' ({comment})'
        lines.append(line)
    await update.message.reply_text(f'Траты за {date_str}:\n' + '\n'.join(lines))


async def on_error(update, context):
    logging.error('Ошибка в обработчике', exc_info=context.error)


def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('whoami', whoami))
    app.add_handler(CommandHandler('add', add))
    app.add_handler(CommandHandler('month', month))
    app.add_handler(CommandHandler('history', history))
    app.add_error_handler(on_error)

    app.run_polling()


if __name__ == '__main__':
    main()