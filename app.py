import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from models import Note, Tag, Address_book, Record, Birthday, Phone, Email, Address, db_session, note_m2m_tag, User, adbooks_user, notes_user, tags_user
from sqlalchemy import or_
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from forms import LoginForm, RegistrationForm, RecordForm
from collections import defaultdict
from new_parsing import get_wp_news
from fileinput import filename
import imghdr
import os
from flask import Flask, render_template, request, redirect, url_for, abort, send_from_directory
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.debug = True
app.env = "development"
app.config['SECRET_KEY'] = 'any secret string'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'uploads'
bcrypt = Bcrypt(app)
MAX_CONTENT_LENGHT = 1024 * 1024

login_manager = LoginManager(app)
login_manager.login_view = "login"

login_manager.login_message_category = "info"

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).get(int(user_id))

@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413

@app.route("/", methods=["GET", "POST"], strict_slashes=False)
def index():
    return render_template("index_example.html")

@app.route("/news", methods=["GET"], strict_slashes=False)
def get_news():
    news = get_wp_news()
    return render_template("news.html", news=news)


@app.route("/registration", methods=["GET", "POST"])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data). \
            decode('utf-8')
        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_password)
        db_session.add(user)
        db_session.commit()
        flash('Account created!Please login', "success")
        return render_template("success.html")
        
    return render_template("registration.html", title="Register", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        print("authenticated")
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db_session.query(User).filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,
                                               form.password.data):
            login_user(user, remember=form.remember.data)
            # next_page = request.args.get("next")
            flash("You have been logged in!", "success")
            return redirect(url_for("index"))
        else:

            flash("Login Unsuccessful. Please check email and password",
                  "danger")

    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/addressbooks", methods=["GET"], strict_slashes=False)
def get_addressbooks():

    user = db_session.query(User).filter_by(id=current_user.id).first()
    address_books = user.addressbooks
    return render_template("address_books.html", address_books=address_books)


@app.route("/addressbook/", methods=["GET", "POST"], strict_slashes=False)
@login_required
def create_addressbook():

    if request.method == "POST":
        name = request.form.get("name")
        adbook = Address_book(name=name)
        user = db_session.query(User).filter_by(id=current_user.id).first()
        user.addressbooks.append(adbook)
        db_session.add(adbook)
        db_session.commit()
        return redirect("/addressbooks")
    
    return render_template("addressbook.html")


@app.route("/record/result/<book_id>", methods=["GET", "POST"], strict_slashes=False)
def search_in_record(book_id):

    if request.method == "POST":
        recorded = []
        key = request.form.get("key")
        records = db_session.query(Record).filter(or_(Record.name.like(f'%{key}%'),Record.id.like(f'%{key}%'))).all()
        for obj in records:
            res_note = db_session.query(Record).filter(Record.id == obj.id).first()
            if res_note:
                if not res_note in recorded:
                    recorded.append(res_note)


        return render_template("record_result.html", recorded=recorded, book_id=book_id, key=key, count_res=1)

@app.route("/records/<book_id>", methods=["GET"], strict_slashes=False)
def get_records(book_id):

    records = db_session.query(Record).filter(Record.book_id == book_id).all()
    return render_template("records.html", records=records, book_id=book_id)


@app.route("/detailrecord/<book_id>/<record_id>", methods=["GET", "POST"], strict_slashes=False)
def detailrecord(book_id, record_id):
    if request.method == "POST":
        record_to_change = db_session.query(Record).filter( (Record.id == record_id) & (Record.book_id == book_id)).first()
        form = RecordForm()
        name = form.name.data
        bd_str_to_date = form.birthday.data
        birthday = Birthday(bd_date=bd_str_to_date)
        phone = form.phone.data
        phones = []
        phones.append(Phone(name=phone))
        email = form.email.data
        emails = []
        emails.append(Email(name=email))
        address = form.address.data
        addresses = []
        addresses.append(Address(name=address))
        record = Record(name=name, birthday=birthday, phones=phones, emails=emails, addresses=addresses)

        adbook = db_session.query(Address_book).filter(Address_book.id == book_id).first()
        adbook.records.append(record)
        db_session.add(adbook)
        db_session.commit()

        return render_template("records.html", records=records)

    record = db_session.query(Record).filter( (Record.id == record_id) & (Record.book_id == book_id)).first()
    birthday = record.birthday.bd_date.strftime('%m.%d.%Y')
    return render_template("detail_record.html", record_id=record_id, book_id=book_id, record=record, birthday=birthday)


@app.route("/record/<book_id>", methods=["GET", "POST"], strict_slashes=False)
def create_record(book_id):

    form = RecordForm()
    if request.method == "POST":
        name = form.name.data
        bd_str_to_date = form.birthday.data
        birthday = Birthday(bd_date=bd_str_to_date)
        phone = form.phone.data
        phones = []
        phones.append(Phone(name=phone))
        email = form.email.data
        emails = []
        emails.append(Email(name=email))
        address = form.address.data
        addresses = []
        addresses.append(Address(name=address))
        record = Record(name=name, birthday=birthday, phones=phones, emails=emails, addresses=addresses)

        adbook = db_session.query(Address_book).filter(Address_book.id == book_id).first()
        adbook.records.append(record)
        db_session.add(adbook)
        db_session.commit()
        return redirect(f"/records/{book_id}")
    
    return render_template("record.html", book_id=book_id, form=form)

@app.route("/change/record/<book_id>/<record_id>", methods=["GET", "POST"], strict_slashes=False)
def change_record(book_id, record_id):

    data_type = request.args.get("name")

    if request.method == "POST":

        name = request.form.get("name")
        record = db_session.query(Record).filter( (Record.id == record_id) & (Record.book_id == book_id)).first()

        fields_dict = {"phone": {"class": Phone, "records_attr": record.phones, "get_name": "phone"},
                       "email": {"class": Email, "records_attr": record.emails, "get_name": "email"},
                       "address": {"class": Address, "records_attr": record.addresses, "get_name": "address"}
                       }
        class_name = fields_dict[data_type]["class"]
        add_list = fields_dict[data_type]["records_attr"]
        add_list.append(class_name(name=name))

        db_session.commit()
        return redirect(url_for("get_record_info", book_id=book_id, record_id=record_id))
    
    return render_template("change_record.html", data_type=data_type, book_id=book_id, record_id=record_id)


@app.route("/record/<book_id>/<record_id>", methods=["GET"], strict_slashes=False)
def get_record_info(book_id, record_id):

    record = db_session.query(Record).filter( (Record.id == record_id) & (Record.book_id == book_id)).first()
    birthday = record.birthday.bd_date.strftime('%m.%d.%Y')
    return render_template("record_info.html", record_id=record_id, book_id=book_id, record=record, birthday=birthday)

@app.route("/add_record/<book_id>/<record_id>", methods=["GET", "POST"], strict_slashes=False)
def add_record(book_id, record_id):
    data_type = request.args.get("name")
    db_session.query(Record).filter( (Record.id == record_id) & (Record.book_id == book_id)).delete()
    db_session.commit()

    return redirect(f"/change/record/{book_id}/{record_id}?name={data_type}")

@app.route("/deleterecord/<book_id>/<record_id>", strict_slashes=False)
def delete_record(book_id, record_id):
    db_session.query(Record).filter( (Record.id == record_id) & (Record.book_id == book_id)).delete()
    db_session.commit()

    return redirect(f"/records/{book_id}")


@app.route("/delete/addressbook/<book_id>", strict_slashes=False)
def delete_addressbook(book_id):
    db_session.query(Address_book).filter(Address_book.id == book_id).delete()
    db_session.commit()

    return redirect(f"/addressbooks")


@app.route("/delete/<book_id>/<record_id>", strict_slashes=False)
def delete_record_info(record_id, book_id):

    field_to_delete = request.args.get("name")
    id_to_delete = request.args.get("id")
    record = db_session.query(Record).filter((Record.id == record_id) & (Record.book_id == book_id)).first()

    fields_dict = {"phone": {"class": Phone, "records_attr": record.phones, "get_name": "phone"},
                "email": {"class": Email, "records_attr": record.emails, "get_name": "email"},
                "address": {"class": Address, "records_attr": record.addresses, "get_name": "address"}
                }
    attr_to_del = fields_dict.get(field_to_delete)["records_attr"]
    item = next(filter(lambda x: x.name==id_to_delete, attr_to_del), None)
    attr_to_del.remove(item)
    db_session.commit()
    return redirect(url_for("get_record_info", book_id=book_id, record_id=record_id))


@app.route("/detail/<id>", methods=["GET", "POST"], strict_slashes=False)
def detail(id):
    user = db_session.query(User).filter_by(id=current_user.id).first()
    tags = user.tags
    if request.method == "POST":
        note_to_change = db_session.query(Note).filter(Note.id==id).first()

        name = request.form.get("name")
        if name:
            note_to_change.name = name

        description = request.form.get("description")
        if description:
            note_to_change.description = description
        
        tags_id_list = request.form.getlist("tag_ch")
        if tags_id_list:
            tags_obj = []
            for tag_id in tags_id_list:
                tags_obj.append(db_session.query(Tag).filter(Tag.id == tag_id).first())
            note_to_change.tags = tags_obj
            
        db_session.add(note_to_change)
        db_session.commit()
        
        notes = user.notes
        tags = user.tags
        redirect(url_for("notebook", notes=notes, tags=tags))
        #return render_template("notebook.html", notes=notes, tags=tags)

    note = db_session.query(Note).filter(Note.id == id).first()
    return render_template("detail.html", note=note, tags=tags)


@app.route("/note/", methods=["GET", "POST"], strict_slashes=False)
def add_note():
    user = db_session.query(User).filter_by(id=current_user.id).first()

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        tags_id= request.form.getlist("tags")
        tags_obj = []
        for tag_id in tags_id:
            tags_obj.append(db_session.query(Tag).filter(Tag.id == tag_id).first())
        note = Note(name=name, description=description, tags=tags_obj)

        user.notes.append(note)

        db_session.add(note)
        db_session.commit()
        return redirect("/notebook")
    else:
        tags = user.tags
        # tags = db_session.query(Tag).all()

    return render_template("note.html", tags=tags)


@app.route("/tag/", methods=["GET", "POST"], strict_slashes=False)
def add_tag():

    user = db_session.query(User).filter_by(id=current_user.id).first()

    if request.method == "POST":
        name = request.form.get("name")
        tag = db_session.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)

        user.tags.append(tag)

        db_session.add(tag)
        db_session.commit()
        return redirect(f"/tag")

    tags = user.tags
    return render_template("tag.html", tags=tags)


@app.route("/delete/<id>", strict_slashes=False)
def delete(id):
    user = db_session.query(User).filter_by(id=current_user.id).first()
    if user:
        note_to_del = db_session.query(Note).filter(Note.id == id).first()
        user.notes.remove(note_to_del)
        for tag in note_to_del.tags:
            tag.notes.remove(note_to_del)
        db_session.query(Note).filter(Note.id == id).delete()
        db_session.commit()

        return redirect("/notebook")


@app.route("/done/<id>", strict_slashes=False)
def done(id):
    db_session.query(Note).filter(Note.id == id).first().done = True
    db_session.commit()

    return redirect("/notebook")


@app.route("/note/result", methods=["GET", "POST"], strict_slashes=False)
def search_in_notes():
    
    if request.method == "POST":
        notes = []
        key= request.form.get("key")

        user = db_session.query(User).filter_by(id=current_user.id).first()
        res = user.notes.filter(notes.name.like(f'%{key}%')).all()
        return f"{[i for i in res]}"
        # asc_table_res = db_session.query(note_m2m_tag).\
        #             join(Note, isouter=True).\
        #             join(Tag, isouter=True).\
        #             filter(or_(
        #                 Note.name.like(f'%{key}%'),
        #                 Tag.name.like(f'%{key}%'),
        #                 Note.description.like(f'%{key}%'))).all()
                        
        if key == 'Done':
            notes = db_session.query(Note).filter(Note.done == 1).all()
            return render_template("note_result.html", notes=notes, key=key, count_res=len(notes))

        for obj in asc_table_res:
            res_note = db_session.query(Note).filter(Note.id == obj.note).first()
            if res_note:
                if not res_note in notes:
                    notes.append(res_note)

        return render_template("note_result.html", notes=notes, key=key, count_res=len(notes))


@app.route("/delete/tag/<id>", strict_slashes=False)
def delete_tag(id):
    tag_to_del = db_session.query(Tag).filter(Tag.id == id).first()
    user = db_session.query(User).filter_by(id=current_user.id).first()
    user.tags.remove(tag_to_del)
    #note_to_del = db_session.query(Note).filter(Tag.id == id).first()
    for note in tag_to_del.notes:
        note.tags.remove(tag_to_del)
    #db_session.query(Tag).filter(Tag.id == id).delete()
    db_session.commit()

    return redirect("/tag")


@app.route("/addressbooks/birthdays", methods=["GET", "POST"], strict_slashes=False)
def coming_birthday():
    range_days = 60

    if request.method == "POST":
        inp_brth = request.form.get("key")
        if inp_brth: 
            range_days = int(inp_brth)

    birthdays_dict = defaultdict(list)
    current_date = datetime.datetime.now().date()
    timedelta_filter = datetime.timedelta(days=range_days)

    for name, birthday in [i for i in db_session.query(Record.name, Birthday.bd_date).join(Birthday, isouter=True).all()]:
        if name and birthday: 
            #birthday_date = datetime.strptime(birthday, '%Y-%m-%d').date()
            birthday_date = birthday
            current_birthday = birthday_date.replace(year=current_date.year)
            if current_date <= current_birthday <= current_date + timedelta_filter:
                birthdays_dict[current_birthday].append(name)
                
    return render_template('addressbooks_birthdays.html',  message= birthdays_dict, range_days=range_days)


@app.route("/notebook", methods=["GET", "POST"], strict_slashes=False)
def notebook():
    user = db_session.query(User).filter_by(id=current_user.id).first()
    notes = user.notes

    if request.method == "POST":
        id_tag = request.form.get("tag_ch")
        if id_tag:
            notes = db_session.query(Note).join(note_m2m_tag, isouter=True).join(Tag, isouter=True).filter(Tag.id == id_tag).all()
    
    tags = user.tags

    return render_template("notebook.html", notes=notes, tags=tags)

@app.route('/download')
def download():
    files = os.listdir(app.config['UPLOAD_PATH'])
    return render_template('upload.html', files=files, filename=filename)

@app.route('/download', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
                file_ext != validate_image(uploaded_file.stream):
            return "Invalid image", 400
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    return '', 204

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

@app.route('/downloaded/<file_name>')
def downloadFile (file_name):
    path = f'uploads/{file_name}'
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run()

