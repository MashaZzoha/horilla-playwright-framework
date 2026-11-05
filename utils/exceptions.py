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
