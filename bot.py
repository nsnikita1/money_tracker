import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from db import init_db, add_expense, get_month_total, get_history
from utils import parse_amount, parse_date, format_money
from db import init_db, add_expense, get_month_total, get_history, count_today

load_dotenv()
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
        line = f'{created_at[11:16]} — {format_money(amount)} {category}'
        if comment:
            line += f' ({comment})'
        lines.append(line)
    await update.message.reply_text(f'Траты за {date_str}:\n' + '\n'.join(lines))


def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('whoami', whoami))
    app.add_handler(CommandHandler('add', add))
    app.add_handler(CommandHandler('month', month))
    app.add_handler(CommandHandler('history', history))
    app.run_polling()


if __name__ == '__main__':
    main()