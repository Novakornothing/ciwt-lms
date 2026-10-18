# LTI 1.3 + LTI Advantage setup (Canvas, Blackboard Learn, Moodle)

Novak Learning acts as an LTI 1.3 **tool**. With it, an LMS course can:

- open lessons, live labs, chapter checks, tests or the class home here (resource link launch, signed in as the LMS user);
- let instructors place those items into the LMS course (Deep Linking 2.0), creating gradebook columns for graded items;
- receive scores from this LMS's gradebook (Assignment and Grade Services, AGS), when an instructor presses
  **Send scores to the LMS**;
- add or link students from the LMS roster (Names and Role Provisioning Services, NRPS), when an instructor presses
  **Sync roster from the LMS**.

> **Status.** This is **not 1EdTech-certified** and **has not been tested against a live Canvas, Blackboard or Moodle**.
> It is tested against the in-repo mock platform (`tools/lti_mock_platform.py`; `tests/test_lti.py`, and
> `tools/lti_e2e.py` in a real browser). Expect to fix small platform differences on the first real connection. Run a
> pilot course before rolling it out.

## Tool URLs (give these to the LMS)

Admin → **LMS (LTI)** shows the exact values for your server. With the server at `https://lms.example.org`:

| What | URL |
|---|---|
| OIDC login initiation URL | `https://lms.example.org/lti/login` (add `?reg=<id>` if one LMS has two registrations here) |
| Redirect URI / target link URI / deep-linking URL | `https://lms.example.org/lti/launch` |
| Public JWKS URL | `https://lms.example.org/lti/jwks` |
| Canvas JSON configuration | `https://lms.example.org/lti/config/canvas.json` |

Signing: RS256. The tool's private key is **never in git**. It is loaded from, in order:

1. `LTI_PRIVATE_KEY` (environment variable holding the PEM text; `\n` escapes are accepted);
2. `LTI_PRIVATE_KEY_FILE` (path to a PEM file);
3. `instance/lti/tool_private.pem`, generated on first use with mode 0600. `instance/` is in `.gitignore`.

On a host with an ephemeral disk (Render, Heroku), set `LTI_PRIVATE_KEY`; otherwise every deploy makes a new key and
the LMS can no longer verify messages from the tool. To rotate, move the old key's PEM to `instance/lti/previous/` and
set the new key. The JWKS keeps publishing the old public key.

Cookies: the launch checks a `state` cookie set at login. Inside an LMS iframe on another site, the browser has to send
that cookie cross-site, which needs HTTPS (the cookie becomes `SameSite=None; Secure` automatically on HTTPS). Some
browsers block third-party cookies entirely. If launches inside an iframe fail with `state_cookie`, set the placement to
open in a new window. The LTI Platform Storage spec, which is the cookieless alternative, is **not** implemented.
`LTI_REQUIRE_STATE_COOKIE=0` turns the check off. The state and nonce stay single-use, but you lose the binding to the
browser, so this is not recommended.

## Canvas

1. **Admin → Developer Keys → + Developer Key → + LTI Key.**
2. **Method: Enter URL** and paste `https://lms.example.org/lti/config/canvas.json`. Alternatively, use *Paste JSON*
   or *Manual Entry* with the URLs above:
   - Redirect URIs: `/lti/launch`
   - Target link URI: `/lti/launch`
   - OpenID Connect Initiation URL: `/lti/login`
   - JWK method: Public JWK URL `/lti/jwks`
3. Under LTI Advantage Services, turn on:
   - *Can create and view assignment data in the gradebook* (line items)
   - *Can view assignment data in the gradebook* (line items, read-only)
   - *Can view submission data* (results)
   - *Can create and update submission results* (scores)
   - *Can retrieve user data associated with the context the tool is installed in* (NRPS)
4. Placements: *Link Selection* and *Assignment Selection* (Deep Linking) and *Course Navigation*. The JSON config
   already sets these.
5. Privacy level **Public**, so names and emails are sent.
6. Save, then turn the key **ON**. Copy the **Client ID**, the number under *Details*.
7. Settings → Apps → **+ App → By Client ID**, paste the Client ID, and install. Open the app's settings cog →
   *Deployment Id* and copy it.
8. Here, go to Admin → LMS (LTI) → **Add an LMS → Canvas** and fill in:
   - Issuer `https://canvas.instructure.com`. Beta: `https://canvas.beta.instructure.com`. Test:
     `https://canvas.test.instructure.com`.
   - Client ID and Deployment ID from steps 6 and 7.
   - OIDC authorization URL `https://sso.canvaslms.com/api/lti/authorize_redirect`
   - Token URL `https://sso.canvaslms.com/login/oauth2/token`
   - JWKS `https://sso.canvaslms.com/api/lti/security/jwks`
   - Beta and Test use `sso.beta.canvaslms.com` and `sso.test.canvaslms.com`.

   Self-hosted Canvas uses your own domain for these three URLs.

## Blackboard Learn

1. Register the tool on the **Anthology/Blackboard Developer Portal** (developer.blackboard.com) → *Register LTI 1.3
   tool*, with:
   - Login initiation URL `/lti/login`
   - Tool redirect URL `/lti/launch`
   - Tool JWKS URL `/lti/jwks`
   - Signing algorithm RS256

   Copy the **Application ID** (the client ID).
2. In Learn: **Administrator Panel → Integrations → LTI Tool Providers → Register LTI 1.3/Advantage Tool**. Paste the
   Application ID and copy the **Deployment ID**. Set *User fields to send* to include name and email, and allow grade
   service access and membership service access.
3. Add *placements*: a **Deep Linking content tool** for instructors, and optionally a course tool with the custom
   parameter `ciwt_target=course`.
4. Here, go to Admin → LMS (LTI) → **Add an LMS → Blackboard Learn** and fill in:
   - Issuer `https://blackboard.com`
   - OIDC authorization URL `https://developer.blackboard.com/api/v1/gateway/oidcauth`
   - Token URL `https://developer.blackboard.com/api/v1/gateway/oauth2/jwttoken`
   - JWKS `https://developer.blackboard.com/api/v1/management/applications/<Application ID>/jwks.json`
   - Client ID: the Application ID
   - Deployment ID from step 2

## Moodle (4.x)

1. **Site administration → Plugins → Activity modules → External tool → Manage tools → configure a tool manually**:
   - Tool URL `/lti/launch`
   - LTI version **LTI 1.3**
   - Public key type **Keyset URL** `/lti/jwks`
   - Initiate login URL `/lti/login`
   - Redirection URI(s) `/lti/launch`
   - Supports Deep Linking: on, with Content Selection URL `/lti/launch`
   - Services:
     - IMS LTI Assignment and Grade Services: *Use this service for grade sync and column management*
     - IMS LTI Names and Role Provisioning: *Use this service to retrieve members' information as per privacy settings*
   - Privacy: share name and email with the tool.
2. Save, then open the tool's **View configuration details** (the list icon) and copy:
   - Platform ID (the issuer, i.e. your site URL)
   - Client ID
   - Deployment ID
   - Public keyset URL (`/mod/lti/certs.php`)
   - Access token URL (`/mod/lti/token.php`)
   - Authentication request URL (`/mod/lti/auth.php`)
3. Here, go to Admin → LMS (LTI) → **Add an LMS → Moodle** and paste those values.

## First use in a course

1. The instructor adds the tool to the LMS course with the LMS's content picker (Deep Linking). The first time,
   Novak Learning asks which **class** this LMS course is. Pick one of your classes. After that, the picker shows that
   class's lessons, chapter checks, tests and live labs. Graded items can get a gradebook column (out of 100).
2. Students open the links from the LMS. The first launch creates their account here, or links an existing one by
   email if the admin allowed that for this LMS. It also enrolls them in the mapped class.
3. **Class → LMS** (`/instructor/section/<id>/lti`) shows the connected LMS course and its placed links, plus the two
   buttons:
   - **Send scores to the LMS.** Scores come from this class's gradebook, with late penalties, overrides and excused
     cells applied. Missing and excused cells are not sent. Labs use the best live-lab score; the class-home link uses
     the course grade. If a link has no line item yet, the tool finds or creates one through AGS.
   - **Sync roster from the LMS.** This pages through NRPS, creates or links accounts, and enrolls learners. Staff are
     linked but not enrolled. Members who are inactive in the LMS are counted and left alone. **Nobody is ever
     removed here.**

## Accounts and roles

- An LMS person is identified by **issuer + client ID + `sub`**, never by name.
- Mapping of LMS roles to roles here:

  | LMS role | Role here |
  |---|---|
  | Instructor, TeachingAssistant, ContentDeveloper, Mentor; institution Faculty or Administrator | instructor |
  | Learner, Student | student |
  | anything | never admin |

- An existing account here keeps its role. If the LMS says the person is staff but their account here is a student
  account, they get a notice and stay a student until an admin changes the role.
- Linking by email is **off by default**. When it is on, it never links admin accounts.
- New accounts get a random password, so they cannot sign in with a password until they reset it.

## What is checked on every launch

- The `state` is known, unexpired (10 minutes) and single-use, and matches the browser's cookie.
- The `id_token` signature verifies with the platform JWKS by `kid`. RS256/384/512 only, so `none` and HS* are
  refused. The key set is re-fetched once if the platform rotated keys.
- The claims:
  - `iss` matches the registration and `aud` contains the client ID; with several audiences, `azp` must be the
    client ID.
  - `exp` and `iat` are checked with 60 s leeway and a maximum age of 1 hour.
  - `nonce` matches the login.
  - LTI `version` is 1.3.0.
  - The message type is `LtiResourceLinkRequest` or `LtiDeepLinkingRequest`.
  - The deployment ID is registered.
  - A resource-link id and a deep-link return URL are present when the message type needs them.
- Service URLs must be HTTPS. Loopback HTTP is allowed only with `LTI_ALLOW_LOOPBACK_HTTP=1`, for development and
  the mock.
- Deep-linking pickers are single-use, expire after an hour, and belong to the instructor who launched them.

## Local try-out with the mock platform

```bash
LTI_ALLOW_LOOPBACK_HTTP=1 DATABASE_URL=sqlite:////tmp/lti-demo.db PORT=5078 python app.py
python tools/lti_mock_platform.py --tool http://127.0.0.1:5078 --port 5088   # prints issuer / client id / URLs
```

Register those printed values under Admin → LMS (LTI), then open http://127.0.0.1:5088/. `tools/lti_e2e.py` does
this end to end in Chromium. The mock's people are fictional demo accounts on the `mock-lms.invalid` domain.

## Not done yet

- 1EdTech certification and a live Canvas, Blackboard or Moodle test.
- LTI Platform Storage (cookieless launches in iframes).
- Dynamic Registration.
- Submission Review.
- Automatic score sync. Today the instructor presses a button; nothing is sent in the background.
- Results service reads.
- Line-item editing and deletion.
- Grading-progress states other than FullyGraded or NotReady.
- Mapping one LMS course to several classes here.
