# electron-update-server
The simplest way to update your Electron app. No DB is required.
## Environment variables
* `SERVER_URL` - An address of the server on which an instance is hosted. This parameter is required to create valid links to the update files.
* `UPLOAD_TOKEN` - Could be any string. This is a basic security implementation. Only with this token a release can be uploaded.
## Volume parameters
* `<PATH_ON_LOCAL_MACHINE:/app/static>` - The path on local machine where to store releases. Keep in mind if this bind is not set you will lose all your releases after container removed.
## URLs
* `POST /upload/<PLATFORM>/<CHANNEL>/<VERSION>` - Method to upload releases. Should be called with header `Authorization: <UPLOAD_TOKEN>`.
* `GET /update/<PLATFORM>/<CHANNEL>/<VERSION>` - Squirrel update method.
## License
