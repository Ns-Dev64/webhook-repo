from flask import Flask, request, jsonify
from flask_cors import CORS
from models import insert_event, get_latest_events
from datetime import datetime

app = Flask(__name__)

CORS(app)  

@app.route("/webhook", methods=["POST"])

def github_webhook():
    
    # Fetch the event type eg: push or pull
    event_type = request.headers.get("X-GitHub-Event")
    payload=request.json
    
    # Construct a data object with the received payload
    data = {
        "type": event_type,
        "timestamp": datetime.now(),
        "raw": payload
    }

    # Handles push event,
    # data parameters => author: user who pushed the commit, to_branch: branch where the commit is being made to
    if event_type == "push":
        data["author"] = payload["pusher"]["name"]
        data["to_branch"] = payload["ref"].split("/")[-1]

    # Handles pull event,
    # data parameters => pr: object containing pull request data
    # if type of request is merge => event = merge
    
    elif event_type == "pull_request":
        pr = payload["pull_request"]
        data["author"] = pr["user"]["login"]
        data["from_branch"] = pr["head"]["ref"]
        data["to_branch"] = pr["base"]["ref"]

        if pr.get("merged"):
            data["type"] = "merge"

    # save the data to mongodb
    insert_event(data)
    return jsonify({"message": "Event received"}), 200

@app.route("/events", methods=["GET"])
def get_events():
    
    # fetch events from database
    events = get_latest_events()
    event_list = []

    
    # iterate through the events, beautify the data and append it to event_list
    for e in events:
        timestamp = e["timestamp"].strftime("%d %B %Y - %I:%M %p UTC")
        if e["type"] == "push":
            formatted = f'{e["author"]} pushed to {e["to_branch"]} on {timestamp}'
        elif e["type"] == "pull_request":
            formatted = f'{e["author"]} submitted a pull request from {e["from_branch"]} to {e["to_branch"]} on {timestamp}'
        elif e["type"] == "merge":
            formatted = f'{e["author"]} merged branch {e["from_branch"]} to {e["to_branch"]} on {timestamp}'
        else:
            continue
        event_list.append(formatted)

    # return the event list
    return jsonify(event_list)

if __name__ == "__main__":
    app.run(debug=True)
