from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from flask_login import current_user
from wtforms import StringField,DateField,SelectField,TextAreaField,SubmitField
from wtforms.validators import DataRequired,Length,ValidationError,Regexp

from lostandfound.models import LostItem,FoundItem

class NewLostItemForm(FlaskForm):
	name = StringField('Name of item',validators=[DataRequired(),Length(min=3,max=20),Regexp('[A-Za-z]',message='Item name can only contain letters')])
	place_lost = SelectField(
		'Where did you lose the item',
        choices=[
        ('', 'Select the location'),
        ('library', 'Library'), ('hostel', 'Hostel'), ('chafua', 'Chafua')
        , ('lecture room', 'Lecture Room'), ('conference center', 'Conference Center'), ('swimming pool area', 'Swimming pool area'), ('stadium', 'Stadium'),('basket ball court', 'Basket Ball Court'),('parking lot', 'Parking lot'),('other', 'Other')],
		validators=[DataRequired()])
	description = TextAreaField('Description of the item',validators=[DataRequired(),Length(min=20)])
	picture = FileField('Upload item picture(optional)',validators=[FileAllowed(['png','jpeg','jpg','webp'])])
	submit = SubmitField('Post item')

class NewFoundItemForm(FlaskForm):
	name = StringField('Name of item',validators=[DataRequired(),Length(min=3,max=20),Regexp('[A-Za-z]',message='Item name can only contain letters')])
	place_found = SelectField(
		'Where did you find the item',
        choices=[
        ('', 'Select the location'),
        ('library', 'Library'), ('hostel', 'Hostel'), ('chafua', 'Chafua')
        , ('class', 'Lecture Room'), ('conference center', 'Conference Center'), ('swimming pool area', 'Swimming pool area'), ('stadium', 'Stadium'),('basket ball court', 'Basket Ball Court'),('parking lot', 'Parking lot'),('other', 'Other')],
		validators=[DataRequired()])
	description = TextAreaField('Description of the item',validators=[DataRequired(),Length(min=20)])
	picture = FileField('Upload item picture',validators=[DataRequired(),FileAllowed(['png','jpeg','jpg','webp'])])
	submit = SubmitField('Post item')

class UpdateLostItemForm(FlaskForm):
	name = StringField('Name of item',validators=[DataRequired(),Length(min=3,max=20),Regexp('[A-Za-z]',message='Item name can only contain letters')])
	place_lost = SelectField(
		'Where did you lose the item',
        choices=[
        ('', 'Select the location'),
        ('library', 'Library'), ('hostel', 'Hostel'), ('chafua', 'Chafua')
        , ('class', 'Lecture Room'), ('conference center', 'Conference Center'), ('swimming pool area', 'Swimming pool area'), ('stadium', 'Stadium'),('basket ball court', 'Basket Ball Court'),('parking lot', 'Parking lot'),('other', 'Other')],
		validators=[DataRequired()])
	description = TextAreaField('Description of the item',validators=[DataRequired(),Length(min=20)])
	picture = FileField('Upload item picture(optional)',validators=[FileAllowed(['png','jpeg','jpg','webp'])])
	submit = SubmitField('Update item')

