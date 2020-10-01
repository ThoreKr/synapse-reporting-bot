# Synapse Reporting Bot

A little bot to send reports handled in synapse to a moderator channel.

## Requirements

For encryption support it is recommended to use pantalaimon.

## Configuration

The bot can be configured via environment variables.

```
APP_ACCOUNT_NAME (Optional): The account for the bot to use
APP_ACCOUNT_PASSWORD (Required): The passwort for the bot account
APP_HOMESERVER (Optional): The homeserver to connect to
APP_LOGGING_ROOM_ID (Required)
APP_DB_HOST (Optional): Database to connect to
APP_DB_NAME (Optional): Database name to use
APP_DB_USER (Optional): Database user to use
APP_DB_PASSWORD (Required): Password to access synapse database
APP_STATE_FILE (Optional): File to store state information (access token, last sent event) in
APP_DEVICE_NAME (Optional): Name of the device to send to the homeserver
LOGLEVEL (Optinal): Standard Python Logger Loglevel to use
```

It will save an access token and the id of the last sent report in a json file (default: `state.json`)
