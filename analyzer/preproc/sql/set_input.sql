-- After running collector app still remains a lot of duplicate rows (tasks).
-- To easily remove them, use one of the following SQL commands.
-- This code removes rows with the same post_uri value
-- and remains one row with higher id value.
-- (c) found on stackoverflow.com

-- very slow on relatively big tables
DELETE FROM news_all
WHERE id NOT IN
	(SELECT MIN(id) FROM news T2
	WHERE T2.uri=news_all.uri);

-- this one works much faster
DELETE task_topic_raw
FROM task_topic_raw T1, task_topic_raw T2
WHERE
	T1.post_uri = T2.post_uri
	AND T1.id > T2.id;

---
DELETE FROM news_all
WHERE EXISTS (
	SELECT id
	FROM news_all T2
	WHERE T2.uri = news_all.uri
	AND T2.id < news_all.id);

---
INSERT INTO news_all
	(meta_name,
	meta_time,
	meta_fails,
	meta_handle,
	river_uri,
	uri,
	title,
	time,
	views,
	comments,
	short_text,
	image_uri,
	full_text,
	response_fb_com,
	response_fb_shr,
	response_tw,
	response_su,
	response_dg,
	response_li,
	response_raw_fb,
	response_raw_tw,
	response_raw_su,
	response_raw_dg,
	response_raw_li)
	SELECT
		meta_name,
		meta_time,
		meta_fails,
		meta_handle,
		river_uri,
		uri,
		title,
		time,
		views,
		comments,
		short_text,
		image_uri,
		full_text,
		response_fb_com,
		response_fb_shr,
		response_tw,
		response_su,
		response_dg,
		response_li,
		response_raw_fb,
		response_raw_tw,
		response_raw_su,
		response_raw_dg,
		response_raw_li
	FROM news_1;

SELECT
	date_trunc('month', time) AS month,
	COUNT(id) AS stories,
	SUM(response_fb_shr) AS likes,
	SUM(response_tw) AS retwitts,
	SUM(response_dg) AS diggs,
	SUM(response_su) AS stamble_upon,
	SUM(response_li) AS linkedin
FROM
	news_all
GROUP BY
	date_trunc('month', time) ORDER BY date_trunc('month', time);

-- This code adds new redundant column containing
-- data for fast full text search. Target table is
-- set_input while do columns(for indexing) are
-- title, short_text and full_text. The second command
-- generate GIN index for redundant column
-- for PostgreSQL >= 8.3 only. For more information,
-- visit http://www.postgresql.org/docs/9.1/static/textsearch.html

ALTER TABLE set_input ADD COLUMN fts tsvector;
UPDATE set_input SET fts =
	to_tsvector('english', title || ' ' || short_text  || ' ' || full_text);
CREATE INDEX set_input_fts_idx ON set_input USING gin(fts);

BEGIN;
CREATE SEQUENCE input_id_tmpseq INCREMENT 1 START WITH 1;
UPDATE set_input 
SET id = set_ordered.id
FROM
	(	SELECT nextval('input_id_tmpseq'::regclass) as id,uri
		FROM set_input
		ORDER BY time ASC) AS set_ordered
WHERE set_input.uri = set_ordered.uri;
DROP SEQUENCE input_id_tmpseq;
COMMIT;