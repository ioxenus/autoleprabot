# -*- coding: utf-8 -*-
DB_PATH = 'sqlite:///lepra.db'

LEPROSORIUM_COOKIES = {
    'lepro.save': '',
    'lepro.sid': '',
    'lepro.uid': '',
    'lepro.rnbum': '',
    'lepro.gstqcsaahbv20': ''
}

REDDIT_CREDENTIALS = {
    'username': '',
    'password': ''
}

REDDIT_COMMENT_SLUG = u"""
{comment}

^\[[#]({comment_url})\] ^([**{rating}**] *{author_prefix} {author}, {author_postfix}*)
"""

REDDIT_USERAGENT = 'auto.leprosorium.ru Tusindo-post fetcher v0.1'
