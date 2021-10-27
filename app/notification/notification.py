import yagmail

from app import app


yagmail.register(username=app.config['MAIL_USERNAME'], password=app.config['MAIL_PASSWORD'])


class Notification:
    _RESET_PASSWORD_MESSAGE = "To reset your password, follow the link\n"

    @classmethod
    def notify_to_email(cls, message: str, email_address: str):
        """
        Send an email with subject 'Price Tracking'

        :param message: A email content.
        :param email_address: A receiver email address.
        :return: True if an email is sent, else - False
        """
        try:
            cls._send_email_with_yagmail(content=message, receiver=email_address, subject='Price Tracking')
        except:
            return False
        return True

    @classmethod
    def send_password_reset_instructions(cls, email_address: str, reset_link: str):
        """
        Send an email with password reset link. Subject - 'Reset Password'
        :param email_address: A receiver email address.
        :param reset_link: A password reset link.
        :return: True if an email is sent, else - False
        """
        content = "To reset your password, follow the link\n" \
                  f"{reset_link}"
        try:
            cls._send_email_with_yagmail(content=content, receiver=email_address, subject='Reset Password')
        except:
            return False
        return True

    @staticmethod
    def _send_email_with_yagmail(content, receiver, subject):
        yag_connection = yagmail.SMTP(app.config['MAIL_USERNAME'])
        yag_connection.send(
            to=receiver,
            subject=subject,
            contents=content
        )