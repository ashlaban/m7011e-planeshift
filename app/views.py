from app import app

@app.route('/')
@app.route('/index')
def index():
    return "Welcome to what will become Planeshift! Stay tuned for more."
