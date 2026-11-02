"""Five business cases from the PDF's linked case-study document."""

CASES = {
    "1. Transaction dynamics": {
        "question": "Which payment categories contribute the most transactions?",
        "sql": """SELECT category,
       SUM(transaction_count) AS transactions,
       SUM(amount) AS value_inr,
       ROUND(100.0 * SUM(transaction_count) /
           (SELECT SUM(transaction_count) FROM aggregated_transaction
            WHERE year = ? AND quarter = ?), 2) AS share_percent
FROM aggregated_transaction
WHERE year = ? AND quarter = ?
GROUP BY category
ORDER BY transactions DESC;""",
        "repeat_parameters": True,
        "recommendation": "Prioritize reliability and capacity for the leading category; investigate smaller categories before investing in expansion.",
    },
    "3. Insurance growth potential": {
        "question": "How many insurance transactions occur per 1,000 registered users in each state?",
        "sql": """SELECT i.state,
       SUM(i.transaction_count) AS insurance_transactions,
       u.registered_users,
       ROUND(1000.0 * SUM(i.transaction_count) /
             NULLIF(u.registered_users, 0), 2) AS transactions_per_1000_users
FROM aggregated_insurance AS i
JOIN aggregated_user AS u
  ON i.state = u.state AND i.year = u.year AND i.quarter = u.quarter
WHERE i.year = ? AND i.quarter = ?
GROUP BY i.state, u.registered_users
ORDER BY transactions_per_1000_users ASC;""",
        "recommendation": "Consider awareness campaigns in states with many users and low insurance activity. This ratio measures transactions, not the percentage of users insured.",
    },
    "5. User engagement": {
        "question": "Which states have the highest app opens per registered user?",
        "sql": """SELECT state, registered_users, app_opens,
       ROUND(1.0 * app_opens / NULLIF(registered_users, 0), 2)
           AS opens_per_registered_user
FROM aggregated_user
WHERE year = ? AND quarter = ?
ORDER BY opens_per_registered_user DESC;""",
        "recommendation": "Investigate low-engagement states for usability or onboarding improvements. App opens are events; they are not unique active users.",
    },
    "7. State and district performance": {
        "question": "Which districts have the greatest transaction value?",
        "sql": """SELECT state, district, transaction_count,
       amount AS value_inr,
       ROUND(amount / NULLIF(transaction_count, 0), 2) AS average_value_inr
FROM map_map
WHERE year = ? AND quarter = ?
ORDER BY amount DESC
LIMIT 10;""",
        "recommendation": "Use leading districts to prioritize service capacity and merchant support. Compare smaller districts using growth and user counts before selecting expansion areas.",
    },
    "9. Insurance PIN-code leaders": {
        "question": "Which published national top PIN codes have the most insurance transactions?",
        "sql": """SELECT entity_name AS pin_code,
       transaction_count AS insurance_transactions,
       amount AS value_inr
FROM top_insurance
WHERE year = ? AND quarter = ?
  AND scope_state = 'india' AND entity_type = 'pincodes' AND entity_name IS NOT NULL
ORDER BY transaction_count DESC
LIMIT 10;""",
        "recommendation": "Study the published leaders as candidate locations for insurance support. Top lists are incomplete subsets and cannot describe all PIN codes.",
    },
}
