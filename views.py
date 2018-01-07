import os
import random
import datetime
from flask import g,render_template,flash,redirect,url_for,request,send_from_directory,session
from flask_login import login_user, logout_user, current_user, login_required
from parking import app,db,login_manager
from models import User, correctLogin, Parking, Booking, Sector,Notification
from forms import RegistrationForm, LoginForm
from werkzeug.utils import secure_filename


@app.route('/')
def home():
    if current_user.is_anonymous:
        return render_template("cover.html")
    return redirect(url_for('dashboard'))

@app.route('/loadsectors',methods=['GET'])
@login_required
def loadsectors():
    for i in range(1,5):
        new_sector = Sector()
        db.session.add(new_sector)
    for i in range(1,5):
        with open('Sector '+str(i)) as sector:
            for line in sector.readlines():
                loclat,loclong = line.split(', ')
                new_parking = Parking() 
                new_parking.sectorid = i
                new_parking.loclat = loclat
                new_parking.loclong = loclong
                new_parking.available= 2
                new_parking.disability = random.choice(range(0,2))
                db.session.add(new_parking)
    db.session.commit()
    flash("successfully added parking spots")
    return redirect(url_for('login'))

@app.route('/viewspaces')
@app.route('/viewspaces/<sector>')
@login_required
def viewspaces(sector=None):
    if sector:
        allparkings=Parking.query.filter(Parking.sectorid==int(sector)).all()
        for parking in allparkings:
            bookings = Booking.query.filter(Booking.parkingid==parking.id).all()
            for booking in bookings:
                if datetime.datetime.now()>=booking.bookingto - datetime.timedelta(minutes=15) and datetime.datetime.now()<booking.bookingto:
                    parking.available=1
                    break
                elif datetime.datetime.now()<booking.bookingto and booking.checkin is not None:
                    parking.available=0
                    break
                else:
                    parking.available=2
            if parking.available == 2 and parking.disability ==1:
                parking.available = 3

        return render_template('viewparkings.html',title='Sector '+str(sector),parkings=allparkings)
    qsectors = Sector.query.all()
    return render_template('viewsectors.html',title='Sectors',sectors=qsectors)

@app.route('/book/',methods=['POST','GET'])
@app.route('/book/<int:slot>',methods=['POST','GET'])
@login_required
def book(slot=None):
    if not slot:
        return redirect(url_for('viewspaces'))

    if request.method=="POST":
        daytime = request.form['arrivalday']+" "+request.form['arrivaltime']
        daytime=datetime.datetime.strptime(daytime, "%Y-%m-%d %H:%M")
        duration = datetime.timedelta(hours=float(request.form['bookingdur']))
        finaltime = daytime + duration
        #conflicts1 = Booking.query.filter(Booking.parkingid==int(slot)).filter(daytime<=Booking.bookingto).filter(Booking.bookingto<=finaltime).count()
        #conflicts2 = Booking.query.filter(Booking.parkingid==int(slot)).filter(daytime<=Booking.bookingfrom).filter(Booking.bookingfrom<=finaltime).count()
        #conflicts = conflicts1+conflicts2
        #if conflicts:
        #    flash("The slot is already booked during that time period. Please try another day or time period.")
        #    return redirect(request.path)
        new_booking = Booking()
        new_booking.parkingid = int(slot)
        new_booking.userid = current_user.id
        new_booking.bookingfrom = daytime
        new_booking.bookingto = finaltime
        db.session.add(new_booking)
        db.session.commit()
        flash("Your booking was successfull")
        return redirect(url_for('viewspaces'))

    return render_template('book.html',title="Booking",slotno=slot)

@app.route('/checkin/')
@app.route('/checkin/<bookingid>')
@login_required
def checkin(bookingid):
    booking = Booking.query.filter(Booking.id==bookingid).first()
    booking.checkin = datetime.datetime.now()
    parkingid = booking.parkingid
    userstonotify = []
    for stupidbooking in Booking.query.filter(Booking.bookingto>=booking.checkin).filter(Booking.bookingto<=booking.bookingto).filter(Booking.checkin==None).all():
        userstonotify.append(stupidbooking.userid)
        stupidbooking.bookingfrom = None
    db.session.commit()
    notifyusers(userstonotify,parkingid)
    flash("Checkin successfull")
    return redirect(url_for('dashboard'))

def texthere(phoneno,textmsg):
    from clockwork import clockwork

    api = clockwork.API('64cb471a7ba66565a1965ac118baadffb36e7b1e')

    message = clockwork.SMS(
    to = phoneno,
    message = textmsg)

    try:
        response = api.send(message)
        logfile = open("logfile","a")

        if response.success:
            logfile.write(str(response.success)+"\n")
        else:
            logfile.writelines([phoneno,response.error_code,response.error_message])
    except:
        pass

def notifyusers(userstonotify,parkingid):
    for user in userstonotify:
        notification = Notification()
        notification.userid = user
        message = "Your spot at "+str(parkingid)+" has been occupied"
        notification.message=message
        texthere(User.query.filter(User.id==user).first().phoneno,message)
        db.session.add(notification)
    db.session.commit()

@app.route('/notifications')
@login_required
def notificaitons():
    return render_template("notifications.html",title="Notifications",notifications=Notification.query.filter(Notification.userid==current_user.id).all())

@app.route('/dashboard')
@login_required
def dashboard():
    booking = Booking.query.filter(Booking.userid==current_user.id).filter(Booking.bookingto>datetime.datetime.now()).filter(Booking.bookingfrom!= None).all()
    return render_template("dashboard.html",bookings=booking,title="Dashboard",notificationcount=Notification.query.filter(Notification.userid==current_user.id).count())

@app.route('/register',methods=['POST','GET'])
def register():
    if not current_user.is_anonymous:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).count() == 0:
            user = User(form.fullname.data,form.email.data,form.password.data,form.phoneno.data)
            db.session.add(user)
            db.session.commit()
            flash('You registered Successfully')
            return redirect(url_for('login'))
        else:
            flash('Email already registered')
    return render_template('register.html',title="Register",form=form)


@app.route('/login',methods=['POST','GET'])
def login():
    if not current_user.is_anonymous:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = load_user(form.email.data)
        if correctLogin(user,form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Credentials')
    return render_template('login.html',title="Login",form=form)

@login_manager.user_loader
def load_user(email):
    return User.query.filter_by(email=email).first()

def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['jpg','png','jpeg','gif'])
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def uploadfile(submitted):
    if submitted and allowed_file(submitted.filename):
        filename = secure_filename(submitted.filename)
        submitted.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        return filename

@app.route('/images/<path>')
def images(path):
    return send_from_directory('images',path)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')
