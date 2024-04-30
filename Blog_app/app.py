from flask import Flask, render_template,redirect,request
from flask_sqlalchemy import SQLAlchemy
import sqlite3,os
from flask import Flask, url_for
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import InputRequired  ,ValidationError,Length
from flask_bcrypt import Bcrypt


app = Flask(__name__)
bcrypt=Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/joker/blog__app/instance/database.db'

app.config['SECRET_KEY'] = 'thisisasecretkey'

Login_Manager=LoginManager()
Login_Manager.init_app(app)
Login_Manager.login_view="login"


# Configure SQLite3 database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS blogs (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        image TEXT
    )
    ''')
    conn.commit()
    conn.close()

init_db()



@Login_Manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


db = SQLAlchemy(app)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False,unique=True)
    password = db.Column(db.String(80), nullable=False)



class registerForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length( min=4, max=20)],
    render_kw={"placeholder": "Username"})
    password =PasswordField(validators=[InputRequired(), Length( min=4, max=20)], 
    render_kw={"placeholder": "Password"})
    submit = SubmitField("register")


def validate_username(self,username):
    existing_user_username=User.query.filter_by(username=username.data).first()
    if existing_user_username:
        raise ValidationError("the user name is already existing please choose a different one ")


class loginform(FlaskForm):
    username = StringField(validators=[InputRequired(), Length( min=4, max=20)],
    render_kw={"placeholder": "Username"})
    password =PasswordField(validators=[InputRequired(), Length( min=4, max=20)], 
    render_kw={"placeholder": "Password"})
    submit = SubmitField("login")


@app.route('/',methods=['GET','POST'])
def login():
    form=loginform()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user)
                return render_template('upload.html')
    return render_template('login.html',form=form)


@app.route('/register',methods=['GET','POST'])
def register():
    form=registerForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html',form=form)

@app.route('/index')
def index():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blogs ORDER BY id DESC")
    blogs = cursor.fetchall()
    conn.close()
    return render_template('upload.html', blogs=blogs)

@app.route('/index1')
def index1():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blogs ORDER BY id DESC")
    blogs = cursor.fetchall()
    conn.close()
    return render_template('index.html',blogs=blogs)

@app.route('/upload', methods=['POST'])
def upload():
    title = request.form['title']
    content = request.form['content']



    # Handle image upload
    image = request.files['image']
    if image:
        image_filename = os.path.join('static/images', image.filename)
        image.save(image_filename)



    # Save to database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO blogs (title, content, image) VALUES (?, ?, ?)", (title, content, image_filename))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))



# ... (your existing imports and code)

@app.route('/delete_all_blogs', methods=['GET', 'POST'])
@login_required
def delete_all_blogs():
    try:
        # Connect to the database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Delete all records from the blogs table
        cursor.execute("DELETE FROM blogs")
        
        # Commit the changes
        conn.commit()

        # Close the connection
        conn.close()

        return redirect(url_for('index'))
    
    except Exception as e:
        return f"An error occurred: {e}"

# ... (your existing routes and code)


@app.route('/delete_blog/<int:blog_id>', methods=['GET', 'POST'])
@login_required
def delete_blog(blog_id):

        # Connect to the database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Delete the blog with the given blog_id
        cursor.execute("SELECT image FROM blogs WHERE id=?",(blog_id,))
        filename = cursor.fetchone()[0]
        filename = "C:\\Users\\joker\\OneDrive\\Desktop\\Blog_app\\"+filename
        if os.path.exists(filename):
            os.remove(filename)
        cursor.execute("DELETE FROM blogs WHERE id=?", (blog_id,))
        
        # Commit the changes
        conn.commit()

        # Close the connection
        conn.close()
        return redirect(url_for('index'))






@app.route('/contact')
@login_required
def contact():
    return render_template('contact.html')



@app.route('/edit', methods=['POST','GET'])
@login_required
def edit():
    blog = eval(request.args.get('blog'))
    print(type(blog))
    return render_template('edit.html', blog=blog)

@app.route('/saveEdits/<int:blog_id>', methods=['POST','GET'])
@login_required
def saveEdits(blog_id):

    blog_title = request.form.get('title')
    blog_content = request.form.get('content')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT image FROM blogs WHERE id=?", (blog_id,))
    filename = cursor.fetchall()[0][0]
    filename = "C:\\Users\\joker\\OneDrive\\Desktop\\Blog_app\\"+filename
    cursor.execute("UPDATE blogs SET title=?,content=? WHERE id=?", (blog_title, blog_content, blog_id))
    blog_image = request.files['image']
    blog_image.save(filename)
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/thankyou')
@login_required
def thankyou():
    return render_template("thankyou.html")

if __name__ == '__main__':
    with app.app_context():
        db.metadata.create_all(bind=db.engine)
        db.create_all()
        db.session.commit()
    app.run(debug=True)