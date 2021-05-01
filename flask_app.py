# Debug logger
import logging
import os
import sys

from flask import Flask, render_template, Response, stream_with_context
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
# Tornado web server
from tornado.wsgi import WSGIContainer

# Initialize Flask.
app = Flask(__name__)

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
    for id, filename in enumerate(os.listdir('static/music')):
        song_info = dict()
        song_info["id"] = str(id + 1)
        song_info["name"], extension = os.path.splitext(filename)
        song_info["link"] = os.path.join("static", "music", filename)
        all_songs.append(song_info)
    print(all_songs)
    return all_songs


def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.disable_buffering()
    return rv


# Route to render GUI
@app.route('/', methods=["GET"])
def show_entries():
    stream_entries = return_dict()
    return render_template('home_page.html', entries=stream_entries, name="Not Playing!")


# Route to stream music
@app.route('/<int:stream_id>', methods=["GET"])
def stream_music(stream_id):
    print("passed id:- ", str(stream_id))
    stream_entries = return_dict()

    def generate():
        data = return_dict()
        # count = 1
        song_path = None
        for item in data:
            if item['id'] == str(stream_id):
                song_path = item['link']
                break
        print(song_path)
        with open(song_path, "rb") as fwav:
            data = fwav.read(1024)
            while data:
                yield data
                data = fwav.read(1024)
                # logging.debug('Music data fragment : ' + str(count))
                # count += 1

    return Response(stream_with_context(stream_template('home_page.html', song=generate(), entries=stream_entries)))


@app.route('/about_us')
def about_us():
    stream_entries = return_dict()
    return render_template('about_us.html', entries=stream_entries, name="Not Playing!")


@app.route('/contact_us')
def contact_us():
    stream_entries = return_dict()
    return render_template('contact_us.html', entries=stream_entries, name="Not Playing!")


# launch a Tornado server with HTTPServer.
if __name__ == "__main__":
    port = 5000
    http_server = HTTPServer(WSGIContainer(app))
    logging.debug("Started Server, Kindly visit http://localhost:" + str(port))
    http_server.listen(port)
    IOLoop.instance().start()
