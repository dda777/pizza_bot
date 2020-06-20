from transitions import Machine
import telebot

API_TOKEN = '1212201755:AAH5bk2m1CIRoa3OMRqciNblp5HxpjtAEMQ'
bot = telebot.TeleBot(API_TOKEN)


class PizzaChat(object):
    def __init__(self, size_list, pay_type_list):
        self.oper_info = {'chat_id': None}
        self.select_operation_info = {'pizza_size': None, 'pay_type': None}
        self.size_list = size_list
        self.pay_type_list = pay_type_list
        states = ['start', 'choice_pizza', 'choice_payment', 'pizza', 'payment', 'check_correct', 'output']
        machine = Machine(model=self, states=states, initial='start')
        machine.add_transition('start', '*', 'choice_pizza')
        machine.add_transition('pizza_size', 'choice_pizza', 'choice_payment', after='put_pizza_size',
                               conditions='is_correct_size')
        machine.add_transition('payment_type', 'choice_payment', 'check_correct', after='put_pay_type',
                               conditions='is_correct_pay_type')
        machine.add_transition('check_correct', 'check_correct', 'output', conditions=['is_correct'])

    def incorrect_select(self):
        return 'Увы, но что-то пошло не так, попробуйте выбрать еще раз'

    def put_pizza_size(self, size):
        self.select_operation_info['pizza_size'] = size

    def put_pay_type(self, pay_type):
        self.select_operation_info['pay_type'] = pay_type

    def is_correct_size(self, size):
        return size in self.size_list

    def is_correct_pay_type(self, pay_type):
        return pay_type in self.pay_type_list

    def is_correct(self, correct):
        if correct.lower() == 'да':
            return True
        else: return False




size_list = ['big', 'small']
pay_type_list = ['cash', 'card']
chat = PizzaChat(size_list, pay_type_list)

@bot.message_handler(commands=['start'])
def pizza_select(message):
    chat.start()
    bot.send_message(message.chat.id, 'Виберете размер пиццы - "Big"/"Small"')
    chat.oper_info['chat_id'] = message.chat.id

@bot.message_handler(func=lambda message: chat.oper_info['chat_id'] == message.chat.id)
def payment_select(message):

    if chat.is_choice_pizza():
        if chat.pizza_size(size=message.text.lower()):
            bot.send_message(message.chat.id, text='Выбирите тип оплаты - Card/Cash')
        else:
            bot.send_message(message.chat.id, text=chat.incorrect_select())

    elif chat.is_choice_payment():
        if chat.payment_type(pay_type=message.text.lower()):
            bot.send_message(message.chat.id,
                             text=f'Вы выбрали {chat.select_operation_info["pizza_size"]} пиццу и платите {chat.select_operation_info["pay_type"]} \n Все верно? "Да"/"Нет"')
        else:
            bot.send_message(message.chat.id, text=chat.incorrect_select())
    elif chat.is_check_correct():
        if message.text.lower() != 'да' and message.text.lower() != 'нет':
            bot.send_message(message.chat.id, text=chat.incorrect_select())
        elif chat.check_correct(correct=message.text.lower()):
            bot.send_message(message.chat.id, text='Хорошего дня!')
        else: pizza_select(message)
    chat.oper_info['chat_id'] = message.chat.id


bot.polling()
