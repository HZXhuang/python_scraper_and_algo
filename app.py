from flask import Flask
from scraper.test import save_file
from scraper.my_utils import check_exists_and_make_dir

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    save_file()
    return 'Hello World!'


if __name__ == '__main__':
    check_exists_and_make_dir("out")
    check_exists_and_make_dir("profile")
    app.run()
