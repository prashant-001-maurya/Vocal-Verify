from flask import Flask, render_template, request, redirect, url_for,jsonify,session
import sqlite3
import os
from werkzeug.utils import secure_filename 
from test import recoder
app = Flask(__name__)
app.secret_key = 'nnasjkfhkjasn9874849njankja'
# Create voice recordings folder if it doesn't exist
VOICE_FOLDER = 'voice'
os.makedirs(VOICE_FOLDER, exist_ok=True)


@app.route('/')
def home2():
    if 'email' in session and session['v']==True:
        return render_template('dashboard.html',email=session['email'])
    return render_template('index.html')


@app.route('/home')
def home():
    if 'email' in session and session['v']==True:
        return render_template('dashboard.html',email=session['email'])
    return render_template('index.html')

@app.route('/index.html')
def home3():
    if 'email' in session and session['v']==True:
        return render_template('dashboard.html',email=session['email'])
    return render_template('index.html')


@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/voice.html')
def pattern():
    return render_template('voice.html')

@app.route('/Secure.html')
def secure():
    return render_template('Secure.html')

@app.route('/Services.html')
def services():
    return render_template('Services.html')

@app.route('/signup.html')
def seign():
    return render_template('signup.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        pin = request.form['pin']
        pattern = request.form['pt']
        
        # Save user details in the database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, phone, pin, pattern) VALUES (?, ?, ?, ?, ?)",
                       (name, email, phone, pin, pattern))
        conn.commit()
        conn.close()
        session['email']=email
        return render_template('voice.html',email=email)
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def log():
    if request.method == 'POST':
        email = request.form['email']
        pin = request.form['pin']
        pattern = request.form['pt']

        # Connect to the database to verify user credentials
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Check if the email exists in the database
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        if user:
            # Check if the pin and pattern match
            stored_pin = user[3]  # Assuming pin is in the 4th column
            stored_pattern = user[4]  # Assuming pattern is in the 5th column

            if pin == stored_pin:
                if pattern == stored_pattern:
                # Login successful, redirect to the dashboard page
                    session['email']=email
                    return redirect(url_for('voice2'))
                else:
                    return render_template('login.html', err="Incorrect Pattern, Please try again.")
            else:
                return render_template('login.html', err="Incorrect Pin, Please try again.")
        else:
            return render_template('login.html', err="Email not found. Please sign up.")
        conn.close()
    return render_template('login.html')

@app.route('/voice2')
def voice2():
    if 'email' not in session:
        return redirect(url_for('login'))
    else:
        return render_template('voice2.html', email=session['email'])

@app.route('/record')
def record():

    email = session['email']
    txt=recoder(email,4)
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Query to check match
    cursor.execute("""
    SELECT *
    FROM users
    WHERE email = ?
    AND (? = text1 OR ? = text2 OR ? = text3)
    """, (email, txt, txt, txt))

    # Fetch result
    result = cursor.fetchone()
    if result:
        session['v']=True
        return redirect(url_for('dashboard'))
    
    else:
        return redirect(url_for('record'))

@app.route('/logout')
def logout():
    session.clear()  # Clear all session data, effectively logging out the user
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'email' in session and session['v']==True:
        return render_template('dashboard.html',email=session['email'])
    elif 'email' in session and session['v']!=True:
        return redirect(url_for('voice2'))
    else:
        return redirect(url_for('login'))

@app.route("/upload")
def upload():
    email=session['email']
    if 'count' not in session:
        session['count']=1
        session['text1']=recoder(email,1)
        count=1
    elif session['count']==1:
        session['count']=2
        session['text2']=recoder(email,2)
        count=2
    elif session['count']==2:
        session['count']=3
        session['text3']=recoder(email,3)
    
    if session['count']<3:
        return render_template('voice.html', email=session['email'],record=count)
    if session['count']==3:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET text1 = ?, text2 = ?, text3 = ?
            WHERE email = ?
        """, (session['text1'],session['text2'],session['text3'], email))
        conn.commit()
        os.makedirs(f'static/doc/{email}')
        session.clear()

    return render_template('login.html')

@app.route('/u_doc', methods=['POST'])
def modelss():
    if request.method == 'POST' and 'email' in session:
        vid = request.files['vid']
        filename = secure_filename(vid.filename)
        directory = f"static/doc/{session['email']}"
        vid.save(os.path.join(directory, filename))
        email = session['email']
        return render_template('dashboard.html', email=email)


@app.route('/view_doc')
def view_doc():
    if 'email' in session:
        email = session['email']
        folder_path = f"static/doc/{email}" 
        files = os.listdir(folder_path)
        document_files = [file for file in files if file.endswith(('.docx', '.pdf', '.txt'))]
        return render_template('document.html', document_files=document_files,folder_path=folder_path,email=session['email'])
    else:
        return render_template('login.html')

@app.route('/delete', methods=['POST'])
def delete_file():
    file_path = request.form['file_path']
    folder_path = request.form['folder_path']
    try:
        os.remove(os.path.join(folder_path, file_path))  # Change this to the actual folder path
    except Exception as e:
        return f"Error deleting file: {str(e)}"
    files = os.listdir(folder_path)
    document_files = [file for file in files if file.endswith(('.docx', '.pdf', '.txt'))]
    return render_template('document.html', document_files=document_files,folder_path=folder_path,email=session['email'])


if __name__ == '__main__':
    app.run(debug=True)
