"""SQL for the Agency Portfolio snapshot. Run each statement on every client account (Engine 9 MCP `sql`).
Definitions match the Fundraising Report (same dates, same channel rules). Year to date = Jan 1 to today.
Usage: python3 portfolio.py   (prints the one statement to run on every account)"""
import sys
from cls import helpers, cls

JAN1 = "MAKEDATE(YEAR(CURDATE()), 1)"
TODAY1 = "(CURDATE() + INTERVAL 1 DAY)"
H = helpers('d.source_code', 'd.source_code_channel')
BASE = ("(SELECT m.id, m.person_id, m.ts, m.amount, m.recurs_id, d.source_code AS transaction_source_code, "
        f"d.source_code_channel, g.channel, {H} FROM `transaction` m "
        "LEFT JOIN source_code_dictionary d ON d.source_code_id = m.final_source_code_id "
        "LEFT JOIN global_message g ON g.id = m.final_message_id")

# One row per account. Scalars plus two packed strings: chan = "channel:this year:last year|...", mon = "month:this year:last year|...".
# Last-year figures stop at today's date a year ago, so they compare like for like.
ONE = f"""
WITH x AS (SELECT {cls('', 'transaction_source_code')} AS channel, ts, amount,
    ts < CURDATE() + INTERVAL 1 DAY - INTERVAL 1 YEAR AS ly_td FROM {BASE}) q
  WHERE ts >= MAKEDATE(YEAR(CURDATE()) - 1, 1) AND ts < {TODAY1}),
ch AS (SELECT channel, ROUND(SUM(CASE WHEN ts >= {JAN1} THEN amount ELSE 0 END), 2) AS ty,
    ROUND(SUM(CASE WHEN ts < {JAN1} AND ly_td THEN amount ELSE 0 END), 2) AS ly FROM x GROUP BY channel),
mo AS (SELECT MONTH(ts) AS m, ROUND(SUM(CASE WHEN ts >= {JAN1} THEN amount ELSE 0 END), 2) AS ty,
    ROUND(SUM(CASE WHEN ts < {JAN1} AND ly_td THEN amount ELSE 0 END), 2) AS ly FROM x GROUP BY MONTH(ts)),
t AS (SELECT YEAR(CURDATE()) - YEAR(ts) AS y,
    ts < CURDATE() + INTERVAL 1 DAY - INTERVAL (YEAR(CURDATE()) - YEAR(ts)) YEAR AS to_date, amount
  FROM `transaction` WHERE (ts >= MAKEDATE(YEAR(CURDATE()) - 1, 1) AND ts < {TODAY1})
     OR (ts >= MAKEDATE(YEAR(CURDATE()) - 4, 1) AND ts < MAKEDATE(YEAR(CURDATE()) - 3, 1))),
p AS (SELECT ROUND(SUM(CASE WHEN y = 0 THEN amount ELSE 0 END), 2) AS ytd, SUM(y = 0) AS gifts_ytd,
    ROUND(SUM(CASE WHEN y = 1 AND to_date THEN amount ELSE 0 END), 2) AS ly_ytd,
    ROUND(SUM(CASE WHEN y = 1 AND NOT to_date THEN amount ELSE 0 END), 2) AS ly_rest,
    ROUND(SUM(CASE WHEN y = 4 AND to_date THEN amount ELSE 0 END), 2) AS mt_ytd,
    ROUND(SUM(CASE WHEN y = 4 AND NOT to_date THEN amount ELSE 0 END), 2) AS mt_rest FROM t),
nd AS (SELECT SUM(k.y = 0) AS new_ty, SUM(k.y = 1) AS new_ly FROM
    (SELECT YEAR(CURDATE()) - YEAR(MIN(ts)) AS y, MIN(ts) AS f FROM `transaction` WHERE person_id IS NOT NULL GROUP BY person_id) k
  WHERE (k.y = 0 AND k.f < {TODAY1}) OR (k.y = 1 AND k.f < CURDATE() + INTERVAL 1 DAY - INTERVAL 1 YEAR)),
rr AS (SELECT ROUND(COALESCE(SUM(amount), 0), 2) AS run_rate, COUNT(*) AS rec_donors FROM
    (SELECT amount, ROW_NUMBER() OVER (PARTITION BY person_id ORDER BY ts DESC) AS rn FROM `transaction`
     WHERE recurs_id > 0 AND person_id IS NOT NULL AND ts >= CURDATE() - INTERVAL 35 DAY AND ts < {TODAY1}) z WHERE rn = 1)
SELECT p.*, nd.new_ty, nd.new_ly, rr.run_rate, rr.rec_donors,
  (SELECT ROUND(COALESCE(SUM(ty), 0), 2) FROM ch WHERE channel IN ('Text (SMS)', 'Meta ads', 'Google ads', 'Paid ads (coded)')) AS ta_rev,
  (SELECT ROUND(COALESCE(SUM(ty), 0), 2) FROM ch WHERE channel IN ('No source code', 'Other source code')) AS unattrib,
  (SELECT ROUND(COALESCE(SUM(ty), 0), 2) FROM ch) AS all_rev,
  ROUND((SELECT COALESCE(SUM(spend), 0) FROM global_message_summary WHERE channel = 'sms' AND publish_date >= {JAN1})
   + (SELECT COALESCE(SUM(COALESCE(spend_override, spend)), 0) FROM global_message_summary_by_date WHERE RIGHT(channel, 3) = '_ad' AND date >= {JAN1}), 2) AS ta_cost,
  (SELECT DATE_FORMAT(MIN(ts), '%Y-%m-%d') FROM `transaction` WHERE ts > '2000-01-01') AS first_gift,
  DATEDIFF(MAKEDATE(YEAR(CURDATE()) + 1, 1), CURDATE()) - 1 AS days_left, CURDATE() AS as_of,
  (SELECT GROUP_CONCAT(CONCAT(channel, ':', ty, ':', ly) SEPARATOR '|') FROM ch) AS chan,
  (SELECT GROUP_CONCAT(CONCAT(m, ':', ty, ':', ly) ORDER BY m SEPARATOR '|') FROM mo) AS mon
FROM p, nd, rr
"""
if __name__ == '__main__':
    print(ONE.strip())
