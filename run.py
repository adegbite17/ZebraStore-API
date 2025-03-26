from backend import app

app.config['DEBUG'] = True  # Enable debug mode

# Checks if the run.py file has executed directly and not imported
if __name__ == '__main__':
    app.run(debug=True)
