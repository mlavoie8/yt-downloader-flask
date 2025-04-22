from flask import Flask, request, render_template, redirect, url_for, flash
import os
import yt_dlp
import time

app = Flask(__name__)
app.secret_key = 'secret'  # Needed for flash messages

# Create downloads folder
output_path = os.path.join(os.path.dirname(__file__), 'downloads')
os.makedirs(output_path, exist_ok=True)

# Track downloaded files
downloaded_files = []

# Progress hook to capture downloaded file paths
def progress_hook(d):
    if d['status'] == 'finished':
        downloaded_files.append(d['filename'])

@app.route('/', methods=['GET', 'POST'])
def index():
    global downloaded_files
    downloaded_files = []

    if request.method == 'POST':
        links = request.form['links'].strip().splitlines()
        if not links:
            flash("No links provided.", "warning")
            return redirect(url_for('index'))

        # yt-dlp options
        ydl_opts = {
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'nooverwrites': True,
            'no_mtime': True,
            'progress_hooks': [progress_hook]
        }

        # Run downloads
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for link in links:
                try:
                    ydl.download([link])
                except Exception as e:
                    flash(f"Error with {link}: {str(e)}", "danger")

        # Update timestamps on downloaded files
        for file in downloaded_files:
            if os.path.exists(file):
                now = time.time()
                os.utime(file, (now, now))  # Modified and accessed times

        flash("Download complete!", "success")
        return redirect(url_for('index'))

    return render_template('index.html')


# Run the Flask server
if __name__ == '__main__':
    app.run(debug=True)
