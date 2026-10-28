"""Capture every app surface (pages, dialogs, menus, popovers, states) for design review.

Usage (frontend dev server on :3100, backend on :8100, signed-in test account):
    python scripts/capture-ui.py <out_dir> [--quick]

Reads the test account from the git-ignored .env.local comments (TEST_USER_EMAIL / TEST_USER_PASSWORD).
Writes JPEGs named <surface>-<width>-<theme>.jpg. --quick limits to 1440 and 375 px; --widths=320,768
picks widths; --only=dashboard|pages|error|gallery runs one group.
"""

import re
import sys
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

BASE = "http://localhost:3100"
WIDTHS = {1440: 900, 768: 1024, 375: 812, 320: 640}
THEMES = ("dark", "light")


def creds() -> tuple[str, str]:
    text = (Path(__file__).resolve().parent.parent / ".env.local").read_text(encoding="utf-8")
    email = re.search(r"TEST_USER_EMAIL=(\S+)", text).group(1)
    password = re.search(r"TEST_USER_PASSWORD=(\S+)", text).group(1)
    return email, password


def shot(page: Page, out: Path, name: str, width: int, theme: str, full: bool = False) -> None:
    page.wait_for_timeout(450)  # let enter animations settle
    page.screenshot(path=str(out / f"{name}-{width}-{theme}.jpg"), type="jpeg", quality=62, full_page=full)


def close_layers(page: Page) -> None:
    for _ in range(3):
        page.keyboard.press("Escape")
        page.wait_for_timeout(120)


def dashboard_states(page: Page, out: Path, width: int, theme: str, quick: bool) -> None:
    page.goto(f"{BASE}/dashboard")
    page.wait_for_selector("text=My tasks")
    page.wait_for_timeout(900)
    shot(page, out, "dashboard", width, theme)

    # Task actions menu, then the delete confirmation
    page.get_by_role("button", name="Task actions").first.click()
    shot(page, out, "task-menu", width, theme)
    page.get_by_role("menuitem", name=re.compile("Delete")).click()
    shot(page, out, "delete-dialog", width, theme)
    close_layers(page)

    # Add task dialog, its selects and the due date popover
    page.get_by_role("button", name=re.compile("Add task", re.I)).first.click()
    page.wait_for_selector("[role=dialog]")
    shot(page, out, "task-dialog", width, theme)
    page.locator("[role=dialog] [role=combobox]").first.click()
    shot(page, out, "form-select", width, theme)
    page.keyboard.press("Escape")
    page.get_by_role("button", name=re.compile("date", re.I)).first.click()
    shot(page, out, "due-date-popover", width, theme)
    close_layers(page)

    # Toolbar select (sort)
    page.get_by_role("combobox").nth(1).click()
    shot(page, out, "sort-select", width, theme)
    close_layers(page)

    # Account menu and notifications
    page.get_by_role("button", name="Account menu").click()
    shot(page, out, "account-menu", width, theme)
    close_layers(page)
    page.get_by_role("button", name=re.compile("^Notifications")).click()
    shot(page, out, "notifications", width, theme)
    close_layers(page)

    if quick and width not in (1440, 375):
        return

    # Filtered to nothing: empty state
    page.get_by_role("searchbox", name="Search tasks").fill("zzzz-no-match")
    page.wait_for_timeout(900)  # debounce + fade
    shot(page, out, "empty-filtered", width, theme)
    page.get_by_role("searchbox", name="Search tasks").fill("")


def error_states(page: Page, out: Path, width: int, theme: str) -> None:
    # Slow task list: the loading state
    tasks_url = re.compile(r".*:8100/api/tasks.*")

    held = []  # requests left hanging so the spinner stays up

    page.route(tasks_url, lambda route: held.append(route))
    page.goto(f"{BASE}/dashboard")
    page.wait_for_timeout(1500)
    shot(page, out, "dashboard-loading", width, theme)
    page.unroute_all(behavior="ignoreErrors")

    # Push permission prompt (shown 3 s after load when the browser has not been asked)
    page.goto(f"{BASE}/dashboard?pushmodal=1")
    page.wait_for_timeout(4500)
    if page.locator("[role=dialog]").count():
        shot(page, out, "push-modal", width, theme)
    close_layers(page)

    # Task list fails to load: the inline error card
    def fail(route):
        if route.request.method == "GET":
            return route.fulfill(status=500, body='{"detail":"boom"}', content_type="application/json")
        return route.continue_()

    page.route(tasks_url, fail)
    page.goto(f"{BASE}/dashboard")
    page.wait_for_timeout(9000)  # the client retries with backoff before the error shows
    shot(page, out, "dashboard-error", width, theme)
    page.unroute(tasks_url)


def pages(page: Page, out: Path, width: int, theme: str) -> None:
    page.goto(f"{BASE}/profile")
    page.wait_for_timeout(900)
    shot(page, out, "profile", width, theme, full=True)
    for tab in ("push", "email", "in-app"):
        page.goto(f"{BASE}/settings/notifications?tab={tab}")
        page.wait_for_timeout(1200)
        shot(page, out, f"settings-{tab}", width, theme, full=True)
        if tab == "push":
            buttons = page.get_by_role("button", name=re.compile("Check permission|Refresh Status"))
            if buttons.count():
                buttons.first.click()
                page.wait_for_timeout(300)
                shot(page, out, "toast", width, theme)
        if tab == "email":
            switches = page.get_by_role("switch")
            if switches.count():
                switches.last.click()
                page.wait_for_timeout(400)
                shot(page, out, "settings-email-unsaved", width, theme)


def gallery(page: Page, out: Path, width: int, theme: str) -> None:
    """Optional: a local /dev-preview page with hard-to-reach states (not part of the app)."""
    if page.goto(f"{BASE}/dev-preview").status != 200:
        return
    page.wait_for_timeout(1200)
    shot(page, out, "gallery", width, theme, full=True)
    page.goto(f"{BASE}/dev-preview?modal=1")
    page.wait_for_timeout(900)
    shot(page, out, "push-modal", width, theme)
    page.goto(f"{BASE}/dev-preview?error=1")
    page.wait_for_timeout(900)
    shot(page, out, "error-page", width, theme)


def main() -> None:
    out = Path(sys.argv[1])
    quick = "--quick" in sys.argv
    only = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--only=")), None)
    out.mkdir(parents=True, exist_ok=True)
    email, password = creds()
    widths = [1440, 375] if quick else list(WIDTHS)
    pick = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--widths=")), None)
    if pick:
        widths = [int(w) for w in pick.split(",")]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for theme in THEMES:
            for width in widths:
                ctx = browser.new_context(viewport={"width": width, "height": WIDTHS[width]}, color_scheme=theme)
                ctx.add_init_script(
                    f"localStorage.setItem('theme', '{theme}');"
                    "if (location.search.includes('pushmodal')) localStorage.removeItem('push_permission_asked');"
                    "else localStorage.setItem('push_permission_asked', 'true');"
                )
                page = ctx.new_page()
                page.goto(f"{BASE}/login")
                page.fill("input[name=email]", email)
                page.fill("input[name=password]", password)
                page.click("button[type=submit]")
                page.wait_for_url("**/dashboard", timeout=30000)
                steps = {
                    "dashboard": lambda: dashboard_states(page, out, width, theme, quick),
                    "pages": lambda: pages(page, out, width, theme),
                    "error": lambda: error_states(page, out, width, theme),
                    "gallery": lambda: gallery(page, out, width, theme),
                }
                for key, step in steps.items():
                    if only and key != only:
                        continue
                    if key == "error" and width not in (1440, 375):
                        continue
                    try:
                        step()
                    except Exception as exc:  # keep going; report what failed
                        print(f"[{theme} {width}] {key} failed: {str(exc).splitlines()[0]}")
                        close_layers(page)
                ctx.close()
                print(f"done {theme} {width}")
        browser.close()


if __name__ == "__main__":
    main()
