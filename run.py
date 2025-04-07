from backend import app, init_db, db

init_db()
app.config['DEBUG'] = True  # Enable debug mode

# Checks if the run.py file has executed directly and not imported
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
