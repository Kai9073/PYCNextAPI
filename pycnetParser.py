import requests
import re
import io

from html2text import html2text

from pycnetTypes import Message, baseUrl, proxyUrl, CredsExpiredException, ValidationError


class pycnet():
    @staticmethod
    def getMessages(cookies, options):
        page = options['page'] if 'page' in options else 1
        index_html = requests.get(
            f'{baseUrl}/formmail/index.php?page={page}&key=&key2=&sort=',
            cookies=cookies).text
        if 'alert("invalid token")' in index_html:
            raise CredsExpiredException
        message_html_pattern = re.compile(
            r'<div class="?row"? id="?divrow[12]"?><div class="?col-md-[1-9]"?><[Ii][Nn][Pp][Uu][Tt] [Tt][Yy][Pp][Ee]="?checkbox"? name="dels\[\]" value="(\d+),(\w+),(\w+),(\d+),(\d+),"> <a href="view\.php\?page=0&?a?m?p?;?id=([0-9]+)"\s+class="?forumlink"?>(((?!<\/a>).)+)<\/a>\s?(<img border="?0"? src="?images\/common\.gif"?>)?\s?<\/div><div class="col-md-[1-9]">([^<]+)<\/div><div class="col-md-[1-9]">(\w+\s\w+,?\s\w+)<\/div><\/div>', re.I)
        messageMatches = re.findall(message_html_pattern, index_html)
        messages_list = []
        for messageMatch in messageMatches:
            messages_list.append(Message(*messageMatch))
        return messages_list

    @staticmethod
    def getMessage(cookies, options):
        if not 'id' in options:
            raise KeyError("Missing message Id in options")
        message_html = requests.get(
            f'{baseUrl}/formmail/view.php?page=0&id={options["id"]}',
            cookies=cookies).text
        if 'alert("invalid token")' in message_html:
            raise CredsExpiredException
        re_pattern1 = re.compile('<div class="row"><div class="col-xs-3 col-md-1 bgcell">From : </div><div class="col-xs-9 col-md-3 bgcell">([^<]*)</div><div class="col-md-4 bgcell">To : [^<]*</div><div class="col-md-4 bgcell">Date : ([^<]*)</div></div>')
        re_pattern2 = re.compile('<div class="row"><div class="col-xs-4 col-md-1 bgcell">Attachment : <\/div><div class="col-xs-8 col-md-11 bgcell">(.*)&nbsp;<\/div><\/div>')
        re_pattern3 = re.compile('<div class="row"><div class="col-xs-3 col-md-1 bgcell">Subject : <\/div><div class="col-xs-9 col-md-11 bgcell">([^<]*)<\/div><\/div>')

        match1 = re_pattern1.search(message_html)
        match2 = re_pattern2.search(message_html)
        match3 = re_pattern3.search(message_html)
        
        message_html_splitted = re.split(r'</?html[^>]*>', message_html)
        if len(message_html_splitted) != 5:
            print(message_html_splitted)
            print(len(message_html_splitted))
            raise ValidationError()
        formatted_message_html = f'<!--?xml encoding="UTF-8"--><html>{message_html_splitted[2]}</html>'
        formatted_message_html = re.sub(
            r'src="image.php\?',
            f'src="https://{proxyUrl}/image?s={cookies["PHPSESSID"]}&t={cookies["access_token"]}&',
            formatted_message_html)
        return {
            'html_content': formatted_message_html,
            'author': match1.group(1),
            'date': match1.group(2),
            'attachments': match2.group(1),
            'subject': match3.group(1)
        }

    @staticmethod
    def getImage(cookies, options):
        response = requests.get(
            f'{baseUrl}/formmail/image.php?dir={options["dir"]}&item={options["item"]}',
            cookies=cookies
        )
        image_bytes = io.BytesIO(response.content)
        return image_bytes