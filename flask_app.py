from flask import Flask, render_template
from flask import request
import sys
# Tornado web server
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import os
import json
# Debug logger
import logging

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


def return_dict():
    # Dictionary to store music file information
    all_songs = list()
    for id,filename in enumerate(os.listdir('static/music')):
        song_info = dict()
        song_info["id"] = str(id+1)
        song_info["name"], extension = os.path.splitext(filename)
        song_info["link"] = "music/"+filename
        all_songs.append(song_info)
    print(all_songs)
    return all_songs


# Initialize Flask.
app = Flask(__name__)


# Route to render GUI
@app.route('/', methods=["GET", "POST"])
def show_entries():
    stream_entries = return_dict()
    content = json.load(open(os.path.join("static","json","content.json")))
    print(content)
    if request.method == 'POST':
        print("request made by -->", request.method)
        print("request.form.get('stream_id')", request.form.get('stream_id'))
        stream_id = request.form.get('stream_id')
        for song in stream_entries:
            if song["id"] == stream_id:
                if song["name"] in content:
                    paragraphs = content[song["name"]]
                else:
                    paragraphs = ["None"]
                return render_template('home_page.html', entries=stream_entries, name=song["name"], song=song["link"] , paragraphs = paragraphs)
    else:
        print("request made by -->", request.method)
        return render_template('home_page.html', entries=stream_entries , name="Not Playing!")

@app.route('/about_us')
def about_us():
    stream_entries = return_dict()
    return render_template('about_us.html', entries=stream_entries , name="Not Playing!")


@app.route('/contact_us')
def contact_us():
    stream_entries = return_dict()
    return render_template('contact_us.html', entries=stream_entries , name="Not Playing!")


# launch a Tornado server with HTTPServer.
if __name__ == "__main__":
    port = 5000
    http_server = HTTPServer(WSGIContainer(app))
    logging.debug("Started Server, Kindly visit http://localhost:" + str(port))
    http_server.listen(port)
    IOLoop.instance().start()
