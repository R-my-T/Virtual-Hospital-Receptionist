from flask import Flask, render_template, request,redirect,session
from flask import redirect, url_for, session
from flask import session, request
import sqlite3
from datetime import datetime
from flask_session import Session
from flask import *

app = Flask(__name__)
app = Flask(__name__, template_folder= "templates")

app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#Global Variables

Global_hid=0
Global_did=0
doctor_hid=0

# Note: Sessions have been implemented thus allowing access to only the logged in hospital admins/doctors . 
# If you are not logged in, you will be redirected to the homepage automatically and displayed an error message.

#-------Home Page-----------
@app.route('/')
def greeting():
   return render_template("Homepage.html")

#-------Registering an Hospital-------
@app.route('/register_hospital', methods=['GET','POST'])
def register_hospital():
   if request.method == 'POST':
      hid = request.form['hid']
      name = request.form['name']
      pswd= request.form['pswd']

      try:
         print ("making a connection")
         connection = sqlite3.connect('hospital_db.db')

         print ("Getting a Cursor")
         cursor = connection.cursor()
         
         print ("Executing the DML")
         cursor.execute("INSERT into hospital (Hospital_ID,Password,Name) values (?,?,?)",(hid,pswd,name))  
         
         print ("Commiting the changes")
         connection.commit()

         print ("Closing the datbase")
         connection.close()

         return redirect(url_for('greeting'))

      except Exception as error:
         return_message = str(error)
         return(return_message)
   else:
      return render_template("register_hospital.html")

#-------Hospital Log in---------
@app.route('/login',methods=['GET','POST'])
def login():
   if request.method == 'POST':
      global Global_hid
      Global_hid = request.form['hid']
      pswd= request.form['pswd']

      try:
         print ("making a connection")
         connection = sqlite3.connect('hospital_db.db')

         print ("Getting a Cursor")
         cursor = connection.cursor()
         
         print ("Executing the DML")
         cursor.execute("SELECT * from hospital where Hospital_ID=?",(Global_hid,))  

         print ("Get the Rows from cursor")
         information = cursor.fetchall() 
         print(information)

         print ("Closing the database")
         connection.close()

         if (pswd==information[0][1]) :
            session['hospital']= Global_hid
            return redirect(url_for('options'))
         else:
            return('Incorrect username/password! Please try again')

      except Exception as error:
         return_message = str(error)
         return(return_message)
   else:
      return render_template("login_hospital.html")

#-------Logging out Doctor-----
@app.route('/logoutdoc')
def logout_doc():
   session['doctor']= None
   return redirect(url_for('greeting'))

#-------Logging out Hospital-----
@app.route('/logouthospital')
def logout_hospital():
   session['hospital']= None
   return redirect(url_for('greeting'))

#--------Viewing the Options---------
@app.route('/options',methods=['GET','POST'])
def options():
   if not session.get("hospital"):
      flash('You are not logged in as the admin')
      return redirect(url_for('greeting'))

   return render_template('options.html')

#--------Registering a new doctor-----
@app.route('/register_doctor',methods=['GET','POST'])
def register_doctor():
   if not session.get("hospital"):
      flash('You are not logged in as the admin')
      return redirect(url_for('greeting'))
   if request.method == 'POST':

      hid = request.form['hid']
      did = request.form['did']
      name = request.form['name']
      gender = request.form['gender']
      qual = request.form['qual']
      about = request.form['about']
      contact = request.form['contact']
      stime = request.form['stime']
      etime = request.form['etime']
      pswd= request.form['pswd']

      try:
         print ("making a connection")
         connection = sqlite3.connect('hospital_db.db')

         print ("Getting a Cursor")
         cursor = connection.cursor()
         
         print ("Executing the DML")
         cursor.execute("INSERT into doctor (Doc_ID,Name,Gender,Qualification,About,Contact,Start_time,End_time,Password,Hospital_ID) values (?,?,?,?,?,?,?,?,?,?)",(did,name,gender,qual,about,contact,stime,etime,pswd,hid))
         
         print ("Commiting the changes")
         connection.commit()

         print ("Closing the datbase")
         connection.close()

         return redirect(url_for('options'))

      except Exception as error:
         return_message = str(error)
         return(return_message)
   else:
      return render_template("register_doctor.html")

#--------Doctor's Login------
@app.route('/doctorlogin',methods=['GET','POST'])
def doctor_login():
   global doctor_hid
   global Global_did
   if request.method == 'POST':
      Global_did = request.form['did']
      doctor_hid = request.form['hid']
      pswd= request.form['pswd']

      try:

         print ("making a connection")
         connection = sqlite3.connect('hospital_db.db')

         print ("Getting a Cursor")
         cursor = connection.cursor()
         
         print ("Executing the DML")
         cursor.execute("SELECT Name,Password from doctor where Hospital_ID=? AND Doc_ID=?",(doctor_hid,Global_did,))  

         print ("Get the Rows from cursor")
         information = cursor.fetchall() 
         print(information)

         print ("Closing the database")
         connection.close()

         if (pswd==information[0][1]) :
            session['doctor']= Global_did
            return redirect(url_for('doctor_view'))

         else:
            return ('Incorrect information entered! Try again')

      except Exception as error:
         return_message = str(error)
         return(return_message)
   else:
      return render_template("doctor_login.html")

#--------Doctor's View--------
@app.route('/doctorview',methods=['GET','POST'])
def doctor_view():
   if not session.get("doctor"):
      flash('You are not logged in as the doctor')
      return redirect(url_for('greeting'))
   global doctor_hid
   global Global_did
   try:
      #Getting casual patients
      print ("making a connection")
      connection = sqlite3.connect('hospital_db.db')

      print ("Getting a Cursor")
      cursor = connection.cursor()
            
      print ("Executing the DML")
      cursor.execute("SELECT P_ID,Name,Gender,Age FROM patients WHERE Doctor_id=? AND Emergency=0 And Hospital_ID=?",(Global_did,doctor_hid))


      print ("Get the Rows from cursor")
      casual_patients = cursor.fetchall() 

      print ("Closing the database")
      connection.close()

      #Getting Emergency patients
      print ("making a connection")
      connection = sqlite3.connect('hospital_db.db')

      print ("Getting a Cursor")
      cursor = connection.cursor()

      print ("Executing the DML")
      cursor.execute("SELECT P_ID,Name,Gender,Age FROM patients WHERE Doctor_id=? AND Emergency=1 And Hospital_ID=?",(Global_did,doctor_hid,))

      print ("Get the Rows from cursor")
      emergency_patients = cursor.fetchall() 

      print ("Closing the database")
      connection.close()

      #Getting doctor's name
      print ("making a connection")
      connection = sqlite3.connect('hospital_db.db')

      print ("Getting a Cursor")
      cursor = connection.cursor()
            
      print ("Executing the DML")
      cursor.execute("SELECT Name FROM doctor WHERE Doc_ID=? AND Hospital_ID=?",(Global_did,doctor_hid,))


      print ("Get the Rows from cursor")
      docname = cursor.fetchall() 

      print ("Closing the database")
      connection.close()

      print(casual_patients)

   except Exception as error:
      return_message = str(error)
      return(return_message)

   return render_template('doctor_view.html',casual =casual_patients, emergency=emergency_patients,docname=docname)

#--------Dismissing a patient----
@app.route("/dismiss/<int:pk>",methods=['GET','POST'])
def dismiss(pk):
   #if not session.get("hospital"):
      #flash('You are not logged in as the doctor')
      #return redirect(url_for('greeting'))
   try:
      #Dismissing
      print ("making a connection")
      connection = sqlite3.connect('hospital_db.db')

      print ("Getting a Cursor")
      cursor = connection.cursor()
            
      print ("Executing the DML")
      cursor.execute("DELETE from patients where P_ID=?",(pk,))

      print ("Commiting the changes")
      connection.commit()

      print ("Closing the database")
      connection.close()

      return redirect(url_for('doctor_view'))

   except Exception as error:
      return_message = str(error)
      return(return_message)
   
#--------Calling the Receptionist-----
@app.route('/receptionist', methods=['GET','POST'])
def reception():
   if not session.get("hospital"):
      flash('You are not logged in as the admin')
      return redirect(url_for('greeting'))
   global Global_hid
   try:
      print ("making a connection")
      connection = sqlite3.connect('hospital_db.db')

      print ("Getting a Cursor")
      cursor = connection.cursor()
            
      print ("Executing the DML")
      cursor.execute("SELECT Doc_ID,Name,Qualification,Start_time,End_time from doctor where Hospital_ID=?",(Global_hid,))

      print("Global HID=",Global_hid)

      print ("Get the Rows from cursor")
      information = cursor.fetchall() 

      print ("Closing the database")
      connection.close()

      print ("making a connection")
      connection = sqlite3.connect('hospital_db.db')

      print ("Getting a Cursor")
      cursor = connection.cursor()

      print ("Executing the DML")
      cursor.execute("SELECT Name,Doctor_id from patients where Hospital_ID=?",(Global_hid,))

      print ("Get the Rows from cursor")
      patient = cursor.fetchall() 

      print ("Closing the database")
      connection.close()

      print ("making a connection")
      connection = sqlite3.connect('hospital_db.db')

      print ("Getting a Cursor")
      cursor = connection.cursor()
            
      print ("Executing the DML")
      cursor.execute("SELECT Name from hospital where Hospital_ID=?",(Global_hid,))

      print ("Get the Rows from cursor")
      hname = cursor.fetchall() 

      print ("Closing the database")
      connection.close()

   except Exception as error:
      return_message = str(error)
      return(return_message)

   return render_template('receptionist.html',doc = information, pat=patient,hname=hname)

#--------Adding new patients to the Queue------
@app.route('/addpatient',methods=['GET','POST'])
def addpatient():
   if not session.get("hospital"):
      flash('You are not logged in as the admin')
      return redirect(url_for('greeting'))
   global Global_hid
   if request.method == 'POST':
      name = request.form['name']
      age = request.form['age']
      gender = request.form['gender']
      did = request.form['did']
      emer = request.form['emer']

      if emer=='y' or emer=='Y':
         emer=1
      else:
         emer=0

      try:

         print ("making a connection")
         connection = sqlite3.connect('hospital_db.db')

         print ("Getting a Cursor")
         cursor = connection.cursor()
         
         print ("Executing the DML")
         cursor.execute("INSERT into patients (Name,Age,Gender,Emergency,Doctor_id,Hospital_ID) values (?,?,?,?,?,?)",(name,age,gender,emer,did,Global_hid))
         
         print ("Commiting the changes")
         connection.commit()

         print ("Closing the datbase")
         connection.close()

         return redirect(url_for('reception'))

      except Exception as error:
         return_message = str(error)
         return(return_message)
   else:
      print ("making a connection")
      connection = sqlite3.connect('hospital_db.db')

      print ("Getting a Cursor")
      cursor = connection.cursor()
            
      print ("Executing the DML")
      cursor.execute("SELECT Doc_ID FROM doctor WHERE Hospital_ID=?",(Global_hid,))


      print ("Get the Rows from cursor")
      doclist = cursor.fetchall() 

      print ("Closing the database")
      connection.close()

      return render_template("add_patient.html",doclist=doclist)

if __name__ == '__main__':
   app.run()
   app.debug = True