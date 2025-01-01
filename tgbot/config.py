from dataclasses import dataclass
from typing import Optional, List

from environs import Env


@dataclass
class DbConfig:
    """
    Database configuration class.
    This class holds the settings for the database, such as host, password, port, etc.

    Attributes
    ----------
    host : str
        The host where the database server is located.
    password : str
        The password used to authenticate with the database.
    user : str
        The username used to authenticate with the database.
    database : str
        The name of the database.
    port : int
        The port where the database server is listening.
    """

    host: str
    password: str
    user: str
    database: str
    port: int = 5432

    # For SQLAlchemy
    def construct_sqlalchemy_url(self, driver="asyncpg", host=None, port=None) -> str:
        """
        Constructs and returns a SQLAlchemy URL for this database configuration.
        """
        # TODO: If you're using SQLAlchemy, move the import to the top of the file!
        from sqlalchemy.engine.url import URL

        if not host:
            host = self.host
        if not port:
            port = self.port
        uri = URL.create(
            drivername=f"postgresql+{driver}",
            username=self.user,
            password=self.password,
            host=host,
            port=port,
            database=self.database,
        )
        return uri.render_as_string(hide_password=False)

    @staticmethod
    def from_env(env: Env):
        """
        Creates the DbConfig object from environment variables.
        """
        host = env.str("DB_HOST")
        password = env.str("POSTGRES_PASSWORD")
        user = env.str("POSTGRES_USER")
        database = env.str("POSTGRES_DB")
        port = env.int("DB_PORT", 5432)
        return DbConfig(
            host=host, password=password, user=user, database=database, port=port
        )


@dataclass
class TgBot:
    """
    Creates the TgBot object from environment variables.
    """

    token: str
    admin_ids: list[int]
    use_redis: bool

    @staticmethod
    def from_env(env: Env):
        """
        Creates the TgBot object from environment variables.
        """
        token = env.str("BOT_TOKEN")
        admin_ids = env.list("ADMINS", subcast=int)
        use_redis = env.bool("USE_REDIS")
        return TgBot(token=token, admin_ids=admin_ids, use_redis=use_redis)

@dataclass
class Payment:
    token: str

    @staticmethod
    def from_env(env: Env):
        token = env.str("PAYMENT_TOKEN")
        return Payment(token=token)


@dataclass
class RedisConfig:
    """
    Redis configuration class.

    Attributes
    ----------
    redis_pass : Optional(str)
        The password used to authenticate with Redis.
    redis_port : Optional(int)
        The port where Redis server is listening.
    redis_host : Optional(str)
        The host where Redis server is located.
    """

    redis_pass: Optional[str]
    redis_port: Optional[int]
    redis_host: Optional[str]

    def dsn(self) -> str:
        """
        Constructs and returns a Redis DSN (Data Source Name) for this database configuration.
        """
        if self.redis_pass:
            return f"redis://:{self.redis_pass}@{self.redis_host}:{self.redis_port}/0"
        else:
            return f"redis://{self.redis_host}:{self.redis_port}/0"

    @staticmethod
    def from_env(env: Env):
        """
        Creates the RedisConfig object from environment variables.
        """
        redis_pass = env.str("REDIS_PASSWORD")
        redis_port = env.int("REDIS_PORT")
        redis_host = env.str("REDIS_HOST")

        return RedisConfig(
            redis_pass=redis_pass, redis_port=redis_port, redis_host=redis_host
        )


@dataclass
class MediaConfig:
    welcome_photo_id: str
    about_club_photo_id: str
    biography_photo_id: str
    reviews_photos: List[str]
    pagination_photos: List[str]
    guides_texting_file_id: str
    guides_seduction_file_id: str
    vip_division_photos: List[str]
    guide_animation: str

    @staticmethod
    def from_env(env: Env) -> "MediaConfig":
        return MediaConfig(
            welcome_photo_id=env.str("WELCOME_PHOTO_ID"),
            about_club_photo_id=env.str("ABOUT_CLUB_PHOTO_ID"),
            biography_photo_id=env.str("BIOGRAPHY_PHOTO_ID"),
            reviews_photos=[
                env.str("REVIEWS_PHOTO_1"),
                env.str("REVIEWS_PHOTO_2"),
            ],
            pagination_photos=[
                env.str("PAGINATION_PHOTO_1"),
                env.str("PAGINATION_PHOTO_2"),
            ],
            vip_division_photos=[
                env.str("VIP_DIVISION_PHOTO_1"),
                env.str("VIP_DIVISION_PHOTO_2"),
            ],
            guides_texting_file_id=env.str("GUIDES_TEXTING_FILE_ID"),
            guides_seduction_file_id=env.str("GUIDES_SEDUCTION_FILE_ID"),
            guide_animation=env.str("GUIDE_ANIMATION"),
        )


@dataclass
class TextConfig:
    read_article_part_1: str
    read_article_part_2: str
    start_message: str
    offer_consent_message: str
    mailing_consent_message: str
    biography_message: str
    tariffs_message: str
    reviews_caption: str
    guide_caption: str
    questions_caption: str
    vip_division_caption: str
    experts_caption: str
    tariff_caption: str
    chat_caption: str
    payment_success_message: str
    payment_inactive_message: str

    @staticmethod
    def from_env(env: Env) -> "TextConfig":
        return TextConfig(
            read_article_part_1=env.str("READ_ARTICLE_PART_1"),
            read_article_part_2=env.str("READ_ARTICLE_PART_2"),
            start_message=env.str("START_MESSAGE"),
            mailing_consent_message=env.str("MAILING_CONSENT_MESSAGE"),
            offer_consent_message=env.str("OFFER_CONSENT_MESSAGE"),
            biography_message=env.str("BIOGRAPHY_MESSAGE"),
            vip_division_caption=env.str("VIP_DIVISION_CAPTION"),
            tariffs_message=env.str("TARIFFS_MESSAGE"),
            reviews_caption=env.str("REVIEWS_CAPTION"),
            guide_caption=env.str("GUIDE_CAPTION"),
            questions_caption=env.str("QUESTIONS_CAPTION"),
            experts_caption=env.str("EXPERTS_CAPTION"),
            tariff_caption=env.str("TARIFF_CAPTION"),
            chat_caption=env.str("CHAT_CAPTION"),
            payment_success_message=env.str("PAYMENT_SUCCESS_MESSAGE"),
            payment_inactive_message=env.str("PAYMENT_INACTIVE_MESSAGE"),
        )



@dataclass
class Miscellaneous:
    private_channel_id: str
    private_chat_id: str
    other_params: Optional[str] = None

    @staticmethod
    def from_env(env: Env) -> "Miscellaneous":
        return Miscellaneous(
            private_channel_id=env.str("PRIVATE_CHANNEL_ID"),
            private_chat_id=env.str("PRIVATE_CHAT_ID"),
            other_params=env.str("OTHER_PARAMS", default=None),
        )


@dataclass
class Config:
    tg_bot: TgBot
    payment: Payment
    db: DbConfig
    redis: RedisConfig
    media: MediaConfig
    text: TextConfig
    misc: Miscellaneous

    @staticmethod
    def from_env(env: Env) -> "Config":
        return Config(
            tg_bot=TgBot.from_env(env),
            payment=Payment.from_env(env),
            db=DbConfig.from_env(env),
            redis=RedisConfig.from_env(env),
            media=MediaConfig.from_env(env),
            text=TextConfig.from_env(env),
            misc=Miscellaneous.from_env(env),
        )


def load_config(path: str = None) -> Config:
    """
    Load the configuration from the specified .env file or environment variables.
    """
    env = Env()
    env.read_env(path)
    return Config.from_env(env)

