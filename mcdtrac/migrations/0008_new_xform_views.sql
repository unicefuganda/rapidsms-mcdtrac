-- create fhd_stats_view
--
CREATE OR REPLACE VIEW "fhd_stats_view" AS
SELECT "rapidsms_xforms_xformsubmissionvalue"."value_ptr_id" AS value_id,
       "rapidsms_xforms_xformsubmission"."id" AS submission_id,

  (SELECT "id"
   FROM "rapidsms_xforms_xformreportsubmission"
   WHERE "report_id" =
       (SELECT "id"
        FROM "rapidsms_xforms_xformreport"
        WHERE "name" = 'FHD')
     AND "id" IN
       (SELECT "xformreportsubmission_id"
        FROM "rapidsms_xforms_xformreportsubmission_submissions"
        WHERE "xformsubmission_id" = "rapidsms_xforms_xformsubmission"."id")) AS xformreportsubmission_id,
       "rapidsms_xforms_xformsubmission"."created",
       "rapidsms_xforms_xformsubmission"."has_errors",

  (SELECT "rapidsms_contact"."name"
   FROM "rapidsms_contact"
   WHERE "rapidsms_contact"."id" = "rapidsms_connection"."contact_id") AS reporting_name,
       "rapidsms_connection"."identity" AS phone,

  (SELECT "HB"."facility_id"
   FROM "healthmodels_healthproviderbase" AS "HB"
   WHERE "HB"."contact_ptr_id" = "rapidsms_connection"."contact_id") AS facility_id,

  (SELECT "HF"."name"
   FROM "healthmodels_healthfacilitybase" AS "HF"
   WHERE "HF"."id" =
       (SELECT "HB"."facility_id"
        FROM "healthmodels_healthproviderbase" AS "HB"
        WHERE "HB"."contact_ptr_id" = "rapidsms_connection"."contact_id")) AS facility,

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

  (SELECT "locations_location"."id"
   FROM "locations_location"
   WHERE "type_id" = 'district'
     AND LOWER("name") IN
       (SELECT LOWER(eav_value.value_text)
        FROM "eav_value"
        WHERE eav_value.attribute_id IN
            (SELECT "eav_attribute"."id"
             FROM "eav_attribute"
             WHERE "eav_attribute"."slug" = 'pow_district')
          AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id)) AS pow_district_id,

  (SELECT "locations_location"."name"
   FROM "locations_location"
   WHERE "type_id" = 'district'
     AND LOWER("name") IN
       (SELECT LOWER(eav_value.value_text)
        FROM "eav_value"
        WHERE eav_value.attribute_id IN
            (SELECT "eav_attribute"."id"
             FROM "eav_attribute"
             WHERE "eav_attribute"."slug" = 'pow_district')
          AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id)) AS pow_district_name,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'pow_code')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS pow_code,

  (SELECT eav_value.value_text
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'pow_name')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS pow_name,

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
        WHERE "eav_attribute"."slug" = 'pcv_pcv1_m')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS pcv_pcv1_m,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'pcv_pcv1_f')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS pcv_pcv1_f,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'pcv_pcv2_m')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS pcv_pcv2_m,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'pcv_pcv2_f')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS pcv_pcv2_f,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'pcv_pcv3_m')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS pcv_pcv3_m,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'pcv_pcv3_f')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS pcv_pcv3_f,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'dorm_male_1to4')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS dorm_male_1to4,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'dorm_female_1to4')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS dorm_female_1to4,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'dorm_male_5to14')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS dorm_male_5to14,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'dorm_female_5to14')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS dorm_female_5to14,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'ryg_red_male')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS ryg_red_male,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'ryg_red_female')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS ryg_red_female,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'ryg_yellow_male')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS ryg_yellow_male,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'ryg_yellow_female')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS ryg_yellow_female,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'ryg_green_male')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS ryg_green_male,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'ryg_green_female')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS ryg_green_female,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'tetn_dose1')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS tetn_dose1,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'tetn_dose2')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS tetn_dose2,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'tetn_dose3')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS tetn_dose3,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'tetn_dose4')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS tetn_dose4,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'tetn_dose5')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS tetn_dose5,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'npet_dose1')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS npet_dose1,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'npet_dose2')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS npet_dose2,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'npet_dose3')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS npet_dose3,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'npet_dose4')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS npet_dose4,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'npet_dose5')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS npet_dose5,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'ancp_anc1')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS ancp_anc1,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'ancp_anc4')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS ancp_anc4,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'ancp_ipt1')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS ancp_ipt1,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'ancp_ipt2')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS ancp_ipt2,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'heid_male')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS heid_male,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'heid_female')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS heid_female,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'heid_tot')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS heid_tot,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'heid_women')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS heid_women,

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
        WHERE "eav_attribute"."slug" = 'bpbs_bpm')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS bpbs_bpm,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'bpbs_bpf')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS bpbs_bpf,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'bpbs_bsm')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS bpbs_bsm,

  (SELECT eav_value.value_int
   FROM "eav_value"
   WHERE eav_value.attribute_id IN
       (SELECT "eav_attribute"."id"
        FROM "eav_attribute"
        WHERE "eav_attribute"."slug" = 'bpbs_bsf')
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS bpbs_bsf,

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
     AND eav_value.id = rapidsms_xforms_xformsubmissionvalue.value_ptr_id) AS eid_female
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
  OR f.eid_female IS NOT NULL;
---
--- INDEXES
---
CREATE INDEX fhd_stats_mview_created_idx ON fhd_stats_mview (created);
CREATE INDEX fhd_stats_mview_has_errors_idx ON fhd_stats_mview (has_errors);
CREATE INDEX fhd_stats_mview_lft_idx ON fhd_stats_mview (lft);
CREATE INDEX fhd_stats_mview_reporting_location_id_idx ON fhd_stats_mview (reporting_location_id);
CREATE INDEX fhd_stats_mview_rght_idx ON fhd_stats_mview (rght);
CREATE INDEX fhd_stats_mview_submission_id_idx ON fhd_stats_mview (submission_id);
