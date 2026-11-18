import random

import cyrtranslit
import randino
from faker import Faker
from russian_names import RussianNames

from utils.allure_utils import attach, step

_fake = Faker('en_US')

"""Действующие в РФ коды мобильных операторов"""
mobile_provider_codes = [900, 901, 902, 903, 904, 905, 906, 908, 909, 910,
                         911, 912, 913, 914, 915, 916, 917, 918, 919, 920,
                         921, 922, 923, 924, 925, 926, 927, 928, 929, 930,
                         931, 932, 933, 934, 936, 937, 938, 939, 941, 942,
                         950, 951, 952, 953, 954, 955, 956, 958, 960, 961,
                         962, 963, 964, 965, 966, 967, 968, 969, 970, 971,
                         977, 978, 979, 980, 981, 982, 983, 984, 985, 986,
                         987, 988, 989, 991, 992, 993, 994, 995, 996, 997, 999]

city_postal = {
    "Moscow": 101000,
    "Saint Petersburg": 190000,
    "Novosibirsk": 630000,
    "Yekaterinburg": 620000,
    "Kazan": 420000,
    "Nizhny Novgorod": 603000,
    "Chelyabinsk": 454000,
    "Samara": 443000,
    "Omsk": 644000,
    "Rostov-on-Don": 344000,
    "Ufa": 450000,
    "Krasnoyarsk": 660000,
    "Voronezh": 394000,
    "Volgograd": 400000,
    "Perm": 614000,
    "Krasnodar": 350000,
    "Saratov": 410000,
    "Tyumen": 625000,
    "Izhevsk": 426000,
    "Barnaul": 656000,
    "Ulyanovsk": 432000,
    "Khabarovsk": 680000,
    "Penza": 440000,
    "Vladivostok": 690000
}


def get_random_word(min_size: int = None):
    """
    Сгенерировать случайное слово заданной минимальной длины
    :param min_size: минимальная длина слова
    """
    word = _fake.word()
    if min_size:
        while len(word) < min_size:
            word += _fake.word()
    return word


def generate_new_fio(split: bool = False):
    """Сгенерировать новые ФИО"""
    gender = random.choice(["М", "Ж"])
    gender = 0.0 if gender == "Ж" else 1.0
    last_name = RussianNames(count=1, name=False, patronymic=False, gender=gender).get_batch()[0]
    first_name = RussianNames(count=1, patronymic=False, surname=False, gender=gender).get_batch()[0]
    middle_name = RussianNames(count=1, name=False, surname=False, gender=gender).get_batch()[0]
    fio = f"{last_name} {first_name} {middle_name}"
    if split:
        fio = fio.split(' ')
    return fio


@step('Создать адрес личной электронной почты для клиента')
def create_email():
    """Создать адрес личной электронной почты для клиента"""
    domain = random.choice(['@gmail.com', '@yandex.ru', '@qq.com', '@mail.ru'])
    fio = generate_new_fio(split=True)
    last_name = cyrtranslit.to_latin(fio[0], 'ru').lower().replace("'", "")
    first_name = cyrtranslit.to_latin(fio[1], 'ru').lower().replace("'", "")
    middle_name = cyrtranslit.to_latin(fio[2], 'ru').lower().replace("'", "")
    email = f"{first_name[0]}{middle_name[0]}.{last_name}{random.randint(10, 99)}{domain}"
    return email


def generate_business_data(
        acc_source: str = None, ownership: str = None, industry: str = None, acc_type: str = None):
    """
    Установить значения для бизнес-параметров пользователя/клиента
    :param acc_source: источник
    :param ownership:
    :param industry:
    :param acc_type:
    :return:
    """
    acc_source_ = ['Website', 'Referral', 'Event', 'Campaign', 'Phone', 'Email', 'Social Media', 'Partner', 'Other']
    ownership_ = ['Public', 'Private', 'Subsidiary', 'Other']
    industry_ = [
        'Finance', 'Healthcare', 'Manufacturing', 'Agriculture', 'Construction',
        'Banking', 'Education', 'Insurance', 'Other']
    acc_type_ = [
        'Prospect', 'Customer - Direct', 'Customer - Channel', 'Channel Partner / Reseller',
        'Installation Partner', 'Technology Partner', 'Other']
    acc_source = random.choice(acc_source_) if not acc_source else acc_source
    ownership = random.choice(ownership_) if not ownership else ownership
    industry = random.choice(industry_) if not industry else industry
    acc_type = random.choice(acc_type_) if not acc_type else acc_type
    return acc_source, ownership, industry, acc_type


def generate_requirements():
    """Генерация требований для поля requirements"""
    requirements = randino.rand_sentence(language='ru')[0].replace('«', '').replace('»', '')
    attach('Сгенерированы требования (requirements): ', requirements)
    return requirements
