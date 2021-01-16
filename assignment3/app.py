from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assignment3.db'

db = SQLAlchemy(app)

class Instructor(db.Model):
	#id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), primary_key=True, unique=True, nullable=False)
	name = db.Column(db.String(50), nullable=False)
	password = db.Column(db.String(100), nullable=False)

	def __init__(self, name, username, password):
		#self.id = id
		self.name = name
		self.username = username
		self.password = password

class Student(db.Model):
	username = db.Column(db.String(50), primary_key=True, unique=True, nullable=False)
	name = db.Column(db.String(50), nullable=False)
	password = db.Column(db.String(100), nullable=False)
	a1 = db.Column(db.Integer())
	a2 = db.Column(db.Integer())
	a3 = db.Column(db.Integer()) 

	def __init__(self, name, username, password, a1, a2, a3):
		#self.id = id
		self.name = name
		self.username = username
		self.password = password
		self.a1 = a1
		self.a2 = a2
		self.a3 = a3


class Feedback(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50))
	#feedback = db.Column(db.String(10000))

	f1 = db.Column(db.String(10000))
	f2 = db.Column(db.String(10000))
	f3 = db.Column(db.String(10000))
	f4 = db.Column(db.String(10000))

	def __repr__(Self):
		return f"Feedback('{self.username}', '{self.f1}', '{self.f2}', '{self.f3}', '{self.f4}')"
		


class Regrade(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50))
	assignment = db.Column(db.String(5))
	reason = db.Column(db.String(10000))

	def __repr__(Self):
		return f"Regrade('{self.username}', '{self.assignment}', '{self.reason}')"









@app.route("/")
def student_or_instructor():
	return render_template("first.html")





@app.route('/signup-instructor', methods=['GET', 'POST'])
def sign_up_instructor():

	return sign_up('i')

@app.route('/signup-student', methods=['GET', 'POST'])
def sign_up_student():

	return sign_up('s')


def sign_up(x):
	if request.method == 'POST':
		req = request.form

		name = req['name']
		username = req['username']
		password = req['password']

		hashed_password = generate_password_hash(password, method='sha256')

		#Practically speaking, the following code will never be
		#run because, html code does not allow for empty
		#strings, forces user for an input.
		if not name:
			return 'No Name!'
		if not password:
			return 'No password!'


		return add_user(name, username, hashed_password, x)

	return render_template('sign-up.html')


def add_user(name, username, password, x):

	try:
		if x == 'i':
			user = Instructor(name=name, username=username, password=password)
			db.session.add(user)
			db.session.commit()
			return render_template('instructorCreated.html')
		if x == 's':
			user = Student(name=name, username=username, password=password, a1=0, a2=0, a3=0)
			db.session.add(user)
			db.session.commit()
			return render_template('studentCreated.html')
	except:
		db.session.rollback()
		return render_template('usernameError.html')



# Dont use  wtf forms or anything else... just query the database 
# if it matches, then sign in... if not return errorpage
# maybe add more marks columns
# Show name. I can do that through passing parameters to render_template()
# First build instructor signIn Page and features once inside.
# But the question is, if we only login using db query, how will we maintain session.

#follow the tut -- delete this comment.









@app.route('/login-instructor', methods=['GET', 'POST'])
def instructor_login():
	if 'instructor_dash' in session:
		return redirect(url_for('instructor_dash'))

	else:

		if request.method == 'POST':
			req = request.form
			username = req['username']
			password = req['password']

			user = Instructor.query.filter_by(username=username).first()
			if user:
				if check_password_hash(user.password, password): 

					session['instructor_dash'] = username
					return redirect(url_for('instructor_dash'))

			return 'Invalid Username or Password'
		else:
			if 	"instructor_dash" in session:
				return redirect(url_for('instructor_dash'))
			return render_template('login.html')



@app.route('/instructor-dash')
def instructor_dash():
	if 'instructor_dash' in session:
		instructor_dash = session["instructor_dash"]
		name = Instructor.query.filter_by(username=instructor_dash).first()
		return render_template('instructor-dash.html', name = name.name)
	else:
		return redirect(url_for('instructor_login'))


@app.route("/logout")
def logout():
	session.pop("instructor_dash", None)
	return redirect(url_for('student_or_instructor'))


@app.route("/class-marks")
def class_marks():
	if 'instructor_dash' in session:
		c = sqlite3.connect('C:\\Users\\HP\\Downloads\\Web Application\\assignment3\\assignment3.db')
		cur = c.cursor()
		cur.execute("SELECT * FROM Student")
		test = cur.fetchall()

		return render_template('class-marks.html', data = test) 
	else:
		return redirect(url_for('instructor_login'))



@app.route("/feedback")
def anon_feedback():
	if 'instructor_dash' in session:

		instructor_dash = session["instructor_dash"]
		name = Instructor.query.filter_by(username=instructor_dash).first()
		use = name.username
		t = str(use)

		c = sqlite3.connect('C:\\Users\\HP\\Downloads\\Web Application\\assignment3\\assignment3.db')
		cur = c.cursor()
		cur.execute('SELECT * FROM Feedback WHERE username=(?)', (t,))
		test = cur.fetchall()

		return render_template('feedback.html', data = test, data1 = name.name) 
	else:
		return redirect(url_for('instructor_login'))






# I think in this function should take in utorID and new mark
# Then query that username and enter that mark 


@app.route("/markupdate", methods=['GET', 'POST'])
def marks_update():

	if 'instructor_dash' in session:

		if request.method == 'POST':
			req = request.form
			utorID = req['utorid']
			assign = req['assign']
			mark = req['mark']
			mark = int(mark)

			student = Student.query.filter_by(username=utorID).first()

			if hasattr(student, assign):
				setattr(student, assign, mark)
				db.session.commit()
				return render_template('newmarks.html', name = student.name, mark = str(getattr(student, assign)))
			else:
				db.session.rollback()
				return render_template('wrongassinment.html')



			
			#return 'done mark'
		return render_template('markupdate.html')
	else:
		return redirect(url_for('instructor_login'))

	
@app.route("/2")
def q():
	return render_template('navbar.html')



@app.route("/viewremark")
def view_remark():
	if 'instructor_dash' in session:

		c = sqlite3.connect('C:\\Users\\HP\\Downloads\\Web Application\\assignment3\\assignment3.db')
		cur = c.cursor()
		cur.execute("SELECT * FROM Regrade")
		test = cur.fetchall()

		return render_template('viewremark.html', data = test) 
	else:
		return redirect(url_for('instructor_login'))





@app.route("/lecs")
def lecss():
	
    if 'instructor_dash' in session:
        return render_template('lecs.html')

@app.route("/labs")
def labss():

    if 'instructor_dash' in session:
        return render_template('labs.html')

@app.route("/asign")
def asignn():

    if 'instructor_dash' in session:
        return render_template('assign.html')





# ------------ Student Functions Begin


#Edit this, this is the student end functionality
#------------------------------------------------------


@app.route('/login-student', methods=['GET', 'POST'])
def student_login():

	if 'student_log' in session:
		return render_template('student.html')

	else:
		if request.method == 'POST':
			req = request.form
			username = req['username']
			password = req['password']

			user = Student.query.filter_by(username=username).first()
			if user:
				if check_password_hash(user.password, password):
					session['student_log'] = username
					return render_template('student.html', name=user.name)
			return 'Invalid Username or Password'
		else:
			if 'student_log' in session:
				return render_template('student.html', name=user.name)
			return render_template('studentlogin.html')








@app.route("/anon-feedback", methods=['GET', 'POST'])
def feed_back():

	try:
		if request.method == 'POST':
			req = request.form
			instName = req['teach_name']
			name = Instructor.query.filter_by(name=instName).first()

			teaching_feedback = req['teaching_feedback']
			IMPROVEMENT_FEEDBACK = req['IMPROVEMENT_FEEDBACK']
			LAB_FEEDBACK = req['LAB_FEEDBACK']
			LAB_IMPROVEMENT_FEEDBACK = req['LAB_IMPROVEMENT_FEEDBACK']
			g = Feedback(username=name.username, f1=teaching_feedback, f2=IMPROVEMENT_FEEDBACK, f3=LAB_FEEDBACK, f4=LAB_IMPROVEMENT_FEEDBACK)
			db.session.add(g)
			db.session.commit()
			return redirect(url_for('student_login'))

	except:
		return redirect(url_for('student_login'))
	# g = Feedback(username='zaheeral', feedback='Toronmto')
	# db.session.add(g)
	# db.session.commit()
	# return 'feedback added'

	c = sqlite3.connect('C:\\Users\\HP\\Downloads\\Web Application\\assignment3\\assignment3.db')
	cur = c.cursor()
	cur.execute("SELECT name FROM Instructor")
	test = cur.fetchall()
	return render_template('final_feed.html', activities=test)



@app.route("/studentmark")
def stumark():

	if 'student_log' not in session:
		return redirect(url_for('student_login'))

	else:

		student_log = session["student_log"]
		name = Student.query.filter_by(username=student_log).first()

		return render_template('remark_req.html', item=name)


@app.route('/remark', methods=['GET', 'POST'])
def re():

	if 'student_log' in session:

		if request.method == 'POST':

			req = request.form
			assign = req['assign']
			reason = req['reason']

			student_log = session["student_log"]
			name = Student.query.filter_by(username=student_log).first()

			g = Regrade(username=name.username, assignment=assign, reason=reason)
			db.session.add(g)
			db.session.commit()

			return redirect(url_for('student_login'))
		

	else:

		return redirect(url_for('student_login'))

	return render_template('markrequest.html')


@app.route("/logout-student")
def logout_student():
	session.pop("student_log", None)
	return redirect(url_for('student_or_instructor'))











# ---------------Student Navbar Pages -----------------



@app.route('/s_calendar',methods=['GET','POST']) #calendar page, if user is in session, send them to calendar.html
def calendar():
    if 'student_log' in session:
        return render_template('s_calendar.html')

@app.route('/s_news',methods=['GET','POST'])
def news():
    if 'student_log' in session:
        return render_template('s_news.html')

@app.route('/s_schedule',methods=['GET','POST'])
def schedule():
    if 'student_log' in session:
        return render_template('s_schedule.html')
@app.route('/s_labs',methods=['GET','POST'])
def labs():
    if 'student_log' in session:
        return render_template('s_labs.html')
@app.route('/s_assignments',methods=['GET','POST'])
def assignments():
    if 'student_log' in session:
        return render_template('s_assignments.html')
@app.route('/s_test',methods=['GET','POST'])
def test():
    if 'student_log' in session:
        return render_template('s_test.html')
@app.route('/s_team',methods=['GET','POST'])
def team():
    if 'student_log' in session:
        return render_template('s_team.html')






if __name__ == '__main__':
	app.run(debug=True)
