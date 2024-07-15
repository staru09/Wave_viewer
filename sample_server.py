from flask import Flask, send_file

app = Flask(__name__)

@app.route('/waveform')
def serve_waveform():
    return send_file('output_waveform.png', mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
