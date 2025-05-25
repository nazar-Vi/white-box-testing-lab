def authenticate_user(username, password, db):
    """
    Функція аутентифікації користувача
    
    Args:
        username (str): Ім'я користувача
        password (str): Пароль
        db (dict): База даних користувачів
    
    Returns:
        str: Результат аутентифікації
    """
    if not username or not password:
        return "Missing credentials"
    
    if username not in db:
        return "User not found"
    
    attempts = db[username].get("attempts", 0)
    if attempts >= 3:
        return "Account locked"
    
    if db[username]["password"] != password:
        db[username]["attempts"] = attempts + 1
        return "Invalid password"
    
    db[username]["attempts"] = 0
    return "Authenticated"