from flask import Flask, render_template, jsonify
import threading
import gesture_control

app = Flask(__name__)

gesture_thread = None  # To track the background process

@app.route("/")
def home():
    return render_template("index.html")  # Loads the HTML interface

@app.route("/start", methods=["POST"])
def start_gesture():
    global gesture_thread

    print("Received START request")  # Debugging print statement

    if not gesture_control.is_running:
        gesture_control.is_running = True
        gesture_thread = threading.Thread(target=gesture_control.run_gesture_control)
        gesture_thread.start()
        return jsonify({"status": "Gesture control started"})
    else:
        return jsonify({"status": "Already running"})

@app.route("/stop", methods=["POST"])
def stop_gesture():
    print("Received STOP request")  # Debugging print statement

    gesture_control.stop_gesture_control()
    return jsonify({"status": "Gesture control stopped"})

if __name__ == "__main__":
    app.run(debug=True)
