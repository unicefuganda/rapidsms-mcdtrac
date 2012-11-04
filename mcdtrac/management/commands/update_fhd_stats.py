from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
import pprint

class Command(BaseCommand):
	"""update FHD materialized view"""
	args = ''
	help = 'Updates the FHD materialzed view in the table "fhd_stats_mview".'

	def handle(self, *args, **options):
		cursor = connection.cursor()
		pp = pprint.PrettyPrinter(indent=4) # debug
		truncate_sql='TRUNCATE TABLE fhd_stats_mview'
		insert_sql="""
INSERT INTO fhd_stats_mview
SELECT f.value_id,
       f.submission_id,
       f.created,
       f.has_errors,
       f.reporting_name,
       f.phone,
       f.lft,
       f.reporting_location_id,
       f.rght,
       f.dpt_male,
       f.dpt_female,
       f.vacm_male,
       f.vacm_female,
       f.vita_male1,
       f.vita_female1,
       f.vita_male2,
       f.vita_female2,
       f.worm_male,
       f.worm_female,
       f.redm_number,
       f.tet_dose2,
       f.tet_dose3,
       f.tet_dose4,
       f.tet_dose5,
       f.anc_number,
       f.eid_male,
       f.eid_female,
       f.breg_male,
       f.breg_female,
       f.expected_pows,
       f.reached_pows
FROM fhd_stats_view f
WHERE f.dpt_male IS NOT NULL
  OR f.dpt_female IS NOT NULL
  OR f.vacm_male IS NOT NULL
  OR f.vacm_female IS NOT NULL
  OR f.vita_male1 IS NOT NULL
  OR f.vita_female1 IS NOT NULL
  OR f.vita_male2 IS NOT NULL
  OR f.vita_female2 IS NOT NULL
  OR f.worm_male IS NOT NULL
  OR f.worm_female IS NOT NULL
  OR f.redm_number IS NOT NULL
  OR f.tet_dose2 IS NOT NULL
  OR f.tet_dose3 IS NOT NULL
  OR f.tet_dose4 IS NOT NULL
  OR f.tet_dose5 IS NOT NULL
  OR f.anc_number IS NOT NULL
  OR f.eid_male IS NOT NULL
  OR f.eid_female IS NOT NULL
  OR f.breg_male IS NOT NULL
  OR f.breg_female IS NOT NULL
  OR f.expected_pows IS NOT NULL
  OR f.reached_pows IS NOT NULL"""
		verbose = False
		quiet = False
		if 'verbosity' in options:
			if options['verbosity'] == '0':
				quiet = True
			if options['verbosity'] == '2':
				verbose = True

		if not quiet:
			self.stdout.write('truncating and reloading fhd_stats_mview...\n')
		#self.stderr.write(pp.pformat(options) + '\n') # debug
		#truncate
		if verbose:
			self.stdout.write('=> ' + truncate_sql + ' []\n')
		cursor.execute(truncate_sql)
		#insert
		if verbose:
			self.stdout.write('=> ' + insert_sql + ' []\n')
		cursor.execute(insert_sql)
		transaction.commit_unless_managed()
		if not quiet:
			self.stdout.write('succesfully updated fhd_stats_mview\n')
