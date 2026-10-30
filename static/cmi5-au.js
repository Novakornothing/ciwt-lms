/* Novak LMS assignable unit. Runs when the page was opened with cmi5 launch parameters. */
(function () {
  var params = new URLSearchParams(window.location.search);
  var endpoint = params.get('endpoint');
  var fetchUrl = params.get('fetch');
  var registration = params.get('registration');
  var activityId = params.get('activityId');
  var actorRaw = params.get('actor');
  if (!endpoint || !fetchUrl || !registration || !activityId || !actorRaw) return;

  var actor;
  try { actor = JSON.parse(actorRaw); } catch (err) { return; }
  if (endpoint.charAt(endpoint.length - 1) !== '/') endpoint += '/';

  var CMI5 = 'https://w3id.org/xapi/cmi5/context/categories/cmi5';
  var MOVEON = 'https://w3id.org/xapi/cmi5/context/categories/moveon';
  var MASTERY = 'https://w3id.org/xapi/cmi5/context/extensions/masteryscore';
  var VERBS = {
    initialized: 'http://adlnet.gov/expapi/verbs/initialized',
    completed: 'http://adlnet.gov/expapi/verbs/completed',
    passed: 'http://adlnet.gov/expapi/verbs/passed',
    failed: 'http://adlnet.gov/expapi/verbs/failed',
    terminated: 'http://adlnet.gov/expapi/verbs/terminated'
  };

  var auth = null;
  var launch = null;
  var started = Date.now();
  var busy = false;

  function status(text) {
    var el = document.getElementById('cmi5-status');
    if (!el) {
      el = document.createElement('p');
      el.id = 'cmi5-status';
      el.className = 'status';
      document.body.insertBefore(el, document.body.firstChild);
    }
    el.textContent = text;
  }

  function uuid() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (ch) {
      var rnd = Math.random() * 16 | 0;
      return (ch === 'x' ? rnd : (rnd & 0x3 | 0x8)).toString(16);
    });
  }

  function duration() {
    var seconds = Math.max(1, Math.round((Date.now() - started) / 1000));
    return 'PT' + seconds + 'S';
  }

  function authHeader(token) {
    if (!token) return '';
    return token.indexOf('Basic ') === 0 ? token : 'Basic ' + token;
  }

  async function call(method, path, body) {
    var headers = {
      'Authorization': auth,
      'X-Experience-API-Version': '1.0.3'
    };
    if (body !== undefined) headers['Content-Type'] = 'application/json';
    var response = await fetch(endpoint + path, {
      method: method,
      headers: headers,
      body: body === undefined ? undefined : JSON.stringify(body)
    });
    var text = await response.text();
    var data = null;
    if (text) {
      try { data = JSON.parse(text); } catch (err) { data = text; }
    }
    if (!response.ok) {
      var error = new Error(typeof data === 'string' ? data : JSON.stringify(data));
      error.status = response.status;
      throw error;
    }
    return data;
  }

  function contextFor(result) {
    var ctx = JSON.parse(JSON.stringify(launch.contextTemplate || {}));
    ctx.registration = registration;
    ctx.contextActivities = ctx.contextActivities || {};
    var categories = ctx.contextActivities.category || [];
    categories = categories.concat([{objectType: 'Activity', id: CMI5}]);
    if (result && (Object.prototype.hasOwnProperty.call(result, 'success') || Object.prototype.hasOwnProperty.call(result, 'completion'))) {
      categories.push({objectType: 'Activity', id: MOVEON});
    }
    ctx.contextActivities.category = categories;
    ctx.extensions = ctx.extensions || {};
    if (result && (result.success === true || result.success === false) && launch.masteryScore != null) {
      ctx.extensions[MASTERY] = launch.masteryScore;
    }
    return ctx;
  }

  function statement(verb, result) {
    var stmt = {
      id: uuid(),
      timestamp: new Date().toISOString(),
      actor: actor,
      verb: {id: VERBS[verb], display: {'en-US': verb}},
      object: {objectType: 'Activity', id: activityId},
      context: contextFor(result)
    };
    if (result) stmt.result = result;
    return stmt;
  }

  async function send(verb, result) {
    try {
      await call('POST', 'statements', statement(verb, result));
    } catch (err) {
      if (err.status === 400 && verb === 'completed' && /only once/i.test(String(err.message))) return;
      throw err;
    }
  }

  function moveOn() { return launch.moveOn || 'NotApplicable'; }

  function wantsCompleted() {
    return moveOn() === 'Completed' || moveOn() === 'CompletedAndPassed' || moveOn() === 'CompletedOrPassed';
  }

  function wantsScore() {
    return moveOn() === 'Passed' || moveOn() === 'CompletedAndPassed' || moveOn() === 'CompletedOrPassed' || launch.masteryScore != null;
  }

  async function finish(kind) {
    if (busy) return;
    busy = true;
    try {
      var mode = launch.launchMode || 'Normal';
      if (mode === 'Normal' && kind !== 'close') {
        if (wantsCompleted() || kind === 'complete') {
          await send('completed', {completion: true, duration: duration()});
        }
        if (kind === 'pass') {
          await send('passed', {success: true, duration: duration(), score: {scaled: 1, raw: 1, min: 0, max: 1}});
        } else if (kind === 'fail') {
          await send('failed', {success: false, duration: duration(), score: {scaled: 0, raw: 0, min: 0, max: 1}});
        }
      }
      await send('terminated', {duration: duration()});
      status('Finished. Returning to the learning system.');
      if (launch.returnURL) window.location.assign(launch.returnURL);
    } catch (err) {
      busy = false;
      status('The learning system did not accept the result. ' + err.message);
    }
  }

  function button(id, label, kind) {
    var existing = document.getElementById(id);
    if (existing) {
      existing.addEventListener('click', function () { finish(kind); });
      return;
    }
    var el = document.createElement('button');
    el.type = 'button';
    el.id = id;
    el.textContent = label;
    el.style.marginRight = '0.5rem';
    el.addEventListener('click', function () { finish(kind); });
    var bar = document.getElementById('cmi5-bar');
    bar.appendChild(el);
  }

  function showControls() {
    if (document.getElementById('cmi5-score')) {
      document.getElementById('cmi5-score').addEventListener('click', function () {
        var form = document.getElementById('cmi5-check');
        var selected = form ? form.querySelector('input[name="answer"]:checked') : null;
        if (!selected) { status('Choose an answer first.'); return; }
        var correct = form.getAttribute('data-correct');
        finish(selected.value === correct ? 'pass' : 'fail');
      });
      return;
    }
    if (document.getElementById('cmi5-complete') && !wantsScore()) {
      document.getElementById('cmi5-complete').addEventListener('click', function () { finish('complete'); });
      return;
    }
    var bar = document.getElementById('cmi5-bar');
    if (!bar) {
      bar = document.createElement('div');
      bar.id = 'cmi5-bar';
      bar.setAttribute('role', 'region');
      bar.setAttribute('aria-label', 'Assignable unit');
      bar.style.cssText = 'position:sticky;bottom:0;padding:.75rem 1rem;background:#0f172a;color:#f8fafc;font-family:system-ui,sans-serif;';
      var note = document.createElement('span');
      note.id = 'cmi5-status';
      note.style.marginRight = '0.75rem';
      bar.appendChild(note);
      document.body.appendChild(bar);
    }
    var mode = launch.launchMode || 'Normal';
    if (mode !== 'Normal') {
      status('Preview only. Satisfaction is not recorded.');
      button('cmi5-close', 'Return', 'close');
      return;
    }
    status('This lesson is an assignable unit.');
    if (wantsScore()) {
      button('cmi5-pass', 'Record pass', 'pass');
      button('cmi5-fail', 'Record fail', 'fail');
    } else if (document.getElementById('cmi5-complete')) {
      document.getElementById('cmi5-complete').addEventListener('click', function () { finish('complete'); });
    } else {
      button('cmi5-complete', 'Mark complete', 'complete');
    }
  }

  async function boot() {
    status('Connecting to the learning system…');
    var fetched = await fetch(fetchUrl, {method: 'POST'});
    var tokenBody = await fetched.json();
    if (!tokenBody['auth-token']) {
      status(tokenBody['error-text'] || 'The launch token could not be used.');
      return;
    }
    auth = authHeader(tokenBody['auth-token']);
    var stateUrl = 'activities/state?stateId=' + encodeURIComponent('LMS.LaunchData')
      + '&activityId=' + encodeURIComponent(activityId)
      + '&agent=' + encodeURIComponent(JSON.stringify(actor))
      + '&registration=' + encodeURIComponent(registration);
    launch = await call('GET', stateUrl);
    try {
      var agentUrl = 'agents/profile?profileId=' + encodeURIComponent('cmi5LearnerPreferences')
        + '&agent=' + encodeURIComponent(JSON.stringify(actor));
      await call('GET', agentUrl);
    } catch (err) { /* preferences are optional for display */ }
    await send('initialized');
    started = Date.now();
    showControls();
    status('Ready.');
  }

  boot().catch(function (err) {
    status('This assignable unit could not start. ' + err.message);
  });
})();
