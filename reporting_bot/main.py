#!/usr/bin/env python3

import logging
import time
from typing import TypedDict

import psycopg2
import psycopg2.extras

import environ
from nio import AsyncClient, MatrixRoom, RoomMessageText, SendRetryError


@environ.config
class Config:
    account_name = environ.var(
        default='@zazu:localhost',
        converter=str,
        help="The account for the bot to use"
    )
    account_password = environ.var(
        converter=str,
        help="The passwort for the bot account"
    )
    homeserver = environ.var(
        default='http://localhost:8008',
        converter=str,
        help="The homeserver to connect to"
    )
    logging_room_id = environ.var(
        converter=str,
        help=""
    )
    db_host = environ.var(
        default='postgres',
        converter=str,
        help="Database to connect to"
    )
    db_name = environ.var(
        default='synapse',
        converter=str,
        help="Database name to use"
    )
    db_user = environ.var(
        default='synapse',
        converter=str,
        help="Database user to use"
    )
    db_password = environ.var(
        converter=str,
        help="Password to access synapse database"
    )

    @property
    def db_connection_string(self) -> str:
        """Generate the postgres connection string

        Returns:
            str: psycopg2 connection string
        """
        return f'dbname={self.db_name} user={self.db_user}, password={self.db_password}'


class ReportLoggingBot:
    """A bot to report reporting events from synapse to a dedicated room
    """

    def __init__(self, config: Config):
        self.config = config
        self.dbCon = psycopg2.connect(config.db_connection_string)

    def __del__(self):
        self.dbCon.close()

    def mark_sent(self, event_id: int) -> None:
        # Open a new transaction as contextmanager
        with self.dbCon:
            with self.dbConn.cursor() as cursor:
                update_query = 'UPDATE event_reports_notified_flag SET notified = 1 WHERE event_report_id = %i'
                cursor.execute(update_query, event_id)

    def poll_events(self) -> None:
        with self.dbCon:
            with self.dbCon.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                qSelect = """
                SELECT
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
                    JOIN event_reports_notified_flag.notified ON event_reports.id = event_reports_notified_flag.event_report_id
                WHERE event_reports_notified_flag.notified = 1;
                """
                cursor.execute(qSelect)
                results = cursor.fetchall()
        for row in results:
            if self.send_to_room(row):
                self.mark_sent(row['id'])

    async def message_callback(self, room: MatrixRoom, event: RoomMessageText) -> None:
        pass

    async def send_to_room(self, message: str) -> bool:
        client = AsyncClient(self.config.homeserver, self.config.account_name)
        # client.add_event_callback(message_callback, RoomMessageText)

        print(await client.login(self.config.account_password))

        # If you made a new room and haven't joined as that user, you can use
        await client.join(self.config.logging_room_id)

        try:
            await client.room_send(
                # Watch out! If you join an old room you'll see lots of old messages
                room_id=self.config.logging_room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": message
                }
            )
        except SendRetryError:
            return False

        return True
