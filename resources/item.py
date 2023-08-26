from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError

from db import db
from schemas import ItemSchema, ItemUpdateSchema
from models import ItemModel


blp = Blueprint("Items", __name__, "Operations on items")


@blp.route("/item/<int:item_id>")
class Item(MethodView):
    @jwt_required()
    @blp.response(200, schema=ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required()
    def delete(self, item_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin priviledge required.")
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted."}

    @jwt_required()
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, schema=ItemSchema)
    def put(self, item_data, item_id):
        item = ItemModel.query.get(item_id)
        if item:
            item.name = item_data["name"]
            item.price = item_data["price"]
        else:
            item = ItemModel(id=item_id, **item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while updating the item")

        return item


@blp.route("/item")
class ItemList(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(ItemSchema)
    @blp.response(201, schema=ItemSchema)
    def post(self, item_data):
        item = ItemModel(**item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the item")

        return item

    @jwt_required()
    @blp.response(200, schema=ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()
