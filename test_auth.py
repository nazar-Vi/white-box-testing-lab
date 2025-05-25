import pytest
from auth import authenticate_user

# Базові тести з завдання
def test_missing_credentials():
    """Тест для перевірки відсутніх облікових даних"""
    db = {}
    assert authenticate_user("", "pass", db) == "Missing credentials"
    assert authenticate_user("user", "", db) == "Missing credentials"
    assert authenticate_user("", "", db) == "Missing credentials"

def test_user_not_found():
    """Тест для перевірки неіснуючого користувача"""
    db = {}
    assert authenticate_user("user", "pass", db) == "User not found"

def test_account_locked():
    """Тест для перевірки заблокованого акаунту"""
    db = {"user": {"password": "pass", "attempts": 3}}
    assert authenticate_user("user", "pass", db) == "Account locked"
    # Перевіряємо, що кількість спроб не змінюється
    assert db["user"]["attempts"] == 3

def test_invalid_password():
    """Тест для перевірки неправильного пароля"""
    db = {"user": {"password": "pass", "attempts": 0}}
    assert authenticate_user("user", "wrong", db) == "Invalid password"
    assert db["user"]["attempts"] == 1
    
    # Тест збільшення лічильника спроб
    db = {"user": {"password": "pass", "attempts": 1}}
    assert authenticate_user("user", "wrong", db) == "Invalid password"
    assert db["user"]["attempts"] == 2

def test_success():
    """Тест успішної аутентифікації"""
    db = {"user": {"password": "pass", "attempts": 1}}
    assert authenticate_user("user", "pass", db) == "Authenticated"
    assert db["user"]["attempts"] == 0

# Додаткові тести для повного покриття

def test_missing_attempts_field():
    """Тест для користувача без поля attempts"""
    db = {"user": {"password": "pass"}}
    assert authenticate_user("user", "pass", db) == "Authenticated"
    assert db["user"]["attempts"] == 0

def test_attempts_less_than_3():
    """Тест з різною кількістю спроб менше 3"""
    # 0 спроб
    db = {"user": {"password": "pass", "attempts": 0}}
    assert authenticate_user("user", "pass", db) == "Authenticated"
    assert db["user"]["attempts"] == 0
    
    # 1 спроба
    db = {"user": {"password": "pass", "attempts": 1}}
    assert authenticate_user("user", "pass", db) == "Authenticated"
    assert db["user"]["attempts"] == 0
    
    # 2 спроби
    db = {"user": {"password": "pass", "attempts": 2}}
    assert authenticate_user("user", "pass", db) == "Authenticated"
    assert db["user"]["attempts"] == 0

def test_attempts_exactly_3():
    """Тест з рівно 3 спробами"""
    db = {"user": {"password": "pass", "attempts": 3}}
    assert authenticate_user("user", "pass", db) == "Account locked"

def test_attempts_more_than_3():
    """Тест з більше ніж 3 спробами"""
    db = {"user": {"password": "pass", "attempts": 5}}
    assert authenticate_user("user", "pass", db) == "Account locked"

def test_edge_cases():
    """Тести граничних випадків"""
    # Порожній username з непорожнім password
    db = {}
    assert authenticate_user("", "password", db) == "Missing credentials"
    
    # Непорожній username з порожнім password
    assert authenticate_user("user", "", db) == "Missing credentials"
    
    # None значення
    assert authenticate_user(None, "pass", db) == "Missing credentials"
    assert authenticate_user("user", None, db) == "Missing credentials"

# MC/DC тести
class TestMCDC:
    """Тести для Modified Condition/Decision Coverage"""
    
    def test_mcdc_credentials_condition(self):
        """MC/DC для умови: not username or not password"""
        db = {"user": {"password": "pass", "attempts": 0}}
        
        # Тест 1: username=False, password=True -> умова True
        assert authenticate_user("", "pass", db) == "Missing credentials"
        
        # Тест 2: username=True, password=False -> умова True
        assert authenticate_user("user", "", db) == "Missing credentials"
        
        # Тест 3: username=True, password=True -> умова False
        assert authenticate_user("user", "pass", db) == "Authenticated"
        
        # Тест 4: username=False, password=False -> умова True
        assert authenticate_user("", "", db) == "Missing credentials"

# Тести для покриття всіх шляхів
class TestPathCoverage:
    """Тести для повного покриття шляхів виконання"""
    
    def test_path_1_missing_credentials(self):
        """Шлях 1: START -> missing credentials"""
        db = {}
        assert authenticate_user("", "pass", db) == "Missing credentials"
    
    def test_path_2_user_not_found(self):
        """Шлях 2: START -> check credentials -> user not found"""
        db = {}
        assert authenticate_user("user", "pass", db) == "User not found"
    
    def test_path_3_account_locked(self):
        """Шлях 3: START -> check credentials -> check user -> get attempts -> account locked"""
        db = {"user": {"password": "pass", "attempts": 3}}
        assert authenticate_user("user", "pass", db) == "Account locked"
    
    def test_path_4_invalid_password(self):
        """Шлях 4: START -> ... -> check password -> increment attempts -> invalid password"""
        db = {"user": {"password": "correct", "attempts": 0}}
        assert authenticate_user("user", "wrong", db) == "Invalid password"
        assert db["user"]["attempts"] == 1
    
    def test_path_5_authenticated(self):
        """Шлях 5: START -> ... -> check password -> reset attempts -> authenticated"""
        db = {"user": {"password": "pass", "attempts": 2}}
        assert authenticate_user("user", "pass", db) == "Authenticated"
        assert db["user"]["attempts"] == 0

# Тести для перевірки модифікації стану бази даних
class TestDataFlowTesting:
    """Тести для аналізу потоку даних (def-use pairs)"""
    
    def test_attempts_def_use_increment(self):
        """Тест def-use для attempts (визначення -> використання -> збільшення)"""
        db = {"user": {"password": "correct", "attempts": 1}}
        authenticate_user("user", "wrong", db)
        assert db["user"]["attempts"] == 2
    
    def test_attempts_def_use_reset(self):
        """Тест def-use для attempts (визначення -> використання -> скидання)"""
        db = {"user": {"password": "correct", "attempts": 2}}
        authenticate_user("user", "correct", db)
        assert db["user"]["attempts"] == 0
    
    def test_attempts_def_use_get_default(self):
        """Тест def-use для attempts з значенням за замовчуванням"""
        db = {"user": {"password": "correct"}}
        # attempts визначається як 0 через get("attempts", 0)
        authenticate_user("user", "correct", db)
        assert db["user"]["attempts"] == 0

if __name__ == "__main__":
    pytest.main(["-v", __file__])