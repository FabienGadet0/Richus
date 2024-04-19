WITH RankedCoefficients AS (
    SELECT
        item_id,
        server_id,
        coefficient,
        last_updated,
        ROW_NUMBER() OVER (PARTITION BY item_id ORDER BY last_updated DESC) AS rn
    FROM
        bronze_brisage_coeff_history
)
SELECT
    item_id,
    coefficient
FROM
    RankedCoefficients
WHERE
    rn = 1
