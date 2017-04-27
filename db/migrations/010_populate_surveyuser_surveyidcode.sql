

BEGIN;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

INSERT INTO survey_surveyuser (global_id, name, deleted, user_id) VALUES(uuid_generate_v4(), 'root', 'f', 1);
INSERT INTO survey_surveyidcode (surveyuser_global_id, idcode) VALUES((SELECT global_id FROM survey_surveyuser WHERE id=1), 1337);

COMMIT;
