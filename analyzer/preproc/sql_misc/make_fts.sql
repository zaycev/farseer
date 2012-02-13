-- This code adds new redundant column containing
-- data for fast full text search. Target table is
-- news while target columns(for indexing) are title,
-- short_text and full_text. The second command
-- generate gin index for redundant column
-- for PostgreSQL >= 9.0 only. For more information,
-- visit http://www.postgresql.org/docs/9.1/static/textsearch.html

ALTER TABLE news ADD COLUMN news_fts_col tsvector;
UPDATE news SET news_fts_col =
	to_tsvector('english', title || ' ' || short_text  || ' ' || full_text);
CREATE INDEX news_fts_idx ON news USING gin(news_fts_col);