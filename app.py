from flask import Flask, render_template, url_for, request, session
import sqlite3
import os
from image_test import *
from video_test import *

connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()

command = """CREATE TABLE IF NOT EXISTS user(name TEXT, password TEXT, mobile TEXT, email TEXT)"""
cursor.execute(command)


app = Flask(__name__)
app.secret_key = 'qwertyiopfggfds'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/userlog', methods=['GET', 'POST'])
def userlog():
    if request.method == 'POST':

        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        name = request.form['name']
        password = request.form['password']

        query = "SELECT name, password FROM user WHERE name = '"+name+"' AND password= '"+password+"'"
        cursor.execute(query)

        result = cursor.fetchall()

        if result:
            return render_template('home.html')
        else:
            return render_template('index.html', msg='Sorry, Incorrect Credentials Provided,  Try Again')
    return render_template('index.html')


@app.route('/userreg', methods=['GET', 'POST'])
def userreg():
    if request.method == 'POST':

        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        name = request.form['name']
        password = request.form['password']
        mobile = request.form['phone']
        email = request.form['email']
        
        print(name, mobile, email, password)

        cursor.execute("INSERT INTO user VALUES ('"+name+"', '"+password+"', '"+mobile+"', '"+email+"')")
        connection.commit()

        return render_template('index.html', msg='Successfully Registered')
    
    return render_template('index.html')

@app.route('/detection')
def detection():
    return render_template('testimage.html')


@app.route('/testimage', methods=['GET', 'POST'])
def testimage():
    if request.method == 'POST':
        src = "static/imgs/"+request.form['src']
        out = "static/testimage_output/output.jpg"
        text = process_image(src, out)
        return render_template('testimage.html', inputimage=src, outputimage=out, text=text)
    return render_template('testimage.html')

@app.route('/testvideo', methods=['GET', 'POST'])
def testvideo():
    if request.method == 'POST':
        src = "static/videos/"+request.form['src']
        out = "static/testvideo_output/output.mp4"
        process_video(src, out)
        return render_template('testvideo.html', inputvideo=src, outputvideo=out)
    return render_template('testvideo.html')


import smtplib
from email.message import EmailMessage

def send_email(from_email_addr, from_email_pass, to_email_addr, subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['From'] = from_email_addr
    msg['To'] = to_email_addr
    msg['Subject'] = subject

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email_addr, from_email_pass)
    server.send_message(msg)
    server.quit()

@app.route('/forgotpassword', methods=['POST', 'GET'])
def forgotpassword():
    if request.method == 'POST':
        gmail = request.form['gmail']
        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()
        cursor.execute("select * from user where email = '"+gmail+"'")
        result = cursor.fetchall()
        if result:
            session['gmail'] = gmail
            import random
            otp = str(random.randint(1111, 9999))
            session['otp'] = otp
            send_email('manikeshjy2002@gmail.com', 'yyjd eyjf oyaf hujx', gmail, 'OTP for change password', otp)
            return render_template('forgotpassword.html', msg2=f'OTP sent to {gmail}')
        else:
            return render_template('index.html', msg="Entered Invalid gmail")
    return render_template('forgotpassword.html')

@app.route('/resetpassword', methods=['POST', 'GET'])
def resetpassword():
    if request.method == 'POST':
        otp = str(request.form['otp'])
        password = request.form['password']
        if otp == session['otp']:
            connection = sqlite3.connect('user_data.db')
            cursor = connection.cursor()
            cursor.execute("update user set password = '"+password+"' where email = '"+session['gmail']+"'")
            connection.commit()
            return render_template('index.html', msg=f'Password reset successfully')
        else:
            return render_template('index.html', msg=f'Entered wrong OTP')
    return render_template('index.html')

@app.route('/logout')
def logout():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)