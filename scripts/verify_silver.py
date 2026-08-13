import duckdb, os
p = os.path.abspath('data/silver/jobs.parquet').replace('\\', '/')
c = duckdb.connect(':memory:')
r = c.execute(f"SELECT COUNT(*) as total, SUM(CASE WHEN status='active' THEN 1 ELSE 0 END) as active, SUM(CASE WHEN country='Sri Lanka' THEN 1 ELSE 0 END) as lk, COUNT(DISTINCT role_category) as cats FROM read_parquet('{p}')").fetchone()
print(f"total={r[0]}, active={r[1]}, sri_lanka={r[2]}, role_cats={r[3]}")
top = c.execute(f"SELECT role_category, COUNT(*) as n FROM read_parquet('{p}') WHERE status='active' GROUP BY role_category ORDER BY n DESC LIMIT 8").fetchall()
print("Top role categories:")
for row in top:
    print(f"  {row[0]}: {row[1]}")
sample = c.execute(f"SELECT job_id, title, company, location, country, role_category, first_seen_at, last_seen_at FROM read_parquet('{p}') LIMIT 3").fetchall()
print("Sample records:")
for row in sample:
    print(f"  {row}")
