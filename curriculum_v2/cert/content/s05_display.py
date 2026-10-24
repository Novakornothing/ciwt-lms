"""A+ Core 1 3.1 (display components and attributes) and 5.3 (video, projector and display issues) — ITSUP 3.4."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG = figure(
    'fig-c-display', 'Display fault isolation: signal path from source to panel',
    ['Source: correct\noutput / Win+P mode', 'Cable and\nconnectors', 'Display: correct\ninput selected', 'Panel / lamp /\nbacklight'],
    'Four boxes in a chain. Start at the source: the computer is sending to the right output and the Win+P projection '
    'mode is correct. Then the cable and both connectors. Then the display itself is set to the matching input. '
    'Finally the panel hardware: a projector lamp, an LCD backlight, or the panel. Swap one link at a time with a '
    'known-good part; the link whose swap fixes the symptom is the faulty one.',
    'Most “no picture” tickets are solved in the first three boxes, before any hardware is replaced.', cols=4)

HTML = ('\n<h4>Display components and attributes (Core 1 3.1)</h4>\n<ul>\n<li><strong>LCD</strong> panels need a backlight. Their panel types trade speed against image quality:\n<strong>TN</strong> (twisted nematic) — fast response, narrow viewing angles and weaker colour; <strong>IPS</strong>\n(in-plane switching) — wide viewing angles and accurate colour; <strong>VA</strong> (vertical alignment) — high contrast,\nbetween the two.</li>\n<li><strong>Mini-LED</strong> is still LCD, but with thousands of small LEDs in local-dimming zones for better contrast.</li>\n<li><strong>OLED</strong> has no backlight; each pixel emits its own light, so black is truly black. Apple notes that OLEDs\ncan show temporary <em>image persistence</em> and, in extreme cases, <strong>burn-in</strong> when the same high-contrast\nimage is shown at high brightness for long periods.</li>\n<li><strong>Inverter</strong> — converts DC to the AC needed by older CCFL backlights; LED-backlit panels do not need one.</li>\n<li><strong>Touch screen / digitizer</strong> — the layer that turns touch or stylus input into coordinates; it can fail\nindependently of the image.</li>\n<li><strong>Attributes:</strong> <strong>resolution</strong> (pixels across × down; LCDs are sharpest at their native\nresolution), <strong>pixel density</strong> (pixels per inch, PPI), <strong>refresh rate</strong> (images per second, Hz)\nand <strong>colour gamut</strong> (the range of colours shown, for example sRGB or DCI-P3).</li>\n</ul>\n' + str(_FIG) + '\n<h4>Display and projector symptoms (Core 1 5.3)</h4>\n<table class="ref-table"><thead><tr><th scope="col">Symptom</th><th scope="col">Likely cause and first check</th></tr></thead><tbody>\n<tr><td>No image, display says “no signal”</td><td>Incorrect input source on the display; Win+P mode; cable seated at both ends</td></tr>\n<tr><td>Dim image; faint picture visible with a torch</td><td>Failed backlight (or inverter on CCFL panels)</td></tr>\n<tr><td>Fuzzy image</td><td>Non-native resolution on an LCD; projector focus or keystone</td></tr>\n<tr><td>Sizing issues (black borders, cut-off edges)</td><td>Scaling, aspect ratio or TV overscan settings</td></tr>\n<tr><td>Flashing or flickering screen</td><td>Microsoft’s test: if Task Manager flickers too, suspect the display driver; if not, an app. Also check the cable and refresh rate.</td></tr>\n<tr><td>Incorrect colour, distorted image</td><td>Loose or damaged cable (a missing colour channel), colour profile, monitor picture settings</td></tr>\n<tr><td>Dead or stuck pixels</td><td>Panel defect; check the vendor’s pixel policy for warranty</td></tr>\n<tr><td>Burn-in</td><td>Static content at high brightness on OLED; reduce brightness, shorten screen time-out</td></tr>\n<tr><td>Burnt-out bulb; projector shuts down intermittently</td><td>Lamp at end of life; blocked vents or a clogged filter causing thermal shutdown</td></tr>\n<tr><td>No sound over HDMI</td><td>Default playback device in Windows Sound settings</td></tr>\n</tbody></table>\n' + str(worked('the dim laptop screen', '''<ol>
<li>Laptop screen is “black”, but the power light is on and an external monitor shows the desktop: the GPU and OS are fine.</li>
<li>Shine a torch at an angle on the panel: a faint image is visible. The LCD is drawing the picture but nothing lights it.</li>
<li>Conclusion: backlight failure (or the inverter, on an older CCFL panel). Quote the panel or backlight repair; no OS work needed.</li></ol>''')) + '\n' + str(scenario('the projector that turns itself off', '''<p>In a training room the projector shuts down after about 40 minutes, every session. The lamp hours are
well inside its rating. The intake filter is grey with dust and the projector sits against a wall. You clean or replace
the filter per the manual and give the vents clearance; the next session runs all day. Intermittent projector shutdown is
usually heat, not electronics.</p>''')) + '\n' + str(cfu(('A laptop screen is dark but a faint image shows under a torch. What has failed?', 'The backlight (or its inverter on older CCFL panels).'),
     ('Why does an LCD look fuzzy at some resolutions?', 'It is not at its native resolution, so pixels are interpolated.'),
     ('Which panel type has no backlight and can suffer burn-in?', 'OLED.'))) + '\n')

SUPPLEMENTS = [{
    'course': 'ITSUP', 'chapter': 3, 'lesson': 4, 'id': 'cert-display',
    'title': 'Display technologies and display, video and projector troubleshooting',
    'cert': ['A1:3.1', 'A1:5.3'],
    'html': sme_note('Display components and attributes, and display/projector troubleshooting (Core 1 3.1 and 5.3).') + HTML,
    'sources': ['apple-oled', 'ms-flicker', 'ms-display'],
}]

GLOSSARY = [
    ('IPS panel', 'In-plane switching LCD: wide viewing angles and accurate colour.'),
    ('TN panel', 'Twisted nematic LCD: fast response but narrow viewing angles and weaker colour.'),
    ('OLED', 'Organic LED display: each pixel emits light, no backlight; can show image persistence or burn-in.'),
    ('Native resolution', 'The physical pixel grid of an LCD; the sharpest setting.'),
    ('Pixel density (PPI)', 'Pixels per inch: how finely detail is shown at a given screen size.'),
    ('Inverter', 'Converts DC to AC for a CCFL backlight in older LCDs.'),
]

ITEMS = [
    match('A1:3.1', 'IT-3.4', 1, 'Match each display technology to its defining characteristic.',
          [('TN', 'Fast response, narrow viewing angles'), ('IPS', 'Wide viewing angles, accurate colour'),
           ('OLED', 'Self-emissive pixels with no backlight'), ('Mini-LED', 'LCD with many local-dimming backlight zones')],
          'TN trades image quality for speed; IPS has the best angles and colour; OLED pixels emit light; Mini-LED is a backlight technology for LCD.',
          decoys=['Needs an inverter for its LEDs']),
    single('A1:3.1', 'IT-3.4', 2, 'A designer needs the widest range of colours for print and video work. Which display attribute matters most?',
           'Colour gamut coverage (for example DCI-P3)',
           ['A refresh rate of 240 Hz or above for smooth motion', 'The fastest grey-to-grey response', 'Support for touch input'],
           'Colour gamut is the range of colours a display can show; refresh and response matter for motion, not colour range.'),
    single('A1:3.1', 'IT-3.4', 3, 'An older laptop has a CCFL-backlit LCD that suddenly went very dim. Which part converts power for that backlight?',
           'The inverter',
           ['The digitizer', 'The GPU', 'The display scaler'],
           'CCFL backlights need AC from an inverter; LED backlights do not.'),
    single('A1:5.3', 'IT-3.4', 1, 'A monitor says “No signal” after being moved to a new desk. The PC is running. What should the technician check first?',
           'The input source selected on the monitor',
           ['The monitor’s backlight assembly and inverter board', 'The GPU’s thermal paste', 'The monitor’s dead-pixel count'],
           'Moving a display often changes which cable is connected; select the matching input before suspecting hardware.'),
    order('A1:5.3', 'IT-3.4', 2, 'A conference-room display shows nothing from a laptop. Put the checks in the order that follows the signal path.',
          ['Press Win+P and choose Duplicate or Extend', 'Reseat or swap the HDMI cable', 'Select the HDMI input on the display', 'Test the display with a known-good source'],
          'Follow the signal: source output mode, cable, display input, then the display hardware.'),
    multi('A1:5.3', 'IT-3.4', 3, 'A projector shuts down after 30–40 minutes in every session. Which TWO causes are most likely? (Choose two.)',
          ['A clogged intake filter', 'Blocked ventilation around the projector'],
          ['The wrong Win+P projection mode', 'An HDMI cable that is too short', 'A laptop set to the wrong resolution'],
          'Intermittent projector shutdown is usually thermal: dirty filters and blocked vents.'),
    single('A1:5.3', 'IT-3.4', 4, 'Video plays on a TV over HDMI but there is no sound. The TV volume is up. What should be checked next?',
           'The default playback device in Windows',
           ['The TV’s colour temperature setting', 'The laptop’s display refresh rate', 'The HDMI cable’s length'],
           'HDMI carries audio, but Windows must use the HDMI device as the output.'),
]
