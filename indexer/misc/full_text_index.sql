ALTER TABLE news ADD COLUMN news_fts_col tsvector;
UPDATE news SET news_fts_col =
	to_tsvector('english', title || ' ' || short_text  || ' ' || full_text);
CREATE INDEX news_fts_idx ON news USING gin(news_fts_col);