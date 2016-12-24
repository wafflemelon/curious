import typing
import re

from curious.dataclasses.bases import Dataclass
from curious.dataclasses import guild as dt_guild
from curious.dataclasses import channel as dt_channel
from curious.dataclasses import member as dt_member
from curious.dataclasses import role as dt_role
from curious.dataclasses import user as dt_user
from curious.util import to_datetime

CHANNEL_REGEX = re.compile(r"<#([0-9]*)>")


class Message(Dataclass):
    """
    Represents a Message.
    """
    def __init__(self, client, **kwargs):
        super().__init__(kwargs.pop("id"), client)

        #: The content of the message.
        self.content = kwargs.pop("content", None)  # type: str

        #: The guild this message was sent in.
        #: This can be None if the message was sent in a DM.
        self.guild = None  # type: dt_guild.Guild

        #: The channel this message was sent in.
        self.channel = None  # type: dt_channel.Channel

        #: The author of this message.
        self.author = None  # type: dt_member.Member

        #: The true timestamp of this message.
        #: This is not the snowflake timestamp.
        self.created_at = to_datetime(kwargs.pop("timestamp", None))

        #: The edited timestamp of this message.
        #: This can sometimes be None.
        edited_timestamp = kwargs.pop("edited_timestamp", None)
        if edited_timestamp is not None:
            self.edited_at = to_datetime(edited_timestamp)
        else:
            self.edited_at = None

        #: The mentions for this message.
        #: This is UNORDERED.
        self._mentions = kwargs.pop("mentions", [])

        #: The role mentions for this array.
        #: This is UNORDERED.
        self._role_mentions = kwargs.pop("mention_roles", [])

    @property
    def mentions(self):
        return self._resolve_mentions(self._mentions, "member")

    @property
    def role_mentions(self) -> typing.List['dt_role.Role']:
        return self._resolve_mentions(self._role_mentions, "role")

    @property
    def channel_mentions(self):
        mentions = CHANNEL_REGEX.findall(self.content)
        return self._resolve_mentions(mentions, "channel")

    def _resolve_mentions(self, mentions, type_: str) -> typing.List[Dataclass]:
        final_mentions = []
        for mention in mentions:
            if type_ == "member":
                id = int(mention["id"])
                obb = self.guild.get_member(id)
                if obb is None:
                    obb = dt_user.User(**mention)
            elif type_ == "role":
                obb = self.guild.get_role(int(mention))
            elif type_ == "channel":
                obb = self.guild.get_channel(int(mention))
            if obb is not None:
                final_mentions.append(obb)

        return final_mentions

    # Message methods
    async def delete(self):
        """
        Deletes this message.

        You must have MANAGE_MESSAGE permissions to delete this message, or have it be your own message.
        """
        await self._bot.http.delete_message(self.channel.id, self.id)

    async def edit(self, new_content: str) -> 'Message':
        """
        Edits this message.

        You must be the owner of this message to edit it.
        This edits the message in-place.

        :param new_content: The new content for this message.
        :return: This message, but edited with the new content.
        """
        message_data = await self._bot.http.edit_message(self.channel.id, self.id, new_content=new_content)
        self.content = message_data.get("content")
        self.edited_at = to_datetime(message_data.get("edited_timestamp", None))

        return self

    async def pin(self):
        """
        Pins this message.

        You must have MANAGE_MESSAGES in the channel to pin the message.
        """
        await self._bot.http.pin_message(self.channel.id, self.id)
