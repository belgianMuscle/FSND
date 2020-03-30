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
from datetime import datetime, timedelta
from logging import Formatter, FileHandler
from flask_wtf import Form, CSRFProtect
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

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
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    shows = db.relationship('Show', lazy=True, cascade="all, delete-orphan", backref='venue')


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
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    available_from = db.Column(db.DateTime, nullable=False)
    available_to = db.Column(db.DateTime, nullable=False)
    shows = db.relationship('Show', lazy=True, cascade="all, delete-orphan", backref='artist')
    albums = db.relationship('Album',lazy=True, cascade="all, delete-orphan", backref='artist')

class Album(db.Model):
    __tablename__ = 'Album'
    id = db.Column(db.Integer,primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    title = db.Column(db.String(120),nullable=False)
    songs = db.Column(db.String(500),nullable=False)

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():

    home_data = {
        'has_recently_listed': False,
        'recent_venues': [],
        'recent_artists': []
    }

    home_data['recent_venues'] = Venue.query.limit(10).all()
    home_data['recent_artists'] = Artist.query.limit(10).all()
    if len(home_data['recent_venues']) > 0 or len(home_data['recent_artists']) > 0:
        home_data['has_recently_listed'] = True

    return render_template('pages/home.html', data=home_data)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    venue_result = Venue.query.order_by('city', 'state', 'name').all()

    data = []
    grouping = {}

    previous_city_state = ''
    for venue in venue_result:
        current_city_state = venue.city + venue.state
        if current_city_state != previous_city_state:
            previous_city_state = current_city_state
            grouping = {
                'city': venue.city,
                'state': venue.state,
                'venues': []
            }
            data.append(grouping)

        venue.shows = Show.query.with_parent(venue).filter(
            Show.start_time > datetime.today()).all()
        grouping['venues'].append({
            'id': venue.id,
            'name': venue.name,
            'num_shows': len(venue.shows)
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')

    search_results = Venue.query.filter(func.lower(
        Venue.name).contains(func.lower(search_term))).all()

    response = {
        'count': len(search_results),
        'data': search_results
    }

    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    # convert the string from DB to a list to be interpreted by the view
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
    # get the form data in object
    form = VenueForm(request.form)

    # create data dict for easier manipulation
    data = {
        'name': form.name.data,
        'image_link': form.image_link.data,
        'city': form.city.data,
        'state': form.state.data,
        'address': form.address.data,
        'phone': form.phone.data,
        'genres': ','.join(form.genres.data),
        'seeking_talent': form.seeking_talent.data,
        'seeking_description': form.seeking_description.data,
        'website': form.website.data,
        'facebook_link': form.facebook_link.data
    }

    if form.validate():
        try:
            # create Venue from data
            venue = Venue(**data)
            db.session.add(venue)
            db.session.commit()
            # on successful db insert, flash success
            flash('Venue ' + venue.name + ' was successfully listed!')
        except:
            db.session.rollback()
            # on unsuccessful db insert, flash an error instead.
            # showing data from the form in case the creation of the Venue object failed
            flash('An error occurred. Venue ' +
                  request.form['name'] + ' could not be listed.')
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
        return jsonify({'success': True})


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    # populate form with values from venue with ID <venue_id>
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.image_link.data = venue.image_link
    form.genres.data = venue.genres.split(',')
    form.website.data = venue.website
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # get filled in form
    form = VenueForm(request.form)

    # create data dict for easier manipulation
    data = {
        'name': form.name.data,
        'image_link': form.image_link.data,
        'city': form.city.data,
        'state': form.state.data,
        'address': form.address.data,
        'phone': form.phone.data,
        'genres': ','.join(form.genres.data),
        'seeking_talent': form.seeking_talent.data,
        'seeking_description': form.seeking_description.data,
        'website': form.website.data,
        'facebook_link': form.facebook_link.data
    }

    if form.validate():
        try:
            # get the venue
            venue = Venue.query.get(venue_id)
            # update venue fields
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
            'id': artist.id,
            'name': artist.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')

    search_results = Artist.query.filter(func.lower(
        Artist.name).contains(func.lower(search_term))).all()

    response = {
        'count': len(search_results),
        'data': search_results
    }

    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if artist:
        artist.genres = artist.genres.split(',')

    artist.shows = Show.query.with_parent(artist).all()
    if artist.available_from:
        artist.available_from = artist.available_from.strftime(
            '%Y-%m-%dT%I:%M:%S.%sZ')
    if artist.available_to:
        artist.available_to = artist.available_to.strftime(
            '%Y-%m-%dT%I:%M:%S.%sZ')

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

    artist.albums = Album.query.with_parent(artist).all()

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
        if artist.available_to:
            form.available_to.data = artist.available_to
        if artist.available_from:
            form.available_from.data = artist.available_from
        form.website.data = artist.website

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    form = ArtistForm(request.form)
    # create data dict for easier manipulation
    data = {
        'name': form.name.data,
        'image_link': form.image_link.data,
        'city': form.city.data,
        'state': form.state.data,
        'phone': form.phone.data,
        'genres': ','.join(form.genres.data),
        'seeking_venue': form.seeking_venue.data,
        'seeking_description': form.seeking_description.data,
        'available_from': form.available_from.data,
        'available_to': form.available_to.data,
        'website': form.website.data,
        'facebook_link': form.facebook_link.data
    }

    if form.validate():
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
            artist.available_from = data['available_from']
            artist.available_to = data['available_to']
            artist.facebook_link = data['facebook_link']
            db.session.commit()
        except:
            error = True
            db.session.rollback()
        finally:
            db.session.close()

    if error:
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    else:
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
        return jsonify({'success': True})

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
        'name': form.name.data,
        'image_link': form.image_link.data,
        'city': form.city.data,
        'state': form.state.data,
        'phone': form.phone.data,
        'genres': ','.join(form.genres.data),
        'seeking_venue': form.seeking_venue.data,
        'seeking_description': form.seeking_description.data,
        'available_from': form.available_from.data,
        'available_to': form.available_to.data,
        'website': form.website.data,
        'facebook_link': form.facebook_link.data
    }

    if form.validate():
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
            flash('An error occurred. Artist ' +
                  request.form['name'] + ' could not be listed.')
        finally:
            db.session.close()
        return render_template('pages/home.html')
    else:
        flash('Please review the form!')
        print(form.errors)
        return render_template('forms/new_artist.html', form=form)


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

@app.route('/artists/<artist_id>/add_album')
def add_album(artist_id):
    form = AlbumForm()
    return render_template('forms/new_album.html', form=form)

@app.route('/artists/<artist_id>/add_album', methods=['POST'])
def add_album_submission(artist_id):
    form = AlbumForm(request.form)
    error = False

    if form.validate():
        try:
            album = Album(artist_id=artist_id,
                        title=form.title.data,
                        songs=form.songs.data)
            db.session.add(album)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
        finally:
            db.session.close()
    else:
        error = True

    if error:
        return render_template('forms/new_album.html', form=form)
    else:
        return redirect(url_for('show_artist', artist_id=artist_id))



@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    form = ShowForm(request.form)
    error = False

    if form.validate():
        artist = Artist.query.get(form.artist_id.data)
        venue = Venue.query.get(form.venue_id.data)

        if not artist:
            flash('The provided artist does not exist!')
            error = True
        else:
            if artist.available_from and artist.available_to:
                if form.start_time.data > artist.available_to or form.start_time.data < artist.available_from:
                    error = True
                    flash('The artist is not available at this time!')

        if not venue:
            flash('The provided venue does not exist!')
            error = True

        if error:
            return render_template('forms/new_show.html', form=form)
        else:
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

            return redirect(url_for('index'))
    else:
        return render_template('forms/new_show.html', form=form)



@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
