-- ============================================================
-- Trading Analytics - Edge Analysis Queries
-- Author : Neema Urassa
-- Database: trading_analytics
-- ============================================================

-- Q1: Overall win rate and R:R metrics

SELECT 
    COUNT(*) AS total_trades,
    ROUND(100.0 * AVG(is_win:: INT),1) AS win_rate_pct, 
    ROUND (AVG(duration_mins)::NUMERIC, 1)  AS avg_hold_mins,
    ROUND(
        ABS(AVG(net_profit) FILTER (WHERE is_win)/ 
        NULLIF (AVG(net_profit) FILTER (WHERE NOT is_win),0 ))
    :: NUMERIC,2) AS risk_reward_ratio
    ROUND(
        SUM(net_profit) FILTER (WHERE is_win)/
        NULLIF(ABS(SUM(net_profit) FILTER (WHERE NOT is_win)), 0)
    ::NUMERIC, 2)  AS profit_factor
FROM trades;

-- Q2: Win rate and edge score by asset class

SELECT 
    asset_class, 
    COUNT(*) AS trades,
    ROUND(100.0 * AVG(is_win::INT),1) AS win_rate_pct,
    ROUND (COUNT(*) * AVG(is_win:: INT),1 ) AS edge_score

FROM trades
GROUP BY asset_class
ORDER BY win_rate_pct DESC; 

-- Q3: Instrument-level edge (min 10 trades)
SELECT
    instrument,
    asset_class,
    COUNT(*)                                        AS trades,
    ROUND(100.0 * AVG(is_win::INT), 1)              AS win_rate_pct,
    ROUND(COUNT(*) * AVG(is_win::INT), 1)           AS edge_score,
    ROUND(AVG(duration_mins)::NUMERIC, 1)                    AS avg_hold_mins
FROM trades
GROUP BY instrument, asset_class
HAVING COUNT(*) >= 10
ORDER BY win_rate_pct DESC;

-- Q4: Win rate by session
SELECT
    session,
    COUNT(*)                                        AS trades,
    ROUND(100.0 * AVG(is_win::INT), 1)              AS win_rate_pct,
    ROUND(COUNT(*) * AVG(is_win::INT), 1)           AS edge_score
FROM trades
GROUP BY session
ORDER BY win_rate_pct DESC;


-- Q5: Win rate by day of week
SELECT
    TO_CHAR(open_time, 'Day')                       AS day_of_week,
    EXTRACT(DOW FROM open_time)                     AS dow_num,
    COUNT(*)                                        AS trades,
    ROUND(100.0 * AVG(is_win::INT), 1)              AS win_rate_pct
FROM trades
WHERE EXTRACT(DOW FROM open_time) BETWEEN 1 AND 5
GROUP BY 1, 2
ORDER BY 2;


-- Q6: Hold duration vs win rate
SELECT
    CASE
        WHEN duration_mins < 15   THEN '1. Scalp (< 15 min)'
        WHEN duration_mins < 60   THEN '2. Short (15-60 min)'
        WHEN duration_mins < 240  THEN '3. Intraday (1-4 hrs)'
        WHEN duration_mins < 1440 THEN '4. Swing (4-24 hrs)'
        ELSE                           '5. Position (> 1 day)'
    END                                             AS duration_bucket,
    COUNT(*)                                        AS trades,
    ROUND(100.0 * AVG(is_win::INT), 1)              AS win_rate_pct
FROM trades
GROUP BY 1
ORDER BY 1;


-- Q7: Concentrated portfolio simulation
-- Only instruments with win rate > 55% and min 10 trades
WITH high_edge AS (
    SELECT instrument
    FROM trades
    GROUP BY instrument
    HAVING COUNT(*) >= 10
    AND AVG(is_win::INT) >= 0.55
)
SELECT
    'Full Portfolio'                                AS portfolio,
    COUNT(*)                                        AS trades,
    ROUND(100.0 * AVG(is_win::INT), 1)              AS win_rate_pct
FROM trades
UNION ALL
SELECT
    'Concentrated Portfolio'                        AS portfolio,
    COUNT(*)                                        AS trades,
    ROUND(100.0 * AVG(is_win::INT), 1)              AS win_rate_pct
FROM trades
WHERE instrument IN (SELECT instrument FROM high_edge);


-- Q8: Buy vs Sell win rate
SELECT
    trade_type,
    COUNT(*)                                        AS trades,
    ROUND(100.0 * AVG(is_win::INT), 1)              AS win_rate_pct,
    ROUND(AVG(duration_mins), 1)                    AS avg_hold_mins
FROM trades
GROUP BY trade_type
ORDER BY win_rate_pct DESC;