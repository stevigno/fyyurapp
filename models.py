from app import db

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String()))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(250))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(300))
    show = db.relationship('Show', backref='Artist', lazy=True)

    def __repr__(self):
      return f'<Venue: {self.id}, name: {self.name}, genres: {self.genres}, city: {self.city}, show: {self.show}>'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(250))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(300))
    show = db.relationship('Show', backref='Venue', lazy=True)

    def __repr__(self):
        return f'<Artist: {self.id}, name: {self.name}, genres: {self.genres}, city: {self.city}, show: {self.show}>'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

    def __repr__(self):
        return f'<Show: {self.id}, artist_id: {self.artist_id}, venue_id {self.venue_id}, start_time: {self.start_time}>'


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
