import random
import datetime
import decimal

from django.core.management.base import BaseCommand, CommandError

from lumina.models import LuminaUser, SessionQuote, SessionQuoteAlternative


class Command(BaseCommand):
    args = '<photographer_id>'
    help = 'Generates random data'

    def handle(self, *the_args, **options):
        if len(the_args) == 0:
            for ph in LuminaUser.objects.filter(user_type=LuminaUser.PHOTOGRAPHER).order_by('id'):
                self.stdout.write("{} - {}".format(ph.id, str(ph)))
            raise(CommandError("You must specify a User id"))

        photographer = LuminaUser.objects.get(pk=int(the_args[0]))
        assert photographer.is_photographer()

        customer = random.choice(photographer.studio.customers.all())
        today = datetime.date.today()
        cost = random.randint(500, 5000)
        stipulated_date = datetime.datetime(today.year, random.randint(1, 12),
            random.randint(1, 28))
        image_quantity = random.randint(1, 50) * 5

        quote = SessionQuote.objects.create(studio=photographer.studio,
            customer=customer,
            image_quantity=image_quantity,
            cost=cost,
            stipulated_date=stipulated_date,
            stipulated_down_payment=0.0)

        quote.confirm(photographer)

        sqa = SessionQuoteAlternative.objects.create(session_quote=quote,
            image_quantity=int(image_quantity * 1.5),
            cost=decimal.Decimal(int(cost * 1.2)))

        if random.randint(0, 3) == 0:
            quote.accept(customer.users.all()[0], (sqa.image_quantity, sqa.cost))
