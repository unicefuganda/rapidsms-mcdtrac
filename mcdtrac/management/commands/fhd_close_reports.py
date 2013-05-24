from django.core.management.base import BaseCommand, CommandError
from mcdtrac.utils import last_reporting_period
from mcdtrac.models import ReportsInProgress
import datetime

class Command(BaseCommand):
    """close open FHD reports"""
    args = ''
    help = 'Closes all open FHD reports at the end of the week'

    def handle(self, *args, **options):
        d = datetime.datetime.now()
        d = datetime.datetime(d.year, d.month, d.day)

        verbose = quiet = False
        if 'verbosity' in options:
            if options['verbosity'] == '0':
                quiet = True
            if options['verbosity'] == '2':
                verbose = True

        if last_reporting_period(period=0)[0] == d :
            if not quiet:
                self.stdout.write(':: closing all open reports newer than "{0}"...\n'.format(last_reporting_period(period=1)[0]))

            for rip in ReportsInProgress.objects.filter( modified__gte=last_reporting_period(period=1)[0], state__endswith='editing') :
                if verbose:
                    self.stdout.write('\t:<pow:{0}>\t:{1}\n'.format(rip.place_of_worship, rip.modified))

                rip.xform_report.status = 'closed'
                rip.xform_report.save()
                rip.state = 'closed'
                rip.save()

            if not quiet:
                self.stdout.write('...done\n')
        else:
            if verbose:
                self.stdout.write(':: nothing to do today \n')

