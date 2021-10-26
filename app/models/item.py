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
    price_updates = db.relationship('ItemPriceHistory', lazy='dynamic', order_by='ItemPriceHistory.date_updated.desc()')
    folder_id = db.Column(db.Integer, db.ForeignKey('items_folders.id', ondelete='CASCADE'), nullable=True)

    def __repr__(self):
        return f'<{self.id}: {self.title} - {self.current_price}>'


class ItemPriceHistory(db.Model):
    __tablename__ = 'items_price_history'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete="CASCADE"))
    price = db.Column(db.Float)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'Item #{self.item_id}. Last price - {self.price} ({self.date_updated})'


class ItemsFolder(db.Model):
    __tablename__ = 'items_folders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    items = db.relationship('Item', lazy=True)

    def __repr__(self):
        return f'"{self.title}" by User-{self.user_id}'