#!/usr/bin/env python3

import os
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import Hero, HeroPower, Power, db

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Index(Resource):
    def get(self):
        return "<h1>Code Challenge</h1>"

class HeroList(Resource):
    def get(self):
        heroes = Hero.query.all()
        return jsonify([hero.to_dict(rules=("-hero_powers",)) for hero in heroes]), 200

class HeroDetail(Resource):
    def get(self, id):
        hero = Hero.query.get(id)
        if not hero:
            return jsonify({"error": "Hero not found"}), 404
        return jsonify(hero.to_dict()), 200

class PowerList(Resource):
    def get(self):
        powers = Power.query.all()
        return jsonify([power.to_dict(rules=("-hero_powers", "-heroes")) for power in powers]), 200

class PowerDetail(Resource):
    def get(self, id):
        power = Power.query.get(id)
        if not power:
            return jsonify({"error": "Power not found"}), 404
        return jsonify(power.to_dict(rules=("-hero_powers", "-heroes"))), 200

    def patch(self, id):
        power = Power.query.get(id)
        if not power:
            return jsonify({"error": "Power not found"}), 404
        
        data = request.get_json()
        description = data.get("description", "")
        
        if len(description) < 20:
            return jsonify({"errors": ["Description must be at least 20 characters long"]}), 400
        
        power.description = description
        db.session.commit()
        return jsonify(power.to_dict()), 200

class HeroPowerCreate(Resource):
    def post(self):
        data = request.get_json()
        strength = data.get("strength")
        hero_id = data.get("hero_id")
        power_id = data.get("power_id")

        if strength not in ["Strong", "Weak", "Average"]:
            return jsonify({"errors": ["Strength must be 'Strong', 'Weak', or 'Average'"]}), 400
        
        hero = Hero.query.get(hero_id)
        power = Power.query.get(power_id)
        
        if not hero or not power:
            return jsonify({"error": "Hero or Power not found"}), 404

        hero_power = HeroPower(strength=strength, hero_id=hero_id, power_id=power_id)
        db.session.add(hero_power)
        db.session.commit()

        return jsonify(hero_power.to_dict()), 201

api.add_resource(Index, '/')
api.add_resource(HeroList, '/heroes')
api.add_resource(HeroDetail, '/heroes/<int:id>')
api.add_resource(PowerList, '/powers')
api.add_resource(PowerDetail, '/powers/<int:id>')
api.add_resource(HeroPowerCreate, '/hero_powers')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
