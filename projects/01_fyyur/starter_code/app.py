#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_migrate import Migrate
from flask_wtf import Form
from forms import *
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate=Migrate(app,db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    genres = db.relationship('VenueGenre',backref='venueGenres')
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='shows', cascade="all,delete")
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.relationship('ArtistGenre',backref='genreList')
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='list')

class Genre(db.Model):
  __tablename='genre'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name=db.Column(db.String,nullable=False,unique=True)

class ArtistGenre(db.Model):
  __tablename='artist_genre'
  id = db.Column(db.Integer, primary_key=True,autoincrement=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=False)

class VenueGenre(db.Model):
  __tablename='venue_genre'
  id = db.Column(db.Integer, primary_key=True,autoincrement=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
  genre_id=db.Column(db.Integer,db.ForeignKey('genre.id'),nullable=False)

class Show(db.Model):
  __tablename__='show'
  id = db.Column(db.Integer, primary_key=True,autoincrement=True)
  date=db.Column(db.DateTime,nullable=False)
  artist_id = db.Column(db.Integer,db.ForeignKey('artist.id'),nullable=False)
  venue_id=db.Column(db.Integer,db.ForeignKey('venue.id'),nullable=False)
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  # result=db.session.query(Artist).first()
  # print(result.genres[0].genre_id)
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  allCities =db.session.query(Venue.city).all()
  allCities=list(dict.fromkeys(allCities))
  data = []
  for city in allCities:
    returnedVenues =db.session.query(Venue).filter(Venue.city==city).all()
    print(len(returnedVenues))
    shows=[]
    venuesObj = []
    for index,ven in enumerate(returnedVenues):
      object=db.session.query(Venue).filter(Venue.id==ven.id).first()
      showNumbers=len(object.shows)
      shows.append(showNumbers)
      venuesObj.append({"id":ven.id,"name":ven.name,"num_upcoming_shows":shows[index]})
    city= str(city).replace('(','').replace(')','').replace('\'','').replace(',','')
    data.append({"city":city,
                 "state":returnedVenues[0].state,
                 "venues":venuesObj
                 })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  name = request.form.get('search_term')
  result = Venue.query.filter(Venue.name.like('%' + name + '%')).all()
  data = []
  shows = []
  for index, ven in enumerate(result):
    showNumbers = db.session.query(Venue.shows).count()
    shows.append(showNumbers)
    data.append({"id": ven.id, "name": ven.name, "num_upcoming_shows": shows[index]})
  response={
    "count": len(shows),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  wantedVenue=db.session.query(Venue).filter(Venue.id==venue_id).first()
  wantedVenueGenres=wantedVenue.genres
  wantedVenueShows=wantedVenue.shows
  upcomingShows=[]
  oldShows=[]
  present = datetime.now()
  for show in wantedVenueShows:
    if(show.date>present.date()):
      upcomingShows.append(str(show.date))
    else:
      oldShows.append(str(show.date))

  genresList=[]
  for gen in wantedVenueGenres:
    genreName=db.session.query(Genre.name).filter(Genre.id == gen.genre_id).first()
    genresList.append(str(genreName))
  data={
    "id": wantedVenue.id,
    "name": wantedVenue.name,
    "genres": genresList,
    "address": wantedVenue.address,
    "city": wantedVenue.city,
    "state": wantedVenue.state,
    "phone": wantedVenue.phone,
    "website": "https://www.themusicalhop.com",
    "facebook_link": wantedVenue.facebook_link,
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": oldShows,
    "upcoming_shows": upcomingShows,
    "past_shows_count": len(oldShows),
    "upcoming_shows_count": len(upcomingShows),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error=False
  try:
    name=request.form['name']
    city=request.form.get('city')
    state=request.form.get('state')
    address=request.form.get('address')
    phone=request.form.get('phone')
    genres=request.form.getlist('genres')
    print(genres)
    facebook_link=request.form.get('facebook_link')
    obj=Venue(name=name,city=city,state=state,address=address,
              phone=phone,facebook_link=facebook_link)
    foundGenres=[]
    for index,gen in enumerate(genres):
      foundGenres.append(db.session.query(Genre).filter(Genre.name==gen).first())
      if(foundGenres[index]==None):
        foundGenres[index]=(Genre(name=gen))
        db.session.add(foundGenres[index])
    db.session.add(obj)
    db.session.flush()
    id=obj.id;
    db.session.commit()

    for gen in genres:
      venueGenre=VenueGenre(venue_id=id,genre_id=db.session.query(Genre.id).filter(Genre.name==gen).first())
      db.session.add(venueGenre)
    db.session.commit()

    #genre does returns none cant use it
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    error=True
    db.session.rollback()
    flash(sys.exc_info())
  finally:
    db.session.close()
  # on successful db insert, flash success
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  returnedObjs=db.session.query(Venue).filter(Venue.id==venue_id).all()
  if(len(returnedObjs)>0):
    db.session.delete(returnedObjs[0])
    db.session.commit()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  returnedObjs=db.session.query(Artist).all()
  data=[]
  for artist in returnedObjs:
    data.append({"id":artist.id,"name":artist.name})
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  name = request.form.get('search_term')
  result = Artist.query.filter(Artist.name.like('%' + name + '%')).all()
  data = []
  shows = []
  for index, arti in enumerate(result):
    returnedArtist= db.session.query(Artist).filter(Artist.id==arti.id).first()
    aristShows=returnedArtist.shows;
    shows.append(len(aristShows))
    data.append({"id": arti.id, "name": arti.name, "num_upcoming_shows": shows[index]})
  response = {
    "count": len(shows),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  object=db.session.query(Artist).filter(artist_id==Artist.id).first()
  if(object==None):
    return render_template('errors/404.html')
  showsRelated=object.shows;
  pastShows=[]
  upcomingShows=[]
  present = datetime.now()
  # print
  # datetime(2015, 04, 30) < present  # should return true
  for show in showsRelated:
    if(show.date>present.date()):
      upcomingShows.append(show)
    else:
      pastShows.append(show)
  data=[]
  genresToReturn = []
  for gen in object.genres:
    genresToReturn.append(str(db.session.query(Genre.name)
                              .filter(Genre.id == gen.genre_id).first()).replace(',','').replace(')','')
                              .replace('(','').replace('\'',''))
  data.append({"id":object.id,"name": object.name,"genres": genresToReturn,
                 "city":object.city,"state": object.state,"phone":object.phone,
                 "website": "https://www.gunsnpetalsband.com",
                 "facebook_link": object.facebook_link,
                 "seeking_venue": True,
                 "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
                 "image_link":object.image_link,
                 "past_shows":pastShows,
                 "upcoming_shows":upcomingShows,
                 "past_shows_count":len(pastShows),
                 "upcoming_shows_count":len(upcomingShows)
                 })
  return render_template('pages/show_artist.html', artist=data[0])

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  object=db.session.query(Artist).filter(artist_id==Artist.id).first()
  if(object==None):
    return render_template('errors/404.html')
  showsRelated=object.shows;
  pastShows=[]
  upcomingShows=[]
  present = datetime.now()
  for show in showsRelated:
    if(show.date>present.date()):
      upcomingShows.append(show)
    else:
      pastShows.append(show)
  data=[]
  genresToReturn=[]
  for gen in object.genres:
    genresToReturn.append(db.session.query(Genre).filter(Genre.id==gen.genre_id))
  data.append({"id":object.id,"name": object.name,"genres": genresToReturn,
                 "city":object.city,"state": object.state,"phone":object.phone,
                 "website": "https://www.gunsnpetalsband.com",
                 "facebook_link": object.facebook_link,
                 "seeking_venue": True,
                 "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
                 "image_link":object.image_link
                 })
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=data[0])

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artistObj=db.session.query(Artist).filter(Artist.id==artist_id).first()
    artistObj.name = request.form['name']
    artistGenres=db.session.query(ArtistGenre).filter(ArtistGenre.artist_id==artist_id).all()
    for gen in artistGenres:
      db.session.delete(gen)
      db.session.commit()
    artistObj.city = request.form.get('city')
    artistObj.state = request.form.get('state')
    artistObj.address = request.form.get('address')
    artistObj.phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    artistObj.facebook_link = request.form.get('facebook_link')
    foundGenres=[]
    for index, gen in enumerate(genres):
      foundGenres.append(db.session.query(Genre).filter(Genre.name == gen).first())
      if (foundGenres[index] == None):
        foundGenres[index] = (Genre(name=gen))
        db.session.add(foundGenres[index])
    db.session.commit()
    for gen in genres:
      artistGenre = ArtistGenre(artist_id=artist_id, genre_id=db.session.query(Genre.id).filter(Genre.name == gen).first())
      db.session.add(artistGenre)
    db.session.commit()
    return redirect(url_for('show_artist', artist_id=artist_id))
  except:
    error = True
    db.session.rollback()
    flash(sys.exc_info())
  finally:
    db.session.close()
  # on successful db insert, flash success

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  object = db.session.query(Venue).filter(venue_id == Venue.id).first()
  if (object == None):
    return render_template('errors/404.html')
  showsRelated = object.shows;
  pastShows = []
  upcomingShows = []
  present = datetime.now()
  for show in showsRelated:
    if (show.date > present.date()):
      upcomingShows.append(show)
    else:
      pastShows.append(show)
  data = []
  genresToReturn = []
  for gen in object.genres:
    genresToReturn.append(db.session.query(Genre).filter(Genre.id == gen.genre_id))
  data.append({"id": object.id, "name": object.name, "genres": genresToReturn,
               "city": object.city, "state": object.state, "phone": object.phone,
               "website": "https://www.gunsnpetalsband.com",
               "facebook_link": object.facebook_link,
               "seeking_venue": True,
               "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
               "image_link": object.image_link
               })
  return render_template('forms/edit_venue.html', form=form, venue=data[0])

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venueObj = db.session.query(Venue).filter(Venue.id == venue_id).first()
    venueObj.name = request.form['name']
    venueGenres = db.session.query(VenueGenre).filter(VenueGenre.venue_id == venue_id).all()
    for gen in venueGenres:
      db.session.delete(gen)
      db.session.commit()
    venueObj.city = request.form.get('city')
    venueObj.state = request.form.get('state')
    venueObj.address = request.form.get('address')
    venueObj.phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    venueObj.facebook_link = request.form.get('facebook_link')
    foundGenres = []
    for index, gen in enumerate(genres):
      foundGenres.append(db.session.query(Genre).filter(Genre.name == gen).first())
      if (foundGenres[index] == None):
        foundGenres[index] = (Genre(name=gen))
        db.session.add(foundGenres[index])
    db.session.commit()
    for gen in genres:
      venueGenre = VenueGenre(venue_id=venue_id,
                                genre_id=db.session.query(Genre.id).filter(Genre.name == gen).first())
      db.session.add(venueGenre)
    db.session.commit()
    return redirect(url_for('show_venue', artist_id=venue_id))
  except:
    error = True
    db.session.rollback()
    flash(sys.exc_info())
  finally:
    db.session.close()
  # on successful db insert, flash success
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    name = request.form['name']
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link')
    obj = Artist(name=name, city=city, state=state,
                phone=phone, facebook_link=facebook_link)
    foundGenres = []
    for index, gen in enumerate(genres):
      foundGenres.append(db.session.query(Genre).filter(Genre.name == gen).first())
      if (foundGenres[index] == None):
        foundGenres[index] = (Genre(name=gen))
        db.session.add(foundGenres[index])
    db.session.add(obj)
    db.session.flush()
    id = obj.id;
    db.session.commit()

    for gen in genres:
      artistGenre = ArtistGenre(artist_id=id, genre_id=db.session.query(Genre.id).filter(Genre.name == gen).first())
      db.session.add(artistGenre)
    db.session.commit()

    # genre does returns none cant use it
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    error = True
    db.session.rollback()
    flash(sys.exc_info())
  finally:
    db.session.close()
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows=db.session.query(Show).all()
  data=[]
  for show in shows:
    artist=db.session.query(Artist).filter(show.artist_id==Artist.id).first()
    venue=db.session.query(Venue).filter(show.venue_id==Venue.id).first()
    data.append({"venue_id": venue.id,
    "venue_name": venue.name,
    "artist_id": artist.id,
    "artist_name": artist.name,
    "artist_image_link": artist.image_link,
    "start_time": str(show.date)})
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  try:
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = datetime.strptime(request.form.get('start_time'), '%Y-%m-%d %H:%M:%S')
    show = Show(venue_id=venue_id
                , artist_id=artist_id, date=start_time)
    db.session.add(show)
    db.session.commit()
    #genre does returns none cant use it
    flash('Show ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
  finally:
    db.session.close()
  #
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
