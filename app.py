from flask import Flask, render_template, request, jsonify

from chatbot import get_response


app = Flask(__name__)


@app.route("/")
def index():

    return render_template(
        "index.html"
    )


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    user_input = data.get(
        "message",
        ""
    )

    result = get_response(
        user_input
    )

    return jsonify(
        result
    )

if __name__ == "__main__":

    app.run(
        debug=True
    )