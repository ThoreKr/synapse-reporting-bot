#!/usr/bin/env python3
import json
import logging
import os
from string import Template

import psycopg2
import psycopg2.extras
from nio import AsyncClient, LoginResponse, SendRetryError

from .config import Config


def write_details_to_disk(resp: LoginResponse, config: Config) -> None:
    """Writes the required login details to disk so we can log in later without
    using a password.

    Args:
        resp (LoginResponse): The successful login response
        config (Config): The configuration object
    """
    # open the config file in write-mode
    with open(config.state_file, "w") as f:
        # write the login details to disk
        json.dump(
            {
                "homeserver": config.homeserver,  # e.g. "https://matrix.example.org"
                "user_id": resp.user_id,  # e.g. "@user:example.org"
                "device_id": resp.device_id,  # device ID, 10 uppercase letters
                "access_token": resp.access_token,  # cryptogr. access token
                "last_message_id": 0
            },
            f
        )


class ReportLoggingBot:
    """A bot to report reporting events from synapse to a dedicated room
    """

    def __init__(self, config: Config):
        self.config = config
        self.dbCon = psycopg2.connect(config.db_connection_string)
        self.logger = logging.getLogger(__name__)

        self.last_message_id = 0
        self.access_token: str = None
        self.user_id: str = None
        self.device_id: str = None

        if os.path.exists(self.config.state_file):
            # open the state file in read-only mode
            with open(self.config.state_file, "r") as f:
                state = json.load(f)

            self.last_message_id = state['last_message_id']
            self.access_token = state['access_token']
            self.user_id = state['user_id']
            self.device_id = state['device_id']

    def __del__(self):
        self.dbCon.close()

    def format_message(self, row: dict) -> str:
        content = json.loads(row['json'])['content']
        if row['room_alias'] is None:
            raw_template = (
            '$user_id has reported a message from $sender in a private room.\n'
            'Report: $reason\n'
            )

            html_template = (
            '<p>$user_id has reported a message from $sender in a private room.<br />'
            'Report: $reason <br />'
            )
        else:
            raw_template = (
                '$user_id has reported a message from $sender in room $room_alias.\n'
                'Report: $reason\n'
                'Concerning message:\n'
                '```\n'
                '$content\n'
                '```\n'
            )

            html_template = (
                '<p>$user_id has reported a message from $sender in room $room_alias.<br />'
                'Report: $reason <br />'
                'Concerning message:</p>\n<pre><code> $content \n</code></pre>\n'
            )

        return [Template(template).substitute(content=content, **row) for template in [raw_template, html_template]]

    def mark_sent(self, event_id: int) -> None:
        # Open a new transaction as contextmanager
        self.last_message_id = event_id

        with open(self.config.state_file, 'r+') as f:
            state = json.load(f)
            # update json here
            state['last_message_id'] = event_id
            f.seek(0)
            f.truncate()
            json.dump(state, f)

    async def poll_events(self) -> None:
        cursor = self.dbCon.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if self.config.view_name is None:
            qSelect = """
                SELECT
                    event_reports.id,
                    event_reports.received_ts,
                    event_reports.room_id,
                    room_aliases.room_alias,
                    events.sender,
                    event_reports.user_id,
                    event_reports.reason,
                    event_json.json
                FROM event_reports
                    LEFT JOIN room_aliases ON room_aliases.room_id = event_reports.room_id
                    JOIN events ON events.event_id = event_reports.event_id
                    JOIN event_json ON event_json.event_id = event_reports.event_id
                WHERE event_reports.id > %s;
            """
        else:
            qSelect = f"SELECT id, received_ts, room_id, room_alias, sender, user_id, reason, json FROM {self.config.view_name} WHERE id > %s;"
        self.logger.debug("Last message id: %i", self.last_message_id)
        cursor.execute(qSelect, (self.last_message_id,))
        for row in cursor:
            if await self.send_to_room(self.format_message(row)):
                self.mark_sent(row['id'])

    async def send_to_room(self, message: str) -> bool:
        client = await self.login()

        # If you made a new room and haven't joined as that user, you can use
        await client.join(self.config.logging_room_id)

        try:
            self.logger.info('Sending report %s', message)
            await client.room_send(
                # Watch out! If you join an old room you'll see lots of old messages
                room_id=self.config.logging_room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": message[0],
                    "format": "org.matrix.custom.html",
                    "formatted_body": message[1]
                }
            )
        except SendRetryError:
            self.logger.error('Error sending report, trying again later.')
            return False
        finally:
            await client.close()

        return True

    async def login(self) -> AsyncClient:
        # If there are no previously-saved credentials, we'll use the password
        if not os.path.exists(self.config.state_file):
            self.logger.info("First time use. Did not find credential file. Using environment variables")

            client = AsyncClient(self.config.homeserver, self.config.account_name)
            resp = await client.login(self.config.account_password, device_name=self.config.device_name)

            # check that we logged in succesfully
            if (isinstance(resp, LoginResponse)):
                write_details_to_disk(resp, self.config)
            else:
                self.logger.warning(
                    f'homeserver = "{self.config.homeserver}"; user = "{self.config.account_name}"')
                self.logger.warning(f'Failed to log in: {resp}')
                exit(1)

            self.logger.info(
                'Logged in using a password. Credentials were stored.',
                'Try running the script again to login with credentials'
            )

        # Otherwise the config file exists, so we'll use the stored credentials
        else:
            client = AsyncClient(self.config.homeserver)
            client.access_token = self.access_token
            client.user_id = self.user_id
            client.device_id = self.device_id

        return client
