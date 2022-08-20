#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import os
import json
import dateutil.parser
import babel
from os import path, environ
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import collections
#from flask_wtf import CsrfProtect


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

collections.Callable = collections.abc.Callable
app = Flask(__name__)
moment = Moment(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Shows', backref='showing', lazy=True)


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue  = db.Column(db.String(120))
    seeking_description  = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Shows', backref='show', lazy=True)

class Shows(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String())

    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

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
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  data = []
  v = []
  Ven = Venue.query.distinct(Venue.city, Venue.state).all()
  for x in Ven:
    vn = Venue.query.filter(Venue.city == x.city, Venue.state == x.state).all()
    for y in vn:
      v += [{
        "id": y.id,
        "name": y.name, 
      }]
    data +=[{
    "city": x.city,
    "state": x.state,
    "venues": v
    }]

    v =[]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  q = request.form['search_term']
  qres =  db.session.query(Venue).filter(Venue.name.ilike(f'%{q}%')).all()

  if qres:
    s_data = []

    for i in qres:
      s_data +=[{
      "id": i.id,
      "name": i.name,
      }]

    response={
      "count": len(qres),
      "data": s_data
    } 
  else:
    response={}
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  res = Venue.query.filter(Venue.id == venue_id).first()
  
  past = db.session.query(Artist, Shows).join(Shows).filter(Shows.venue_id==res.id, Shows.start_time<=datetime.now().strftime("%Y-%m-%d %H:%M:%S")).all()
  past_shows = []
    
  if past:
      for item, sh in past:
        past_shows +=[{
          "artist_id": item.id,
          "artist_name": item.name,
          "artist_image_link": item.image_link,
          "start_time": sh.start_time,
        }]
  
  upcoming = db.session.query(Artist, Shows).join(Shows).filter(Shows.venue_id==res.id, Shows.start_time>=datetime.now().strftime("%Y-%m-%d %H:%M:%S")).all()
  upcoming_shows = []
    
  if upcoming:
      for item, sh in upcoming:
        upcoming_shows +=[{
          "artist_id": item.id,
          "artist_name": item.name,
          "artist_image_link": item.image_link,
          "start_time": sh.start_time,
        }]
  data={
    "id": res.id,
    "name": res.name,
    "genres": [res.genres],
    "address": res.address,
    "city": res.city,
    "state": res.state,
    "phone": res.phone,
    "website": res.website_link,
    "facebook_link": res.facebook_link,
    "seeking_talent": res.seeking_talent,
    "seeking_description": res.seeking_description,
    "image_link": res.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
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
  #req = request.form
  form = VenueForm()
  #if form.validate_on_submit():
  if form.validate():
        try:
          '''newVenue= Venue(name= req['name'], 
                          genres=req.getlist('genres'),
                          address=req['address'],
                          city = req['city'],
                          state = req['state'],
                          phone=req['phone'], 
                          website_link = req['website_link'],
                          facebook_link = req['facebook_link'],
                          seeking_talent = bool(req.get('seeking_talent')),
                          seeking_description = req['seeking_description'],
                          image_link = req['image_link'],
                          )'''
          name = request.form.get('name') 
          city = request.form.get('city') 
          state = request.form.get('state') 
          phone = request.form.get('phone') 
          address = request.form.get('address') 
          genres = ",".join(request.form.get('genres')) 
          facebook_link = request.form.get('facebook_link') 
          website_link = request.form.get('website_link')  
          image_link = request.form.get('image_link') 
          seeking_description = request.form.get('seeking_description') 
          seeking_talent = request.form.get('seeking_talent')
        
          data = Venue(name=name, city=city, state=state,phone=phone, address=address, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website_link, seeking_talent=seeking_talent, seeking_description = seeking_description)
          db.session.add(data)
          db.session.commit()
          flash('Venue ' + request.form['name'] + ' was successfully listed!')

        except:
          db.session.rollback()
          flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed')
        finally:
          db.session.close()
  else:
        for field, message in form.errors.items():
          flash(field + ' - ' + str(message), 'danger')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Item = Venue.query.get(venue_id)
    Item.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  res = Artist.query.all()
  data =[]

  for item in res:
    data+=[{
    "id": item.id,
    "name": item.name,
    }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }

  q = request.form['search_term']
  qres =  db.session.query(Artist).filter(Artist.name.ilike(f'%{q}%')).all()

  if qres:
    s_data = []

    for i in qres:
      s_data +=[{
      "id": i.id,
      "name": i.name,
      }]

    response={
      "count": len(qres),
      "data": s_data
    } 
  else:
    response={}
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  res = Artist.query.filter(Artist.id == artist_id).first()

  past = db.session.query(Artist, Shows).join(Shows).filter(Shows.artist_id==res.id, Shows.start_time<=datetime.now().strftime("%Y-%m-%d %H:%M:%S")).all()
  past_shows = []
    
  if past:
      for item, sh in past:
        past_shows +=[{
          "artist_id": item.id,
          "artist_name": item.name,
          "artist_image_link": item.image_link,
          "start_time": sh.start_time,
        }]
  
  upcoming = db.session.query(Artist, Shows).join(Shows).filter(Shows.artist_id==res.id, Shows.start_time>=datetime.now().strftime("%Y-%m-%d %H:%M:%S")).all()
  upcoming_shows = []
    
  if upcoming:
      for item, sh in upcoming:
        upcoming_shows +=[{
          "artist_id": item.id,
          "artist_name": item.name,
          "artist_image_link": item.image_link,
          "start_time": sh.start_time,
        }]
  data={
    "id": res.id,
    "name": res.name,
    "genres": [res.genres],
    "city": res.city,
    "state": res.state,
    "phone": res.phone,
    "website": res.website_link,
    "facebook_link": res.facebook_link,
    "seeking_venue": res.seeking_venue,
    "seeking_description": res.seeking_description,
    "image_link": res.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter(Artist.id == artist_id).first()
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  item = Artist.query.get(artist_id)
  req = request.form
  item.name = req['name']
  item.phone = req['phone']
  item.city = req['city']
  item.state = req['state']
  item.genres = req.getlist('genres')
  item.facebook_link = req['facebook_link']
  item.image_link = req['image_link']
  item.website_link = req['website_link']
  item.seeking_venue = bool(req.get('seeking_venue'))
  item.seeking_description = req['seeking_description']
  db.session.commit()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter(Venue.id == venue_id).first()
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  item = Venue.query.get(venue_id)
  req = request.form
  ltn = Location.query.filter(Location.city == req['city'], Location.state == req['state'] ).first()
  item.name = req['name']
  item.phone = req['phone']
  item.location_id = ltn.id
  item.address = req['address']
  item.genres = req.getlist('genres')
  item.facebook_link = req['facebook_link']
  item.image_link = req['image_link']
  item.website_link = req['website_link']
  item.seeking_talent = bool(req.get('seeking_talent'))
  item.seeking_description = req['seeking_description']
  db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  req = request.form
  form = ArtistForm()
  if form.validate_on_submit():
    try:
      newArtist= Artist(name= req['name'], 
                      genres=req.getlist('genres'),
                      city = req['city'],
                      state = req['state'],
                      phone=req['phone'], 
                      website_link = req['website_link'],
                      facebook_link = req['facebook_link'],
                      seeking_venue = bool(req.get('seeking_talent')),
                      seeking_description = req['seeking_description'],
                      image_link = req['image_link'],
                      )
      db.session.add(newArtist)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + req['name'] + ' could not be listed')
    finally:
      db.session.close()
  else:
    for field, message in form.errors.items():
      flash(field + ' - ' + str(message), 'danger')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  res = db.session.query(Venue, Shows, Artist).select_from(Venue).join(Shows).join(Artist).all()

  data = []
  for venue, shows, artist in res: 
    data +=[{
    "venue_id": venue.id,
    "venue_name": venue.name,
    "artist_id": artist.id,
    "artist_name": artist.name,
    "artist_image_link": artist.image_link,
    "start_time": shows.start_time
  }]

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  req = request.form
  try:
    newShow = Shows(venue_id = req['venue_id'],
                artist_id = req['artist_id'], 
                start_time = req['start_time'] )
    db.session.add(newShow)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
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



# Specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)

# Default port:
#if __name__ == '__main__':
#    app.run()