from curious import client
from curious.dataclasses.bases import Dataclass, Messagable
from curious.dataclasses import channel as dt_channel
from curious.dataclasses import message as dt_message


class User(Dataclass, Messagable):
    """
    This represents a bare user - i.e, somebody without a guild attached.

    This is used in DMs and similar. All members are Users, but no Users are Members.
    """

    def __init__(self, client, **kwargs):
        super().__init__(kwargs.pop("id"), client)

        #: The username of this user.
        self.username = kwargs.pop("username", None)

        #: The discriminator of this user.
        #: Note: This is a string, not an integer.
        self.discriminator = kwargs.pop("discriminator", None)

        #: The avatar hash of this user.
        self._avatar_hash = kwargs.pop("avatar", None)

        #: If this user is verified or not.
        self.verified = kwargs.pop("verified", True)

        #: If this user has MFA enabled or not.
        self.mfa_enabled = kwargs.pop("mfa_enabled", None)

    def _copy(self):
        new_object = object.__new__(self.__class__)
        new_object.id = self.id
        new_object.username = self.username
        new_object.discriminator = self.discriminator
        new_object._avatar_hash = self._avatar_hash
        new_object.verified = self.verified
        new_object.mfa_enabled = self.mfa_enabled

        new_object._bot = self._bot

        return new_object

    @property
    def name(self):
        return self.username

    @property
    def mention(self):
        """
        :return: A string that mentions this user.
        """
        nick = getattr(self, "nickname", None)
        if nick:
            return "<@!{}>".format(self.id)

        return "<@{}>".format(self.id)

    @property
    def created_at(self):
        """
        :return: The time this user was created.
        """
        return self.timestamp

    def __str__(self):
        return "{}#{}".format(self.username, self.discriminator)

    async def open_private_channel(self) -> 'dt_channel.Channel':
        """
        Opens a private channel with a user.

        :return: The newly created private channel.
        """
        # First, try and access the channel from the channel cache.

        original_channel = self._bot.state._get_channel(self.id)
        if original_channel:
            return original_channel

        channel_data = await self._bot.http.open_private_channel(self.id)
        channel = self._bot.state.new_private_channel(channel_data)
        return channel

    async def send(self, content: str = None, *args, **kwargs) -> 'dt_message.Message':
        """
        Sends a message to the user over a private channel.

        :param content: The contet of the message to send.
        :return: A new :class:`Message` representing the sent message.
        """
        channel = await self.open_private_channel()
        message = await channel.send(content)

        return message
