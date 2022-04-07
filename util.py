import os

from werkzeug.datastructures import FileStorage

ASSETS_DIR = "static"
BUILD_CHANNELS = ("alpha", "beta", "stable")


def store_version_asset(platform, build_channel, version, asset: FileStorage, asset_ext):
    path_to_platform = f"{ASSETS_DIR}/{platform}"
    path_to_channel = f"{path_to_platform}/{build_channel}"
    path_to_version = f"{path_to_channel}/{version}"

    for path in [ASSETS_DIR, path_to_platform, path_to_channel, path_to_version]:
        if not os.path.exists(path):
            os.mkdir(path)

    asset_filename = "{}-{}{}".format(platform, version, asset_ext)
    asset_path = os.path.join(path_to_version, asset_filename)
    asset.save(asset_path)

    return asset_path
