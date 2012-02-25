SELECT date_trunc('day'::text, set_input."time") AS day,
	count(set_input.id) AS set_size,
	sum(set_input.fb_shr) AS fb_shr,
	sum(set_input.fb_com) AS fb_com,
	sum(set_input.tw) AS tw,
	sum(set_input.dg) AS dg,
	sum(set_input.su) AS su,
	sum(set_input.li) AS li
FROM set_input
GROUP BY date_trunc('day'::text, set_input."time")
ORDER BY date_trunc('day'::text, set_input."time");