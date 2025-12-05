
-- SELECT *
-- FROM storm_events_details_invalid
-- LIMIT 20;
 --ELECT COUNT(*) FROM storm_events_details;
-- SELECT COUNT(*) FROM storm_events_details_cleaned;
-- SELECT COUNT(*) FROM storm_events_details_invalid;
SELECT * FROM storm_events_details 
ORDER BY DAMAGE_PROPERTY DESC
LIMIT 1;
