import datetime
from flask import Flask, render_template, request, redirect, url_for
from models import Note, Tag, Address_book, Record, Birthday, Phone, Email, Address, db_session, note_m2m_tag
from sqlalchemy import or_
from forms import RecordForm#, LoginForm, RegisterForm
from collections import defaultdict
from new_parsing import get_wp_news


app = Flask(__name__)
app.debug = True
app.env = "development"
app.config['SECRET_KEY'] = 'any secret string'
MAX_CONTENT_LENGHT = 1024 * 1024

@app.route("/", methods=["GET", "POST"], strict_slashes=False)
def index():
    return render_template("index_example.html")

@app.route("/news", methods=["GET"], strict_slashes=False)
def get_news():
    news = get_wp_news()
    return render_template("news.html", news=news)


@app.route("/addressbooks", methods=["GET"], strict_slashes=False)
def get_addressbooks():

    address_books = db_session.query(Address_book).all()
    return render_template("address_books.html", address_books=address_books)


@app.route("/addressbook/", methods=["GET", "POST"], strict_slashes=False)
def create_addressbook():
    
    if request.method == "POST":
        name = request.form.get("name")
        adbook = Address_book(name=name)
        db_session.add(adbook)
        db_session.commit()
        return redirect("/addressbooks")
    
    return render_template("addressbook.html")


@app.route("/records/<book_id>", methods=["GET"], strict_slashes=False)
def get_records(book_id):

    records = db_session.query(Record).filter(Record.book_id == book_id).all()
    return render_template("records.html", records=records, book_id=book_id)


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
    if request.method == "POST":
        note_to_change = db_session.query(Note).filter(Note.id==id).first()

        name = request.form.get("name")
        if name:
            note_to_change.name = name

        description = request.form.get("description")
        if description:
            note_to_change.description = description
        
        tags = request.form.get("tags")
        if tags:
            pass
            # db.session.query(Address).filter(Address.contact_id == id).update({"addr": address}, synchronize_session="fetch")
            # if not cont.address:
            #     cont.address = [Address(addr=address, contact_id=id)]

        db_session.add(note_to_change)
        db_session.commit()
        
        notes = db_session.query(Note).all()
        tags = db_session.query(Tag).all()

        return render_template("notebook.html", notes=notes, tags=tags)

    note = db_session.query(Note).filter(Note.id == id).first()
    return render_template("detail.html", note=note)


@app.route("/note/", methods=["GET", "POST"], strict_slashes=False)
def add_note():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        tags_id= request.form.getlist("tags")
        tags_obj = []
        for tag_id in tags_id:
            tags_obj.append(db_session.query(Tag).filter(Tag.id == tag_id).first())
        note = Note(name=name, description=description, tags=tags_obj)
        db_session.add(note)
        db_session.commit()
        return redirect("/notebook")
    else:
        tags = db_session.query(Tag).all()

    return render_template("note.html", tags=tags)


@app.route("/tag/", methods=["GET", "POST"], strict_slashes=False)
def add_tag():
    if request.method == "POST":
        name = request.form.get("name")
        tag = Tag(name=name)
        db_session.add(tag)
        db_session.commit()
        return redirect(f"/tag")

    tags = db_session.query(Tag).all()
    return render_template("tag.html", tags=tags)


@app.route("/delete/<id>", strict_slashes=False)
def delete(id):
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
        
        asc_table_res = db_session.query(note_m2m_tag).\
                    join(Note, isouter=True).\
                    join(Tag, isouter=True).\
                    filter(or_(
                        Note.name.like(f'%{key}%'),
                        Tag.name.like(f'%{key}%'),
                        Note.description.like(f'%{key}%'))).all()
        if key == 'Done' or 'done':
            asc_table_res = db_session.query(Note).filter(Note.done == 1).all()

        for obj in asc_table_res:
            res_note = db_session.query(Note).filter(Note.id == obj.id).first()
            if res_note:
               notes.append(res_note)

        
        # res_notes = [db_session.query(Note).filter(Note.id == obj.id).first() for obj in asc_table_res]#temp code. add rel. to m2m table (example -  https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html)
        # return f"{res_notes}"
        return render_template("note_result.html", notes=notes, key=key, count_res=len(notes))


@app.route("/delete/tag/<id>", strict_slashes=False)
def delete_tag(id):
    db_session.query(Tag).filter(Tag.id == id).delete()
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
    notes = db_session.query(Note).all()

    if request.method == "POST":
        id_tag = request.form.get("tag_ch")
        if id_tag:
            notes = db_session.query(Note).join(note_m2m_tag, isouter=True).join(Tag, isouter=True).filter(Tag.id == id_tag).all()
    
    tags = db_session.query(Tag).all()

    return render_template("notebook.html", notes=notes, tags=tags)
# @app.route("/login", methods=["POST", "GET"])
# def login():

#     form = LoginForm()
#     if form.validate_on_submit():
#         user = dbase.getUserByEmail(form.email.data)
#         if user and check_password_hash(user['psw'], form.psw.data):
#             userlogin = UserLogin().create(user)
#             rm = form.remember.data
#             login_user(userlogin, remember=rm)
#             return redirect(request.args.get("next") or url_for("profile"))

#         flash("Неверная пара логин/пароль", "error")

#     return render_template("login_test.html", menu=dbase.getMenu(), title="Авторизация", form=form)


# @app.route("/register", methods=["POST", "GET"])
# def register():
#     form = RegisterForm()
#     if form.validate_on_submit():
#             hash = generate_password_hash(request.form['psw'])
#             res = dbase.addUser(form.name.data, form.email.data, hash)
#             if res:
#                 flash("Вы успешно зарегистрированы", "success")
#                 return redirect(url_for('login'))
#             else:
#                 flash("Ошибка при добавлении в БД", "error")

#     return render_template("register.html", menu=dbase.getMenu(), title="Регистрация", form=form)

if __name__ == "__main__":
    app.run()

