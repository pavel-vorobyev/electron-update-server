import os
import uuid
import psycopg2

from psycopg2.extras import DictCursor, RealDictCursor

DB_HOST = os.environ['DB_HOST']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']

db = psycopg2.connect(f"dbname='{DB_NAME}' user='{DB_USER}' host='{DB_HOST}' password='{DB_PASSWORD}'")
db.autocommit = True


def _create_versions_table(db_cursor: DictCursor):
    db_cursor.execute("CREATE TABLE versions "
                      "(id VARCHAR PRIMARY KEY, "
                      "version_code SERIAL, "
                      "version_name VARCHAR UNIQUE, "
                      "build_channel VARCHAR)")


def _create_assets_table(db_cursor: DictCursor):
    db_cursor.execute("CREATE TABLE assets "
                      "(id VARCHAR PRIMARY KEY, "
                      "platform VARCHAR, "
                      "version_code INTEGER, "
                      "version_path VARCHAR UNIQUE)")


def _setup_tables():
    with db.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("SELECT to_regclass('versions')")
        result = cursor.fetchone().values()

        if "versions" not in result:
            _create_versions_table(cursor)

        cursor.execute("SELECT to_regclass('assets')")
        result = cursor.fetchone().values()

        if "assets" not in result:
            _create_assets_table(cursor)


_setup_tables()


def _generate_id():
    return str(uuid.uuid4())


def add_version(platform, build_channel, version_name, version_path):
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(f"SELECT * FROM versions WHERE version_name = '{version_name}'")
        version = cursor.fetchone()

        if not version:
            version_id = _generate_id()
            cursor.execute(f"INSERT INTO versions(id, version_name, build_channel) "
                           f"VALUES('{version_id}', '{version_name}', '{build_channel}')")

            cursor.execute(f"SELECT * FROM versions WHERE version_name = '{version_name}'")
            version = cursor.fetchone()

        version_code = version["version_code"]

        cursor.execute(f"SELECT COUNT(id) FROM assets WHERE version_code = {version_code}")
        asset_exists = cursor.fetchone()["count"] > 0

        if not asset_exists:
            add_version_asset(platform, version_code, version_path)


def add_version_asset(platform, version_code, version_path):
    version_id = _generate_id()

    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(f"INSERT INTO assets VALUES('{version_id}', '{platform}', {version_code}, '{version_path}')")


def get_version(version):
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(f"SELECT * FROM versions WHERE version_name = '{version}'")
        return cursor.fetchone()


def get_latest_version(platform, channel):
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        if channel == "beta":
            cursor.execute(f"SELECT * FROM versions WHERE version_code = "
                           f"(SELECT MAX(version_code) FROM versions WHERE build_channel != 'alpha')")
        elif channel == "stable":
            cursor.execute(f"SELECT * FROM versions WHERE version_code = "
                           f"(SELECT MAX(version_code) FROM versions WHERE build_channel = 'stable')")
        else:
            cursor.execute(f"SELECT * FROM versions WHERE version_code = "
                           f"(SELECT MAX(version_code) FROM versions)")

        version = cursor.fetchone()

        if version:
            version_code = version["version_code"]

            cursor.execute(f"SELECT * FROM assets WHERE platform = '{platform}' AND version_code = {version_code}")
            asset = cursor.fetchone()

            if asset:
                return {
                    "version": version,
                    "asset": asset
                }

        return None
