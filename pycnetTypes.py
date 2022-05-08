from html2text import html2text

baseUrl = "https://www2.pyc.edu.hk/pycnet"
proxyUrl = "PYCNextAPI.ookai9097oo.repl.co"


class CredsExpiredException(Exception):
    pass


class PropertyException(Exception):
    pass


class ValidationError(Exception):
    pass


class Message:
    def __init__(
        self,
        messageId,
        attachmentId,
        authorId,
        secondaryId,
        isImportant,
        _unused1,
        title,
        _unused2,
        attachmentIcon,
        author,
        date
    ):
        del _unused1, _unused2
        self.messageId = messageId
        self.attachmentId = attachmentId
        self.authorId = authorId
        self.secondaryId = secondaryId
        self.important = bool(int(isImportant))
        self.title = title
        self.attachmentIcon = None if attachmentIcon == "" else attachmentIcon
        self.author = author
        self.date = date
        self.url = f'{baseUrl}/formmail/view.php?page=0&id={messageId}'

    @property
    def hasAttachments(self):
        if (self.attachmentIcon is None and self.attachmentId != 0):
            raise PropertyException(
                'Message has attachmentId {} while icon is {}'.format(
                    self.attachmentId, None))
        return (self.attachmentIcon is not None and self.attachmentId != 0)

    @property
    def dict(self):
        return {
            'title': self.title,
            'url': self.url,
            'icon': self.attachmentIcon,
            'author': {
                'name': self.author,
                'id': self.authorId
            },
            'id': {
                'main': self.messageId,
                'secondary': self.secondaryId
            },
            'date': self.date,
            'isImportant': self.important
        }

    def delete(self):
        pass
        """
        response = self.session.post(
            self.session.baseUrl +
            '/formmail/index.php?page=1key=&key2=&sort=', {}, {
                "dels[]": f'{self.messageId},{self.attachmentId},' +
                f'{self.authorId},{self.messageId2},{self.sp_param},',
                "page": 1,
                "submit": "Delete checked"
            })
        if response.status_code == 200:
            return
        else:
            return

    def getText(self) -> str:
        message_html = self.session.get(self.url).text

        message_md = html2text(message_html)
        message_md = message_md.split('\n\nMessage :\n\n')[1]
        message_md = message_md.split('\n\nCopyright (C)')[0]

        return message_md
      """
