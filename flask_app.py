# Debug logger
import logging
import os
import sys
import json

from flask import Flask, render_template, Response
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
# Tornado web server
from tornado.wsgi import WSGIContainer

from flask import send_file

# Initialize Flask.
app = Flask(__name__)

root = logging.getLogger()
root.setLevel(logging.DEBUG)
url = "http://localhost:5000/"

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


def return_song_dict():
    # Dictionary to store music file information
    all_songs = list()
    for id, filename in enumerate(os.listdir('static/music')):
        song_info = dict()
        song_info["id"] = str(id + 1)
        song_info["name"], extension = os.path.splitext(filename)
        song_info["link"] = os.path.join("static", "music", filename)
        song_info["url"] = '{}/{}'.format(url, song_info["name"])
        all_songs.append(song_info)
    # print(all_songs)
    return all_songs


# Route to render GUI
@app.route('/', methods=["GET"])
def show_entries():
    stream_entries = return_song_dict()
    return render_template('home_page.html', entries=stream_entries, name="Not Playing!")


@app.route('/<song_name>', methods=['GET'])
def song_url_sender(song_name):
    stream_entries = return_song_dict()
    song_details = json.load(open(os.path.join("static", "json", "content.json")))
    display_song_name = "Not Found"
    display_song_id = None
    for item_dict in stream_entries:
        for key, value in item_dict.items():
            if song_name == value:
                display_song_id = item_dict["id"]
                display_song_name = value
                break

    return render_template('home_page.html', entries=stream_entries, name=display_song_name, song_id=display_song_id,
                           paragraphs = song_details.get(song_name, ["Please click on any song",
                                                                     "you are trying to visit non valid link"]))


# Route to stream music
@app.route('/<int:stream_id>', methods=["GET"])
def stream_music(stream_id):
    # print("passed id:- ", str(stream_id))

    def generate():
        data = return_song_dict()
        print("aaya")
        # count = 1
        song_path = None
        for item in data:
            if item['id'] == str(stream_id):
                song_path = item['link']
                break
        # print(song_path)
        with open(song_path, "rb") as fwav:
            data = fwav.read(1024)
            while data:
                yield data
                data = fwav.read(1024)
                # logging.debug('Music data fragment : ' + str(count))
                # count += 1

    return Response(generate(), mimetype="audio/mp3")


@app.route('/about_us')
def about_us():
    stream_entries = return_song_dict()
    return render_template('about_us.html', entries=stream_entries, name="Not Playing!")


@app.route('/contact_us')
def contact_us():
    stream_entries = return_song_dict()
    return render_template('contact_us.html', entries=stream_entries, name="Not Playing!")


# launch a Tornado server with HTTPServer.
if __name__ == "__main__":
    port = 5000
    http_server = HTTPServer(WSGIContainer(app))
    logging.debug("Started Server, Kindly visit http://localhost:" + str(port))
    http_server.listen(port)
    IOLoop.instance().start()
