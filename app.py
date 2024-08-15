from flask import Flask, request, redirect, url_for, session, render_template_string
from telethon.sync import TelegramClient
from telethon import functions, types

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Telegram API Settings
api_id = 'your_api_id'
api_hash = 'your_api_hash'

@app.route('/')
def index():
    if 'phone_number' in session:
        return 'Logged in successfully! <a href="/logout">Logout</a>'
    return render_template_string('''
        <h1>Login to Telegram</h1>
        <form action="/login" method="post">
            <label for="phone_number">Phone Number:</label>
            <input type="text" id="phone_number" name="phone_number" required>
            <button type="submit">Login</button>
        </form>
    ''')

@app.route('/login', methods=['POST'])
def login():
    session['phone_number'] = request.form['phone_number']
    client = TelegramClient(session['phone_number'], api_id, api_hash)
    client.connect()
    
    if not client.is_user_authorized():
        client.send_code_request(session['phone_number'])
        return redirect(url_for('verify'))
    
    session['logged_in'] = True
    return redirect(url_for('index'))

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        code = request.form['code']
        client = TelegramClient(session['phone_number'], api_id, api_hash)
        client.connect()
        
        try:
            client.sign_in(session['phone_number'], code)
            session['logged_in'] = True
            return redirect(url_for('index'))
        except Exception as e:
            return f'Error: {e}'
    
    return render_template_string('''
        <h1>Verify Code</h1>
        <form action="/verify" method="post">
            <label for="code">Code:</label>
            <input type="text" id="code" name="code" required>
            <button type="submit">Verify</button>
        </form>
    ''')

@app.route('/logout')
def logout():
    session.pop('phone_number', None)
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
          
