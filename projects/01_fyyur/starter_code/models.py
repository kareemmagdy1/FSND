# from __main__ import db
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ARRAY, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
db = SQLAlchemy()

# connect to a local postgresql database
def db_setup(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    return db

class Venue(db.Model):
  __tablename__ = 'venue'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  genres = db.relationship('VenueGenre', backref='venueGenres')
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  shows = db.relationship('Show', backref='shows', cascade="all,delete")
  website = db.Column(db.String(120))
  seeking_talent = db.Column(db.String(20))
  seeking_description = db.Column(db.String(120))
  # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
  __tablename__ = 'artist'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.relationship('ArtistGenre', backref='genreList')
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  shows = db.relationship('Show', backref='list')


class Genre(db.Model):
  __tablename = 'genre'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String, nullable=False, unique=True)


class ArtistGenre(db.Model):
  __tablename = 'artist_genre'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=False)


class VenueGenre(db.Model):
  __tablename = 'venue_genre'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
  genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=False)


class Show(db.Model):
  __tablename__ = 'show'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  date = db.Column(db.DateTime, nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
