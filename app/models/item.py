from app import db

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<{self.title} - {self.current_price}>'
