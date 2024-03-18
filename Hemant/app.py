from flask import Flask, render_template, url_for, request, redirect, session
import nltk
from nltk.tokenize import sent_tokenize
from nltk import word_tokenize, pos_tag
from nltk.corpus import stopwords
import psycopg2
import json

def download_nltk_data():
    try:
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('universal_tagset')
    except LookupError:
        pass


download_nltk_data()
app = Flask(__name__)
app.secret_key = '2030'

from psycopg2 import OperationalError

def create_conn():
    conn = None
    try:
        # database connection parameters, replace with your actual details
        conn = psycopg2.connect(
            dbname="database_o8cv",
            user="root",
            password="F2UN0PWkaEiVW7d1S3dlHUdhsT4J3LBU",
            host="dpg-cnmv2p821fec7399860g-a",
            port="5432",
        )
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    return conn

conn = create_conn()
cur = conn.cursor()

def create_dat_table():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dat_table (
            id SERIAL PRIMARY KEY,
            Text TEXT,
            Word_Count INTEGER,
            sent_count INTEGER,
            stop_count INTEGER,
            upos_tag_dict JSON,
            upos_tag_count INTEGER
        )
    """)
    conn.commit()

create_dat_table()

from newspaper import Article

@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")

@app.route("/process", methods=['POST'])
def process():
    global url
    url = request.form.get("url")
    if url:
        try:
            # Extract text from the news article
            article = Article(url)
            print(1)
            article.download()
            print(2)
            article.parse()
            print(3)
            text = article.text
            # text = text[:500]
            print(4)

            # Process the text and insert into the database
            word_lst = word_tokenize(text)
            print(5)
            word_count = len(word_lst)
            print(6)
            sent_tokenize_list = sent_tokenize(text)
            print(7)
            sen_count = len(sent_tokenize_list)
            print(8)
            stopwords_lst = stopwords.words('english')
            print(9)
            stop_count = len([word for word in word_lst if word in stopwords_lst])
            print(10)
            upos_tags = pos_tag(word_lst, tagset = 'universal')
            print(11)
            tag_count_dict = {}
            for word, tag in upos_tags:
                if tag in tag_count_dict:
                    tag_count_dict[tag] += 1
                else:
                    tag_count_dict[tag] = 1
            tag_count = len(tag_count_dict)
            print(12)
            tag_count_dict = json.dumps(tag_count_dict)
            print(13)
            cur.execute("INSERT INTO dat_table (Text, Word_Count, sent_count, stop_count, upos_tag_dict, upos_tag_count) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                        (text, word_count, sen_count, stop_count, tag_count_dict, tag_count))
            id = cur.fetchone()[0]
            conn.commit()
            return redirect(url_for('result', id=id, url=url))
        except Exception as e:
            error = f"An error occurred: {str(e)}"
            return render_template("index.html", error=error,url=url)
    return redirect(url_for('index',url=url))

@app.route('/result/<int:id>', methods=['GET'])
def result(id):

    cur.execute("SELECT * FROM dat_table WHERE id = %s", (id,))
    data = cur.fetchone()

    if not data:
        return render_template('error.html', error='Data not found.')

    #url = request.form.get("url")  # Replace this with the actual URL
    text = data[1]  # The text of the news article
    num_sentences = data[3]  # The number of sentences in the text
    num_words = data[2]  # The number of words in the text
    pos_counts = data[5]  # The POS counts in the text

    return render_template('result.html', url=url, text=text, num_sentences=num_sentences, num_words=num_words, pos_counts=pos_counts)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'admin' in session:
        return redirect(url_for('history'))
    if request.method == 'POST':
        password = request.form.get("password")
        if password == '123':  # replace '123' with your actual admin password
            session['admin'] = True
            return redirect(url_for('history'))
    return render_template('login.html')

from flask_dance.contrib.google import make_google_blueprint, google

# Create a blueprint for Google OAuth2
google_bp = make_google_blueprint(
    client_id="485950043701-cri7tkmprkdmbq49cvd67m91ds05lhhd.apps.googleusercontent.com",  # Replace with your Google Client ID
    client_secret="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",  # Replace with your Google Client Secret
    scope=["profile", "email"],
    offline=True,
    reprompt_consent=True,
)
app.register_blueprint(google_bp, url_prefix="/login-google")

@app.route("/login-google")
def login_google():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v1/userinfo")
    if not resp.ok:
        return "Failed to fetch user info from Google.", 500
    google_info = resp.json()
    return "You are {email} on Google".format(email=google_info["email"])


@app.route("/history", methods=['GET', 'POST'])
def history():
    if 'admin' not in session:
        return redirect(url_for('login'))
    cur.execute("SELECT * FROM dat_table")
    users = cur.fetchall()  # Change 'rows' to 'users'
    return render_template("history.html", users=users)  # Change 'rows' to 'users'


@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)
