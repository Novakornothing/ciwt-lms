"""Raise every ITSUP lesson to Chapter 1 structural bar.
Appends only missing sections. Does not replace Chapter 1 prose.
"""


def _has(html, token):
    return token in (html or "")


def apply_raised_bar(pack):
    for ch in pack:
        if not isinstance(ch, dict):
            continue
        ch_no = ch.get("order")
        for les in ch.get("lessons") or []:
            html = les.get("html") or ""
            extra = []
            title = les.get("title") or ""
            if not _has(html, "plain-english"):
                extra.append(
                    f'<div class="plain-english"><h4>In plain English</h4>'
                    f"<p>{title} is the same support job as Chapter 1: name the outcome, "
                    f"pick the domain, change one thing, write action → result.</p></div>"
                )
            if not _has(html, "build-on"):
                extra.append(
                    f'<div class="build-on"><strong>Builds on:</strong> Chapter 1 ticket habits '
                    f"and the isolation order already taught. Do not skip identify.</div>"
                )
            if not _has(html, "live-demo"):
                extra.append(
                    '<div class="live-demo"><h4>Do this before you leave</h4>'
                    "<p>Say the pass bar out loud. If a lab button sits under this lesson, launch it. "
                    "If this lesson is a paper drill, fill the table — do not invent a CLI.</p></div>"
                )
            if not _has(html, "port-table"):
                extra.append(
                    '<table class="port-table"><tr><th>Field</th><th>Write</th></tr>'
                    "<tr><td>Outcome</td><td>What they must do again</td></tr>"
                    "<tr><td>Domain</td><td>Safety / POST / OS / address / name / SaaS</td></tr>"
                    "<tr><td>Test</td><td>Action → result</td></tr>"
                    "<tr><td>Next</td><td>A person or a command</td></tr></table>"
                )
            if not _has(html, "miss-box"):
                extra.append(
                    '<div class="miss-box"><h4>Common misses</h4><ul>'
                    "<li>Skipping identify because the user already named a cause</li>"
                    "<li>Changing two things at once</li>"
                    "<li>Putting a password in the ticket</li>"
                    "</ul></div>"
                )
            if not _has(html, "check-box"):
                extra.append(
                    '<div class="check-box"><h4>Check yourself</h4>'
                    "<details><summary>What does closed mean?</summary>"
                    "<p>The required workflow works and the notes are complete.</p></details></div>"
                )
            if extra:
                les["html"] = html + "\n" + "\n".join(extra)
            les.setdefault("minutes", 35)
    return pack
