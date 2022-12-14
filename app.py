# app.py

from flask import Flask, request,jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from flask_restx import Api, Resource
from create_data import data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('director')
genre_ns = api.namespace('genre')


with db.session.begin():
    db.session.commit()

class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()

@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        all_movie = db.session.query(Movie)
        movie_schema = MovieSchema(many=True)
        director_id = request.args.get('director_id')
        if director_id is not None:
            all_movie = all_movie.filter(Movie.director_id == director_id)

        genre_id = request.args.get('genre_id')
        if genre_id is not None:
            all_movie = all_movie.filter(Movie.genre_id == genre_id)

        return movie_schema.dump(all_movie), 200

    def post(self):
        req_j = request.json
        add_db = Movie(**req_j)
        db.session.add(add_db)
        db.session.commit()
        return '', 204

@movie_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid: int):
        movie_schema = MovieSchema()
        all_movie = db.session.query(Movie).get(uid)
        return movie_schema.dump(all_movie), 200

    def put(self, uid: int):
        update_movie = db.session.query(Movie).filter(Movie.id == uid).update(request.json)
        if update_movie != 1:
            return '', 404
        db.session.commit()
        return '', 204

    def patch(self, uid:int):
        update_column = db.session.query(Movie).filter(Movie.id == uid).update(request.json)
        db.session.commit()
        return '', 204

    def delete(self, uid:int):
        del_movie = db.session.query(Movie).get(uid)
        db.session.delete(del_movie)
        db.session.commit()
        return '', 204

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


@director_ns.route('/')
class DirectorView(Resource):

    def get(self):
        director_schema = DirectorSchema(many=True)
        director = db.session.query(Director)
        return director_schema.dump(director), 200
    def post(self):
        req_j = request.json
        director = Director(**req_j)
        db.session.add(director)
        db.session.commit()
        return '', 204

class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


@genre_ns.route('/')
class GenreView(Resource):

    def get(self):
        genre = db.session.query(Genre)
        genre_schema = GenreSchema(many=True)
        return genre_schema.dump(genre), 200

    def post(self):
        reg_j = request.json
        add_genre = Genre(**reg_j)
        db.session.add(add_genre)
        db.session.commit()
        return '', 204

if __name__ == '__main__':
    app.run(debug=True)
