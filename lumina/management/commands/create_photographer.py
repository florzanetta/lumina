import random
import datetime
import decimal

from django.core.management.base import BaseCommand, CommandError

from lumina.models import LuminaUser, Studio


class Command(BaseCommand):
    args = '<username>'
    help = 'Creates a photographer'

    def handle(self, *the_args, **options):
        if len(the_args) != 1:
            raise CommandError("You must specify <username> for the photographer")

        username = the_args[0]

        studio = Studio.objects.create(name='Studio of {}'.format(username),
                                       default_terms='Terms and conditions (...)')

        user = LuminaUser.objects.create(username=username,
                                         email="{}@example.com".format(username),
                                         user_type=LuminaUser.PHOTOGRAPHER,
                                         studio=studio,
                                         user_for_customer=None,
                                         phone=None,
                                         cellphone=None,
                                         alternative_email=None,
                                         notes=None)

        photographer = LuminaUser.objects.get(username=username)
        assert photographer.is_photographer()

        user.set_password(username)
        user.save()

        self.stdout.write("Photographer created: {}".format(photographer.id))
