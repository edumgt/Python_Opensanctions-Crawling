BEGIN;

-- cache (10)
INSERT INTO public."cache" ("key","text","dataset","timestamp") VALUES
('cache:ua_edr:page:1','UA EDR page 1 cached response','ua_edr','2026-01-16 15:00:00'),
('cache:ua_edr:page:2','UA EDR page 2 cached response','ua_edr','2026-01-16 15:02:00'),
('cache:gb_fca:feed','FCA feed snapshot','gb_fca_firds','2026-01-16 15:05:00'),
('cache:ofac:snapshot:2026-01-16','OFAC daily snapshot','us_ofac_sdn','2026-01-16 15:06:00'),
('cache:eu:sanctions:latest','EU sanctions latest payload','eu_sanctions_map','2026-01-16 15:08:00'),
('cache:pep:kr:search:park','KR PEP search results: park','kr_pep_demo','2026-01-16 15:10:00'),
('cache:entity:QX-1001','Entity profile cache','demo_dataset','2026-01-16 15:12:00'),
('cache:entity:QX-1002','Entity profile cache','demo_dataset','2026-01-16 15:12:30'),
('cache:news:pep:daily','Daily PEP related news digest','news_demo','2026-01-16 15:14:00'),
('cache:stats:entity_count','Cached entity count stats','system','2026-01-16 15:20:00');

-- entity_flattened (10)  (all values ASCII-only)
INSERT INTO public."entity_flattened"
("entity_id","schema","dataset","name","alias","first_name","last_name","birth_date","country","nationality","gender","address","passport_number","id_number","source_url","topics")
VALUES
('QX-1001','Person','ua_edr','Oleksandr Petrov','Oleksandr Petrov','Oleksandr','Petrov','1979-04-21','UA','Ukrainian','male','Kyiv, Ukraine','UA1234567','UA-ID-778899','https://example.org/ua/edr/QX-1001','["pep","sanctions"]'),
('QX-1002','Person','us_ofac_sdn','Maria Gonzales','Maria G','Maria','Gonzales','1985-09-02','MX','Mexican','female','Monterrey, Mexico','MX9988776','MX-ID-112233','https://example.org/ofac/QX-1002','["sanctions"]'),
('QX-1003','Organization','eu_sanctions_map','Baltic Trade LLC','Baltic Trade','', '', NULL,'LV','Latvian',NULL,'Riga, Latvia',NULL,'REG-LV-556677','https://example.org/eu/QX-1003','["sanctions","trade"]'),
('QX-1004','Person','gb_fca_firds','John Smith','J Smith','John','Smith','1972-01-15','GB','British','male','London, United Kingdom','GB4455667','GB-NIN-AB123456C','https://example.org/fca/QX-1004','["finance","regulatory"]'),
('QX-1005','Person','kr_pep_demo','Minseo Park','Minseo Park','Minseo','Park','1990-06-30','KR','Korean','female','Seoul, Republic of Korea','KR7788990','KR-ID-9006302','https://example.org/kr/pep/QX-1005','["pep"]'),
('QX-1006','Organization','demo_dataset','Orion Shipping Co','Orion Shipping','', '', NULL,'SG','Singaporean',NULL,'Singapore','SG-REG-9988','SG-BIZ-009988','https://example.org/demo/QX-1006','["shipping","trade"]'),
('QX-1007','Person','demo_dataset','Ahmed Al-Farsi','Ahmed Farsi','Ahmed','Al-Farsi','1968-11-09','AE','Emirati','male','Abu Dhabi, United Arab Emirates','AE3322110','AE-ID-445566','https://example.org/demo/QX-1007','["pep","finance"]'),
('QX-1008','Person','demo_dataset','Yuki Tanaka','Yuki Tanaka','Yuki','Tanaka','1994-03-12','JP','Japanese','female','Tokyo, Japan','JP5544332','JP-ID-778899','https://example.org/demo/QX-1008','["travel"]'),
('QX-1009','Organization','demo_dataset','Nova Minerals Inc','Nova Minerals','', '', NULL,'CA','Canadian',NULL,'Toronto, Canada',NULL,'CA-BIZ-110022','https://example.org/demo/QX-1009','["mining"]'),
('QX-1010','Person','demo_dataset','Sergey Ivanov','Sergey Ivanov','Sergey','Ivanov','1976-08-05','RU','Russian','male','Moscow, Russia','RU1010101','RU-ID-101010','https://example.org/demo/QX-1010','["sanctions","pep"]');

-- nation_code (10)  (country names kept in English to avoid encoding issues)
INSERT INTO public."nation_code" ("code","nation_kor","count") VALUES
('KR','Korea, Republic of',1250),
('US','United States',980),
('UA','Ukraine',410),
('GB','United Kingdom',520),
('JP','Japan',360),
('CN','China',870),
('RU','Russia',640),
('DE','Germany',300),
('FR','France',290),
('SG','Singapore',140);

-- position (10)
INSERT INTO public."position"
("entity_id","caption","countries","is_pep","topics","dataset","created_at","modified_at","modified_by","deleted_at")
VALUES
('QX-1001','Deputy Minister of Infrastructure','{"codes":["UA"],"names":["Ukraine"]}'::json,true,'["pep","government"]'::json,'ua_edr','2026-01-10 09:00:00',NULL,NULL,NULL),
('QX-1002','Sanctioned Individual - Associate','{"codes":["MX","US"],"names":["Mexico","United States"]}'::json,false,'["sanctions"]'::json,'us_ofac_sdn','2026-01-11 10:00:00',NULL,NULL,NULL),
('QX-1004','Approved Person (FCA)','{"codes":["GB"],"names":["United Kingdom"]}'::json,false,'["finance","regulatory"]'::json,'gb_fca_firds','2026-01-12 11:30:00','2026-01-13 08:00:00','admin',NULL),
('QX-1005','Member of National Assembly','{"codes":["KR"],"names":["Korea, Republic of"]}'::json,true,'["pep","politics"]'::json,'kr_pep_demo','2026-01-09 14:00:00',NULL,NULL,NULL),
('QX-1007','Board Chair - State Fund','{"codes":["AE"],"names":["United Arab Emirates"]}'::json,true,'["pep","finance"]'::json,'demo_dataset','2026-01-08 08:00:00',NULL,NULL,NULL),
('QX-1008','Consulate Staff','{"codes":["JP"],"names":["Japan"]}'::json,true,'["pep","diplomacy"]'::json,'demo_dataset','2026-01-07 13:20:00','2026-01-15 09:00:00','reviewer1',NULL),
('QX-1010','State-owned Enterprise Executive','{"codes":["RU"],"names":["Russia"]}'::json,true,'["pep","sanctions"]'::json,'demo_dataset','2026-01-06 16:10:00',NULL,NULL,NULL),
('QX-1003','Beneficial Owner (Company)','{"codes":["LV"],"names":["Latvia"]}'::json,false,'["ownership","trade"]'::json,'eu_sanctions_map','2026-01-05 17:00:00',NULL,NULL,NULL),
('QX-1006','Ship Operator','{"codes":["SG"],"names":["Singapore"]}'::json,false,'["shipping"]'::json,'demo_dataset','2026-01-04 12:00:00',NULL,NULL,NULL),
('QX-1009','Mining License Holder','{"codes":["CA"],"names":["Canada"]}'::json,false,'["mining"]'::json,'demo_dataset','2026-01-03 09:45:00',NULL,NULL,'2026-01-14 00:00:00');

-- program (10)
INSERT INTO public."program" ("key","title","url") VALUES
('OFAC-SDN','OFAC SDN Program','https://example.org/programs/ofac-sdn'),
('EU-SAN','EU Consolidated Sanctions','https://example.org/programs/eu-sanctions'),
('UK-HMT','UK HMT Sanctions','https://example.org/programs/uk-hmt'),
('UN-SC','UN Security Council Sanctions','https://example.org/programs/un-sc'),
('FATF-HR','FATF High-Risk Jurisdictions','https://example.org/programs/fatf-high-risk'),
('PEP-GOV','Politically Exposed Persons (Gov)','https://example.org/programs/pep-gov'),
('FIN-REG','Financial Regulators List','https://example.org/programs/fin-reg'),
('AML-WATCH','AML Watchlist','https://example.org/programs/aml-watch'),
('TRADE-CTRL','Trade Control Program','https://example.org/programs/trade-control'),
('DEMO-PROG','Demo Program','https://example.org/programs/demo');

-- resolver (10)
INSERT INTO public."resolver"
("target","source","judgement","score","user","created_at","deleted_at")
VALUES
('QX-1001','QX-1001','match',1.000,'admin','2026-01-16T14:00:00+09:00',NULL),
('QX-1002','QX-1002','match',1.000,'admin','2026-01-16T14:01:00+09:00',NULL),
('QX-1004','QX-1004','match',1.000,'admin','2026-01-16T14:02:00+09:00',NULL),
('QX-1005','QX-1005','match',1.000,'reviewer1','2026-01-16T14:03:00+09:00',NULL),
('QX-1007','QX-1010','possible',0.812,'reviewer2','2026-01-16T14:04:00+09:00',NULL),
('QX-1008','QX-1008','match',0.995,'reviewer1','2026-01-16T14:05:00+09:00',NULL),
('QX-1010','QX-1010','match',1.000,'admin','2026-01-16T14:06:00+09:00',NULL),
('QX-1003','QX-1006','no_match',0.120,'reviewer3','2026-01-16T14:07:00+09:00',NULL),
('QX-1006','QX-1009','possible',0.640,'reviewer2','2026-01-16T14:08:00+09:00','2026-01-16T14:30:00+09:00'),
('QX-1009','QX-1009','match',1.000,'admin','2026-01-16T14:09:00+09:00',NULL);

-- review (10)  (ASCII-only source_value)
INSERT INTO public."review"
("key","dataset","extraction_schema","source_value","source_mime_type","source_label","source_url","accepted","crawler_version","original_extraction","origin","extracted_data","last_seen_version","modified_at","modified_by","deleted_at")
VALUES
('rev:ua_edr:QX-1001','ua_edr','{"fields":["name","birth_date","country"]}'::json,'<html>sample ua edr page</html>','text/html','UA EDR Page','https://example.org/ua/edr/QX-1001',true,12,'{"name":"Oleksandr Petrov"}'::json,'web','{"entity_id":"QX-1001","name":"Oleksandr Petrov","country":"UA"}'::json,'v12','2026-01-16 13:10:00','reviewer1',NULL),
('rev:ofac:QX-1002','us_ofac_sdn','{"fields":["name","alias","topics"]}'::json,'{"raw":"ofac json snippet"}','application/json','OFAC SDN JSON','https://example.org/ofac/QX-1002',true,5,'{"name":"Maria Gonzales"}'::json,'api','{"entity_id":"QX-1002","name":"Maria Gonzales","topics":["sanctions"]}'::json,'v5','2026-01-16 13:12:00','reviewer1',NULL),
('rev:fca:QX-1004','gb_fca_firds','{"fields":["name","source_url"]}'::json,'PDF bytes omitted','application/pdf','FCA Register PDF','https://example.org/fca/QX-1004',false,3,'{"name":"John Smith"}'::json,'web','{"entity_id":"QX-1004","name":"John Smith","status":"needs_check"}'::json,'v3','2026-01-16 13:15:00','reviewer2',NULL),
('rev:krpep:QX-1005','kr_pep_demo','{"fields":["name","position"]}'::json,'<html>kr pep page</html>','text/html','KR PEP Page','https://example.org/kr/pep/QX-1005',true,1,'{"name":"Minseo Park"}'::json,'web','{"entity_id":"QX-1005","name":"Minseo Park","pep":true}'::json,'v1','2026-01-16 13:20:00','reviewer2',NULL),
('rev:demo:QX-1007','demo_dataset','{"fields":["name","nationality"]}'::json,'{"raw":"demo payload"}','application/json','Demo Payload','https://example.org/demo/QX-1007',true,2,'{"name":"Ahmed Al-Farsi"}'::json,'manual','{"entity_id":"QX-1007","name":"Ahmed Al-Farsi","nationality":"Emirati"}'::json,'v2','2026-01-16 13:25:00','admin',NULL),
('rev:demo:QX-1008','demo_dataset','{"fields":["name","country"]}'::json,'<html>jp page</html>','text/html','JP Page','https://example.org/demo/QX-1008',true,2,'{"name":"Yuki Tanaka"}'::json,'web','{"entity_id":"QX-1008","name":"Yuki Tanaka","country":"JP"}'::json,'v2','2026-01-16 13:30:00','reviewer3',NULL),
('rev:demo:QX-1003','eu_sanctions_map','{"fields":["name","id_number"]}'::json,'Company register snippet','text/plain','Company Snippet','https://example.org/eu/QX-1003',false,7,'{"name":"Baltic Trade LLC"}'::json,'web','{"entity_id":"QX-1003","name":"Baltic Trade LLC","flag":"verify_owner"}'::json,'v7','2026-01-16 13:32:00','reviewer3',NULL),
('rev:demo:QX-1006','demo_dataset','{"fields":["name","topics"]}'::json,'{"raw":"shipping record"}','application/json','Shipping Record','https://example.org/demo/QX-1006',true,2,'{"name":"Orion Shipping Co"}'::json,'api','{"entity_id":"QX-1006","name":"Orion Shipping Co","topics":["shipping","trade"]}'::json,'v2','2026-01-16 13:35:00','admin',NULL),
('rev:demo:QX-1009','demo_dataset','{"fields":["name","country"]}'::json,'{"raw":"mining license"}','application/json','Mining License','https://example.org/demo/QX-1009',true,2,'{"name":"Nova Minerals Inc"}'::json,'api','{"entity_id":"QX-1009","name":"Nova Minerals Inc","country":"CA"}'::json,'v2','2026-01-16 13:38:00','reviewer1',NULL),
('rev:demo:QX-1010','demo_dataset','{"fields":["name","topics"]}'::json,'<html>ru profile</html>','text/html','RU Profile','https://example.org/demo/QX-1010',true,2,'{"name":"Sergey Ivanov"}'::json,'web','{"entity_id":"QX-1010","name":"Sergey Ivanov","topics":["pep","sanctions"]}'::json,'v2','2026-01-16 13:40:00','admin',NULL);

-- statement (10) (ASCII-only originals)
INSERT INTO public."statement"
("id","entity_id","canonical_id","prop","prop_type","schema","value","original_value","dataset","origin","lang","external","first_seen","last_seen")
VALUES
('st-0001','QX-1001','QX-1001','name','string','Person','Oleksandr Petrov','Oleksandr Petrov','ua_edr','web','uk',false,'2026-01-10 09:05:00','2026-01-16 13:10:00'),
('st-0002','QX-1001','QX-1001','birthDate','date','Person','1979-04-21',NULL,'ua_edr','web',NULL,false,'2026-01-10 09:05:00','2026-01-16 13:10:00'),
('st-0003','QX-1002','QX-1002','name','string','Person','Maria Gonzales','Maria Gonzales','us_ofac_sdn','api','es',true,'2026-01-11 10:05:00','2026-01-16 13:12:00'),
('st-0004','QX-1002','QX-1002','topics','list','Person','sanctions',NULL,'us_ofac_sdn','api',NULL,true,'2026-01-11 10:05:00','2026-01-16 13:12:00'),
('st-0005','QX-1004','QX-1004','name','string','Person','John Smith',NULL,'gb_fca_firds','web','en',false,'2026-01-12 11:35:00','2026-01-16 13:15:00'),
('st-0006','QX-1005','QX-1005','name','string','Person','Minseo Park','Minseo Park','kr_pep_demo','web','en',false,'2026-01-09 14:05:00','2026-01-16 13:20:00'),
('st-0007','QX-1006','QX-1006','name','string','Organization','Orion Shipping Co',NULL,'demo_dataset','api','en',false,'2026-01-04 12:05:00','2026-01-16 13:35:00'),
('st-0008','QX-1007','QX-1007','nationality','string','Person','Emirati',NULL,'demo_dataset','manual','en',false,'2026-01-08 08:05:00','2026-01-16 13:25:00'),
('st-0009','QX-1008','QX-1008','country','string','Person','JP',NULL,'demo_dataset','web','ja',false,'2026-01-07 13:25:00','2026-01-16 13:30:00'),
('st-0010','QX-1010','QX-1010','topics','list','Person','pep,sanctions',NULL,'demo_dataset','web','ru',true,'2026-01-06 16:15:00','2026-01-16 13:40:00');

COMMIT;
