from sportloto import settings
from mailchimp3 import MailChimp


class AppMailchimp():
    instance = None

    @classmethod
    def get_instance(cls):
        """
        :rtype: MailChimp
        """

        if cls.instance == None:
            cls.instance = MailChimp(settings.MAILCHIMP_LOGIN, settings.MAILCHIMP_API_KEY)

        return cls.instance
