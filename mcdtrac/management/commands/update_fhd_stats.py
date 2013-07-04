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
        insert_sql="""INSERT INTO fhd_stats_mview
SELECT f.value_id,
       f.submission_id,
       f.xformreportsubmission_id,
       f.created,
       f.has_errors,
       f.reporting_name,
       f.phone,
       f.facility,
       f.facility_id,
       f.lft,
       f.reporting_location_id,
       f.rght,
       f.pow_district_id,
       f.pow_district_name,
       f.pow_code,
       f.pow_name,
       f.dpt_male,
       f.dpt_female,
       f.vacm_male,
       f.vacm_female,
       f.vita_male1,
       f.vita_female1,
       f.vita_male2,
       f.vita_female2,
       f.pcv_pcv1_m,
       f.pcv_pcv1_f,
       f.pcv_pcv2_m,
       f.pcv_pcv2_f,
       f.pcv_pcv3_m,
       f.pcv_pcv3_f,
       f.dorm_male_1to4,
       f.dorm_female_1to4,
       f.dorm_male_5to14,
       f.dorm_female_5to14,
       f.ryg_red_male,
       f.ryg_red_female,
       f.ryg_yellow_male,
       f.ryg_yellow_female,
       f.ryg_green_male,
       f.ryg_green_female,
       f.tetn_dose1,
       f.tetn_dose2,
       f.tetn_dose3,
       f.tetn_dose4,
       f.tetn_dose5,
       f.npet_dose1,
       f.npet_dose2,
       f.npet_dose3,
       f.npet_dose4,
       f.npet_dose5,
       f.ancp_anc1,
       f.ancp_anc4,
       f.ancp_ipt1,
       f.ancp_ipt2,
       f.heid_male,
       f.heid_female,
       f.heid_tot,
       f.heid_women,
       f.breg_male,
       f.breg_female,
       f.bpbs_bpm,
       f.bpbs_bpf,
       f.bpbs_bsm,
       f.bpbs_bsf,
       f.worm_male,
       f.worm_female,
       f.redm_number,
       f.tet_dose2,
       f.tet_dose3,
       f.tet_dose4,
       f.tet_dose5,
       f.anc_number,
       f.eid_male,
       f.eid_female
FROM fhd_stats_view f
WHERE f.pow_district_id IS NOT NULL
  OR f.pow_district_name IS NOT NULL
  OR f.pow_code IS NOT NULL
  OR f.pow_name IS NOT NULL
  OR f.dpt_male IS NOT NULL
  OR f.dpt_female IS NOT NULL
  OR f.vacm_male IS NOT NULL
  OR f.vacm_female IS NOT NULL
  OR f.vita_male1 IS NOT NULL
  OR f.vita_female1 IS NOT NULL
  OR f.vita_male2 IS NOT NULL
  OR f.vita_female2 IS NOT NULL
  OR f.pcv_pcv1_m IS NOT NULL
  OR f.pcv_pcv1_f IS NOT NULL
  OR f.pcv_pcv2_m IS NOT NULL
  OR f.pcv_pcv2_f IS NOT NULL
  OR f.pcv_pcv3_m IS NOT NULL
  OR f.pcv_pcv3_f IS NOT NULL
  OR f.dorm_male_1to4 IS NOT NULL
  OR f.dorm_female_1to4 IS NOT NULL
  OR f.dorm_male_5to14 IS NOT NULL
  OR f.dorm_female_5to14 IS NOT NULL
  OR f.ryg_red_male IS NOT NULL
  OR f.ryg_red_female IS NOT NULL
  OR f.ryg_yellow_male IS NOT NULL
  OR f.ryg_yellow_female IS NOT NULL
  OR f.ryg_green_male IS NOT NULL
  OR f.ryg_green_female IS NOT NULL
  OR f.tetn_dose1 IS NOT NULL
  OR f.tetn_dose2 IS NOT NULL
  OR f.tetn_dose3 IS NOT NULL
  OR f.tetn_dose4 IS NOT NULL
  OR f.tetn_dose5 IS NOT NULL
  OR f.npet_dose1 IS NOT NULL
  OR f.npet_dose2 IS NOT NULL
  OR f.npet_dose3 IS NOT NULL
  OR f.npet_dose4 IS NOT NULL
  OR f.npet_dose5 IS NOT NULL
  OR f.ancp_anc1 IS NOT NULL
  OR f.ancp_anc4 IS NOT NULL
  OR f.ancp_ipt1 IS NOT NULL
  OR f.ancp_ipt2 IS NOT NULL
  OR f.heid_male IS NOT NULL
  OR f.heid_female IS NOT NULL
  OR f.heid_tot IS NOT NULL
  OR f.heid_women IS NOT NULL
  OR f.breg_male IS NOT NULL
  OR f.breg_female IS NOT NULL
  OR f.bpbs_bpm IS NOT NULL
  OR f.bpbs_bpf IS NOT NULL
  OR f.bpbs_bsm IS NOT NULL
  OR f.bpbs_bsf IS NOT NULL
  OR f.worm_male IS NOT NULL
  OR f.worm_female IS NOT NULL
  OR f.redm_number IS NOT NULL
  OR f.tet_dose2 IS NOT NULL
  OR f.tet_dose3 IS NOT NULL
  OR f.tet_dose4 IS NOT NULL
  OR f.tet_dose5 IS NOT NULL
  OR f.anc_number IS NOT NULL
  OR f.eid_male IS NOT NULL
  OR f.eid_female IS NOT NULL"""
        verbose = False
        quiet = False
        if 'verbosity' in options:
            if options['verbosity'] == '0':
                quiet = True
            if options['verbosity'] == '2':
                verbose = True

        if not quiet:
            self.stdout.write(':: truncating and reloading fhd_stats_mview...\n')
        #self.stderr.write(pp.pformat(options) + '\n') # debug
        #truncate
        if verbose:
            self.stdout.write('   = ' + truncate_sql + ' []\n')
        cursor.execute(truncate_sql)
        #insert
        if verbose:
            self.stdout.write('   = ' + insert_sql + ' []\n')
        cursor.execute(insert_sql)
        transaction.commit_unless_managed()
        if not quiet:
            self.stdout.write(':: succesfully updated fhd_stats_mview\n')
