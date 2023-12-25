# setup.py アプリケーションを立ち上げる
from flaskr import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
