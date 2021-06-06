# electron-update-server
The easiest way to update your Electron app. No DB is required. It only provides the basic functionality and has a lot of TODOs. First, it was done for personal purposes only. Hope this helps you too :)

[DockerHub](https://hub.docker.com/r/pavelvorobyev/electron-update-server)

## Usage
```
docker run --label <YOUR_LABEL> --name <YOUR_NAME> -d -p <YOUR_PORT>:3591 -e SERVER_URL=<YOUR_SERVER_URL> -e UPLOAD_TOKEN=<YOUR_UPLOAD_TOKEN> -v <YOUR_PATH>:/app/static pavelvorobyev/electron-update-server
```

## Environment variables
* `SERVER_URL` - The address of the server hosting the instance. This parameter is required to create valid links to update files.
* `UPLOAD_TOKEN` - It can be any string. This is the basic security implementation. Only with this token the release can be uploaded.

## Volume parameters
* `<PATH_ON_LOCAL_MACHINE:/app/static>` - The path on the local machine for storing releases. Keep in mind if this binding is not set you will lose all your releases after the container removed.

## URLs
* `POST /upload/<PLATFORM>/<CHANNEL>/<VERSION>` - Method to upload releases. Should be called with header `Authorization: <UPLOAD_TOKEN>`.
* `GET /update/<PLATFORM>/<CHANNEL>/<VERSION>` - Squirrel update method.

## License
[MIT License](https://github.com/pavel-vorobyev/electron-update-server/blob/main/LICENSE)
