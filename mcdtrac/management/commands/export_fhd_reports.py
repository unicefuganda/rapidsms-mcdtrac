from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.conf import settings
import pprint
import datetime
import dateutil
import openpyxl
import os
from mcdtrac.utils import dictfetchall, XLS_DIR
from optparse import make_option

class Command(BaseCommand):
    """export excels of the latest week/quarterly report"""
    help = 'Creates quarterly/weekly spreadsheets for download.'
    pp = pprint.PrettyPrinter(indent=4)  # debug
    base_width = 10.47
    debug_fhd = False

    option_list = BaseCommand.option_list + (
            make_option(
                '-d',
                '--debug',
                action='store_true',
                dest='debug_fhd',
                default=False,
                help='Debug FHD CMD'
            ),
        )

    def get_districts(self):
        """rows of district objects with FHD data."""
        cursor = connection.cursor()
        sql = """SELECT l.lft,
                   l.id,
                   l.name AS District ,
                   l.rght
            FROM fhd_stats_mview f ,
                 locations_location l
            WHERE f.has_errors = FALSE
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
        cursor.execute(sql)
        rows = dictfetchall(cursor)
        transaction.commit_unless_managed()
        return rows

    def generate_sql(self, district_level=False, district_id=None):
        """
        generate SQL used by the handle() below as follows:

        if district_level = False:
            generate the strings suitable for a global level worksheets
        else:
            generate the sql suitable for a particular district specified
            as the <district_id> option. Raise CommandError if no <district_id>
        """
        if district_level:
            if not (district_id and isinstance(district_id, (int, long))):
                raise CommandError("If you want a district give me a district_id")
            else:
                grp_sql_title = 'SELECT f.facility AS "Facility"'
                sql_id = 'l.id = {0}'.format(int(district_id))
                grp_sql_name = 'f.facility'
        else:
            grp_sql_title = 'SELECT l.name AS "District"'
            sql_id = """l.id in (SELECT "locations_location"."id"
                FROM "locations_location"
                WHERE ("locations_location"."lft" <= 15257
                       AND "locations_location"."lft" >= 2
                       AND "locations_location"."tree_id" = 1
                       AND "locations_location"."type_id" = E'district'))"""
            grp_sql_name = 'l.name'

        grouped_sql = """{0},
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
                AND {1}
            GROUP BY l.lft,
                     l.id,
                     {2},
                     l.rght""".format(grp_sql_title, sql_id, grp_sql_name)

        individual_sql = """SELECT f.submission_id,
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
                AND {0}""".format(sql_id)

        return (grouped_sql, individual_sql)

    def populate_worksheet(self, ws=None, title='', sql_list=[], col_widths={}):

        if not (ws and title and sql_list):
            raise CommandError('Got incomplete arguments')

        cursor = connection.cursor()
        ws.title = title
        ws.show_gridlines = False  # doesn't seem to work
        sql_str = sql_list.pop(0)

        cursor.execute(sql_str, sql_list)
        headers = [col[0] for col in cursor.description]
        rows = dictfetchall(cursor)
        transaction.commit_unless_managed()

        col = 0
        row = 0
        for h in headers:
            cell = ws.cell(row=row, column=col)
            cell.value = h
            col += 1

        col = 0
        row = 1
        for r in rows:
            for key in r:
                ws.cell(row=row, column=col).value = r[key]
                col += 1
            row += 1
            col = 0

        ws.row_dimensions[1].height = 42.0
        for c in ws.column_dimensions:
            ws.column_dimensions[c].width = self.base_width

        if col_widths:
            for c in col_widths:
                ws.column_dimensions[c].width = col_widths[c]

        for cell in ws.rows[0]:
            cell.style.alignment.vertical = openpyxl.style.Alignment.VERTICAL_TOP
            cell.style.alignment.wrap_text = True
            cell.style.font.bold = True
            cell.style.fill.fill_type = openpyxl.style.Fill.FILL_SOLID
            cell.style.fill.start_color.index = 'FFE6E6E6'
            #todo: add borders
        return ws

    def handle(self, *args, **options):
        self.debug_fhd = options['debug_fhd']
        if self.debug_fhd:
            self.stdout.write(self.pp.pformat(options))
        wb = openpyxl.Workbook()
        quarter_months = ['01', '04', '07', '10']
        quarter_start = dateutil.parser.parse(
            str(datetime.date.today().year) + '-' +
            str(quarter_months[(datetime.date.today().month - 1) // 3]) + '-' +
            '01'
        ).date()
        q_str = 'Q' + str((datetime.date.today().month - 1) // 3 + 1)
        y_str = str(datetime.date.today().year)
        quarter = y_str + '_' + q_str
        xls_fdir = os.path.join(settings.MTRACK_ROOT, XLS_DIR, 'uganda/{0}/{1}'.format(y_str, str.lower(q_str)))
        try:
            os.makedirs(xls_fdir)
        except OSError:
            pass
        xls_fpath = os.path.join(xls_fdir, 'fhd_stats-' + quarter + '.xlsx')
        if self.debug_fhd:
            self.stdout.write(
                'DEBUG: Writing spreadsheet to: "{0}"\n'.format(xls_fpath)
            )
        grouped_sql, individual_sql = self.generate_sql()
        self.stdout.write(':: generating district summaries.\n')
        self.populate_worksheet(
            ws=wb.get_active_sheet(),
            title="District Summaries",
            sql_list=[grouped_sql, quarter_start])
        self.stdout.write(':: generating individual entries.\n')
        self.populate_worksheet(
            ws=wb.create_sheet(),
            title="Individual Entries",
            sql_list=[individual_sql, quarter_start],
            col_widths={
                'A': self.base_width * 1.5,
                'D': self.base_width * 1.5,
                'E': self.base_width * 2,
                'F': self.base_width * 3
            })
        if self.debug_fhd:
            self.stdout.write(
                    'DEBUG: Workbook is: ' +
                    self.pp.pformat(wb.worksheets) + '\n'
                )
        wb.save(xls_fpath)
