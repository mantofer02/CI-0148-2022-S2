from distutils.log import debug
from flask import Flask

app = Flask(__name__)


@app.route("/members")
def members():
    return {"members": ["Marco", "Roy"]}


if __name__ == "__main__":
    app.run(debug=True)
