# 0.0.0.1 | 0 | stable
# 0.0.1-alpha1 | 1 | alpha
# 0.0.1-alpha2 | 2 | alpha
# 0.0.1-beta1 | 3 | beta
# 0.0.1-beta2 | 4 | beta
# 0.0.1-beta3 | 5 | beta
# 0.0.1 | 6 | stable
# 0.0.2-alpha1 | 7 | alpha
# 0.0.2-alpha2 | 8 | alpha
# 0.0.2-beta1 | 9 | beta
# 0.0.2 | 10 | stable
# 0.0.3-alpha1 | 11 | alpha


import os

from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

from db import add_version, get_version, get_latest_version
from util import store_version_asset

SERVER_URL = os.environ['SERVER_URL']
UPLOAD_TOKEN = os.environ['UPLOAD_TOKEN']


def handle_http_error(e):
    return jsonify(error=e.description), e.code


app = Flask(__name__)
app.register_error_handler(HTTPException, handle_http_error)


@app.route('/upload/<platform>/<channel>/<version>', methods=['POST'])
def upload_version(platform, channel, version):
    if request.headers.get("Authorization") != UPLOAD_TOKEN:
        return jsonify(error="Not authorized"), 401

    if 'file' not in request.files:
        return jsonify(error="No file attached"), 400

    asset = request.files['file']
    asset_filename, asset_ext = os.path.splitext(asset.filename)

    if asset_filename == '':
        return jsonify(error="No file attached"), 400

    if asset_ext not in ['.zip', '.exe', '.deb']:
        return jsonify(error="Unsupported file extension. Allowed: `.zip`, `.exe`, `.deb`"), 400

    version_path = store_version_asset(platform, channel, version, asset, asset_ext)

    add_version(platform, channel, version, version_path)
    return jsonify(platform=platform, version=version, channel=channel)


@app.route('/update/<platform>/<channel>/latest', methods=['GET'])
def get_channel_latest_version(platform, channel):
    latest_version = get_latest_version(platform, channel)

    if not latest_version:
        return {}, 204

    version_path = latest_version["asset"]["version_path"]
    return jsonify(url=f"{SERVER_URL}/{version_path}")


@app.route('/update/<platform>/<channel>/<version>')
def check_for_update(platform, channel, version):
    latest_version = get_latest_version(platform, channel)

    if not latest_version:
        return {}, 204

    latest_version_path = latest_version["asset"]["version_path"]
    current_version = get_version(version)

    if not current_version:
        return jsonify(url=f"{SERVER_URL}/{latest_version_path}")

    current_version_code = int(current_version["version_code"])
    latest_version_code = int(latest_version["version"]["version_code"])

    if current_version_code < latest_version_code:
        return jsonify(url=f"{SERVER_URL}/{latest_version_path}")

    return {}, 204


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3591)
