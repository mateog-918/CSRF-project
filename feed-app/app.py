from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super-secret-key-123'


# Prosta baza "użytkowników"
users = {
    'batman@obawim.com': {
        'username': 'Batman',
        'password': 'password123',
        'phone': '123456789',
        'active': True
    }
}

# Dekorator sprawdzający logowanie
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_email' in session:
        return redirect(url_for('feed'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email in users and users[email]['password'] == password and users[email]['active']:
            session['user_email'] = email
            session['username'] = users[email]['username']
            return redirect(url_for('feed'))
        else:
            flash('Invalid credentials or account deleted')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/feed')
@login_required
def feed():
    posts = [
        {'username': 'Batman', 'handle': '@Batman', 'date': 'Apr 1', 'content': 'Did someone call me?'},
        {'username': 'Bemu', 'handle': '@Bemu', 'date': 'Mar 29', 'content': 'Whats uppp <strong>samuirai</strong>?'},
        {'username': 'Elon Musk', 'handle': '@musk', 'date': 'Mar 28', 'content': 'I am going to Mars. See ya mfs'},
        {'username': 'JohnPaul2 ', 'handle': '@JohnPaul2', 'date': 'Mar 28', 'content': 'Check out this guy <a href="http://127.0.0.1:5001/malicious" target="_blank">dont clik this link</a>'},
    ]
    return render_template('feed.html', posts=posts)

@app.route('/settings')
@login_required
def settings():
    email = session['user_email']
    user = users[email]
    return render_template('settings.html', user=user, email=email)

@app.route('/update-settings', methods=['POST'])
@login_required
def update_settings():
    email = session['user_email']
    users[email]['phone'] = request.form.get('phone', users[email]['phone'])
    flash('Settings updated successfully')
    return redirect(url_for('settings'))


# PODATNA FUNKCJA - BRAK OCHRONY CSRF!
# Używa GET zamiast POST - BARDZO NIEBEZPIECZNE!
@app.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    email = session['user_email']
    users[email]['active'] = False
    session.clear()
    flash('Account deleted successfully')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

    
