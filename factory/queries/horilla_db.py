from utils.postgresql_provider import attach_source_query


class HorillaQueries:
    """Шаблоны запросов к БД PostgreSQL horilla_db"""

    @staticmethod
    @attach_source_query
    def get_changes_by_logentry(logentry: str):
        return f"SELECT changes FROM auditlog_logentry WHERE object_repr = '{logentry}'"
