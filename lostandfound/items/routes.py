from lostandfound import db
from lostandfound.utils import SMS
from lostandfound.models import LostItem,FoundItem
from lostandfound.items.forms import (NewLostItemForm,
	UpdateLostItemForm,NewFoundItemForm)
from lostandfound.items.utils import (save_item_picture,
	delete_item_picture,PredictImage,sendPushNotification)
from flask import (render_template,flash,redirect,
	url_for,request,Blueprint,abort,current_app)
from flask_login import current_user,login_required
import os


#create Blueprint for items routes

items = Blueprint('items',__name__)

@items.route("/lostitems/")
@login_required
def lost_items():
	page = request.args.get('page',1,type=int)
	#fetch limited number of items per page
	items = LostItem.query.order_by(LostItem.date_reported.desc()).paginate(page=page,per_page=4)
	return render_template('lost_items.html',title='Lost Items',items=items)

@items.route("/founditems/")
@login_required
def found_items():
	user_lost_items = LostItem.query.filter_by(owner=current_user).first()
	#some little access control
	if user_lost_items:
		page = request.args.get('page',1,type=int)
		#fetch limited number of items per page
		items = FoundItem.query.order_by(FoundItem.date_reported.desc()).paginate(page=page,per_page=4)
		return render_template('found_items.html',title='Found Items',items=items)
	else:
		flash('You have to report a lost item to access that page','warning')
		return redirect(url_for('users.home'))

@items.route("/lostitem/new/",methods=['GET','POST'])
@login_required
def new_lost_item():
	form = NewLostItemForm()
	if form.validate_on_submit():
		item_picture = 'default.png'
		if form.picture.data:
			item_picture = save_item_picture(form.picture.data)
		item = LostItem(name=form.name.data.capitalize(),item_image=item_picture,place_lost=form.place_lost.data.capitalize(),description=form.description.data.title(),owner=current_user)
		db.session.add(item)
		db.session.commit()
		flash(f"Item has been posted","success")
		return redirect(url_for('items.lost_items'))

	return render_template('add_lost_item.html',title='New Lost Item',form=form)

@items.route('/item/<int:item_id>/update/',methods=['GET','POST'])
@login_required
def update_lost_item(item_id):
	item = LostItem.query.get_or_404(item_id)
	if item.owner != current_user:
		abort(403)
	form = UpdateLostItemForm()
	if form.validate_on_submit():
		item_picture = item.item_image
		if form.picture.data:
			item_picture = save_item_picture(form.picture.data)
		item.name = form.name.data.capitalize()
		item.place_lost = form.place_lost.data.capitalize()
		item.description = form.description.data.capitalize()
		item.item_image = item_picture
		db.session.commit()
		flash("The item has been updated","success")
		return redirect(url_for('items.lost_items'))
	elif request.method == 'GET':
		form.name.data = item.name
		form.place_lost.data = item.place_lost
		form.description.data = item.description
	return render_template('update_lost_item.html',title='Update item',form=form)
#notify owner of a lost item 
#when found by another user
@items.route('/item/<int:item_id>/notify/',methods=['POST'])
@login_required
def send_notification_to_item_owner(item_id):
	item = LostItem.query.get_or_404(int(item_id))
	sms = SMS()
	message = "Hello {}.\n{} found your lost {}\n.Phone:{}\nEmail:{}".format(item.owner.username,current_user.username,item.name,current_user.phone,current_user.email)
	recipient = list(item.owner.phone)
	try:
		response = sms.send(recipient,message)
		#code for debugging purposes
		print(response)
		flash(f"A notification has been sent to the owner of that item.Wait as they contact you.","success")
		return redirect(url_for('items.lost_items'))
	except Exception as e:
		#error while sending SMS
		flash(f"There was an error on our end.Please try again after some time.","danger")
		return redirect(url_for('items.lost_items'))


@items.route('/founditem/new/',methods=['GET','POST'])
@login_required
def new_found_item():
	form = NewFoundItemForm()
	if form.validate_on_submit():
		item_picture = save_item_picture(form.picture.data)
		item = FoundItem(name=form.name.data.capitalize(),item_image=item_picture,place_found=form.place_found.data.capitalize(),description=form.description.data.title(),finder=current_user)
		db.session.add(item)
		db.session.commit()

		#predict what image was uploaded
		Predictor = PredictImage(os.path.join(current_app.root_path,'static/item_pics',item_picture))
		matched_name = Predictor.makeInference()

		print("\n\nThe model predicted {}\n\n".format(matched_name))

		#Get the matched items from the database
		
		matched_items = LostItem.query.filter_by(name=matched_name.capitalize()).all()

		#list comprehensions much cheaper than loops

		recipients = [item.owner.phone for item in matched_items]
		
		#construct the message for each individual user to be notified of the found item
		message = "Hello.{} found a {}.This could be the item you are looking for.Check it out.".format(current_user.username,matched_name.capitalize())

		#send message
		try:
			response = SMS().send(recipients,message)
			#print(response)
		except Exception as e:
			#debugging code
			print(e)
		pusher_client = sendPushNotification()
		pusher_client.trigger('notification','found-item',{'message':'Someone posted a found item'})

		flash(f"Item has been posted","success")
		return redirect(url_for('items.found_items'))

	return render_template('add_found_item.html',title='New Found Item',form=form)

@items.route('/lost-item/<int:item_id>/delete/',methods=['POST'])
@login_required
def delete_lost_item(item_id):
	item = LostItem.query.get_or_404(item_id)
	if item.owner != current_user:
		abort(403)
	#delete the item image from the filesystem
	delete_item_picture(item.item_image)
	#delete item from database
	db.session.delete(item)
	db.session.commit()
	flash(f"Item has been deleted","success")
	return redirect(url_for('items.lost_items'))

@items.route('/found-item/<int:item_id>/delete/',methods=['POST'])
@login_required
def delete_found_item(item_id):
	item = FoundItem.query.get_or_404(item_id)
	if item.finder != current_user:
		abort(403)
	#delete the item image from the filesystem
	delete_item_picture(item.item_image)
	#delete item from database
	db.session.delete(item)
	db.session.commit()
	flash(f"Item has been deleted","success")
	return redirect(url_for('items.found_items'))

@items.route('/search/lostitems/')
@login_required
def search_lostitems():
	page = request.args.get('page',1,type=int)
	#fetch limited number of items per page
	items = LostItem.query.whoosh_search(request.args.get('query')).order_by(LostItem.date_reported.desc()).paginate(page=page,per_page=4)
	return render_template('lost_items.html',title='Lost Items',items=items)

@items.route('/search/founditems/')
@login_required
def search_founditems():
	page = request.args.get('page',1,type=int)
	#fetch limited number of items per page
	items = FoundItem.query.whoosh_search(request.args.get('query')).order_by(FoundItem.date_reported.desc()).paginate(page=page,per_page=4)
	return render_template('found_items.html',title='Found Items',items=items)

