import os

from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

SERVER_URL = os.environ['SERVER_URL']
UPLOAD_TOKEN = os.environ['UPLOAD_TOKEN']
ASSETS_DIR = 'static'


def handle_http_error(e):
    return jsonify(error=e.description), e.code


app = Flask(__name__)
app.register_error_handler(HTTPException, handle_http_error)


@app.route('/upload/<platform>/<channel>/<version>', methods=['POST'])
def upload_version(platform, version, channel):
    if request.headers.get("Authorization") != UPLOAD_TOKEN:
        return {}, 401

    path_to_platform = "{}/{}".format(ASSETS_DIR, platform)
    path_to_channel = "{}/{}".format(path_to_platform, channel)
    path_to_version = "{}/{}".format(path_to_channel, version)

    for path in [ASSETS_DIR, path_to_platform, path_to_channel, path_to_version]:
        if not os.path.exists(path):
            os.mkdir(path)

    if 'file' not in request.files:
        return jsonify(error="No file attached"), 400

    asset = request.files['file']
    asset_filename, asset_ext = os.path.splitext(asset.filename)

    if asset_filename == '':
        return jsonify(error="No file attached"), 400

    if asset_ext not in ['.zip', '.exe', '.deb']:
        return jsonify(error="Unsupported file extension. User: `.zip`, `.exe`, `.deb`"), 400

    asset_filename = "{}-{}{}".format(platform, version, asset_ext)
    asset_path = os.path.join(path_to_version, asset_filename)
    asset.save(asset_path)

    return jsonify(platform=platform, version=version, channel=channel)


@app.route('/update/<platform>/<channel>/<version>', methods=['GET'])
def get_version(platform, version, channel):
    path_to_channel = "{}/{}/{}".format(ASSETS_DIR, platform, channel)

    if not os.path.exists(path_to_channel):
        return {}, 204

    current_version = parse_version(version, channel)
    version_paths = os.listdir(path_to_channel)
    last_version_path = None

    for version_path in version_paths:
        platform_version = parse_version(version_path, channel)

        if platform_version > current_version:
            last_version_path = version_path

    if not last_version_path:
        return {}, 204

    release_path = "{}/{}".format(path_to_channel, last_version_path)
    release_path_content = os.listdir(release_path)
    if len(last_version_path) == 0:
        return {}, 204

    release = "{}/{}".format(release_path, release_path_content[0])
    if not os.path.isfile(release):
        return {}, 204

    return jsonify(url="{}/{}".format(SERVER_URL, release))


def parse_version(version, channel):
    parsed_version = version \
        .replace(".", "") \
        .replace("-{}".format(channel), ".")

    return float(parsed_version)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3591)
