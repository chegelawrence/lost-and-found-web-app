from lostandfound import db,bcrypt
from lostandfound.users.forms import (LoginForm,RegistrationForm,UpdateAccountForm,
	ChangePasswordForm,RequestPasswordResetForm,
	ResetPasswordForm,UpdateProfilePictureForm,PhoneVerificationForm)
from lostandfound.models import User,LostItem
from lostandfound.users.utils import save_profile_picture,send_reset_email
from flask import render_template,flash,redirect,url_for,request,Blueprint,abort,current_app,session
from flask_login import login_user,current_user,logout_user,login_required
from authy.api import AuthyApiClient


#create Blueprint for user routes

users = Blueprint('users',__name__)

@users.route("/",methods=['GET','POST'])
def index():
	if current_user.is_authenticated:
		return redirect(url_for('users.home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()

		if user and bcrypt.check_password_hash(user.password,form.password.data):
			login_user(user,remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for("users.home"))
            
		else:
			flash(f"The email or password is wrong","danger")
	return render_template('index.html',form=form,title='Login')

@users.route("/register/",methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('users.home'))

	#set up the phone verification api
	twilioApi = AuthyApiClient(current_app.config['AUTHY_API_KEY'])
	form = RegistrationForm()
	if form.validate_on_submit():

		session['phone_number'] = form.phone.data
		try:
			twilioApi.phones.verification_start(form.phone.data,'+254',via='sms')
		except Exception as e:
			print(e)

		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		#create new user
		user = User(username=form.username.data.capitalize(),email=form.email.data.lower(),phone=form.phone.data,password=hashed_password)
		#create session and commit
		db.session.add(user)
		db.session.commit()
		return redirect(url_for("users.verify_phone"))

	return render_template("register.html",form=form,title='Register')

@users.route('/phone-verification/',methods=['GET','POST'])
def verify_phone():
	#logout the user first to prevent redirecting to dashboard
	logout_user()
	form = PhoneVerificationForm()
	if form.validate_on_submit():
		code = form.verification_code.data
		phone_number = session.get('phone_number')
		twilioApi = AuthyApiClient(current_app.config['AUTHY_API_KEY'])
		try:
			verification = twilioApi.phones.verification_check(phone_number,'+254',code)
			if verification.ok():
				#phone successfully verified
				flash("You can now log in with your account","success")
				return redirect(url_for('users.index'))
			else:
				flash("The code you entered is not correct.Try again","danger")
				return redirect(url_for('users.verify_phone'))

		except Exception as e:
			return redirect(url_for('users.index'))
	return render_template('verify_phone.html',title='Phone verification',form=form)

@users.route("/home/")
@login_required
def home():
	return render_template('home.html',title='Home')



@users.route("/account/",methods=['GET','POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		form_username = form.username.data
		form_email = form.email.data
		current_user.username = str(form_username).capitalize()
		current_user.email = str(form_email).lower()
		current_user.phone = form.phone.data
		db.session.commit()
		flash(f"Your account has been updated!","success")
		return redirect(url_for("users.account"))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
		form.phone.data = current_user.phone
	return render_template("account.html",title='User Account',form=form)

@users.route('/profile-picture/',methods=['GET','POST'])
@login_required
def update_profile_picture():
	form = UpdateProfilePictureForm()
	if form.validate_on_submit():
		profile_image = save_profile_picture(form.picture.data)
		current_user.profile_image = profile_image
		db.session.commit()
		flash('You profile picture has been updated','success')
		redirect(url_for('users.update_profile_picture'))
	return render_template('profile_picture.html',form=form)

@users.route("/reset-password/",methods=['GET','POST'])
@login_required
def changepassword():
	form = ChangePasswordForm()

	if form.validate_on_submit():
		current_user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		db.session.commit()
		flash(f"Password update successful","success")
		return redirect(url_for("users.changepassword"))
	return render_template('changepassword.html',form=form,title='Change Password')

@users.route("/items/<string:username>/")
def user_items(username):
	page = request.args.get('page',1,type=int)
	user = User.query.filter_by(username=username).first_or_404()
	if user != current_user:
		#this user does not have enough permissions
		abort(403)
	items = LostItem.query.filter_by(owner=user)\
	.order_by(LostItem.date_reported.desc())\
	.paginate(page=page,per_page=4)
	return render_template('user_items.html',items=items,user=user)

@users.route("/forgot-password/",methods=['GET','POST'])
def forgotpassword():
	if current_user.is_authenticated:
		return redirect(url_for('users.home'))
	form = RequestPasswordResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash(f"An email has been sent with instructions on how to reset your password","success")
		return redirect(url_for('users.index'))
	return render_template('forgotpassword.html',form=form,title='Forgot Password')

#reset the user
@users.route("/forgot-password/<token>/",methods=['GET','POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('users.home'))
	user = User.verify_reset_token(token)

	if user is None:
		flash(f"That is an invalid token","warning")
		return redirect(url_for('users.forgotpassword'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		new_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = new_password
		db.session.commit()
		flash(f"Your password has been updated!","success")
		return redirect(url_for('users.index'))
	return render_template('reset_password.html',title='Reset password',form=form)


@users.route("/logout/")
@login_required
def logout():
    #destroy user session
    logout_user()
    flash(f"You have been logged out","success")
    return redirect(url_for("users.index"))
