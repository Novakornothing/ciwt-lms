"""Desktop and 390px screenshots of Skip What You Know, Help Desk Queue, and Daily Review.

usage: python tools/learner_shots.py OUT --base http://127.0.0.1:5055
"""
import argparse
import os

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('out')
ap.add_argument('--base', required=True)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
BASE = a.base.rstrip('/')


def login(page, email, password):
    page.goto(BASE + '/login', wait_until='networkidle')
    page.fill('input[name=email]', email)
    page.fill('input[name=password]', password)
    page.click('button[type=submit]')
    page.wait_for_load_state('networkidle')


def shot(page, name, width):
    page.wait_for_timeout(250)
    over = page.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth')
    page.screenshot(path=os.path.join(a.out, f'{name}-{width}.png'), full_page=False)
    flag = f' OVERFLOW {over}px' if over > 1 else ''
    print(f'{page.url} {name}-{width}{flag}')
    return over


def run_student(page, width):
    page.goto(BASE + '/student', wait_until='networkidle')
    shot(page, 'dashboard', width)
    page.goto(BASE + '/student/section/1/placement', wait_until='networkidle')
    if page.locator('button:has-text("Start")').count():
        page.click('button:has-text("Start")')
        page.wait_for_load_state('networkidle')
    shot(page, 'placement-question', width)
    for _ in range(30):
        if 'Your plan' in page.content():
            break
        if page.locator('button:has-text("Save answer")').count() == 0:
            break
        page.locator('input[name=choice]').first.check()
        page.click('button:has-text("Save answer")')
        page.wait_for_load_state('networkidle')
    shot(page, 'placement-plan', width)
    page.goto(BASE + '/student/section/1/helpdesk', wait_until='networkidle')
    shot(page, 'helpdesk-queue', width)
    link = page.locator('a[href*="/helpdesk/hd-"]').first
    if link.count():
        link.click()
        page.wait_for_load_state('networkidle')
    if page.locator('text=How urgent').count():
        page.locator('input[name=priority][value=high]').check()
        page.click('button:has-text("Set priority")')
        page.wait_for_load_state('networkidle')
    if page.locator('input[name=qid]').count():
        page.locator('input[name=qid]').first.check()
        page.click('button:has-text("Ask")')
        page.wait_for_load_state('networkidle')
    shot(page, 'helpdesk-ticket', width)
    page.goto(BASE + '/student/section/1/daily-review', wait_until='networkidle')
    shot(page, 'daily-review', width)
    if page.locator('#dailyAnswer').count():
        page.fill('#dailyAnswer', 'ipconfig /all')
        page.click('button:has-text("Check")')
        page.wait_for_load_state('networkidle')
        shot(page, 'daily-review-next', width)
    elif page.locator('input[name=answer]').count():
        page.locator('input[name=answer]').first.check()
        page.click('button:has-text("Check")')
        page.wait_for_load_state('networkidle')
        shot(page, 'daily-review-next', width)


def run_instructor(page, width):
    page.goto(BASE + '/instructor', wait_until='networkidle')
    page.click('#itab-practice')
    page.wait_for_timeout(200)
    shot(page, 'instructor-practice', width)
    page.goto(BASE + '/instructor/section/1/helpdesk', wait_until='networkidle')
    shot(page, 'instructor-helpdesk', width)
    page.goto(BASE + '/instructor/section/1/placement', wait_until='networkidle')
    shot(page, 'instructor-placement', width)


def main():
    overflows = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for width, height, mobile in ((1280, 800, False), (390, 844, True)):
            ctx = browser.new_context(viewport={'width': width, 'height': height}, is_mobile=mobile, has_touch=mobile)
            page = ctx.new_page()
            login(page, 'student1@lms.local', 'student123')
            run_student(page, width)
            ctx.close()
            ctx = browser.new_context(viewport={'width': width, 'height': height}, is_mobile=mobile, has_touch=mobile)
            page = ctx.new_page()
            login(page, 'instructor@lms.local', 'teach123')
            run_instructor(page, width)
            ctx.close()
        browser.close()
    print('done', a.out)


if __name__ == '__main__':
    main()
