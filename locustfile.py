import random

from locust import HttpUser, task, between

complaints = [
    "Не пришёл чек после оплаты.",
    "Списаны деньги, но услуга не активирована.",
    "Платёж прошёл дважды, нужен возврат.",
    "Не могу найти историю платежей в личном кабинете.",
    "Почему с меня взяли комиссию?",
    "Где мои деньги?! Оплатил, а доступа нет!",
    "Опять двойное списание! Надоело!",
    "Почему нет никаких уведомлений о платежах?!",
    "Это что, скрытые платежи? Верните деньги!",
    "Сколько можно ждать возврата средств?!",
    "О, снова 'технический сбой' при списании денег. Как неожиданно!",
    "Спасибо за двойной платёж, очень приятно!",
    "Вы вообще отслеживаете платежи или как?",
    "Классно, что комиссия всегда в пользу сервиса!",
    "Очередной 'автоплатёж' без моего согласия. Отлично!",
    "Сайт не грузится уже час.",
    "Не получается войти в аккаунт.",
    "Приложение вылетает при открытии.",
    "Форма обратной связи не работает.",
    "Почему нет кнопки отмены подписки?",
    "Сколько можно?! Сервис опять лежит!",
    "Почему я не могу зайти в свой профиль?!",
    "Исправьте уже эти бесконечные баги!",
    "Вы вообще тестируете обновления? Всё сломалось!",
    "Где техподдержка?! Никто не отвечает!",
    "Очередной 'гениальный' апдейт, который всё сломал.",
    "Спасибо, что сделали вход сложнее, чем в ФБР!",
    "Кто-то тестирует ваши обновления? Или это шутка?",
    "Приложение тормозит, как будто 1999 год.",
    "Отличная работа! Теперь вообще ничего не работает."
]
base_api_url = "http://localhost:8000/api/v1"

class CreateComplaints(HttpUser):
    """Creating random complaints."""
    wait_time = between(7.0, 10.0)

    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        pass

    def on_stop(self):
        """ on_stop is called when the TaskSet is stopping """
        pass

    @task(1)
    def new_complaint(self):
        self.client.post(f"{base_api_url}/complaint/",
                         json={"text": random.choice(complaints)})


class UpdateComplaints(HttpUser):
    """Get all complaints and update status for 3 of all"""
    wait_time = between(3.0, 10.0)

    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        pass

    def on_stop(self):
        """ on_stop is called when the TaskSet is stopping """
        pass

    @task(1)
    def update(self):
        response = self.client.get(f"{base_api_url}/complaint/")
        data = response.json()
        upd_data = [
            {"status": "closed" if item['status'] == "open" else "open",
             "id": item['id']}
            for item in data
        ]
        for _ in range(3):
            upd_data_item = random.choice(upd_data)
            self.client.patch(f"{base_api_url}/complaint/{upd_data_item['id']}/",
                              json={"status": upd_data_item['status']})

