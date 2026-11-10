class NotFoundPageInStore(Exception):
    """Ошибка: страница не найдена в каталоге страниц"""
    pass


class RegistrationLocatorsException(Exception):
    """Ошибка регистрации локаторов"""
    pass


class LocatorNotFound(Exception):
    """Ошибка: локатор не найден в файле .yaml локаторов страницы"""
    pass


class ElementsNotFound(Exception):
    """Ошибка: элементы не найдены на странице"""
    pass


class RegistryUrlException(Exception):
    """Ошибка регистрации URL-адреса"""
    pass


class NotFoundUrlInStorage(Exception):
    """Ошибка: URL-адрес отсутствует в каталоге адресов"""
    pass


class UnsupportedStorePages(Exception):
    """Ошибка: неподдерживаемый формат страниц"""
    pass


class UnsupportedUrlManager(Exception):
    """Ошибка: неподдерживаемый URL-менеджер"""
    pass


class UnknownDbException(Exception):
    """Ошибка БД"""
    pass


class UnknownConfigException(Exception):
    """Ошибка конфигурации"""
