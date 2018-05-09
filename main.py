#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import time
from google.appengine.ext import ndb
from google.appengine.api import users
import jinja2
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"),
                                       extensions=["jinja2.ext.autoescape"],
                                       autoescape=True)


class User(ndb.Model):
    id_user = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)


class Deck(ndb.Model):
    name = ndb.StringProperty(required=True)
    description = ndb.StringProperty()
    owner = ndb.KeyProperty(required=True, kind=User)
    rating = ndb.IntegerProperty(required=True, default=1500)
    grow_rate = ndb.IntegerProperty(required=True, default=100)
    link = ndb.StringProperty()
    image = ndb.BlobProperty(default=None)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:

            db_user = User.query(User.id_user == user.user_id()).get()

            if not db_user:
                db_user = User(id_user=user.user_id(), name=user.nickname().partition("@")[0])
                db_user.put()
            self.redirect("/deck")
        else:
            labels = {
                "user_login": users.create_login_url("/")
            }
            template = JINJA_ENVIRONMENT.get_template("login.html")
            self.response.write(template.render(labels))


class DeckHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            decks = Deck.query().order(-Deck.rating)

            owners = []
            for deck in decks:
                owners.append(User.query(User.key == deck.owner).get())

            values = {
                'decks': decks,
                "username": user.nickname().partition("@")[0],
                'owners': owners,
                'user': user,
                "user_id": user.user_id(),
                'user_logout': users.create_logout_url("/"),
                'add': self.request.get("add"),
                'del': self.request.get("del"),
                'edi': self.request.get("edi"),
                'game': self.request.get("game")
            }

            template = JINJA_ENVIRONMENT.get_template("deck/deck.html")
            self.response.write(template.render(values))
        else:
            self.redirect("/")


class AddDeckHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            values = {
                "user": user.nickname(),
                "username": user.nickname().partition("@")[0],
                "user_logout": users.create_logout_url("/")
            }

            template = JINJA_ENVIRONMENT.get_template("deck/deck_add.html")
            self.response.write(template.render(values))
        else:
            self.redirect("/")

    def post(self):
        user = users.get_current_user()

        if user:
            name = self.request.get("name")
            link = self.request.get("link")
            desc = self.request.get("desc")
            rating = int(self.request.get("rating"))
            grow = int(self.request.get("grow"))
            owner = User.query(User.id_user == user.user_id()).get().key

            image_file = None
            if self.request.get("image") != "":
                # Store the added image
                image_file = self.request.get("image", None)

            deck = Deck(name=name, owner=owner, link=link, image=image_file, rating=rating, grow_rate=grow, description=desc)

            deck.put()
            time.sleep(1)

            self.redirect("/deck?add=True")
        else:
            self.redirect("/")


class DeleteDeckHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        db_user = User.query(User.id_user == user.user_id()).get()

        if user and db_user:
            deck_id = int(self.request.get("id"))
            deck = Deck.query(Deck.key == ndb.Key(Deck, deck_id), Deck.owner == db_user.key).get()

            if deck:
                deck.key.delete()
                time.sleep(1)

                self.redirect("deck?del=True")
            else:
                self.redirect("deck?del=False")
        else:
            self.redirect("/")


class EditDeckHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        db_user = User.query(User.id_user == user.user_id()).get()

        if user and db_user:
            deck_id = int(self.request.get("id"))
            deck = Deck.query(Deck.key == ndb.Key(Deck, deck_id), Deck.owner == db_user.key).get()

            if deck:
                values = {
                    "user": user.nickname(),
                    "username": user.nickname().partition("@")[0],
                    "user_logout": users.create_logout_url("/"),
                    "deck": deck
                }

                template = JINJA_ENVIRONMENT.get_template("deck/deck_edit.html")
                self.response.write(template.render(values))
            else:
                self.redirect("deck?edi=False")
        else:
            self.redirect("/")

    def post(self):
        user = users.get_current_user()
        db_user = User.query(User.id_user == user.user_id()).get()

        if user and db_user:
            deck_id = int(self.request.get("id"))
            deck = Deck.query(Deck.key == ndb.Key(Deck, deck_id), Deck.owner == db_user.key).get()

            if deck:
                deck.name = self.request.get("name")
                deck.link = self.request.get("link")
                deck.description = self.request.get("desc")

                if self.request.get("image") != "":
                    # Store the added image
                    image_file = self.request.get("image", None)
                    deck.image = image_file

                deck.put()
                time.sleep(1)

                self.redirect("deck?edi=True")
            else:
                self.redirect("deck?edi=False")
        else:
            self.redirect("/")


class AddGameHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            decks = Deck.query()

            values = {
                "user": user.nickname(),
                "username": user.nickname().partition("@")[0],
                "user_logout": users.create_logout_url("/"),
                "decks": decks,
                "fail": self.request.get("fail")
            }

            template = JINJA_ENVIRONMENT.get_template("game/game_add.html")
            self.response.write(template.render(values))

    def post(self):
        winner_id = int(self.request.get("winner"))
        players_ids = self.request.params.getall("players")
        players_ids[:] = [int(x) for x in players_ids]

        if len(players_ids) < 3 or len(players_ids) > 8 or (winner_id not in players_ids):
            self.redirect("addGame?fail=True")
        else:
            winner = Deck.query(Deck.key == ndb.Key(Deck, winner_id)).get()
            players = []
            players[:] = [Deck.query(Deck.key == ndb.Key(Deck, x)).get() for x in players_ids]
            players[:] = adjust_elo(players, winner)

            for deck in players:
                deck.put()
                time.sleep(.1)

            self.redirect("deck?game=True")


def adjust_elo(players, winner):
    toret = players

    for position, player in enumerate(players, 0):
        is_winner = 0
        exp_win = []
        if player.key == winner.key:
            is_winner = 1
        for opponent in (y for y in players if y.key != player.key):
            exp_win.append(10 ** ((opponent.rating - player.rating) / 400))
        expected = 1 / (1 + sum(exp_win))
        toret[position].rating = int(round(player.rating + player.grow_rate * (is_winner - expected)))
        if toret[position].grow_rate > 30:
            toret[position].grow_rate -= 10

    return toret


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/deck', DeckHandler),
    ('/addDeck', AddDeckHandler),
    ('/delDeck', DeleteDeckHandler),
    ('/addGame', AddGameHandler),
    ('/editDeck', EditDeckHandler)
], debug=True)
