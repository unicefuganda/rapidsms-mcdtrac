from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
#from django.conf import settings
import pprint
import datetime
import dateutil
import openpyxl
#from openpyxl import Workbook, style
#from openpyxl.cell import Cell
from mcdtrac.utils import dictfetchall

class Command(BaseCommand):
    """export excels of the latest week/quarterly report"""
    help = 'Creates quarterly/weekly spreadsheets for download.'

    def handle(self, *args, **options):
        wb = openpyxl.Workbook()
        ws1 = wb.get_active_sheet()
        ws1.show_gridlines = False;
        ws1.title = "District Summaries"
        ws2 = wb.create_sheet()
        ws2.title = "Individual Entries"

        cursor = connection.cursor()
        pp = pprint.PrettyPrinter(indent=4) # debug
        quarter_months = ['01', '04', '07', '10']
        quarter_start = dateutil.parser.parse(
            str(datetime.date.today().year) + '-' +
            str(quarter_months[(datetime.date.today().month - 1)//3]) + '-' +
            '01'
        ).date()
        quarter = 'Q' + str((datetime.date.today().month - 1)//3 + 1) + str(datetime.date.today().year)
        xls_dir = '/var/www/prod/mtrack/mtrack_project/rapidsms_mcdtrac/mcdtrac/static/spreadsheets/'
        #xls_dir = '/tmp/'
        xls_fpath = xls_dir + 'fhd_stats' + quarter + '.xlsx'
        grouped_sql="""SELECT l.name AS "District",
       COUNT(f.dpt_male) AS "Entries",
       SUM(dpt_male) AS "DPT (M)",
       SUM(dpt_female) AS "DPT (F)",
       SUM(vacm_male) AS "Measles (M)",
       SUM(vacm_female) AS "Measles (F)",
       SUM(vita_male1) AS "Vitamin A Males (6-11m)",
       SUM(vita_female1) AS "Vitamin A Females (6-11m)",
       SUM(vita_male2) AS "Vitamin A Males (12-59m)",
       SUM(vita_female2) AS "Vitamin A Females (12-59m)",
       SUM(worm_male) AS "Deworming (M)",
       SUM(worm_female) AS "Deworming (F)",
       SUM(redm_number) AS "MUAC in Red Zone",
       SUM(tet_dose2) AS "Tetanus dose2",
       SUM(tet_dose3) AS "Tetanus dose3",
       SUM(tet_dose4) AS "Tetanus dose4",
       SUM(tet_dose5) AS "Tetanus dose5",
       SUM(anc_number) AS "Four or more ANC visits",
       SUM(eid_male) AS "HIV Children < 1year (M)",
       SUM(eid_female) AS "HIV Children < 1year (F)",
       SUM(breg_male) AS "Birth Registration (M)",
       SUM(breg_female) AS "Birth Registration (F)",
       SUM(expected_pows) AS "Expected POWs",
       SUM(reached_pows) AS "Reached POWs"
FROM fhd_stats_mview f,
     locations_location l
WHERE f.has_errors = FALSE
    AND f.created <= now()
    AND f.created >= %s
    AND l.lft <= f.lft
    AND l.rght >= f.rght
    AND l.id IN
        (SELECT "locations_location"."id"
         FROM "locations_location"
         WHERE ("locations_location"."lft" <= 15257
                AND "locations_location"."lft" >= 2
                AND "locations_location"."tree_id" = 1
                AND "locations_location"."type_id" = E'district'))
GROUP BY l.lft,
         l.id,
         l.name,
         l.rght"""

        individual_sql="""SELECT f.submission_id,
       f.created::date AS "Date",
       l.name AS district,
       f.facility AS facility,
    (SELECT ll.name
     FROM locations_location ll
     WHERE f.reporting_location_id = ll.id) AS "reporting location",
       f.reporting_name AS reporter,
       f.has_errors,
       f.dpt_male AS "DPT (M)",
       f.dpt_female AS "DPT (F)",
       f.vacm_male AS "Measles (M)",
       f.vacm_female AS "Measles (F)",
       f.vita_male1 AS "Vitamin A Males (6-11m)" ,
       f.vita_female1 AS "Vitamin A Females (6-11m)",
       f.vita_male2 AS "Vitamin A Males (12-59m)",
       f.vita_female2 AS "Vitamin A Females (12-59m)",
       f.worm_male AS "Deworming (M)",
       f.worm_female AS "Deworming (F)",
       f.redm_number AS "MUAC in Red Zone",
       f.tet_dose2 AS "Tetanus dose2",
       f.tet_dose3 AS "Tetanus dose3",
       f.tet_dose4 AS "Tetanus dose4",
       f.tet_dose5 AS "Tetanus dose5",
       f.anc_number AS "Four or more ANC visits",
       f.eid_male AS "HIV Children < 1year (M)",
       f.eid_female AS "HIV Children < 1year (F)",
       f.breg_male AS "Birth Registration (M)",
       f.breg_female AS "Birth Registration (F)",
       f.expected_pows AS "Expected POWs",
       f.reached_pows AS "Reached POWs"
FROM fhd_stats_mview f ,
     locations_location l
WHERE f.created <= now()
    AND f.created >= %s
    AND l.lft <= f.lft
    AND l.rght >= f.rght
    AND l.id IN
        (SELECT "locations_location"."id"
         FROM "locations_location"
         WHERE ("locations_location"."lft" <= 15257
                AND "locations_location"."lft" >= 2
                AND "locations_location"."tree_id" = 1
                AND "locations_location"."type_id" = E'district'))
        """

        self.stdout.write(':: generating district summaries.')
        cursor.execute(grouped_sql, [quarter_start])
        headers = [col[0] for col in cursor.description]
        rows = dictfetchall(cursor)
        transaction.commit_unless_managed()
        col = 0 ; row = 0
        for h in headers:
            cell = ws1.cell(row = row, column = col)
            cell.value = h

            col += 1
        #ws.row_dimensions[1].height = ??
        col = 0 ; row = 1
        for r in rows:
            for key in r:
                ws1.cell(row = row, column = col).value = r[key]
                col += 1
            row += 1 ; col = 0

        ws1.row_dimensions[1].height = 42.0
        for c in ws1.column_dimensions:
            ws1.column_dimensions[c].width = 10.47

        # for c in ws1.rows[0]:
        #     c.style.wrap_text = True
        #     c.style.alignment.vertical = openpyxl.style.Alignment.VERTICAL_TOP
        #     c.style.alignment.horizontal = openpyxl.style.Alignment.HORIZONTAL_CENTER
        #     c.style.fill.fill_type = openpyxl.style.Fill.FILL_SOLID
        #     c.style.fill.start_color.index = 'e6e6e6'
        #     c.style.borders.all_borders.border_style = openpyxl.style.Border.BORDER_MEDIUM
        self.stdout.write(':: generating individual entries.')
        cursor.execute(individual_sql, [quarter_start])
        headers = [col[0] for col in cursor.description]
        rows = dictfetchall(cursor)
        transaction.commit_unless_managed()
        col = 0 ; row = 0
        for h in headers:
            cell = ws2.cell(row = row, column = col)
            cell.value = h
            col += 1
        col = 0 ; row = 1
        for r in rows:
            for key in r:
                ws2.cell(row = row, column = col).value = r[key]
                col += 1
            row += 1 ; col = 0

        ws2.row_dimensions[1].height = 42.0
        for c in ws2.column_dimensions:
            ws2.column_dimensions[c].width = 10.47

        wb.save(xls_fpath)

