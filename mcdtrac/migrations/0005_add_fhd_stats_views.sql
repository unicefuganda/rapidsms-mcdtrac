-- create fhd_stats_view
--
CREATE OR REPLACE VIEW "fhd_stats_view" AS
SELECT "rapidsms_xforms_xformsubmissionvalue"."value_ptr_id" AS value_id,
       "rapidsms_xforms_xformsubmission"."id" AS submission_id,
       "rapidsms_xforms_xformsubmission"."created",
       "rapidsms_xforms_xformsubmission"."has_errors",

  (SELECT "rapidsms_contact"."name"
   FROM "rapidsms_contact"
   WHERE "rapidsms_contact"."id" = "rapidsms_connection"."contact_id") AS reporting_name,
       "rapidsms_connection"."identity" AS phone,

  (SELECT "locations_location"."lft"
   FROM "locations_location"
   LEFT JOIN "rapidsms_contact" ON "locations_location"."id" = "rapidsms_contact"."reporting_location_id"
   WHERE "rapidsms_contact"."id" = "rapidsms_connection"."contact_id") AS lft,

  (SELECT "rapidsms_contact"."reporting_location_id"
   FROM "rapidsms_contact"
   WHERE "rapidsms_contact"."id" = "rapidsms_connection"."contact_id") AS reporting_location_id,

  (SELECT "locations_location"."rght"
   FROM "locations_location"
   LEFT JOIN "rapidsms_contact" ON "locations_location"."id" = "rapidsms_contact"."reporting_location_id"
   WHERE "rapidsms_contact"."id" = "rapidsms_connection"."contact_id") AS rght,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'dpt_male')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS dpt_male,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'dpt_female')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS dpt_female,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'vacm_male')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS vacm_male,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'vacm_female')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS vacm_female,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'vita_male1')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS vita_male1,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'vita_female1')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS vita_female1,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'vita_male2')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS vita_male2,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'vita_female2')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS vita_female2,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'worm_male')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS worm_male,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'worm_female')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS worm_female,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'redm_number')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS redm_number,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'tet_dose2')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS tet_dose2,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'tet_dose3')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS tet_dose3,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'tet_dose4')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS tet_dose4,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'tet_dose5')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS tet_dose5,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'anc_number')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS anc_number,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'eid_male')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS eid_male,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'eid_female')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS eid_female,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'breg_male')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS breg_male,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'breg_female')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS breg_female,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'sum_exp'
          OR "eav_attribute"."slug" = 'summary_exp')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS expected_pows,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'sum_tot'
          OR "eav_attribute"."slug" = 'summary_tot')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS reached_pows
FROM "rapidsms_xforms_xformsubmissionvalue"
INNER JOIN "rapidsms_xforms_xformsubmission" ON "rapidsms_xforms_xformsubmissionvalue"."submission_id" = "rapidsms_xforms_xformsubmission"."id"
INNER JOIN "rapidsms_connection" ON "rapidsms_xforms_xformsubmission"."connection_id" = "rapidsms_connection"."id"
WHERE "rapidsms_connection"."contact_id" IS NOT NULL;
--
-- fake a materialized view
--
CREATE TABLE fhd_stats_mview AS
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
  OR f.reached_pows IS NOT NULL;
---
--- INDEXES
---
CREATE INDEX fhd_stats_mview_created_idx ON fhd_stats_mview (created);
CREATE INDEX fhd_stats_mview_has_errors_idx ON fhd_stats_mview (has_errors);
CREATE INDEX fhd_stats_mview_lft_idx ON fhd_stats_mview (lft);
CREATE INDEX fhd_stats_mview_reporting_location_id_idx ON fhd_stats_mview (reporting_location_id);
CREATE INDEX fhd_stats_mview_rght_idx ON fhd_stats_mview (rght);
CREATE INDEX fhd_stats_mview_submission_id_idx ON fhd_stats_mview (submission_id);
