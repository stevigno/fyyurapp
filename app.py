#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
from wsgiref import validate
from wsgiref.validate import validator
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import func
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import *
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

 # https://docs.sqlalchemy.org/en/14/orm/extensions/orderinglist.html?highlight=append#sqlalchemy.ext.orderinglist.OrderingList.append
 # https://docs.sqlalchemy.org/en/14/orm/query.html?highlight=join#sqlalchemy.orm.Query.join
 # https://docs.sqlalchemy.org/en/14/orm/query.html?highlight=with_entities#sqlalchemy.orm.Query.with_entities
  all = Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state, Venue.name).outerjoin(Show, Venue.id == Show.venue_id).group_by(Venue.city, Venue.state, Venue.name).all()
  data = []
  for a in all:
    area_venues = Venue.query.filter_by(state=a.state).filter_by(city=a.city).all()
    all_data = []
    num_up = len(Show.query.filter(Show.venue_id==1).filter(Show.start_time>datetime.now()).all())
    for venue in area_venues:
      all_data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_up
      })
    data.append({
      "city": a.city,
      "state": a.state, 
      "venues": all_data
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  try:
  
    term = request.form.get('search_term', '')
    search = Venue.query.filter(Venue.name.ilike(f'%{term}%')).all()
    data = []
    if len(search) > 0 :
      for final in search:
          data.append({
            "id": final.id,
            "name": final.name,
            "num_upcoming_shows": len(final.show)
          })
      
      response={
        "count": len(search),
        "data": data
      }
    else:
      flash(f'An error occured, could not search with {term} was not exist!') 
      return render_template('pages/home.html')

  except:
    print(sys.exc_info())

  return render_template('pages/search_venues.html', results=response, search_term=term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id

  # https://docs.sqlalchemy.org/en/14/orm/query.html?highlight=join#sqlalchemy.orm.Query.join
  ve = Venue.query.get(venue_id)
  venue = Show.query.join(Artist).filter(Show.venue_id == venue_id).all()
  
  past_shows = []
  for a in venue :
    if a.start_time <= datetime.now():
      past_shows.append({
        'artist_id': a.artist_id,
        'artist_name':a.Artist.name,
        'artist_image_link':a.Artist.image_link,
        'start_time':a.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })

  upcoming_shows = []
  for b in venue:
    if b.start_time >= datetime.now():
      upcoming_shows.append({
        'artist_id': b.artist_id,
        'artist_name':b.Artist.name,
        'artist_image_link':b.Artist.image_link,
        'start_time':b.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })

  data = {
    "id": ve.id,
    "name": ve.name,
    "address": ve.address,
    "city": ve.city,
    "state": ve.state,
    "phone": ve.phone,
    "image_link": ve.image_link,
    "genres": ve.genres,
    "website_link": ve.website_link,
    "facebook_link": ve.facebook_link,
    "seeking_talent": ve.seeking_talent,
    "seeking_description": ve.seeking_description,
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
  #https://wtforms.readthedocs.io/en/3.0.x/crash_course/
  form =  VenueForm(request.form)

  # vérifie si la (venue.name) existe déja dans la base de donnée.
  verify = Venue.query.filter( Venue.name.ilike(f'%{form.name.data}%')).all()
  try:
    if request.method == 'POST' and len(verify) > 0:
      flash('Venue name ' + request.form['name'] +' already exists!')
      return render_template('forms/new_venue.html', form=form)
    else:  

      venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data
      )
    db.session.add(venue)
    db.session.commit()
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close() 
  return render_template('pages/home.html')
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # https://docs.sqlalchemy.org/en/20/orm/query.html?highlight=delete#sqlalchemy.orm.Query.delete
  # https://video.udacity-data.com/topher/2019/August/5d5fc44f_todoapp-updates-deletes/todoapp-updates-deletes.zip
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue: was successfully deleted!')
  except:
    print(sys.exc_info())
    flash('Venue: was not successfully deleted!')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  data1=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  try:
    term = request.form.get('search_term', '')
    search = Artist.query.filter(Artist.name.ilike(f'%{term}%')).all()
    data = []
    if len(search) > 0:
      for final in search:
          data.append({
            "id": final.id,
            "name": final.name,
            "num_upcoming_shows": len(final.show)
          })
      
      response={
        "count": len(search),
        "data": data
      }
    else:
      flash(f'An error occured, could not search with {term} was not exist!') 
      return render_template('pages/home.html')  
  except:
    print(sys.exc_info())

  return render_template('pages/search_artists.html', results=response, search_term=term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  Artistget = Artist.query.get(artist_id)
  artiste = Show.query.join(Venue).filter(Show.artist_id==artist_id).all()
  past_shows = []
  upcoming_shows = []

  for past in artiste:
    if past.start_time >= datetime.now():
      upcoming_shows.append({
        "venue_id": past.venue_id,
        "venue_name": past.Venue.name,
        "venue_image_link": past.Venue.image_link,
        "start_time": past.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
    else:
      past_shows.append({
        "venue_id": past.venue_id,
        "venue_name": past.Venue.name,
        "venue_image_link": past.Venue.image_link,
        "start_time": past.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })

  data = {
    "id": Artistget.id,
    "name": Artistget.name,
    "genres": Artistget.genres,
    "city": Artistget.city,
    "state": Artistget.state,
    "phone": Artistget.phone,
    "website_link": Artistget.website_link,
    "facebook_link": Artistget.facebook_link,
    "seeking_venue": Artistget.seeking_venue,
    "seeking_description": Artistget.seeking_description,
    "image_link": Artistget.image_link,
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
  error = False
  try:
      artist =  Artist.query.get(artist_id)

      form.name.data = artist.name
      form.city.data = artist.city
      form.state.data = artist.state
      form.phone.data = artist.phone
      form.genres.data = artist.genres
      form.image_link.data = artist.image_link
      form.facebook_link.data = artist.facebook_link
      form.website_link.data = artist.website_link
      form.seeking_venue.data = artist.seeking_venue
      form.seeking_description.data = artist.seeking_description
  except:  
    flash('Artist was not successfully loaded!')
    error = True
    print(sys.exc_info())  
   # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)

  try:
    artist = Artist.query.get(artist_id)

    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.image_link = form.image_link.data
    artist.facebook_link = form.facebook_link.data
    artist.website_link = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data

    db.session.commit()
    flash('Artist was successfully edited!')
  except:
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  error = False
  try:
      venue =  Venue.query.get(venue_id)

      form.name.data = venue.name
      form.city.data = venue.city
      form.address.data = venue.address
      form.state.data = venue.state
      form.phone.data = venue.phone
      form.genres.data = venue.genres
      form.image_link.data = venue.image_link
      form.facebook_link.data = venue.facebook_link
      form.website_link.data = venue.website_link
      form.seeking_talent.data = venue.seeking_talent
      form.seeking_description.data = venue.seeking_description
  except:  
    flash('Venue was not successfully loaded!')
    error = True
    print(sys.exc_info())

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form =  VenueForm(request.form)

  try:
    venue = Venue.query.get(venue_id)

    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.image_link = form.image_link.data
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data
    venue.website_link = form.website_link.data
    venue.seeking_description = form.seeking_description.data

    db.session.commit()
    flash('Venue was successfully modified')
  except:
    error=True
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  # verifie l'existence de l'artiste dans la base de données
  verify = Artist.query.filter(Artist.name.ilike(f'%{form.name.data}%')).all()
  try:
    if request.method == 'POST' and len(verify) > 0:
      flash('Artist name ' + request.form['name'] + ' already exists!')
      return render_template('forms/new_artist.html', form=form)
    else:  

      artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data
      )
    db.session.add(artist)
    db.session.commit()  
  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except :
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  all_show = Show.query.join(Artist).join(Venue).filter(Venue.name != None).filter(Artist.name != None).all()
  data = []

  for show in all_show:
    data.append({
      'venue_id': show.venue_id,
      'venue_name': show.Venue.name,
      'artist_id': show.artist_id,
      'artist_name': show.Artist.name, 
      'artist_image_link': show.Artist.image_link,
      'start_time': show.start_time.strftime('%Y-%m-%dT%H:%M:%S')
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  try:
      show = Show(
          artist_id=form.artist_id.data,
          venue_id=form.venue_id.data,
          start_time=form.start_time.data
          )
      db.session.add(show)
      db.session.commit()
       # on successful db insert, flash success
      flash('Show was successfully listed!')
  except :
      error = True
      db.session.rollback()
      print(sys.exc_info())
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
