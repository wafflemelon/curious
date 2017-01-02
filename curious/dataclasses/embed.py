import datetime

# attrdict, useful for embed parts
from curious.dataclasses.bases import IDObject

attrdict = type("attrdict", (dict,), {
    "__getattr__": dict.__getitem__,
    "__setattr__": dict.__setitem__,
    "__doc__": "A dict that allows attribute access as well as item access for "
               "keys."
})


def _(s, n, v): raise KeyError(n)


class Attachment(IDObject, attrdict):
    def __init__(self, **kwargs):
        IDObject.__init__(self, int(kwargs.pop("id", 0)))
        attrdict.__init__(self, **kwargs)


class Embed(object):  # not an IDObject! Embeds don't have IDs.
    """
    Represents an Embed object on Discord.
    """

    def __init__(self, *,
                 title: str = None,
                 description: str = None,
                 colour: int = None,
                 type_: str = None,
                 url: str = None,
                 timestamp: str = None,
                 **kwargs):

        #: The title of this embed.
        self.title = title

        #: The description of this embed.
        self.description = description

        if colour is None:
            # for passing in from discord
            colour = kwargs.get("color")

        #: The colour of this embed.
        self.colour = colour

        #: The type of this embed.
        self.type_ = type_

        #: The URL for this embed.
        self.url = url

        #: The timestamp for this embed.
        self.timestamp = timestamp  # type: datetime.datetime

        #: The fields for this embed.
        self._fields = []

        #: The footer for this embed.
        self.footer = attrdict(**kwargs.get("footer", {}))

        #: The author of this embed.
        self.author = attrdict(**kwargs.get("author", {}))

        #: The image for this embed.
        self.image = attrdict(**kwargs.get("image", {}))

        #: The video for this embed.
        self.video = attrdict(**kwargs.get("video", {}))

        #: The thumbnail for this embed.
        self.thumbnail = attrdict(**kwargs.get("thumbnail", {}))

    def add_field(self, *, name: str, value: str,
                  inline: bool = True) -> 'Embed':
        """
        Adds a field to the embed.

        :param name: The field name.
        :param value: The field value.
        :param inline: Is this field inline?
        :return: The Embed object.
        """
        self._fields.append(attrdict({"name": name, "value": value, "inline": inline}))
        return self

    def set_author(self, *, name: str = None, url: str = None) -> 'Embed':
        """
        Sets the author of this embed.

        :param name: The name of the author.
        :param url: The URL of the author.
        :return: The Embed object.
        """

        self.author = attrdict()
        if name:
            self.author.name = name

        if url:
            self.author.url = url

        return self

    def set_footer(self, *, text: str = None, icon_url: str = None) -> 'Embed':
        """
        Sets the footer of this embed.

        :param text: The footer text of this embed.
        :param icon_url: The icon URL for the footer.
        :return: The Embed object.
        """
        self.footer = attrdict()
        if text:
            self.footer.text = text

        if icon_url:
            self.footer.icon_url = icon_url

    def set_image(self, *, image_url: str) -> 'Embed':
        """
        Sets the image of this embed.

        :param image_url: The image URL of this embed.
        :return: The Embed object.
        """
        self.image = attrdict()
        if image_url:
            self.image.image_url = image_url

        return self

    def to_dict(self):
        """
        Converts this embed into a flattened dict.
        """
        payload = {
            "type": self.type_
        }

        if self.title:
            payload["title"] = self.title

        if self.description:
            payload["description"] = self.description

        if self.url:
            payload["url"] = self.url

        if self.colour:
            payload["colour"] = self.colour

        if self.timestamp:
            payload["timestamp"] = self.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")

        # attrdicts can be automatically json dumped easily
        # so we just go and shove these right in there
        if self.footer:
            payload["footer"] = self.footer

        if self.thumbnail:
            payload["thumbnail"] = self.thumbnail

        if self.image:
            payload["image"] = self.image

        if self.author:
            payload["author"] = self.author

        payload["fields"] = self._fields

        return payload