from string import ascii_lowercase
from random import choice, randint
from json import loads, dumps
from yoomoney import Client, Quickpay

def get_data():
    with open('yoomoney_parameteres.json', 'r', encoding='utf-8') as file:
        return loads(file.read())

def set_data(data:dict):
    with open('yoomoney_parameteres.json', 'w', encoding='utf-8') as file:
        file.write(dumps(data))

class Yoomoney:

    def __init__(self):
        _data = get_data()
        self._token = _data['token']
        self._account = _data['account']
        self._client = Client(self._token)

        self._not_important_data = {
            "quickpay_form": "button",
            "targets": "Bot Taxi",
            "paymentType": "AC"
        }

    def _get_label(self):
        return "".join("".join(choice(ascii_lowercase) for _ in range(randint(0, 5)))+str(randint(10, 99)) for _ in range(randint(5, 15)))

    def build_quickpay(self):
        label = self._get_label()
        return [Quickpay(
            **self._not_important_data,
            receiver=self._account,
            label=label
        ).base_url, label]

    def check_pay(self, label:str):
        history = self._client.operation_history(label=label)
        for operation in history.operations:
            if operation.status == 'success':
                return True
        return False