from flask import Flask, request, jsonify , render_template , send_file, abort
from datetime import datetime ,date,timedelta
import  sqlite3
from io import BytesIO
import base64
conn = sqlite3.connect("data.db")

def close_db(conn):
    if conn:
        conn.close()
def get_db():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
app.secret_key = 'testjopsappkey'
app.permanent_session_lifetime = timedelta(minutes=66731)
session_cookie_samesite=app.config["SESSION_COOKIE_SAMESITE"]



@app.route('/get_app')
def get_report():
    report_path = 'app-release.apk'  # Replace with the actual path to your file
    try:
        return send_file(report_path, as_attachment=True, download_name=report_path)
    except FileNotFoundError:
        abort(404)


@app.route("/", methods=["GET"])
def routee():
    conn = sqlite3.connect("data.db")

    c = conn.cursor()
    
    return render_template("route.html" )

@app.route('/register', methods=['POST'])
def register_user():
    # Get the JSON data from the request body
    conn = sqlite3.connect("data.db")

    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    type TEXT NOT NULL,
    image BLOB  
        )""") 
    
    username    = request.form['username']
    email  = request.form['email']
    user_type = request.form['is_job_seeker']
    password = request.form['password']

# Check if email already exists
    c.execute("SELECT id FROM users WHERE email = ?", (email,))
    existing_user = c.fetchone()
    
    if existing_user:
        close_db(conn)
        return jsonify({'message': 'Email already exists'}), 409

    try:
        
        c.execute("""INSERT INTO users (username, email, password, type,image )
                        VALUES (?, ?, ?, ?,?)""",
                       (username, email, password, user_type,None))
        conn.commit()
        
        return jsonify({'message': 'User registered successfully'}), 200
    except sqlite3.Error as e:
        conn.rollback()
        
        return jsonify({'message': f'Database error: {e}'}), 500


@app.route('/posts', methods=['POST'])
def post_user():
    
    # # Get the JSON data from the request body
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userid TEXT NOT NULL,
    email TEXT NOT NULL,
    username TEXT NOT NULL,
    datetime TEXT  NOT NULL,
    postext TEXT NOT NULL,
    reaction INTEGER NOT NULL,
    image BLOB  
        )""") 
    # print(request.json)
    username    = request.json['username']
    email  = request.json['email']
    userid = request.json['userId']
    postext = request.json['postText']

    dateTime = datetime.now()
    data = request.get_json()

    if "image" in data:
        image    = request.json['image']
        image = base64.b64decode(image)
        print("image")
    else:
        image    = None
        print("not image")

    try:      
        c.execute("""INSERT INTO posts (userid, email, username, postext,reaction,datetime,image )
                        VALUES (?, ?, ?, ?,?,?,?)""",
                       (userid, email, username, postext,0,str(dateTime),image))
        
        conn.commit()
        
        return jsonify({'message': 'post ok'}), 201
    except sqlite3.Error as e:
        conn.rollback()
        
        return jsonify({'message': f'Database error: {e}'}), 500


@app.route('/posts/apply/<int:id>', methods=['GET'])
def applyview(id):
    
    # # Get the JSON data from the request body
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS apply (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userid TEXT NOT NULL,
    postid TEXT NOT NULL,
    username TEXT NOT NULL,
    email TEXT  NOT NULL,
    phone TEXT NOT NULL,
    comment TEXT
      
        )""") 
    try:      
        result = c.execute("""select * from apply where postid =  """+str(id)+""" ;""").fetchall()
        
        posts_data = []
        for row in result:
            post = {}
            
            
            post['email'] = row[4]
            post['username'] = row[3]
            post['phone'] = row[5]
            post['note'] = row[6]
            
            
            posts_data.append(post)
            print(posts_data)
        return jsonify({'message': 'apply ok' , 'data':posts_data}), 201
        
    except sqlite3.Error as e:
        conn.rollback()
        
        return jsonify({'message': f'Database error: {e}'}), 500
    



@app.route('/apply', methods=['POST'])
def post_user_apply():
   
    # # Get the JSON data from the request body
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS apply (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userid TEXT NOT NULL,
    postid TEXT NOT NULL,
    username TEXT NOT NULL,
    email TEXT  NOT NULL,
    phone TEXT NOT NULL,
    comment TEXT
      
        )""") 
    print(request.form)
    username    = request.form['username']
    email  = request.form['email']
    userid = request.form['userid']
    postid = request.form['postid']
    email  = request.form['email']
    phone = request.form['phone']
    Note = request.form['Note']

    
    # return jsonify({'message': 'apply ok'}), 201
    c.execute("SELECT id FROM apply WHERE userid = ? and postid = ? ", (userid,postid))
    existing_user = c.fetchone()
    
    if existing_user:
        close_db(conn)
        return jsonify({'message': 'already exists'}), 201

    try:      
        c.execute("""INSERT INTO apply (userid, postid, username, email,phone,comment )
                        VALUES (?, ?, ?, ?,?,? )""",
                       (userid, postid, username, email,phone,Note))
        c.execute("UPDATE posts SET reaction = reaction + 1 WHERE id = ?", (postid,))
        conn.commit()
        
        return jsonify({'message': 'post ok'}), 201
    except sqlite3.Error as e:
        conn.rollback()
        print(e)
        return jsonify({'message': f'Database error: {e}'}), 500







@app.route('/posts/view', methods=['GET'])
def post_userVIEW():
    
    # # Get the JSON data from the request body
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userid TEXT NOT NULL,
    email TEXT NOT NULL,
    username TEXT NOT NULL,
    datetime TEXT  NOT NULL,
    postext TEXT NOT NULL,
    reaction INTEGER NOT NULL,
    image BLOB  
        )""") 
    try:      
        result = c.execute("""select * from posts ORDER BY datetime DESC ;""").fetchall()
        
        posts_data = []
        for row in result:
            post = {}
            post['id'] = row[0]
            post['userid'] = row[1]
            post['email'] = row[2]
            post['username'] = row[3]
            post['datetime'] = row[4]
            post['postext'] = row[5]
            post['reaction'] = row[6]
            if row[7]:
                post['image'] = base64.b64encode(row[7]).decode('utf-8')
            else:
                post['image'] = None  # Or some other representation for no image
            posts_data.append(post)
        return jsonify({'message': 'post ok' , 'data':posts_data}), 201
    except sqlite3.Error as e:
        conn.rollback()
        
        return jsonify({'message': f'Database error: {e}'}), 500



@app.route('/posts/view/user/<int:user_id>', methods=['GET'])
def post_userVIEWuser(user_id):
    
    # # Get the JSON data from the request body
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userid TEXT NOT NULL,
    email TEXT NOT NULL,
    username TEXT NOT NULL,
    datetime TEXT  NOT NULL,
    postext TEXT NOT NULL,
    reaction INTEGER NOT NULL,
    image BLOB  
        )""") 
    try:      
        result = c.execute("""select * from posts where userid = """+str(user_id)+""" ORDER BY datetime DESC ;""").fetchall()
        
        posts_data = []
        for row in result:
            post = {}
            post['id'] = row[0]
            post['userid'] = row[1]
            post['email'] = row[2]
            post['username'] = row[3]
            post['datetime'] = row[4]
            post['postext'] = row[5]
            post['reaction'] = row[6]
            if row[7]:
                post['image'] = base64.b64encode(row[7]).decode('utf-8')
            else:
                post['image'] = None  # Or some other representation for no image
            posts_data.append(post)
        return jsonify({'message': 'post ok' , 'data':posts_data}), 201
    except sqlite3.Error as e:
        conn.rollback()
        
        return jsonify({'message': f'Database error: {e}'}), 500


@app.route('/posts/delete/user/<int:id>', methods=['GET'])
def post_userDeleteuser(id):
    
    # # Get the JSON data from the request body
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userid TEXT NOT NULL,
    email TEXT NOT NULL,
    username TEXT NOT NULL,
    datetime TEXT  NOT NULL,
    postext TEXT NOT NULL,
    reaction INTEGER NOT NULL,
    image BLOB  
        )""") 
    try:      
        result = c.execute("""delete from posts where id = """+str(id)+""";""")
        conn.commit()
        return jsonify({'message': 'post deleted' }), 201
    except sqlite3.Error as e:
        conn.rollback()
        
        return jsonify({'message': f'Database error: {e}'}), 500
    



@app.route('/login', methods=['POST'])
def login_user():
    

    email = request.form['email']
    password = request.form['password']

    conn = sqlite3.connect("data.db")

    c = conn.cursor()
    cursor = conn.cursor()

    # Try to find the user by username or email
    cursor.execute("SELECT * FROM users WHERE email = ? and password = ?", (email, password))
    user = cursor.fetchone()
    close_db(conn)

    if user:
        # In a real application, you would compare a hashed password here
        
        return jsonify({'message': 'Login successful', 'user_id': user[0], 'username': user[1], 'email': user[2], 'type': user[4]}), 200
        
    else:
        return jsonify({'message': 'User not found'}), 404


@app.route('/users/<int:user_id>/image')
def get_user_image(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT image FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    close_db(conn)

    if result and result['image']:
        image_data = BytesIO(result['image'])
        # Determine the image MIME type (you might need to store this in the database too)
        # For now, let's assume it's a common type like JPEG or PNG
        # You might need more sophisticated logic to determine the actual type
        mime_type = 'image/jpeg'  # Default assumption, adjust as needed

        return send_file(image_data, mimetype=mime_type)
    else:
        abort(404)  # User not found or has no image

@app.route('/post/image/<int:post_id>')
def get_post_image(post_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT image FROM posts WHERE id = ?", (post_id,))
    result = cursor.fetchone()
    close_db(conn)
    if result and result['image']:
        image_data = BytesIO(result['image'])
        mime_type = 'image/jpeg'  # Default assumption, adjust as needed
        return send_file(image_data, mimetype=mime_type)
    else:
        abort(404)  # User not found or has no image


# @app.errorhandler(404)
# def not_found(error):
#     return 'not working know'  
if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")