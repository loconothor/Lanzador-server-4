import webview
from api import Api
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    api = Api()

    webview.create_window(
        "Esparcraft Server Launcher",
        os.path.join(BASE_DIR, "web", "index.html"),
        width=1300,
        height=760,
        js_api=api
    )

    webview.start(debug=True)
