from collections import Counter
from datetime import datetime
from html import escape

from app.models.job import JobPosting


def _fmt_datetime(value: datetime | None) -> str:
    if value is None:
        return "N/A"
    return value.strftime("%Y-%m-%d")


def _fmt_salary(job: JobPosting) -> str:
    if job.salary_min is None and job.salary_max is None:
        return "N/A"
    currency = job.salary_currency or ""
    if job.salary_min is not None and job.salary_max is not None:
        return f"{currency} {job.salary_min:,} - {job.salary_max:,}".strip()
    if job.salary_min is not None:
        return f"{currency} {job.salary_min:,}+".strip()
    return f"Up to {currency} {job.salary_max:,}".strip()


def _render_stat_list(title: str, values: dict[str, int]) -> str:
    if not values:
        items = "<li>No data yet</li>"
    else:
        items = "".join(
            f"<li><span>{escape(str(key))}</span><strong>{value}</strong></li>"
            for key, value in values.items()
        )
    return f"""
    <section class="panel">
      <h3>{escape(title)}</h3>
      <ul class="stat-list">{items}</ul>
    </section>
    """


def render_dashboard_html(
    stats: dict,
    jobs: list[JobPosting],
    filters: dict[str, str | bool | int | None],
) -> str:
    top_skills = Counter(
        skill
        for job in jobs
        for skill in (job.skills or [])
    ).most_common(8)
    skill_badges = (
        "".join(
            f'<span class="skill-pill">{escape(skill)} <strong>{count}</strong></span>'
            for skill, count in top_skills
        )
        or '<span class="muted">No skills extracted yet</span>'
    )

    job_rows = "".join(
        f"""
        <tr>
          <td>
            <div class="job-title">{escape(job.title)}</div>
            <div class="job-meta">{escape(job.company_name or "Unknown company")}</div>
          </td>
          <td>{escape(job.source)}</td>
          <td>{escape(job.remote_type or "N/A")}</td>
          <td>{escape(job.seniority or "N/A")}</td>
          <td>{escape(job.location_text or "N/A")}</td>
          <td>{escape(_fmt_salary(job))}</td>
          <td>{_fmt_datetime(job.last_seen_at)}</td>
          <td>{('<a href="' + escape(job.apply_url) + '" target="_blank" rel="noreferrer">Apply</a>') if job.apply_url else "N/A"}</td>
        </tr>
        """
        for job in jobs
    )
    if not job_rows:
        job_rows = """
        <tr>
          <td colspan="8" class="empty-state">No jobs match the current filters.</td>
        </tr>
        """

    source = escape(str(filters.get("source") or ""))
    q = escape(str(filters.get("q") or ""))
    remote_type = escape(str(filters.get("remote_type") or ""))
    seniority = escape(str(filters.get("seniority") or ""))
    active_only = "checked" if filters.get("active_only", True) else ""

    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Labor Market Intelligence Dashboard</title>
    <style>
      :root {{
        --bg: #f4f0e8;
        --paper: #fffdf8;
        --ink: #1f2937;
        --muted: #5b6470;
        --line: #d9cfbf;
        --brand: #0f766e;
        --brand-soft: #dff4ef;
        --accent: #b45309;
        --accent-soft: #fef0c7;
        --shadow: 0 16px 40px rgba(63, 40, 20, 0.10);
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: Georgia, "Times New Roman", serif;
        background:
          radial-gradient(circle at top left, rgba(180, 83, 9, 0.10), transparent 28%),
          radial-gradient(circle at top right, rgba(15, 118, 110, 0.10), transparent 24%),
          var(--bg);
        color: var(--ink);
      }}
      .shell {{
        max-width: 1280px;
        margin: 0 auto;
        padding: 32px 20px 48px;
      }}
      .hero {{
        background: linear-gradient(135deg, rgba(255,255,255,0.94), rgba(250,244,236,0.98));
        border: 1px solid var(--line);
        border-radius: 28px;
        box-shadow: var(--shadow);
        padding: 28px;
        margin-bottom: 24px;
      }}
      .hero-kicker {{
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: var(--brand-soft);
        color: var(--brand);
        font-size: 13px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
      }}
      h1 {{
        margin: 14px 0 10px;
        font-size: clamp(2rem, 5vw, 3.8rem);
        line-height: 0.95;
      }}
      .hero p {{
        max-width: 72ch;
        color: var(--muted);
        font-size: 1.02rem;
        line-height: 1.65;
      }}
      .grid {{
        display: grid;
        gap: 18px;
      }}
      .metrics {{
        grid-template-columns: repeat(4, minmax(0, 1fr));
        margin-bottom: 20px;
      }}
      .metric-card, .panel {{
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: 22px;
        box-shadow: var(--shadow);
      }}
      .metric-card {{
        padding: 20px;
      }}
      .metric-label {{
        color: var(--muted);
        font-size: 0.92rem;
      }}
      .metric-value {{
        margin-top: 8px;
        font-size: clamp(1.8rem, 4vw, 2.6rem);
        font-weight: 700;
      }}
      .metric-note {{
        margin-top: 6px;
        color: var(--muted);
        font-size: 0.9rem;
      }}
      .content {{
        grid-template-columns: 320px minmax(0, 1fr);
        align-items: start;
      }}
      .sidebar {{
        display: grid;
        gap: 18px;
      }}
      .panel {{
        padding: 20px;
      }}
      .panel h2, .panel h3 {{
        margin: 0 0 14px;
      }}
      form {{
        display: grid;
        gap: 12px;
      }}
      label {{
        display: grid;
        gap: 6px;
        color: var(--muted);
        font-size: 0.92rem;
      }}
      input, select {{
        width: 100%;
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 11px 12px;
        background: #fff;
        color: var(--ink);
        font: inherit;
      }}
      .checkbox-row {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding-top: 4px;
      }}
      .checkbox-row input {{
        width: auto;
      }}
      .actions {{
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 4px;
      }}
      .btn {{
        border: 0;
        border-radius: 999px;
        padding: 11px 16px;
        font: inherit;
        cursor: pointer;
        text-decoration: none;
      }}
      .btn-primary {{
        background: var(--brand);
        color: #fff;
      }}
      .btn-secondary {{
        background: var(--accent-soft);
        color: #7c2d12;
      }}
      .skill-wrap {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
      }}
      .skill-pill {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 999px;
        background: #f7f2e8;
        border: 1px solid var(--line);
        font-size: 0.95rem;
      }}
      .stat-list {{
        list-style: none;
        margin: 0;
        padding: 0;
        display: grid;
        gap: 10px;
      }}
      .stat-list li {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding-bottom: 10px;
        border-bottom: 1px dashed var(--line);
      }}
      .table-card {{
        overflow: hidden;
      }}
      .table-head {{
        padding: 20px 22px 10px;
      }}
      .table-head h2 {{
        margin: 0;
      }}
      .table-head p {{
        margin: 8px 0 0;
        color: var(--muted);
      }}
      .table-wrap {{
        overflow-x: auto;
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
      }}
      th, td {{
        text-align: left;
        padding: 14px 22px;
        border-top: 1px solid rgba(217, 207, 191, 0.75);
        vertical-align: top;
      }}
      th {{
        font-size: 0.86rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: var(--muted);
        background: rgba(244, 240, 232, 0.65);
      }}
      .job-title {{
        font-weight: 700;
        margin-bottom: 4px;
      }}
      .job-meta {{
        color: var(--muted);
        font-size: 0.92rem;
      }}
      .empty-state {{
        text-align: center;
        color: var(--muted);
        padding: 28px;
      }}
      a {{
        color: var(--brand);
      }}
      .muted {{
        color: var(--muted);
      }}
      @media (max-width: 980px) {{
        .metrics {{
          grid-template-columns: repeat(2, minmax(0, 1fr));
        }}
        .content {{
          grid-template-columns: 1fr;
        }}
      }}
      @media (max-width: 640px) {{
        .shell {{
          padding: 18px 14px 28px;
        }}
        .hero, .panel, .metric-card {{
          border-radius: 18px;
          padding: 18px;
        }}
        .metrics {{
          grid-template-columns: 1fr;
        }}
        th, td {{
          padding: 12px 14px;
        }}
      }}
    </style>
  </head>
  <body>
    <main class="shell">
      <section class="hero">
        <span class="hero-kicker">Phase 1 dashboard</span>
        <h1>Labor Market Intelligence Dashboard</h1>
        <p>
          A first operational dashboard layer for exploring ingested jobs, checking health signals,
          validating enrichment, and spotting early market patterns directly from the FastAPI app.
        </p>
      </section>

      <section class="grid metrics">
        <article class="metric-card">
          <div class="metric-label">Total jobs</div>
          <div class="metric-value">{stats["total_jobs"]}</div>
          <div class="metric-note">Canonical records stored</div>
        </article>
        <article class="metric-card">
          <div class="metric-label">Active jobs</div>
          <div class="metric-value">{stats["active_jobs"]}</div>
          <div class="metric-note">Currently visible in source systems</div>
        </article>
        <article class="metric-card">
          <div class="metric-label">Inactive jobs</div>
          <div class="metric-value">{stats["inactive_jobs"]}</div>
          <div class="metric-note">Tracked through historical snapshots</div>
        </article>
        <article class="metric-card">
          <div class="metric-label">Jobs in view</div>
          <div class="metric-value">{len(jobs)}</div>
          <div class="metric-note">Current filtered result set</div>
        </article>
      </section>

      <section class="grid content">
        <aside class="sidebar">
          <section class="panel">
            <h2>Filters</h2>
            <form method="get" action="/dashboard">
              <label>
                Search
                <input type="text" name="q" value="{q}" placeholder="python, backend, remote..." />
              </label>
              <label>
                Source
                <input type="text" name="source" value="{source}" placeholder="greenhouse" />
              </label>
              <label>
                Remote type
                <select name="remote_type">
                  <option value="">All</option>
                  <option value="remote" {"selected" if remote_type == "remote" else ""}>Remote</option>
                  <option value="hybrid" {"selected" if remote_type == "hybrid" else ""}>Hybrid</option>
                  <option value="onsite" {"selected" if remote_type == "onsite" else ""}>Onsite</option>
                </select>
              </label>
              <label>
                Seniority
                <select name="seniority">
                  <option value="">All</option>
                  <option value="junior" {"selected" if seniority == "junior" else ""}>Junior</option>
                  <option value="mid" {"selected" if seniority == "mid" else ""}>Mid</option>
                  <option value="senior" {"selected" if seniority == "senior" else ""}>Senior</option>
                  <option value="management" {"selected" if seniority == "management" else ""}>Management</option>
                </select>
              </label>
              <label class="checkbox-row">
                <input type="checkbox" name="active_only" value="true" {active_only} />
                Show only active jobs
              </label>
              <div class="actions">
                <button class="btn btn-primary" type="submit">Apply filters</button>
                <a class="btn btn-secondary" href="/dashboard">Reset</a>
              </div>
            </form>
          </section>
          <section class="panel">
            <h2>Top skills in current view</h2>
            <div class="skill-wrap">{skill_badges}</div>
          </section>
          {_render_stat_list("By source", stats.get("by_source", {}))}
          {_render_stat_list("By remote type", stats.get("by_remote_type", {}))}
          {_render_stat_list("By seniority", stats.get("by_seniority", {}))}
        </aside>

        <section class="panel table-card">
          <div class="table-head">
            <h2>Recent jobs</h2>
            <p>Use this view to validate ingestion quality, enrichment coverage, and current market slices.</p>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Role</th>
                  <th>Source</th>
                  <th>Remote</th>
                  <th>Seniority</th>
                  <th>Location</th>
                  <th>Salary</th>
                  <th>Last seen</th>
                  <th>Link</th>
                </tr>
              </thead>
              <tbody>
                {job_rows}
              </tbody>
            </table>
          </div>
        </section>
      </section>
    </main>
  </body>
</html>"""

