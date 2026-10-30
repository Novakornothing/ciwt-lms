"""cmi5 defined-verb ordering and statement shape checks (Quartz).

The LRS rejects an assignable-unit statement that conflicts with section 9 of the
cmi5 specification instead of storing it. Order follows the statement timestamp.
"""
from .util import (
    AU_VERBS, CMI5_CATEGORY, DUR_RE, LMS_VERBS, MASTERY_EXT, MOVEON_CATEGORY,
    SESSION_EXT, VERB_NAME, ApiError, agents_match, as_decimal, category_ids,
    grouping_ids, is_duration, parse_iso, session_id_of,
)


def _ts(stmt):
    raw = stmt.get('timestamp')
    if not raw:
        raise ApiError(403, 'cmi5 statements must include a timestamp')
    return parse_iso(raw)


def _extensions(stmt):
    return ((stmt.get('context') or {}).get('extensions') or {})


def check_au_statement(stmt, session, registration, au, actor, template_grouping, prior_session, prior_registration):
    """Raise ApiError when this AU-authenticated statement breaks cmi5 rules."""
    if session.terminated_at or session.abandoned_at:
        raise ApiError(403, 'This session is closed. No further statements are accepted.')

    verb_id = ((stmt.get('verb') or {}).get('id'))
    name = VERB_NAME.get(verb_id)
    defined = name in AU_VERBS or name in LMS_VERBS or CMI5_CATEGORY in category_ids(stmt)

    if name in LMS_VERBS:
        raise ApiError(403, f'The AU cannot record the LMS verb "{name}".')

    if session.launch_mode in ('Browse', 'Review') and name in AU_VERBS and name not in ('initialized', 'terminated'):
        raise ApiError(403, f'{session.launch_mode} launch mode only allows initialized and terminated.')

    prior_session = list(prior_session)
    prior_names = [VERB_NAME.get(((p.get('verb') or {}).get('id'))) for p in prior_session]
    has_init = 'initialized' in prior_names
    has_term = 'terminated' in prior_names
    if has_term:
        raise ApiError(403, 'terminated is the last statement in a session.')

    if not defined:
        if not has_init:
            raise ApiError(403, 'initialized must be the first statement in the session.')
        if MOVEON_CATEGORY in category_ids(stmt):
            raise ApiError(403, 'Only passed, failed, and completed statements may include the moveOn category.')
        _require_template(stmt, session, registration, actor, template_grouping, allow_category=False)
        return

    if name not in AU_VERBS:
        raise ApiError(403, 'A statement with the cmi5 category must use a cmi5 verb.')

    if CMI5_CATEGORY not in category_ids(stmt):
        raise ApiError(403, 'cmi5 defined statements must include the cmi5 category activity.')

    _require_template(stmt, session, registration, actor, template_grouping, allow_category=True)
    obj = stmt.get('object') or {}
    if obj.get('id') != au.lms_activity_id:
        raise ApiError(403, 'The statement object id must be the activityId from the launch URL.')
    if obj.get('objectType') not in (None, 'Activity'):
        raise ApiError(403, 'The AU object must be an Activity.')

    ts = _ts(stmt)
    for prior in prior_session:
        prior_name = VERB_NAME.get(((prior.get('verb') or {}).get('id')))
        # launched, satisfied, abandoned, and waived are LMS statements. The AU's
        # initialized statement is the first statement the AU sends, after launched.
        if prior_name in LMS_VERBS:
            continue
        prior_ts = _ts(prior) if prior.get('timestamp') else None
        if name == 'initialized' and prior_ts and prior_ts <= ts:
            raise ApiError(403, 'initialized must be the first statement in the session.')
        if name != 'initialized' and prior_name == 'initialized' and prior_ts and ts < prior_ts:
            raise ApiError(403, 'initialized must be the first statement by timestamp.')
        if prior_name == 'terminated' and prior_ts and ts >= prior_ts:
            raise ApiError(403, 'terminated must be the last statement in the session.')

    if name != 'initialized' and not has_init:
        raise ApiError(403, 'initialized must be the first statement in the session.')
    if name in prior_names:
        raise ApiError(403, f'"{name}" was already recorded in this session.')
    if name == 'passed' and 'failed' in prior_names:
        raise ApiError(403, 'passed and failed cannot both be used in one session.')
    if name == 'failed' and 'passed' in prior_names:
        raise ApiError(403, 'passed and failed cannot both be used in one session.')

    reg_names = [VERB_NAME.get(((p.get('verb') or {}).get('id'))) for p in prior_registration]
    if name == 'completed' and 'completed' in reg_names:
        raise ApiError(403, 'completed can be recorded only once for this registration.')
    if name == 'passed' and 'passed' in reg_names:
        raise ApiError(403, 'passed can be recorded only once for this registration.')
    if name == 'failed' and 'passed' in reg_names:
        raise ApiError(403, 'failed cannot follow passed in this registration.')

    _check_result(stmt, name, session, au)


def _require_template(stmt, session, registration, actor, template_grouping, allow_category):
    if (stmt.get('actor') or {}).get('objectType') not in (None, 'Agent'):
        raise ApiError(403, 'The actor must be an Agent.')
    if not agents_match(stmt.get('actor') or {}, actor):
        raise ApiError(403, 'The actor must be the learner from the launch URL.')
    ctx = stmt.get('context') or {}
    if ctx.get('registration') != registration.uuid:
        raise ApiError(403, 'The registration must be the value from the launch URL.')
    if session_id_of(stmt) != session.uuid:
        raise ApiError(403, 'The session id extension must be the value from LMS.LaunchData.')
    present = set(grouping_ids(stmt))
    missing = [item for item in template_grouping if item not in present]
    if missing:
        raise ApiError(403, 'The statement must keep the contextTemplate grouping activities.')
    if not allow_category and CMI5_CATEGORY in category_ids(stmt):
        raise ApiError(403, 'cmi5 allowed statements must not include the cmi5 category.')


def _check_result(stmt, name, session, au):
    result = stmt.get('result') or {}
    if not isinstance(result, dict):
        raise ApiError(403, 'result must be an object.')
    has_success = 'success' in result
    has_completion = 'completion' in result
    has_moveon = MOVEON_CATEGORY in category_ids(stmt)
    if has_success or has_completion:
        if not has_moveon:
            raise ApiError(403, 'Statements with success or completion must include the moveOn category.')
    elif has_moveon:
        raise ApiError(403, 'The moveOn category is only allowed when success or completion is set.')

    if 'score' in result and name not in ('passed', 'failed'):
        raise ApiError(403, 'Only passed and failed statements may include a score.')
    score = result.get('score') if isinstance(result.get('score'), dict) else None
    if score and score.get('raw') is not None and ('min' not in score or 'max' not in score):
        raise ApiError(403, 'A raw score must include min and max.')
    if has_success and name not in ('passed', 'failed'):
        raise ApiError(403, 'Only passed and failed statements may include success.')
    if has_completion and name != 'completed':
        raise ApiError(403, 'Only completed statements may include completion.')
    if name == 'passed' and result.get('success') is not True:
        raise ApiError(403, 'passed requires result.success true.')
    if name == 'failed' and result.get('success') is not False:
        raise ApiError(403, 'failed requires result.success false.')
    if name == 'completed' and result.get('completion') is not True:
        raise ApiError(403, 'completed requires result.completion true.')

    duration = result.get('duration')
    if name in ('completed', 'passed', 'failed', 'terminated'):
        if not is_duration(duration):
            raise ApiError(403, f'{name} requires an ISO 8601 duration.')
    elif duration is not None and not is_duration(duration):
        raise ApiError(403, 'duration must be an ISO 8601 duration.')

    if name in ('passed', 'failed') and au.mastery_score not in (None, ''):
        mastery = as_decimal(au.mastery_score)
        ext = _extensions(stmt).get(MASTERY_EXT)
        score = result.get('score') if isinstance(result.get('score'), dict) else {}
        if score and ext is None:
            raise ApiError(403, 'A scored passed or failed statement must include the masteryScore extension.')
        if ext is not None and (as_decimal(ext) is None or abs(as_decimal(ext) - mastery) > as_decimal('0.0001')):
            raise ApiError(403, 'passed and failed must repeat the masteryScore from LMS.LaunchData.')
        score = result.get('score') or {}
        if isinstance(score, dict) and score.get('scaled') is not None:
            scaled = as_decimal(score.get('scaled'))
            if scaled is None or scaled < 0 or scaled > 1:
                raise ApiError(403, 'scaled score must be between 0 and 1.')
            if name == 'passed' and scaled < mastery:
                raise ApiError(403, 'A passing scaled score must be at least the masteryScore.')
            if name == 'failed' and scaled >= mastery:
                raise ApiError(403, 'A failing scaled score must be below the masteryScore.')
    if duration is not None and not DUR_RE.match(duration or ''):
        raise ApiError(403, 'duration must be an ISO 8601 duration.')
