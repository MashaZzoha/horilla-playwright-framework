import random
from utils.allure_utils import step
from russian_names import RussianNames
import cyrtranslit


def generate_new_fio():
    """Сгенерировать новые ФИО"""
    gender = random.choice(["М", "Ж"])
    gender = 0.0 if gender == "Ж" else 1.0
    last_name = RussianNames(count=1, name=False, patronymic=False, gender=gender).get_batch()[0]
    first_name = RussianNames(count=1, patronymic=False, surname=False, gender=gender).get_batch()[0]
    middle_name = RussianNames(count=1, name=False, surname=False, gender=gender).get_batch()[0]
    fio = f"{last_name} {first_name} {middle_name}"
    return fio


@step('Создать адрес личной электронной почты для клиента')
def create_email():
    """Создать адрес личной электронной почты для клиента"""
    domain = random.choice(['@gmail.com', '@yandex.ru', '@qq.com', '@mail.ru'])
    fio = generate_new_fio().split(' ')
    last_name = cyrtranslit.to_latin(fio[0], 'ru').lower().replace("'", "")
    first_name = cyrtranslit.to_latin(fio[1], 'ru').lower().replace("'", "")
    middle_name = cyrtranslit.to_latin(fio[2], 'ru').lower().replace("'", "")
    email = f"{first_name[0]}{middle_name[0]}.{last_name}{random.randint(10, 99)}{domain}"
    return email
