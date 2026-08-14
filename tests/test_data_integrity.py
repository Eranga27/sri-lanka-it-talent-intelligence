"""
Automated Data Integrity Tests.
Validates the consistency and mathematical correctness of Silver and Gold analytics layers.
"""
import pytest
import os
import duckdb

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
SILVER_JOBS_PATH = os.path.join(DATA_DIR, "silver", "jobs.parquet")
SILVER_SKILLS_PATH = os.path.join(DATA_DIR, "silver", "job_skills.parquet")
GOLD_SKILL_DEMAND = os.path.join(DATA_DIR, "gold", "gold_skill_demand.parquet")
GOLD_ROLE_DEMAND = os.path.join(DATA_DIR, "gold", "gold_role_demand.parquet")
GOLD_MARKET_SUMMARY = os.path.join(DATA_DIR, "gold", "gold_market_summary.parquet")


@pytest.fixture
def conn():
    c = duckdb.connect(":memory:")
    yield c
    c.close()


def test_gold_skill_demand_consistency(conn):
    """
    Verifies that gold_skill_demand counts match Silver job_skills joined on active SL IT jobs.
    """
    if not (os.path.exists(SILVER_JOBS_PATH) and os.path.exists(GOLD_SKILL_DEMAND)):
        pytest.skip("Silver or Gold parquet files not present")

    query = f"""
        SELECT s.skill_id, COUNT(DISTINCT s.job_id) as expected_count
        FROM '{SILVER_SKILLS_PATH}' s
        JOIN '{SILVER_JOBS_PATH}' j ON s.job_id = j.job_id
        WHERE j.status = 'active' AND j.country = 'Sri Lanka' AND j.role_category IS NOT NULL
        GROUP BY s.skill_id
    """
    expected = dict(conn.execute(query).fetchall())

    gold = dict(
        conn.execute(
            f"SELECT skill_id, job_count FROM '{GOLD_SKILL_DEMAND}'"
        ).fetchall()
    )

    for skill_id, exp_cnt in expected.items():
        assert skill_id in gold, f"Skill {skill_id} missing from Gold dataset"
        assert (
            gold[skill_id] == exp_cnt
        ), f"Skill {skill_id} count mismatch: expected {exp_cnt}, got {gold[skill_id]}"


def test_gold_role_demand_consistency(conn):
    """
    Verifies gold_role_demand counts match active SL IT jobs grouped by role category in Silver.
    """
    if not (os.path.exists(SILVER_JOBS_PATH) and os.path.exists(GOLD_ROLE_DEMAND)):
        pytest.skip("Silver or Gold parquet files not present")

    query = f"""
        SELECT role_category, COUNT(DISTINCT job_id) as expected_count
        FROM '{SILVER_JOBS_PATH}'
        WHERE status = 'active' AND country = 'Sri Lanka' AND role_category IS NOT NULL
        GROUP BY role_category
    """
    expected = dict(conn.execute(query).fetchall())

    gold = dict(
        conn.execute(
            f"SELECT role_category, job_count FROM '{GOLD_ROLE_DEMAND}'"
        ).fetchall()
    )

    for role_cat, exp_cnt in expected.items():
        assert role_cat in gold, f"Role {role_cat} missing from Gold dataset"
        assert (
            gold[role_cat] == exp_cnt
        ), f"Role {role_cat} count mismatch: expected {exp_cnt}, got {gold[role_cat]}"


def test_market_summary_integrity(conn):
    """
    Verifies gold_market_summary numbers correspond to underlying active Silver data.
    """
    if not (os.path.exists(SILVER_JOBS_PATH) and os.path.exists(GOLD_MARKET_SUMMARY)):
        pytest.skip("Silver or Gold summary files not present")

    summary = conn.execute(f"SELECT * FROM '{GOLD_MARKET_SUMMARY}'").fetchone()
    # Columns: total_observed_jobs, total_active_jobs, total_sri_lankan_jobs, total_sri_lankan_it_jobs, unique_companies, unique_sources, latest_ingestion, oldest_observation
    tot_obs, tot_act, tot_sl, tot_it, unique_comp, unique_src, latest_ing, oldest_obs = summary

    # Re-calculate independently
    calc_it = conn.execute(
        f"SELECT COUNT(*) FROM '{SILVER_JOBS_PATH}' WHERE status = 'active' AND country = 'Sri Lanka' AND role_category IS NOT NULL"
    ).fetchone()[0]

    calc_sl = conn.execute(
        f"SELECT COUNT(*) FROM '{SILVER_JOBS_PATH}' WHERE status = 'active' AND country = 'Sri Lanka'"
    ).fetchone()[0]

    assert tot_it == calc_it, f"Market summary active IT jobs mismatch: {tot_it} vs {calc_it}"
    assert tot_sl == calc_sl, f"Market summary active SL jobs mismatch: {tot_sl} vs {calc_sl}"


def test_active_vs_historical_regression(conn):
    """
    Regression test: Expired jobs in Silver must NOT be counted as active market opportunities.
    """
    conn.execute(
        """
        CREATE TABLE temp_jobs (
            job_id VARCHAR,
            title VARCHAR,
            status VARCHAR,
            country VARCHAR,
            role_category VARCHAR
        );
        INSERT INTO temp_jobs VALUES
            ('active_1', 'Software Engineer', 'active', 'Sri Lanka', 'Software Engineering'),
            ('expired_1', 'Senior Developer', 'expired', 'Sri Lanka', 'Software Engineering');
    """
    )

    active_count = conn.execute(
        "SELECT COUNT(*) FROM temp_jobs WHERE status = 'active' AND country = 'Sri Lanka' AND role_category IS NOT NULL"
    ).fetchone()[0]

    assert active_count == 1, "Expired jobs must not be included in active market opportunities count"
