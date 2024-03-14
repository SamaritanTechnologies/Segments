from django.conf import settings
from django.core.mail import EmailMessage


class EmailService(object):

    def send_email_with_attachment(self, recipient_email, attachment_content, attachment_filename,
                                   attachment_content_type):
        """
        Sends an email with attachment to the specified recipient.
        """
        email = EmailMessage(
            subject="Your Results",
            body=None,
            from_email=settings.EMAIL_HOST_USER,
            to=[recipient_email],
        )
        email.attach(attachment_filename, attachment_content.getvalue(), attachment_content_type)
        email.send()
