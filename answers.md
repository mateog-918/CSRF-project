# Rozwiązania zadań - TYLKO DLA PROWADZĄCYCH

## Zadanie 1: Zabezpieczenie przed CSRF

### Krok po kroku - szczegółowe rozwiązanie:

---

#### Krok 1: Instalacja Flask-WTF

Upewnij się, że środowisko wirtualne jest aktywowane, następnie zainstaluj bibliotekę:

```powershell
pip install flask-wtf
```

---

#### Krok 2: Modyfikacja pliku `feed-app/app.py`

**Lokalizacja:** `feed-app/app.py`

**Co zmienić:**

1. **Dodaj import na początku pliku** (po linii `from functools import wraps`):

```python
from flask_wtf.csrf import CSRFProtect
```

2. **Zainicjalizuj CSRF protection** (po linii `app.secret_key = 'super-secret-key-123'`):

```python
csrf = CSRFProtect(app)
```

**Pełny przykład początku pliku po zmianach:**

```python
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = 'super-secret-key-123'
csrf = CSRFProtect(app)
```

**Wyjaśnienie:**
- `CSRFProtect(app)` automatycznie włącza ochronę CSRF dla wszystkich żądań POST, PUT, PATCH, DELETE
- Flask-WTF automatycznie sprawdza czy w formularzu znajduje się poprawny token CSRF
- Bez tokena lub z niepoprawnym tokenem, żądanie zostanie odrzucone z błędem 400

---

#### Krok 3: Modyfikacja pliku `feed-app/templates/settings.html`

**Lokalizacja:** `feed-app/templates/settings.html`

**Co zmienić:**

Dodaj ukryte pole z tokenem CSRF do **OBU** formularzy w pliku.

##### Formularz 1: Update Settings

Znajdź formularz aktualizacji ustawień i dodaj token:

```html
<form method="POST" action="{{ url_for('update_settings') }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
    <div class="form-group">
        <label>Email</label>
        <input type="email" value="{{ email }}" disabled>
    </div>
    
    <div class="form-group">
        <label>Phone</label>
        <input type="text" name="phone" value="{{ user.phone }}" required>
    </div>
    
    <button type="submit" class="btn-save">Save</button>
</form>
```

##### Formularz 2: Delete Account

Znajdź formularz usuwania konta i dodaj token:

```html
<form method="POST" action="{{ url_for('delete_account') }}" onsubmit="return confirm('Are you sure you want to delete your account?');">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
    <button type="submit" class="btn-delete">Delete Account</button>
</form>
```

**Wyjaśnienie:**
- `{{ csrf_token() }}` to funkcja Jinja2 dostarczana przez Flask-WTF
- Generuje unikalny token dla danej sesji użytkownika
- Token jest sprawdzany po stronie serwera przy każdym żądaniu POST

---

#### Krok 4: Testowanie rozwiązania

**Test 1: Normalne użycie aplikacji (powinno działać)**

1. Uruchom aplikację: `python app.py` w folderze `feed-app`
2. Zaloguj się (batman@obawim.com / password123)
3. Przejdź do Account Settings
4. Zmień numer telefonu i kliknij "Save"
5. ✅ Ustawienia powinny zostać zapisane (flash message: "Settings updated successfully")

**Test 2: Atak CSRF (powinien zostać zablokowany)**

1. Pozostań zalogowany w aplikacji
2. Uruchom złośliwą aplikację: `python app.py` w folderze `malicious-app`
3. Otwórz w nowej karcie: http://localhost:5001/malicious
4. ❌ Powinien pojawić się błąd **400 Bad Request** z komunikatem o brakującym tokenie CSRF
5. Wróć do aplikacji głównej - konto NIE zostało usunięte!

**Test 3: Ręczna próba ataku (opcjonalnie)**

Spróbuj wysłać POST request bez tokena używając curl lub Postman:

```powershell
curl -X POST http://localhost:5000/delete-account -H "Cookie: session=TWOJA_SESJA"
```

Powinien zwrócić błąd 400.

---

### Podsumowanie zmian:

**Pliki do edycji:**
1. ✅ `feed-app/app.py` - dodanie importu i inicjalizacji CSRFProtect
2. ✅ `feed-app/templates/settings.html` - dodanie tokenów CSRF do obu formularzy

**Nowe zależności:**
- `flask-wtf` - biblioteka zapewniająca ochronę CSRF

**Efekt:**
- ✅ Aplikacja jest zabezpieczona przed atakami CSRF
- ✅ Normalne użycie aplikacji działa bez zmian
- ✅ Złośliwe żądania z innych domen są blokowane
- ✅ Użytkownik widzi przyjazny komunikat błędu (400 Bad Request)

---

### Dodatkowe informacje techniczne:

**Jak działa CSRF token?**
1. Przy renderowaniu strony, Flask generuje losowy token powiązany z sesją użytkownika
2. Token jest osadzony w formularzu jako ukryte pole
3. Przy wysłaniu formularza, token jest wysyłany razem z innymi danymi
4. Serwer sprawdza czy token jest poprawny i pasuje do sesji
5. Jeśli token jest nieprawidłowy lub brak go - żądanie jest odrzucane

**Dlaczego złośliwa strona nie może ominąć tego?**
- Złośliwa strona nie ma dostępu do tokena (Same-Origin Policy)
- Token jest unikalny dla każdej sesji
- Token nie jest przechowywany w cookies (tylko w HTML)
- Atakujący nie może odczytać zawartości strony z innej domeny

**Co jeśli chcę wyłączyć CSRF dla konkretnego endpointu?**
```python
@app.route('/api/endpoint', methods=['POST'])
@csrf.exempt
def api_endpoint():
    # Ten endpoint nie będzie sprawdzał CSRF
    pass
```

---

### Możliwe problemy i ich rozwiązania:

**Problem:** "400 Bad Request" przy normalnym użyciu aplikacji
- **Przyczyna:** Brak tokena w formularzu
- **Rozwiązanie:** Upewnij się, że wszystkie formularze POST mają `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>`

**Problem:** "KeyError: 'csrf_token'"
- **Przyczyna:** Flask-WTF nie jest zainstalowany lub nie został zainicjalizowany
- **Rozwiązanie:** Sprawdź czy wykonałeś `pip install flask-wtf` i dodałeś `csrf = CSRFProtect(app)`

**Problem:** Token wygasa zbyt szybko
- **Przyczyna:** Domyślny czas wygaśnięcia tokena (3600 sekund)
- **Rozwiązanie:** Możesz zmienić konfigurację:
```python
app.config['WTF_CSRF_TIME_LIMIT'] = None  # Nigdy nie wygasa
```

---

## Zadanie 2: Mechanizmy obrony - SameSite Cookies i walidacja Origin/Referer

### Krok po kroku - szczegółowe rozwiązanie:

---

#### Część A: Implementacja SameSite Cookies

##### Krok 1: Konfiguracja SameSite w `feed-app/app.py`

**Lokalizacja:** `feed-app/app.py`

**Co zmienić:**

Znajdź sekcję z konfiguracją aplikacji (zaraz po `app.secret_key`) i dodaj/zmień konfigurację cookies:

**PRZED (podatna konfiguracja):**
```python
app = Flask(__name__)
app.secret_key = 'super-secret-key-123'

# WYŁĄCZ SameSite całkowicie - CELOWO NIEBEZPIECZNE dla demo CSRF!
app.config.update(
    SESSION_COOKIE_SAMESITE=None,
    SESSION_COOKIE_HTTPONLY=True
)
```

**PO (bezpieczna konfiguracja):**
```python
app = Flask(__name__)
app.secret_key = 'super-secret-key-123'

# Bezpieczna konfiguracja cookies z SameSite
app.config.update(
    SESSION_COOKIE_SAMESITE='Strict',  # Najsilniejsza ochrona
    SESSION_COOKIE_HTTPONLY=True,      # Zapobiega dostępowi przez JavaScript
    SESSION_COOKIE_SECURE=False        # W produkcji: True (wymaga HTTPS)
)
```

**Wyjaśnienie poszczególnych wartości SameSite:**

1. **`SameSite='Strict'`** (NAJBEZPIECZNIEJSZE)
   - Cookies NIE są wysyłane w ŻADNYCH requestach cross-site
   - Nawet kliknięcie linku z innej strony nie wyśle cookies
   - Użytkownik będzie musiał zalogować się ponownie po kliknięciu linku z zewnątrz
   - **Blokuje wszystkie ataki CSRF**

2. **`SameSite='Lax'`** (KOMPROMIS)
   - Cookies są wysyłane tylko dla "bezpiecznych" requestów cross-site (GET, HEAD, OPTIONS)
   - Cookies NIE są wysyłane dla POST, PUT, DELETE z innych domen
   - Normalna nawigacja (kliknięcie linku) działa prawidłowo
   - **Blokuje większość ataków CSRF** (te używające POST)

3. **`SameSite=None`** (NIEBEZPIECZNE)
   - Cookies są wysyłane we wszystkich requestach cross-site
   - Wymaga `SESSION_COOKIE_SECURE=True` (HTTPS)
   - **Nie chroni przed CSRF** - używane tylko do demo!

---


#### Krok 4: Testowanie rozwiązania

**Test 1: SameSite=Strict**

1. Ustaw w `app.py`:
   ```python
   SESSION_COOKIE_SAMESITE='Strict'
   ```

2. Restart aplikacji (Ctrl+C, potem `python app.py`)

3. Wyczyść cookies w przeglądarce (F12 → Application → Clear site data)

4. Zaloguj się na http://localhost:5000

5. Spróbuj normalnie używać aplikacji:
   - ✅ Zmiana ustawień powinna działać
   - ✅ Usuwanie konta z aplikacji powinno działać

6. Otwórz w nowej karcie: http://localhost:5001/malicious
   - ❌ Atak się NIE powiedzie
   - W konsoli przeglądarki (F12) zobaczysz że cookies nie zostały wysłane
   - W logach feed-app NIE powinno być żądania POST do `/delete-account`

**Test 2: SameSite=Lax**

1. Ustaw w `app.py`:
   ```python
   SESSION_COOKIE_SAMESITE='Lax'
   ```

2. Restart i wyczyść cookies

3. Zaloguj się i przetestuj:
   - ✅ Normalne użycie działa
   - ❌ POST z malicious-app jest blokowany
   - ⚠️ Jeśli atak używa GET, może przejść (dlatego nigdy nie używaj GET do zmiany stanu!)

---

### Podsumowanie zmian:

**Plik do edycji:**
- ✅ `feed-app/app.py`

**Co zostało dodane:**
1. ✅ Konfiguracja `SESSION_COOKIE_SAMESITE='Strict'`
2. ✅ Funkcja `validate_request_origin()`
3. ✅ Walidacja w endpointach `/delete-account` i `/update-settings`

**Efekt:**
- ✅ Cookies nie są wysyłane w requestach cross-site
- ✅ Requesty z innych domen są odrzucane
- ✅ Normalne użycie aplikacji działa bez zmian
- ✅ Ataki CSRF są skutecznie blokowane

---

### Dodatkowe informacje techniczne:

**Hierarchia zabezpieczeń (Defense in Depth):**

1. **CSRF Tokens** (Zadanie 1) - Najlepsza ochrona
   - Unikalne tokeny dla każdego formularza
   - Niemożliwe do odgadnięcia przez atakującego
   - Standard w nowoczesnych aplikacjach

2. **SameSite Cookies** (Zadanie 2A) - Dodatkowa warstwa
   - Ochrona na poziomie przeglądarki
   - Działa automatycznie bez zmian w formularzach
   - Nie wszystkie przeglądarki to wspierają (stare wersje)

**Najlepsza praktyka:** Używaj wszystkich trzech mechanizmów razem!

---

### Porównanie skuteczności:

| Mechanizm | Skuteczność | Łatwość implementacji | Wsparcie przeglądarek |
|-----------|-------------|----------------------|----------------------|
| CSRF Tokens | ⭐⭐⭐⭐⭐ | Średnia | 100% |
| SameSite=Strict | ⭐⭐⭐⭐⭐ | Bardzo łatwa | ~95% |
| SameSite=Lax | ⭐⭐⭐⭐ | Bardzo łatwa | ~95% |
| Origin/Referer | ⭐⭐⭐ | Łatwa | 100% |

---

### Możliwe problemy i ich rozwiązania:

**Problem:** Po ustawieniu `SameSite=Strict` użytkownik zostaje wylogowany po kliknięciu linku z zewnątrz
- **Przyczyna:** To normalne zachowanie Strict
- **Rozwiązanie:** Użyj `SameSite='Lax'` jeśli to problem, lub zostaw Strict dla maksymalnego bezpieczeństwa

**Problem:** Walidacja Origin blokuje legit requesty
- **Przyczyna:** Origin może być null w niektórych przypadkach (redirect, otwieranie w nowej karcie)
- **Rozwiązanie:** Dodaj logikę obsługi przypadków gdy `origin is None` i `referer is None`

**Problem:** Aplikacja działa lokalnie ale nie na produkcji
- **Przyczyna:** `SESSION_COOKIE_SECURE` powinno być True na HTTPS
- **Rozwiązanie:** Dodaj konfigurację zależną od środowiska:
  ```python
  import os
  app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
  ```

**Problem:** SameSite=None nie działa
- **Przyczyna:** Wymaga HTTPS (SESSION_COOKIE_SECURE=True)
- **Rozwiązanie:** W dev środowisku nie używaj None, użyj Lax lub Strict


