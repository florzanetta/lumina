import random
import datetime
import decimal
import uuid

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from lumina import models


class Command(BaseCommand):
    args = '<photographer_id_or_username> <number_of_inserts>'
    help = 'Generates random data'

    WORDS = None

    def gen_name(self):
        if not self.WORDS:
            try:
                word_file = "/usr/share/dict/spanish"
                self.WORDS = open(word_file).read().splitlines()
            except:
                pass

        if self.WORDS:
            return " ".join([random.choice(self.WORDS), random.choice(self.WORDS), random.choice(self.WORDS)])
        else:
            return str(uuid.uuid4())

    def handle(self, *the_args, **options):
        if len(the_args) != 2:
            for ph in models.LuminaUser.objects.filter(user_type=models.LuminaUser.PHOTOGRAPHER).order_by('id'):
                self.stdout.write("{} - {}".format(ph.id, str(ph.username)))
            raise CommandError("You must specify <photographer_id_or_username> and <number_of_inserts>")

        user_id_or_username, how_many_inserts = the_args

        try:
            photographer = models.LuminaUser.objects.get(pk=int(user_id_or_username))
        except ValueError:
            photographer = models.LuminaUser.objects.get(username=user_id_or_username)
        assert photographer.is_photographer()

        customer_types = models.CustomerType.objects.for_photographer_ordered(photographer)
        ct_worked_hours_media = dict([
            (ct.id, (i+1) * 20) for i, ct in enumerate(customer_types)
        ])
        ct_cost_media = dict([
            (ct.id, (i+1) * 2000) for i, ct in enumerate(reversed(customer_types))
        ])

        today = datetime.date.today()
        for _ in range(0, int(how_many_inserts)):
            customer = random.choice(photographer.studio.customers.all())
            cost = random.randint(ct_cost_media[customer.customer_type.id] - 1000,
                                  ct_cost_media[customer.customer_type.id] + 2000)

            stipulated_date = datetime.datetime(today.year + 1,
                                                random.randint(1, 12),
                                                random.randint(1, 28))
            stipulated_date = timezone.make_aware(stipulated_date)

            created = datetime.datetime(random.randint(today.year - 1, today.year),
                                        random.randint(1, 12),
                                        random.randint(1, 28))
            created = timezone.make_aware(created)

            image_quantity = random.randint(1, 50) * 5
            session_type = random.choice(models.SessionType.objects.filter(studio=photographer.studio))

            # Create quote
            quote = models.SessionQuote.objects.create(
                name=self.gen_name(),
                studio=photographer.studio,
                customer=customer,
                image_quantity=image_quantity,
                cost=cost,
                archived=True,
                stipulated_date=stipulated_date,
                stipulated_down_payment=0.0)
            quote.created = created
            quote.save()
            quote.confirm(photographer)
            self.stdout.write(" - Quote created: {} / {}".format(quote.id, quote.name))

            # Create quote alternative
            sqa = models.SessionQuoteAlternative.objects.create(
                session_quote=quote,
                image_quantity=int(image_quantity * 1.5),
                cost=decimal.Decimal(int(cost * 1.2)))

            if random.randint(0, 3) == 0:
                self.stdout.write("   - Accepting extended quote")
                quote.accept(random.choice(customer.users.all()), sqa.id)
            else:
                self.stdout.write("   - Accepting original quote")
                quote.accept(random.choice(customer.users.all()), None)

            # Create session
            session = models.Session.objects.create(
                name=quote.name,
                studio=photographer.studio,
                photographer=photographer,
                customer=quote.customer,
                session_type=session_type,
            )

            quote.session = session
            quote.save()

            self.stdout.write("   - Session created: {}".format(session.id))
            session.worked_hours = random.randint(ct_worked_hours_media[customer.customer_type.id],
                                                  ct_worked_hours_media[customer.customer_type.id] + 30)
            session.archived = True
            session.save()
