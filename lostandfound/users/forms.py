from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from flask_login import current_user
from wtforms import StringField,PasswordField,SubmitField,BooleanField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError,Regexp
from lostandfound import bcrypt

from lostandfound.models import User

class LoginForm(FlaskForm):
	email = StringField('Email',validators=[DataRequired(),Email()])
	password = PasswordField('Password',validators=[DataRequired()])
	remember = BooleanField('Keep me logged in')
	submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
	username = StringField('Username',validators=[DataRequired(),Length(min=5,max=20),Regexp('[A-Za-z]',message='Username can only contain letters')])
	email = StringField('Email',validators=[DataRequired(),Email()])
	phone = StringField('Phone',validators=[DataRequired(),Length(max=100),Regexp('[0-9]',message='Phone can only contain numbers')])
	password = PasswordField('Password',validators=[DataRequired(),Length(min=8)])
	confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
	submit = SubmitField('Create account')

	def validate_username(self,username):
		user = User.query.filter_by(username=username.data.capitalize()).first()
		if user:
			raise ValidationError('This username is already taken')
	def validate_email(self,email):
		user = User.query.filter_by(email=email.data.lower()).first()
		if user:
			raise ValidationError('This email is already taken')
	def validate_phone(self,phone):
		user = User.query.filter_by(phone=phone.data).first()
		if user:
			raise ValidationError('This phone number is already taken')

class PhoneVerificationForm(FlaskForm):
	verification_code = StringField('Enter the code here',validators=[DataRequired(),Length(max=4),Regexp('[0-9]')])
	submit = SubmitField('Verify')

class UpdateAccountForm(FlaskForm):
	username = StringField('Username',validators=[DataRequired(),Length(min=5,max=20)])
	email = StringField('Email',validators=[DataRequired(),Email()])
	phone = StringField('Phone',validators=[DataRequired(),Length(max=100)])
	submit = SubmitField('Update account')

	def validate_username(self,username):
		form_username = str(username.data)
		if form_username.capitalize() != current_user.username:
			user = User.query.filter_by(username=username.data.capitalize()).first()
			if user:
				raise ValidationError('This username is already taken')
	def validate_email(self,email):
		form_email = str(email.data)
		if form_email.lower() != current_user.email:
			user = User.query.filter_by(email=email.data.lower()).first()
			if user:
				raise ValidationError('This email is already taken')
	def validate_phone(self,phone):
		if phone.data != current_user.phone:
			user = User.query.filter_by(phone=phone.data).first()
			if user:
				raise ValidationError('This phone number is already taken')

class UpdateProfilePictureForm(FlaskForm):
	picture = FileField('',validators=[DataRequired(),FileAllowed(['png','jpeg','jpg'])])
	submit = SubmitField('Update')

#change password
class ChangePasswordForm(FlaskForm):
	oldpassword = PasswordField('Current password',validators=[DataRequired()])
	password = PasswordField('New password',validators=[DataRequired(),Length(min=8)])
	confirm_password = PasswordField('Confirm new password',validators=[DataRequired(),EqualTo('password')])
	submit = SubmitField('Change password')

	def validate_oldpassword(self,password):
		if not bcrypt.check_password_hash(current_user.password,password.data):
			raise ValidationError('Current password is wrong')

#reset password if forgotten
class RequestPasswordResetForm(FlaskForm):
	email = StringField('Enter your email address',validators=[DataRequired(),Email()])
	submit = SubmitField('Submit')

	def validate_email(self,email):
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			raise ValidationError('This email does not match any records.You must register first')

class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password',validators=[DataRequired(),Length(min=8)])
	confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
	submit = SubmitField('Reset password')
