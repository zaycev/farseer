-- After running collector app still remains a lot of duplicate rows (tasks).
-- To easily remove them, use one of the following SQL commands.
-- This code removes rows with the same post_uri value
-- and remains one row with higher id value.
-- (c) found on stackoverflow.com

-- very slow on relatively big tables
DELETE FROM task_topic_raw
WHERE id NOT IN
	(SELECT MIN(id) FROM task_topic_raw T2
	WHERE T2.post_uri=task_topic_raw.post_uri);

-- this one works much faster
DELETE task_topic_raw
FROM task_topic_raw T1, task_topic_raw T2
WHERE
	T1.post_uri = T2.post_uri
	AND T1.id > T2.id;
