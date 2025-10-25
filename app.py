from flask import Flask, render_template, request, jsonify, session
from dynamic_memory import MemoryManager
import os

app = Flask(__name__)
app.secret_key = "secure-session-key"

# Store memory manager instances in session or global dict
memory_managers = {}

@app.route("/")
def home():
    # If user hasn't initialized memory, show setup page
    if "user_id" not in session or session["user_id"] not in memory_managers:
        return render_template("setup.html")
    mm = memory_managers[session["user_id"]]
    blocks = sorted(mm.blocks.items(), key=lambda x: x[1]["start"])
    return render_template("index.html", blocks=blocks, total=mm.total_size)

@app.route("/initialize", methods=["POST"])
def initialize():
    total_size = int(request.form.get("total_size"))
    from uuid import uuid4
    user_id = str(uuid4())
    session["user_id"] = user_id
    memory_managers[user_id] = MemoryManager(total_size)
    return jsonify(success=True)

@app.route("/allocate", methods=["POST"])
def allocate():
    user_id = session.get("user_id")
    if not user_id or user_id not in memory_managers:
        return jsonify(error="Memory not initialized"), 400
    mm = memory_managers[user_id]
    size = int(request.form.get("size"))
    strategy = request.form.get("strategy", "best")
    mm.allocate(size, strategy)
    return jsonify(success=True)

@app.route("/deallocate", methods=["POST"])
def deallocate():
    user_id = session.get("user_id")
    if not user_id or user_id not in memory_managers:
        return jsonify(error="Memory not initialized"), 400
    mm = memory_managers[user_id]
    block_id = int(request.form.get("block_id"))
    mm.deallocate(block_id)
    return jsonify(success=True)

@app.route("/reset", methods=["POST"])
def reset():
    user_id = session.get("user_id")
    if user_id in memory_managers:
        del memory_managers[user_id]
    if "user_id" in session:
        session.pop("user_id")
    return jsonify(success=True)

@app.route("/memory_state")
def memory_state():
    user_id = session.get("user_id")
    if not user_id or user_id not in memory_managers:
        return jsonify(error="Memory not initialized"), 400
    mm = memory_managers[user_id]

    total_free = sum(b["size"] for _, b in mm.blocks.items() if b["free"])
    total_allocated = sum(b["size"] for _, b in mm.blocks.items() if not b["free"])
    usage_percent = round((total_allocated / mm.total_size) * 100, 2)

    return jsonify({
        "blocks": sorted(mm.blocks.items(), key=lambda x: x[1]["start"]),
        "total_allocated": total_allocated,
        "total_free": total_free,
        # fragmentation metrics removed per request
        "usage_percent": usage_percent,
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)