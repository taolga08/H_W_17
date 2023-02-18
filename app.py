# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


movie_schema = MovieSchema()

api = Api(app)
movie_ns = api.namespace('movies')


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        req_id = Movie.query
        if director_id:
            req_id = req_id.filter(Movie.director_id == director_id)
        if genre_id:
            req_id = req_id.filter(Movie.genre_id == genre_id)
        movies = req_id.all()
        return movie_schema.dump(movies, many=True), 200

    def post(self):
        movie_data = request.json
        new_movie = Movie(**movie_data)
        db.session.add(new_movie)
        db.session.commit()
        return "", 201


@movie_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid: int):
        movie = Movie.query.get(mid)
        return movie_schema.dump(movie), 200

    def put(self, mid: int):
        movie = Movie.query.get(mid)
        if not movie:
            return '', 404
        movie_data = request.json
        movie.title = movie_data.get('title')
        movie.description = movie_data.get('description')
        movie.trailer = movie_data.get('trailer')
        movie.year = movie_data.get('year')
        movie.rating = movie_data.get('rating')
        movie.genre_id = movie_data.get('genre_id')
        movie.director_id = movie_data.get('director_id')

        db.session.add(movie)
        db.session.commit()
        return '', 204

    def delete(self, mid: int):
        movie = Movie.query.get(mid)
        if not movie:
            return '', 404
        db.session.delete(movie)
        db.session.commit()
        return '', 204


if __name__ == '__main__':
    app.run(debug=True)
