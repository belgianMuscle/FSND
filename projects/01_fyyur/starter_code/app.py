#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database
db = SQLAlchemy(app)
migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    shows = db.relationship('Show',lazy=True,backref='venue')

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show',lazy=True,backref='artist')

class Show(db.Model):
      __tablename__ = 'Show'
      id = db.Column(db.Integer,primary_key=True)
      venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable=False)
      artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)
      start_time = db.Column(db.DateTime,nullable=False)

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
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO  num_shows should be aggregated based on number of upcoming shows per venue.
  venue_result = Venue.query.order_by('city','state','name').all()

  data = []
  grouping = { }

  previous_city_state = ''
  for venue in venue_result:
    current_city_state = venue.city + venue.state
    if current_city_state != previous_city_state:
      previous_city_state = current_city_state
      grouping = {
        'city':venue.city,
        'state':venue.state,
        'venues':[]
      }
      data.append(grouping)

    venue.shows = Show.query.with_parent(venue).filter(Show.start_time > datetime.today()).all()
    grouping['venues'].append({
      'id':venue.id,
      'name':venue.name,
      'num_shows':len(venue.shows)
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term=request.form.get('search_term', '')

  search_results = Venue.query.filter(func.lower(Venue.name).contains(func.lower(search_term))).all()

  response = {
    'count':len(search_results),
    'data':search_results
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  #convert the string from DB to a list to be interpreted by the view
  if venue:
    venue.genres = venue.genres.split(',')
  
  venue.shows = Show.query.with_parent(venue).all()
  
  venue.upcoming_shows_count = 0
  venue.upcoming_shows = []
  venue.past_shows_count = 0
  venue.past_shows = []
  for show in venue.shows:
    if show.start_time > datetime.today():
      venue.upcoming_shows_count += 1
      show.artist_id = show.artist.id
      show.artist_name = show.artist.name
      show.artist_image_link = show.artist.image_link
      show.start_time = show.start_time.strftime('%Y-%m-%dT%I:%M:%S.%sZ')
      venue.upcoming_shows.append(show)
    else:
      venue.past_shows_count += 1
      show.artist_id = show.artist.id
      show.artist_name = show.artist.name
      show.artist_image_link = show.artist.image_link
      show.start_time = show.start_time.strftime('%Y-%m-%dT%I:%M:%S.%sZ')
      venue.past_shows.append(show)

  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  #get the form data in object 
  form = VenueForm(request.form)

  #create data dict for easier manipulation
  data = {
    'name':form.name.data,
    'image_link':form.image_link.data,
    'city':form.city.data,
    'state':form.state.data,
    'address':form.address.data,
    'phone':form.phone.data,
    'genres':','.join(form.genres.data),
    'seeking_talent':form.seeking_talent.data,
    'seeking_description':form.seeking_description.data,
    'website':form.website.data,
    'facebook_link':form.facebook_link.data
  }
  
  try:
    #create Venue from data
    venue = Venue(**data)
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + venue.name + ' was successfully listed!')
  except:
    db.session.rollback()
    # on unsuccessful db insert, flash an error instead.
    # showing data from the form in case the creation of the Venue object failed
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False

  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  
  if error:
    abort(500)
  else:
    return jsonify({'success':True})


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  # populate form with values from venue with ID <venue_id>
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.image_link.data = venue.image_link
  form.genres.data = venue.genres.split(',')
  form.website.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  #get filled in form
  form = VenueForm(request.form)

  #create data dict for easier manipulation
  data = {
    'name':form.name.data,
    'image_link':form.image_link.data,
    'city':form.city.data,
    'state':form.state.data,
    'address':form.address.data,
    'phone':form.phone.data,
    'genres':','.join(form.genres.data),
    'seeking_talent':form.seeking_talent.data,
    'seeking_description':form.seeking_description.data,
    'website':form.website.data,
    'facebook_link':form.facebook_link.data
  }

  try:
    #get the venue
    venue = Venue.query.get(venue_id)
    #update venue fields
    venue.name = data['name']
    venue.image_link = data['image_link']
    venue.city = data['city']
    venue.state = data['state']
    venue.address = data['address']
    venue.phone = data['phone']
    venue.genres = data['genres']
    venue.seeking_talent = data['seeking_talent']
    venue.seeking_description = data['seeking_description']
    venue.website = data['website']
    venue.facebook_link = data['facebook_link']
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []

  artists = Artist.query.all()

  for artist in artists:
    data.append({
      'id':artist.id,
      'name':artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term=request.form.get('search_term', '')

  search_results = Artist.query.filter(func.lower(Artist.name).contains(func.lower(search_term))).all()

  response = {
    'count':len(search_results),
    'data':search_results
  }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  if artist:
    artist.genres = artist.genres.split(',')

  artist.shows = Show.query.with_parent(artist).all()
  
  artist.upcoming_shows_count = 0
  artist.upcoming_shows = []
  artist.past_shows_count = 0
  artist.past_shows = []
  for show in artist.shows:
    if show.start_time > datetime.today():
      artist.upcoming_shows_count += 1
      show.venue_id = show.venue.id
      show.venue_name = show.venue.name
      show.venue_image_link = show.venue.image_link
      show.start_time = show.start_time.strftime('%Y-%m-%dT%I:%M:%S.%sZ')
      artist.upcoming_shows.append(show)
    else:
      artist.past_shows_count += 1
      show.venue_id = show.venue.id
      show.venue_name = show.venue.name
      show.venue_image_link = show.venue.image_link
      show.start_time = show.start_time.strftime('%Y-%m-%dT%I:%M:%S.%sZ')
      artist.past_shows.append(show)

  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  artist = Artist.query.get(artist_id)
  if artist:
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres.split(',')
    form.image_link.data = artist.image_link
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    form.website.data = artist.website

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  form = ArtistForm(request.form)
  #create data dict for easier manipulation
  data = {
    'name':form.name.data,
    'image_link':form.image_link.data,
    'city':form.city.data,
    'state':form.state.data,
    'phone':form.phone.data,
    'genres':','.join(form.genres.data),
    'seeking_venue':form.seeking_venue.data,
    'seeking_description':form.seeking_description.data,
    'website':form.website.data,
    'facebook_link':form.facebook_link.data
  }

  try:
    artist = Artist.query.get(artist_id)
    artist.name = data['name']
    artist.image_link = data['image_link']
    artist.city = data['city']
    artist.state = data['state']
    artist.phone = data['phone']
    artist.genres = data['genres']
    artist.seeking_venue = data['seeking_venue']
    artist.seeking_description = data['seeking_description']
    artist.website = data['website']
    artist.facebook_link = data['facebook_link']
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close() 

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  error = False    

  try:
      artist = Artist.query.get(artist_id)
      db.session.delete(artist)
      db.session.commit()
  except:
      db.session.rollback()
  finally:
      db.session.close()
  
  if error:
    abort(500)
  else:
    return jsonify({'success':True}) 

#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  form = ArtistForm(request.form)

  data = {
    'name':form.name.data,
    'image_link':form.image_link.data,
    'city':form.city.data,
    'state':form.state.data,
    'phone':form.phone.data,
    'genres':','.join(form.genres.data),
    'seeking_venue':form.seeking_venue.data,
    'seeking_description':form.seeking_description.data,
    'website':form.website.data,
    'facebook_link':form.facebook_link.data
  }

  try:
    artist = Artist(**data)
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + artist.name + ' was successfully listed!')
  except:
    db.session.rollback()
    # on unsuccessful db insert, flash an error instead.
    # showing data from the form in case the creation of the Venue object failed
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.order_by(Show.start_time).all()

  for show in shows:
    show.venue_name = show.venue.name
    show.artist_name = show.artist.name
    show.artist_image_link = show.artist.image_link
    show.start_time = show.start_time.strftime('%Y-%m-%dT%I:%M:%S.%sZ')

  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  form = ShowForm(request.form)

  try:
    show = Show(venue_id=form.venue_id.data,
    artist_id=form.artist_id.data,
    start_time=form.start_time.data)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

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
