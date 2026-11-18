from utils.postgresql_provider import attach_source_query


class HorillaQueries:
    """Шаблоны запросов к БД PostgreSQL horilla_db"""

    @staticmethod
    @attach_source_query
    def get_lead_by_email(email: str):
        """
        Получить информацию по потенциальному клиенту из таблицы leads_lead по email
        :param email: адрес электронной почты
        """
        return f"SELECT * FROM leads_lead WHERE email = '{email}'"

    @staticmethod
    @attach_source_query
    def get_account_by_phone(phone: str):
        """
        Получить информацию по потенциальному клиенту из таблицы leads_lead по email
        :param phone: номер телефона в формате +7 9847701216
        """
        phone = f'{phone[:2]} {phone[2:]}'
        return f"SELECT * FROM accounts_account WHERE contact_number = '{phone}'"
