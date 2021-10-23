from app.models import User, Item


class Notification:
    @classmethod
    def notify_about_price_changing(cls, user: User, item: Item):
        print(f'Sending a notification to {user} about {item}. The price has changed.')

    @classmethod
    def notify_about_allowable_price(cls, user: User, item: Item):
        print(f'Sending a notification to {user} about {item}. '
              f'The price of the acceptable maximum. You will no longer receive a price alert.')

    @classmethod
    def notify_about_desired_price(cls, user: User, item: Item):
        print(f'Sending a notification to {user} about {item}. The price has reached the desired mark.')

