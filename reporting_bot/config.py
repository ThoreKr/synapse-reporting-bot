import environ


@environ.config
class Config:
    account_name = environ.var(
        default='@zazu:localhost',
        converter=str,
        help='The account for the bot to use'
    )
    account_password = environ.var(
        converter=str,
        help='The passwort for the bot account'
    )
    homeserver = environ.var(
        default='http://localhost:8008',
        converter=str,
        help='The homeserver to connect to'
    )
    logging_room_id = environ.var(
        converter=str,
        help=''
    )
    db_host = environ.var(
        default='postgres',
        converter=str,
        help='Database to connect to'
    )
    db_name = environ.var(
        default='synapse',
        converter=str,
        help='Database name to use'
    )
    db_user = environ.var(
        default='synapse',
        converter=str,
        help='Database user to use'
    )
    db_password = environ.var(
        converter=str,
        help='Password to access synapse database'
    )
    state_file = environ.var(
        default='state.json',
        converter=str,
        help='File to store state information (access token, last sent event) in'
    )
    device_name = environ.var(
        default='Reporting Bot',
        converter=str,
        help='Name of the device to send to the homeserver'
    )
    poll_interval = environ.var(
        default=300,
        converter=int,
        help='Interval to poll the DB for new reports'
    )

    @property
    def db_connection_string(self) -> str:
        """Generate the postgres connection string

        Returns:
            str: psycopg2 connection string
        """
        return f'dbname={self.db_name} user={self.db_user} host={self.db_host} password={self.db_password}'
