import datetime
from flask import Flask, render_template, request, redirect, url_for
from models import Note, Tag, Address_book, Record, Birthday, Phone, Email, Address, db_session, note_m2m_tag
from sqlalchemy import or_


app = Flask(__name__)
app.debug = True
app.env = "development"


@app.route("/", methods=["GET", "POST"], strict_slashes=False)
def index():
    notes = db_session.query(Note).all()

    if request.method == "POST":
        id_tag = request.form.get("tag_choose")
        if id_tag:
            notes = db_session.query(Note).join(note_m2m_tag, isouter=True).join(Tag, isouter=True).filter(Tag.id == id_tag).all()
    tags = db_session.query(Tag).all()

    return render_template("index.html", notes=notes, tags=tags)


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

    if request.method == "POST":

        name = request.form.get("name")
        bd_str_to_date = datetime.datetime.strptime(request.form.get("birthday"), "%d.%m.%Y").date()
        birthday = Birthday(bd_date=bd_str_to_date)
        record = Record(name=name, birthday=birthday)

        fields_dict = {"phone": {"class": Phone, "records_attr": record.phones, "get_name": "phone"},
                       "email": {"class": Email, "records_attr": record.emails, "get_name": "email"},
                       "address": {"class": Address, "records_attr": record.addresses, "get_name": "address"}
                       }
        for item in fields_dict.values():
            entries = request.form.getlist(item.get("get_name"))
            for entry in entries:
                attr_name = item.get("records_attr")
                class_name = item.get("class")
                attr_name.append(class_name(name=entry))

        adbook = db_session.query(Address_book).filter(Address_book.id == book_id).first()
        adbook.records.append(record)
        db_session.add(adbook)
        db_session.commit()
        return redirect(f"/records/{book_id}")
    
    return render_template("record.html", book_id=book_id)


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


@app.route("/detail/<id>", strict_slashes=False)
def detail(id):
    note = db_session.query(Note).filter(Note.id == id).first()
    return render_template("detail.html", note=note)


@app.route("/note/", methods=["GET", "POST"], strict_slashes=False)
def add_note():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        tags = request.form.getlist("tags")
        tags_obj = []
        for tag in tags:
            tags_obj.append(db_session.query(Tag).filter(Tag.name == tag).first())
        note = Note(name=name, description=description, tags=tags_obj)
        db_session.add(note)
        db_session.commit()
        return redirect("/")
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
        return redirect("/")

    return render_template("tag.html")


@app.route("/delete/<id>", strict_slashes=False)
def delete(id):
    db_session.query(Note).filter(Note.id == id).delete()
    db_session.commit()

    return redirect("/")


@app.route("/done/<id>", strict_slashes=False)
def done(id):
    db_session.query(Note).filter(Note.id == id).first().done = True
    db_session.commit()

    return redirect("/")


@app.route("/note/result", methods=["GET", "POST"], strict_slashes=False)
def search_in_notes():
    if request.method == "POST":
        key= request.form.get("key")
        asc_table_res = db_session.query(note_m2m_tag).\
                    join(Note, isouter=True).\
                    join(Tag, isouter=True).\
                    filter(or_(
                        Note.name.like(f'%{key}%'),
                        Tag.name.like(f'%{key}%'),
                        Note.description.like(f'%{key}%'))).all()
        res_notes = [db_session.query(Note).filter(Note.id == obj.id).first() for obj in asc_table_res]#temp code. add rel. to m2m table (example -  https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html)
        return render_template("note_result.html", notes=res_notes, key=key, count_res=len(res_notes))


if __name__ == "__main__":
    app.run()
