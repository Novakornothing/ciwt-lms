/* Daily Review offline cache. The server is the source of truth. IndexedDB keeps
   today's cards and any answer that could not be posted. No answer keys are stored. */
(function () {
  var form = document.getElementById('dailyForm');
  var raw = document.getElementById('dailySync');
  var note = document.getElementById('dailyOffline');
  if (!form || !raw || !window.indexedDB) return;
  var payload;
  try { payload = JSON.parse(raw.textContent || '{}'); } catch (e) { return; }
  var DB = 'novak-daily-review';
  var userKey = 'u' + (payload.user_id || '');

  function openDb() {
    return new Promise(function (resolve, reject) {
      var req = indexedDB.open(DB, 1);
      req.onupgradeneeded = function () {
        var db = req.result;
        if (!db.objectStoreNames.contains('kv')) db.createObjectStore('kv');
      };
      req.onsuccess = function () { resolve(req.result); };
      req.onerror = function () { reject(req.error); };
    });
  }

  function put(db, key, value) {
    return new Promise(function (resolve, reject) {
      var tx = db.transaction('kv', 'readwrite');
      tx.objectStore('kv').put(value, key);
      tx.oncomplete = function () { resolve(); };
      tx.onerror = function () { reject(tx.error); };
    });
  }

  function get(db, key) {
    return new Promise(function (resolve, reject) {
      var tx = db.transaction('kv', 'readonly');
      var req = tx.objectStore('kv').get(key);
      req.onsuccess = function () { resolve(req.result || null); };
      req.onerror = function () { reject(req.error); };
    });
  }

  function answerFromForm() {
    var card = form.querySelector('input[name="card_id"]');
    var field = form.querySelector('[name="answer"]');
    var value = '';
    if (field && field.type === 'radio') {
      var picked = form.querySelector('input[name="answer"]:checked');
      value = picked ? picked.value : '';
    } else if (field) {
      value = field.value || '';
    }
    return { card_id: card ? card.value : '', answer: value, at: Date.now() };
  }

  openDb().then(function (db) {
    put(db, userKey + ':state', payload);
    if (!navigator.onLine) return;
    return get(db, userKey + ':pending').then(function (pending) {
      if (!pending || !pending.length) return;
      var left = [];
      var chain = Promise.resolve();
      pending.forEach(function (item) {
        chain = chain.then(function () {
          return fetch(form.action, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'fetch', 'Accept': 'application/json' },
            body: JSON.stringify({ card_id: item.card_id, answer: item.answer })
          }).then(function (res) {
            if (!res.ok) left.push(item);
          }).catch(function () { left.push(item); });
        });
      });
      return chain.then(function () { return put(db, userKey + ':pending', left); });
    });
  }).catch(function () {});

  form.addEventListener('submit', function (ev) {
    var item = answerFromForm();
    openDb().then(function (db) {
      return get(db, userKey + ':pending').then(function (pending) {
        pending = pending || [];
        pending.push(item);
        return put(db, userKey + ':pending', pending);
      });
    }).catch(function () {});
    if (!navigator.onLine) {
      ev.preventDefault();
      if (note) note.classList.remove('d-none');
    }
  });
})();
