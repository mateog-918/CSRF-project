from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super-secret-key-123'


@app.route('/malicious')
def malicious():
    return render_template('malicious.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)