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

### 2.25
Jak nie działa flask to wykonaj:
```power shell
python -m pip install --upgrade pip
```

### 2.5 Sklonuj repozytorium
```powershell
git clone https://github.com/mateog-918/CSRF-project.git
```

### 2.75
Wejdź do folderu repozytorium.

### 3. Uruchomienie aplikacji

**Terminal 1 - Główna aplikacja:**
```powershell
cd feed-app
python app.py
```
Aplikacja będzie dostępna pod: http://127.0.0.1:5000

**Terminal 2 - Złośliwa aplikacja:**
```powershell
cd malicious-app
python app.py
```
Aplikacja będzie dostępna pod: http://127.0.0.1:5001

---

## Przetestuj atak CSRF (demo z prezentacji):

### Krok 1 - Zaloguj się
- Otwórz przeglądarkę i wejdź na http://127.0.0.1:5000
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
1. Zaloguj się do aplikacji (http://127.0.0.1:5000)
2. Zmień numer telefonu w ustawieniach - ✅ powinno zadziałać
3. Otwórz złośliwą stronę (http://127.0.0.1:5001/malicious) - ❌ powinna pojawić się strona błędu 400 Bad Request
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

**Test 3: Walidacja Origin/Referer**
1. Dodaj sprawdzanie nagłówków przed wykonaniem akcji
2. Request z 127.0.0.1:5001 powinien być odrzucony
3. Request z 127.0.0.1:5000 powinien być akceptowany

---

## Zadanie 3: JSON-based CSRF Attack

### Cel zadania
Zrozumieć że **API endpointy obsługujące JSON** mogą być równie podatne na CSRF jak tradycyjne formularze HTML.

### Wprowadzenie
Wielu programistów błędnie zakłada, że przejście z formularzy HTML na JSON API automatycznie chroni przed CSRF. W tym zadaniu poznasz:
- Dlaczego JSON API może być podatne na CSRF
- Jak przeprowadzić atak CSRF na endpoint JSON
- Jak poprawnie zabezpieczyć API przed CSRF

### Kroki do wykonania:

1. **Przeanalizuj endpoint w feed-app**
   - Spójrz an `/api/change-email` akceptujący JSON
   - Endpoint zmienia email użytkownika
   - Celowo pozostawiono go bez zabezpieczenia CSRF

2. **Stwórz stronę atakującą**
   - W malicious-app otwórz plik `templates/json-attack.html`
   - W `<body>` strony zaimplementuj formularz z `enctype="text/plain"`
   - Użyj tricku z nazwą inputa aby wysłać dane wyglądające jak JSON
   - Dodaj automatyczne wysyłanie formularza przez JavaScript
   - **Dodaj route** `/json-attack` w `malicious-app/app.py`

3. **Przetestuj podatność**

   - Zaloguj się do aplikacji
   - Otwórz stronę atakującą
   - Sprawdź czy email został zmieniony bez Twojej zgody

4. **Zabezpiecz endpoint**
   - Dodaj CSRF token w custom header (`X-CSRF-Token`)
   - Waliduj Content-Type (akceptuj tylko `application/json`)
   - Sprawdź token przed wykonaniem akcji

### Wskazówki:
- Proste formularze mogą "podszywać się" pod JSON używając `enctype="text/plain"`
- CORS nie chroni przed CSRF (cookies są wysyłane!)
- CSRF token można przesłać w custom headerze zamiast w body

<details>
<summary>💡 Podpowiedź - Kliknij aby rozwinąć</summary>

### Atak przez formularz (json-attack.html):
```html
<form method="POST" action="http://127.0.0.1:5000/api/change-email" enctype="text/plain">
    <input name='{"new_email":"hacker@evil.com", "ignore":"' value='"}' type='hidden'>
</form>
<script>document.forms[0].submit();</script>
```

### Zabezpieczenie - dodaj do endpoint:
```python
# Sprawdź CSRF token w headerze
token = request.headers.get('X-CSRF-Token')
if not token or token != session.get('csrf_token'):
    return jsonify({'error': 'CSRF token missing or invalid'}), 403

# Walidacja Content-Type
if request.content_type != 'application/json':
    return jsonify({'error': 'Content-Type must be application/json'}), 415
```

### Które pliki trzeba zmodyfikować:
- `feed-app/app.py` - dodaj endpoint `/api/change-email`
- `malicious-app/templates/json-attack.html` - nowy plik atakujący
- `malicious-app/app.py` - dodaj route do json-attack

</details>

---

### Jak sprawdzić czy działa?

**Test 1: Atak (bez zabezpieczenia)**
1. Zaloguj się do aplikacji (http://127.0.0.1:5000)
2. Sprawdź swój obecny email w ustawieniach
3. Otwórz http://127.0.0.1:5001/json-attack w nowej karcie
4. Email powinien zostać zmieniony na `hacker@evil.com`
5. To pokazuje że JSON API jest podatne na CSRF.

**Test 2: Zabezpieczenie (z tokenem)**
1. Dodaj walidację CSRF tokena w headerze
2. Dodaj sprawdzanie Content-Type
3. Spróbuj ponownie ataku
4. Endpoint powinien zwrócić błąd.
5. Email nie powinien zostać zmieniony



