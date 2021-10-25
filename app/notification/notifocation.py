import yagmail

yagmail.register(username='price.monitoring.dev@gmail.com', password='ihj5DTw9K6XWmQM')


class Notification:

    @classmethod
    def notify_to_email(cls, message, email_address):
        try:
            cls._send_email_with_yagmail(content=message, receiver=email_address)
        except:
            return False
        return True


    @classmethod
    def _send_email_with_yagmail(cls, content, receiver):
        yag_connection = yagmail.SMTP('price.monitoring.dev@gmail.com')
        yag_connection.send(
            to=receiver,
            subject='Price Tracking',
            contents=content
        )