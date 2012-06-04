import sys
import xlrd
from django.core.management.base import BaseCommand
from rapidsms.contrib.locations.models import Location
from rapidsms.models import Connection, Contact
from healthmodels.models.HealthFacility import HealthFacility
from healthmodels.models.HealthProvider import HealthProvider
from script.utils.handling import find_closest_match
from django.contrib.auth.models import Group
from uganda_common.utils import assign_backend
from django.conf import settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        if (len(args) < 1):
            print "Please specify file with reporters"
            return
        self.order = getattr(settings, 'REPORTER_EXCEL_FIELDS', {
                'district':0, 'hsd':1,
                'sub_county':2, 'facility':3,
                'title':4, 'name':5,
                'gender':6, 'phone':7
                })

        l = self.read_all_reporters(args[0])

        self.load_reporters(l[1:])

    def read_all_reporters(self, filename):
        wb = xlrd.open_workbook(filename)
        l = []
        #lets stick to sheet one only
        #num_of_sheets = wb.nsheets
        num_of_sheets = 1
        for i in xrange(num_of_sheets):
            sh = wb.sheet_by_index(i)
            for rownum in range(sh.nrows):
                vals = sh.row_values(rownum)
                l.append(vals)
        #print l
        return l

    def load_reporters(self, data):
        for d in data:
            if not d[self.order['name']]:
                continue
            print d
            _name = d[self.order['name']].strip()
            _phone = '%s' % d[self.order['phone']]
            _district = d[self.order['district']].strip()
            _role = 'Other Health Workers'
            _fac = d[self.order['facility']].strip()
#            _fac_type = d[self.order['facility_type']]
            _village = d[self.order['sub_county']].strip()
#            _village_type = d[self.order['village_type']].strip()
#            _pvht = d[self.order['pvht']]
            _phone = _phone.split('e')[0].split('.')[0].replace('-','')
            nums = _phone.split('/')
            _phone2 = ''
            if len(nums) > 1:
                _phone = nums[0]
                _phone2 = nums[1]

            print _name, _phone, _role
            district = find_closest_match(_district, Location.objects.filter(type='district'))
            roles = Group.objects.filter(name='Other Health Workers')
            role = Group.objects.get(name='Other Health Workers')
            facility = find_closest_match(_fac, HealthFacility.objects.all(), True)
            village = None
            if _village:
                if district:
                    village = find_closest_match(_village, district.get_descendants(include_self=True))
                else:
                    village = find_closest_match(_village, Location.objects.all())
            if _name:
                _name = ' '.join([n.capitalize() for n in _name.lower().split()])
            msisdn, backend = assign_backend(_phone)
            print msisdn
            try:
                connection = Connection.objects.get(identity=msisdn, backend=backend)
            except Connection.DoesNotExist:
                connection = Connection.objects.create(identity=msisdn, backend=backend)
            except Connection.MultipleObjectsReturned:
                connection = Connection.objects.filter(identity=msisdn, backend=backend)[0]

            try:
                contact = connection.contact or HealthProvider.objects.get(name=_name, \
                                      reporting_location=(village or  district), \
                                      village=village, \
                                      village_name=_village)
            except Contact.DoesNotExist, Contact.MultipleObectsReturned:
                contact = HealthProvider.objects.create()

            connection.contact = contact
            connection.save()
            if _name:
                contact.name = _name

            if facility:
                contact.facility = facility

            if village:
                contact.reporting_location = village
                contact.village = village
                contact.village_name = None
            else:
                if district:
                    contact.reporting_location = district
                else:
                    contact.reporting_location = Location.tree.root_nodes()[0]
                contact.village_name = _village
                contact.village = None

            contact.groups.clear()
            for role in roles:
                contact.groups.add(role)

            if _phone2:
                msisdn2, backend2 = assign_backend(_phone2)
                try:
                    connection2 = Connection.objects.get(identity=msisdn2, backend=backend2)
                except Connection.DoesNotExist:
                    connection2 = Connection.objects.create(identity=msisdn2, backend=backend2)
                contact.connection_set.add(connection2)
            contact.save()
