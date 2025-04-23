
from flask import Flask, request, render_template, redirect, url_for, send_file, abort, after_this_request
import os
import yt_dlp
import time
import threading
from urllib.parse import quote, unquote
import glob

app = Flask(__name__)
app.secret_key = 'secret'

output_path = os.path.join(os.path.dirname(__file__), 'downloads')
os.makedirs(output_path, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        links = request.form['links'].strip().splitlines()
        selected_format = request.form.get('format', 'mp4')

        if not links:
            return render_template('index.html', filenames=[])

        if selected_format == 'mp3':
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{output_path}/%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'nooverwrites': True,
                'no_mtime': True
            }
            ext = 'mp3'
        else:
            ydl_opts = {
                'outtmpl': f'{output_path}/%(title)s.%(ext)s',
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
                'nooverwrites': True,
                'no_mtime': True
            }
            ext = 'mp4'

        before_files = set(glob.glob(os.path.join(output_path, f'*.{ext}')))

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for link in links:
                try:
                    ydl.download([link])
                except Exception as e:
                    print(f"Error with {link}: {str(e)}")

        after_files = set(glob.glob(os.path.join(output_path, f'*.{ext}')))
        new_files = after_files - before_files

        for file in new_files:
            os.utime(file, (time.time(), time.time()))

        filenames = [quote(os.path.basename(f)) for f in sorted(new_files, key=os.path.getctime)]
        return render_template('index.html', filenames=filenames)

    return render_template('index.html', filenames=[])

@app.route('/download/<path:filename>')
def download_file(filename):
    from urllib.parse import unquote
    filename = unquote(filename)
    file_path = os.path.join(output_path, filename)

    if not os.path.exists(file_path):
        abort(404)

    def safe_delete(path):
        try:
            os.remove(path)
            print(f"✅ Deleted: {path}")
        except FileNotFoundError:
            print(f"⚠️ File already deleted or not found: {path}")
        except Exception as e:
            print(f"❌ Could not delete file: {e}")

    @after_this_request
    def delete_file(response):
        threading.Timer(5, safe_delete, args=(file_path,)).start()
        return response

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
