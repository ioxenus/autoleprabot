#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from logging import debug, error

import requests

from requests.exceptions import HTTPError
from praw import Reddit

from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from config import (DB_PATH, LEPROSORIUM_COOKIES, REDDIT_CREDENTIALS, REDDIT_COMMENT_SLUG,
                    REDDIT_USERAGENT)
from models import Base, Post, Comment

# logging settings
logging.basicConfig(format='%(asctime)-15s [%(name)s] %(levelname)s | %(message)s',
                    level=logging.DEBUG)

requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

debug("Initializing parser...")

# init reddit session
reddit = Reddit(user_agent=REDDIT_USERAGENT)

try:
    debug("Logging in to Reddit...")
    reddit.login(**REDDIT_CREDENTIALS)
except HTTPError as e:
    error("Couldn't login to reddit: {0}".format(e))


# create DB session
engine = create_engine(DB_PATH)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


if __name__ == '__main__':
    request_session = requests.session()

    for post in session.query(Post).all():
        # load reddit post
        submission = reddit.get_submission(submission_id=post.reddit_post_id)

        # load lepra post
        debug("Fetching leprosorium post #{0}...".format(post.lepra_post_id))
        lepra_url = "http://auto.leprosorium.ru/comments/{0}".format(post.lepra_post_id)
        response = request_session.get(lepra_url, cookies=LEPROSORIUM_COOKIES)
        bs_tree = BeautifulSoup(response.text)

        # parse lepra post

        debug("Parsing comments...")
        # for comment in comments
        for node in bs_tree.findAll('div', attrs={'class': 'post', 'class': 'indent_0'}):
            comment_id = int(node['id'])
            debug("Parsing comment #{0}:".format(comment_id))
            content = node.find('div', attrs={'class': 'dt'})
            urls = [link['href'] for link in content.findAll('a') if 'youtube.com' in link['href']]

            if not urls:
                debug("  No YouTube URLs found. Skipping this comment.")
                continue

            # convert <a href="..."> tags to plain-text URLs
            for link in content.findAll('a', href=True):
                link.replace_with(link['href'])

            # remove all images
            for img in content.findAll('img'):
                img.extract()

            # convert <br> to \n
            text = ''
            for element in content.recursiveChildGenerator():
                if isinstance(element, basestring):
                    text += element.strip()
                elif element.name == 'br':
                    text += '  \n'

            lepra_comment_url = '{0}#{1}'.format(lepra_url, comment_id)
            rating = int(node.find('span', attrs={'class': 'rating'}).text)
            author = (node.find('div', attrs={'class': 'dd'})
                          .find(attrs={'class': 'p'})
                          .findAll('a')[1]
                          .text)

            sa_comment = session.query(Comment).filter_by(lepra_comment_id=comment_id).first()

            changed = False

            if not sa_comment:
                debug("  Comment isn't fetched yet. Saving it to DB...")
                sa_comment = Comment(post_id=post.id,
                                     lepra_comment_id=comment_id,
                                     author=author,
                                     youtube_url=urls[0],
                                     rating=rating,
                                     comment=text)
                session.add(sa_comment)
                session.commit()
            else:
                if sa_comment.rating != rating:
                    debug("  Comment's rating changed.")
                    sa_comment.rating = rating
                    changed = True

                if sa_comment.comment != text:
                    debug("  Comment's text changed.")
                    sa_comment.comment = text
                    changed = True

                if changed:
                    debug("  Saving changes to DB...")
                    session.commit()


            reddit_comment_text = REDDIT_COMMENT_SLUG.format(comment=text,
                                                             comment_url=lepra_comment_url,
                                                             rating=rating,
                                                             author=author)

            if not sa_comment.reddit_comment_id:
                debug("  No comment at reddit yet. Posting a comment on Reddit...")
                r_comment = submission.add_comment(reddit_comment_text)

                debug("  Comment posted. Saving its ID ({0}) into DB...".format(r_comment.id))
                sa_comment = session.query(Comment).filter_by(lepra_comment_id=comment_id).first()
                sa_comment.reddit_comment_id = r_comment.id
                session.commit()
            elif sa_comment.reddit_comment_id and changed:
                # edit comment at reddit (update rating there)
                r_comment_id = sa_comment.reddit_comment_id
                debug("  Comment already exists ({0}). Updating...".format(r_comment_id))
                r_comment = [c for c in submission.comments if c.id == r_comment_id]
                r_comment = r_comment[0]
                r_comment.edit(reddit_comment_text)

            if not changed:
                debug("  No changes.")

