"""Render every email template to HTML and screenshot it (light + dark client, 640 and 375 px).

Usage (from backend/):
    .venv/Scripts/python scripts/render_emails.py <out_dir>            # write the .html files
    python scripts/render_emails.py <out_dir> --shots                  # screenshot them (any Python with Playwright)
Sample data only; nothing is sent.
"""

import sys
from pathlib import Path

NAMES = ["task-due", "task-overdue", "task-assigned", "daily-digest", "weekly-summary", "welcome"]


def samples():
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from app.services.email_service import EmailTemplates

    return {
        "task-due": lambda: EmailTemplates.task_due("Send the Q4 report draft to Sara", "Thu 29 Oct, 17:00", "/dashboard?task=12", "tok"),
        "task-overdue": lambda: EmailTemplates.task_overdue("Call the bank about the card limit", "Tue 27 Oct, 10:00", "/dashboard?task=7", "tok"),
        "task-assigned": lambda: EmailTemplates.task_assigned("Prepare slides for Thursday standup", "Kairos", "/dashboard?task=9", "tok"),
        "daily-digest": lambda: EmailTemplates.daily_digest([
        {"title": "Send the Q4 report draft to Sara", "due_date": "Today 17:00"},
        {"title": "Buy milk, eggs and rice", "due_date": "Today 19:30"},
        {"title": "Water the plants", "due_date": "Today 13:00", "completed": True},
        {"title": "Read two chapters of Atomic Habits", "due_date": None},
    ]),
        "weekly-summary": lambda: EmailTemplates.weekly_summary({"completed": 12, "pending": 5, "overdue": 1}),
        "welcome": lambda: EmailTemplates.welcome("ayla@example.test", "Ayla", "tok"),
    }


def main() -> None:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    if "--shots" not in sys.argv:
        for name, build in samples().items():
            (out / f"{name}.html").write_text(build(), encoding="utf-8")
        print("wrote", len(NAMES), "emails to", out)
        return

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for scheme in ("light", "dark"):
            for width in (640, 375):
                page = browser.new_page(viewport={"width": width, "height": 900}, color_scheme=scheme)
                for name in NAMES:
                    page.goto((out / f"{name}.html").resolve().as_uri())
                    page.wait_for_timeout(150)
                    page.screenshot(path=str(out / f"{name}-{width}-{scheme}.jpg"), type="jpeg", quality=62, full_page=True)
                page.close()
        browser.close()
    print("screenshots in", out)


if __name__ == "__main__":
    main()
