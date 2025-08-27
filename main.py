from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/greet", methods=["POST"])
def greet():
    data = request.get_json()
    name = data.get("name", "Guest")
    return jsonify({"message": f"Hello, {name}! Welcome to Flask + JS demo 🚀"})

if __name__ == "__main__":
    app.run(debug=True)
