from app import app, db
from datetime import datetime

class Item(db.Model):
    """
    Item model description
    """
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    item_url = db.Column(db.String, nullable=False)
    current_price = db.Column(db.Float)
    html_attrs = db.Column(db.String)
    min_desired_price = db.Column(db.Float, nullable=True)
    max_allowable_price = db.Column(db.Float, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))

    def __repr__(self):
        return f'<{self.id}: {self.title} - {self.current_price}>'


class ItemPriceHistory(db.Model):
    __tablename__ = 'items_price_history'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete="CASCADE"))
    price = db.Column(db.Float)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'Item #{self.item_id}. Last price - {self.price} ({self.update_datetime})'
