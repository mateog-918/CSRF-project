# CSRF Attack Demo

## Struktura projektu

```
CSRF - projekt/
├── feed-app/              # Główna aplikacja (podatna na CSRF)
│   ├── app.py            # Backend aplikacji Flask
│   ├── templates/        # Szablony HTML
│   │   ├── login.html
│   │   ├── feed.html
│   │   └── settings.html
│   └── static/
│       └── style.css
├── malicious-app/        # Złośliwa strona atakująca
│   ├── app.py           # Serwer ze złośliwą stroną
│   └── templates/
│       └── malicious.html
├── README.md            # Ten plik
```

## Jak uruchomić projekt (Windows):

### 1. Przygotowanie środowiska wirtualnego

```powershell
# Utwórz środowisko wirtualne
python -m venv venv

# Aktywuj środowisko wirtualne
.\venv\Scripts\activate

# Jeśli wystąpi błąd polityki wykonywania, uruchom:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Instalacja zależności

```powershell
pip install flask
```

### 3. Uruchomienie aplikacji

**Terminal 1 - Główna aplikacja:**
```powershell
cd feed-app
python app.py
```
Aplikacja będzie dostępna pod: http://localhost:5000

**Terminal 2 - Złośliwa aplikacja:**
```powershell
cd malicious-app
python app.py
```
Aplikacja będzie dostępna pod: http://localhost:5001

---

## Przetestuj atak CSRF (demo z prezentacji):

### Krok 1 - Zaloguj się
- Otwórz przeglądarkę i wejdź na http://localhost:5000
- Zaloguj się używając:
  - Email: `batman@obawim.com`
  - Hasło: `password123`

### Krok 2 - Zobacz swoją stronę
- Po zalogowaniu zobaczysz feed z postami
- Kliknij "Account Settings" aby zobaczyć ustawienia konta

### Krok 3 - Wykonaj atak CSRF
- **Pozostań zalogowany** w przeglądarce
- Otwórz w **nowej karcie** link z feeda: http://127.0.0.1:5001/malicious
- Strona automatycznie wykona atak CSRF i usunie Twoje konto!

## Co się dzieje?

1. **Brak ochrony CSRF**: Endpoint `/delete-account` nie ma żadnej ochrony przed CSRF
2. **Automatyczne wysłanie formularza**: Złośliwa strona automatycznie wysyła POST request
3. **Cookie jest wysyłane**: Przeglądarka automatycznie dołącza ciasteczko sesji
4. **Konto zostaje usunięte**: Bez Twojej świadomej zgody!

## Zrozumienie
Ważne jest abyś zrozumiał/a powyższą koncepcję, została ona wyjaśniona podczas prezentacji.

Jeżeli coś przespałeś podnieś rękę to podejdziemy ;)

# Zadania do wykonania

## Zadanie 1: Zabezpieczenie przed CSRF

### Cel zadania
Zabezpiecz aplikację przed atakami CSRF używając tokenów CSRF. Po poprawnej implementacji, atak z złośliwej strony nie będzie już działał.

### Kroki do wykonania:

1. **Zainstaluj bibliotekę Flask-WTF**
   ```powershell
   pip install flask-wtf
   ```

2. **Zaimplementuj ochronę CSRF w aplikacji**
   - Dodaj CSRF protection do aplikacji Flask
   - Zabezpiecz endpointy `/delete-account` i `/update-settings`
   - Dodaj tokeny CSRF do formularzy w templates

3. **Przetestuj zabezpieczenie**
   - Zaloguj się do aplikacji
   - Spróbuj zmienić ustawienia - powinno działać
   - Otwórz złośliwą stronę - atak powinien się NIE udać (błąd 400)

### Wskazówki:
- Flask-WTF automatycznie generuje tokeny CSRF
- Tokeny muszą być dodane do każdego formularza POST
- CSRF protection sprawdza obecność tokena przy każdym żądaniu POST

<details>
<summary>💡 Podpowiedź - Kliknij aby rozwinąć</summary>

### Potrzebne importy:
```python
from flask_wtf.csrf import CSRFProtect
```

### Inicjalizacja w app.py:
```python
csrf = CSRFProtect(app)
```

### W formularzach HTML dodaj:
```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
```

### Które pliki trzeba zmodyfikować:
- `feed-app/app.py` - dodaj CSRFProtect
- `feed-app/templates/settings.html` - dodaj token do obu formularzy
- `feed-app/templates/login.html` - dodaj token do formularza logowania

</details>

---

### Jak sprawdzić czy działa?
1. Zaloguj się do aplikacji (http://localhost:5000)
2. Zmień numer telefonu w ustawieniach - ✅ powinno zadziałać
3. Otwórz złośliwą stronę (http://localhost:5001/malicious) - ❌ powinna pojawić się strona błędu 400 Bad Request
4. Konto NIE powinno zostać usunięte!
5. Otwierając narzędzia developerskie odnajdując wstawiony fragment  ```html <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/> ```  zobaczymy w value nasz token.

---

## Zadanie 2: Mechanizmy obrony - SameSite Cookies

### Cel zadania
Zaimplementuj dodatkowe mechanizmy obrony przed CSRF:
- Użyj SameSite cookies do ograniczenia wysyłania cookies między domenami

### Kroki do wykonania:

1. **Skonfiguruj SameSite cookies**
   - Ustaw odpowiednie flagi dla session cookies
   - Przetestuj jak różne wartości (`Strict`, `Lax`) wpływają na bezpieczeństwo

2. **Przetestuj zabezpieczenia**
   - Sprawdź czy normalne użycie aplikacji działa
   - Sprawdź czy atak CSRF jest blokowany
   - Porównaj skuteczność różnych konfiguracji

### Wskazówki:
- SameSite cookies ograniczają kiedy przeglądarka wysyła cookies
- Różne wartości SameSite oferują różny poziom ochrony

<details>
<summary>💡 Podpowiedź - Kliknij aby rozwinąć</summary>

### SameSite cookies w app.py:
```python
app.config.update(
    SESSION_COOKIE_SAMESITE='Strict',  # lub 'Lax'
    SESSION_COOKIE_HTTPONLY=True
)
```

### Które pliki trzeba zmodyfikować:
- `feed-app/app.py` - dodaj konfigurację SameSite i walidację

</details>

---

### Jak sprawdzić czy działa?

**Test 1: SameSite=Strict**
1. Ustaw `SESSION_COOKIE_SAMESITE='Strict'`
2. Zaloguj się i spróbuj użyć aplikacji normalnie - ✅ powinno działać
3. Otwórz złośliwą stronę - ❌ atak powinien być zablokowany (cookies nie są wysyłane)

**Test 2: SameSite=Lax**
1. Ustaw `SESSION_COOKIE_SAMESITE='Lax'`
2. Sprawdź czy POST requesty z innych domen są blokowane
3. Sprawdź czy GET requesty mogą być wykonane


