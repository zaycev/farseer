-- PRINT DATASETS
SELECT id, name,
	   (SELECT COUNT(*)
		FROM collector_rawdocument
		WHERE dataset_id=collector_dataset.id)
		as rawodc_size,
		(SELECT COUNT(DISTINCT url)
		FROM collector_rawdocument
		WHERE dataset_id=collector_dataset.id)
		as real_rawdoc_rsize,
		(SELECT COUNT(url)
		FROM collector_document
		WHERE dataset_id=collector_dataset.id)
		as size,
		(SELECT COUNT(DISTINCT url)
		FROM collector_document
		WHERE dataset_id=collector_dataset.id)
		as real_size,
		(SELECT COUNT(*) FROM collector_probe
		WHERE dataset_id=collector_dataset.id AND tag='vi')
		as views_size,
		(SELECT COUNT(*) FROM collector_probe
		WHERE dataset_id=collector_dataset.id AND tag='vi' AND signal <> -1)
		as views_pos_size,
		(SELECT COUNT(*) FROM collector_probe
		WHERE dataset_id=collector_dataset.id AND tag='tw')
		as twi_size,
		(SELECT COUNT(*) FROM collector_probe
		WHERE dataset_id=collector_dataset.id AND tag='tw' AND signal > 0)
		as twi_pos_size
FROM collector_dataset;

-- SELECT SIGNAL TYPES
SELECT DISTINCT tag FROM collector_probe;

-- SELECT RANDOM PAGE WITH
SELECT target FROM collector_probe WHERE signal=-1 AND tag='vi' ORDER BY RANDOM() LIMIT 1;

-- REMOVE DATASET
DELETE FROM collector_rawdocument WHERE dataset_id=72;
DELETE FROM collector_rawriver WHERE dataset_id=72;
DELETE FROM collector_documenturl WHERE dataset_id=72;
DELETE FROM collector_dataset WHERE id=72;



--- @@@
SELECT * FROM
(SELECT DISTINCT ON (url)
	id,
	url,
	title,
	content,
	published,
	dataset_id as source_dataset,
	EXTRACT(YEAR FROM published) as year,
	EXTRACT(MONTH FROM published) as month,
	EXTRACT(DAY FROM published) as day,
	EXTRACT(DOW FROM published) as dow,
	(published::date - (SELECT MIN(published) FROM collector_document WHERE dataset_id=15)::date)::int4 as day_id,
	(SELECT signal FROM collector_probe WHERE target=url AND tag='vi') as views,
	(SELECT signal FROM collector_probe WHERE target=url AND tag='tw') as twits,
	(SELECT signal FROM collector_probe WHERE target=url AND tag='co') as comms
FROM collector_document WHERE dataset_id=15) as docs
ORDER BY day_id;


-- year - EXTRACT(MONTH FROM published) as month_id,
-- year - EXTRACT(DAY FROM published) as day_id








