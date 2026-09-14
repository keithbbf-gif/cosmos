/* deck_profiles.js — per-profile MOTIF engine panel for cDeck.
 *
 * Exposes window.DeckProfiles.  Serves all 7 occupancy profiles:
 *   forge · crucible · diligence · docket · ups · differentiator · website
 *
 * Each profile page renders:
 *   • skin wallpaper from /cdeck/skins/<profile>-<flavor>.jpg
 *   • MOTIF 9-stage tabs (left tabs for non-forge; top bar for forge)
 *   • dest / seat setup fields
 *   • SAVE SETUP — writes to /api/v1/profiles.  Never starts MOTIF.
 *
 * GET  /api/v1/profiles?profile=<id>  → snapshot (read-only)
 * POST /api/v1/profiles               → save engine (no MOTIF start)
 */

(function (global) {
  'use strict';

  /* ── skin filename lookup ────────────────────────────────────────── */
  const SKIN_NAMES = {
    forge:         'forge-engineroom',
    crucible:      'crucible-chamber',
    diligence:     'diligence-dealroom',
    docket:        'docket-archive',
    ups:           'ups-lab',
    differentiator:'differentiator-clinic',
    website:       'website-studio',
  };

  /* Ordered profile IDs — must match cosmos_profiles.PROFILES order. */
  const PROFILE_ORDER = [
    'forge', 'crucible', 'diligence', 'docket', 'ups', 'differentiator', 'website',
  ];

  /* ── helpers ─────────────────────────────────────────────────────── */
  function skinUrl(profileId) {
    const n = SKIN_NAMES[profileId];
    return n ? '/cdeck/skins/' + n + '.jpg' : null;
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function el(tag, attrs, inner) {
    const a = Object.entries(attrs || {})
      .map(([k, v]) => v == null ? '' : ` ${k}="${esc(v)}"`)
      .join('');
    return `<${tag}${a}>${inner || ''}</${tag}>`;
  }

  /* ── API calls ───────────────────────────────────────────────────── */
  async function fetchProfile(baseUrl, profileId, token) {
    const u = baseUrl + '/api/v1/profiles?profile=' + encodeURIComponent(profileId);
    const h = token ? { Authorization: 'Bearer ' + token } : {};
    const r = await fetch(u, { headers: h });
    if (!r.ok) throw new Error('profiles GET ' + r.status);
    return r.json();
  }

  async function postProfile(baseUrl, body, token) {
    const h = { 'Content-Type': 'application/json' };
    if (token) h['Authorization'] = 'Bearer ' + token;
    const r = await fetch(baseUrl + '/api/v1/profiles', {
      method: 'POST', headers: h, body: JSON.stringify(body),
    });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(j.detail || ('profiles POST ' + r.status));
    return j;
  }

  /* ── render helpers ──────────────────────────────────────────────── */
  function renderProfileSwitcher(profiles, activeId) {
    const items = PROFILE_ORDER.map(pid => {
      const p = (profiles || []).find(x => x.id === pid) || { id: pid, label: pid };
      const active = p.id === activeId ? ' dp-active' : '';
      const thumb = skinUrl(p.id);
      const bg = thumb
        ? ` style="background-image:url('${thumb}');background-size:cover;background-position:center"`
        : '';
      return `<button class="dp-prof-btn${active}" data-pid="${esc(p.id)}" title="${esc(p.label)}">
        <span class="dp-thumb"${bg}></span>
        <span class="dp-plabel">${esc(p.label)}</span>
      </button>`;
    }).join('');
    return `<nav class="dp-switcher">${items}</nav>`;
  }

  function renderSkinHeader(snap) {
    const pid = snap.profile;
    const url = skinUrl(pid);
    const bgStyle = url
      ? `background-image:url('${url}');background-size:cover;background-position:center top`
      : 'background:var(--dp-skin-fallback,#1a2030)';
    return `<div class="dp-skin-header" style="${bgStyle}">
      <div class="dp-skin-overlay">
        <span class="dp-profile-label">${esc(snap.label || pid)}</span>
        ${snap.engine && snap.engine.kind === 'OK'
          ? '<span class="dp-saved-badge">SAVED</span>' : ''}
      </div>
    </div>`;
  }

  function renderMotifTopBar(stages, activeStageId) {
    const tabs = (stages || []).map(s =>
      `<button class="dp-motif-tab${s.id === activeStageId ? ' dp-active' : ''}"
        data-stage="${esc(s.id)}" title="${esc(s.hint || '')}">${s.n}&#8202;${esc(s.name)}</button>`
    ).join('');
    return `<div class="dp-motif-topbar">${tabs}</div>`;
  }

  function renderMotifLeftTabs(stages, activeStageId) {
    const tabs = (stages || []).map(s =>
      `<button class="dp-stage-tab${s.id === activeStageId ? ' dp-active' : ''}"
        data-stage="${esc(s.id)}">${s.n}&#8202;${esc(s.name)}</button>`
    ).join('');
    return `<nav class="dp-stage-nav">${tabs}</nav>`;
  }

  function renderStagePane(snap, stageId) {
    const s = (snap.stages || []).find(x => x.id === stageId) || {};
    const eng = snap.engine || {};
    const ss = (eng.step_setup || {})[stageId] || {};
    const stageNote = (eng.stages || {})[stageId] || '';

    const barCat = snap.bar_catalog || [];
    const barOpts = barCat.map(b =>
      `<option value="${esc(b.id)}" ${ss.bar === b.id ? 'selected' : ''}>${esc(b.label)}</option>`
    ).join('');
    const hasBars = ['research', 'arch', 'consensus1', 'critics', 'consensus2'];
    const showBar = hasBars.includes(stageId);

    return `<div class="dp-stage-pane" data-pane="${esc(stageId)}">
      <p class="dp-stage-hint">${esc(s.hint || '')}</p>
      <label class="dp-field">
        <span>Note</span>
        <textarea name="stage_note" rows="2" placeholder="Stage notes…">${esc(stageNote)}</textarea>
      </label>
      <label class="dp-field">
        <span>Folders</span>
        <input name="folders" type="text" value="${esc(ss.folders || '')}" placeholder="V:\\A\\Ai\\COSMOS\\docs">
      </label>
      <label class="dp-field">
        <span>Files</span>
        <input name="files" type="text" value="${esc(ss.files || '')}" placeholder="MOTIF.md">
      </label>
      <label class="dp-field">
        <span>Prompt</span>
        <input name="prompt" type="text" value="${esc(ss.prompt || '')}" placeholder="SGH + GEM first…">
      </label>
      <label class="dp-field">
        <span>Roles</span>
        <input name="roles" type="text" value="${esc(ss.roles || '')}" placeholder="SGH · GEM">
      </label>
      ${showBar ? `<label class="dp-field">
        <span>Bar</span>
        <select name="bar">${barOpts}</select>
      </label>
      <label class="dp-field">
        <span>N free CLI</span>
        <input name="n_free" type="number" min="0" max="5" value="${esc(ss.n_free != null ? ss.n_free : 3)}">
      </label>` : ''}
    </div>`;
  }

  function renderDestPane(snap) {
    const eng = snap.engine || {};
    const dest = eng.dest || {};
    const catalog = snap.dest_catalog || [];
    const opts = catalog.map(d =>
      `<option value="${esc(d.id)}" ${dest.kind === d.id ? 'selected' : ''}>${esc(d.label)}</option>`
    ).join('');
    const giturDests = new Set(['github', 'gitlab']);
    const isGitur = giturDests.has(dest.kind || '');

    return `<div class="dp-dest-pane">
      <h4 class="dp-section-head">IMPLEMENT dest</h4>
      <label class="dp-field">
        <span>Destination</span>
        <select name="dest_kind">${opts}</select>
      </label>
      <label class="dp-field dp-dest-path ${isGitur ? '' : 'dp-hidden'}" id="dp-dest-path-row">
        <span>Path / repo</span>
        <input name="dest_path" type="text" value="${esc(dest.path || '')}"
          placeholder="keithbbf-gif/cosmos">
      </label>
      <p class="dp-dest-note ${isGitur ? 'dp-hidden' : ''}" id="dp-dest-gitur-note">
        <em>Via Gitur — branch before the live tree.</em>
      </p>
      <p class="dp-dest-note" id="dp-dest-publish-note" style="${dest.kind === 'publish' ? '' : 'display:none'}">
        <em>Publish is Keith's click. SAVE SETUP does not publish.</em>
      </p>
    </div>`;
  }

  function renderDefinePane(snap) {
    const eng = snap.engine || {};
    const def = eng.define || {};
    return `<div class="dp-define-pane">
      <h4 class="dp-section-head">PROBLEM STATEMENT / STATED GOAL</h4>
      <label class="dp-field">
        <span>Statement</span>
        <textarea name="define_text" rows="5"
          placeholder="WHAT: … WHY: … Acceptance: …">${esc(def.text || '')}</textarea>
      </label>
      ${def.saved_at ? `<p class="dp-saved-at">Saved ${esc(def.saved_at)}</p>` : ''}
    </div>`;
  }

  function renderSaveBar(saving, lastSave, errorMsg) {
    const note = 'SAVE SETUP — writes engine. Never starts MOTIF. Never publishes.';
    return `<div class="dp-save-bar">
      <button class="dp-save-btn" id="dp-save-btn" ${saving ? 'disabled' : ''}>
        ${saving ? 'Saving…' : 'SAVE SETUP'}
      </button>
      <span class="dp-save-note">${esc(note)}</span>
      ${errorMsg ? `<span class="dp-save-err">${esc(errorMsg)}</span>` : ''}
      ${lastSave && !errorMsg ? `<span class="dp-save-ok">Saved ${esc(lastSave)}</span>` : ''}
    </div>`;
  }

  /* ── ProfilesApp ─────────────────────────────────────────────────── */
  function ProfilesApp(rootEl, baseUrl, token) {
    this._root = rootEl;
    this._base = baseUrl || '';
    this._token = token || '';
    this._snap = null;
    this._activeProfile = 'website';
    this._activeStage = 'define';
    this._saving = false;
    this._lastSave = null;
    this._error = null;
  }

  ProfilesApp.prototype.init = function () {
    this._root.innerHTML = this._shellHtml();
    this._bindShell();
    this._load(this._activeProfile);
  };

  ProfilesApp.prototype._shellHtml = function () {
    return `<div class="dp-shell">
      <div class="dp-left" id="dp-left">
        <div class="dp-switcher-wrap" id="dp-switcher-wrap">
          <div class="dp-loading">Loading profiles…</div>
        </div>
      </div>
      <div class="dp-right" id="dp-right">
        <div class="dp-loading">Loading…</div>
      </div>
    </div>`;
  };

  ProfilesApp.prototype._load = function (profileId) {
    const self = this;
    self._setStatus('loading');
    fetchProfile(self._base, profileId, self._token)
      .then(function (snap) {
        self._snap = snap;
        self._activeProfile = snap.profile;
        /* honour forge motif_top: forge starts on define tab too */
        self._activeStage = (snap.engine || {}).saved_at
          ? self._activeStage
          : 'define';
        self._render();
      })
      .catch(function (e) {
        self._setStatus('error: ' + e.message);
      });
  };

  ProfilesApp.prototype._setStatus = function (msg) {
    const r = this._root.querySelector('#dp-right');
    if (r) r.innerHTML = `<div class="dp-loading">${esc(msg)}</div>`;
  };

  ProfilesApp.prototype._render = function () {
    const snap = this._snap;
    if (!snap) return;

    /* switcher (left) */
    const sw = this._root.querySelector('#dp-switcher-wrap');
    if (sw) sw.innerHTML = renderProfileSwitcher(snap.profiles, snap.profile);

    /* main panel (right) */
    const r = this._root.querySelector('#dp-right');
    if (!r) return;

    const motifTop = !!snap.motif_top;
    const stages = snap.stages || [];
    const activeStage = this._activeStage;

    const topBar = motifTop ? renderMotifTopBar(stages, activeStage) : '';
    const leftNav = !motifTop ? renderMotifLeftTabs(stages, activeStage) : '';

    const stagePane = renderStagePane(snap, activeStage);
    const destPane  = renderDestPane(snap);
    const defPane   = renderDefinePane(snap);
    const saveBar   = renderSaveBar(this._saving, this._lastSave, this._error);

    if (motifTop) {
      /* forge layout: top MOTIF bar, single main area */
      r.innerHTML = `
        ${renderSkinHeader(snap)}
        ${topBar}
        <div class="dp-main-area" id="dp-main-area">
          <form id="dp-form" class="dp-form">
            ${defPane}
            ${stagePane}
            ${destPane}
            ${saveBar}
          </form>
        </div>`;
    } else {
      /* standard layout: left stage tabs, right pane */
      r.innerHTML = `
        ${renderSkinHeader(snap)}
        <div class="dp-body">
          ${leftNav}
          <div class="dp-main-area" id="dp-main-area">
            <form id="dp-form" class="dp-form">
              ${defPane}
              ${stagePane}
              ${destPane}
              ${saveBar}
            </form>
          </div>
        </div>`;
    }

    this._bindPanel();
  };

  ProfilesApp.prototype._bindShell = function () {
    const self = this;
    this._root.addEventListener('click', function (e) {
      const btn = e.target.closest('.dp-prof-btn');
      if (btn && btn.dataset.pid) {
        self._activeProfile = btn.dataset.pid;
        self._activeStage = 'define';
        self._error = null;
        self._load(btn.dataset.pid);
      }
    });
  };

  ProfilesApp.prototype._bindPanel = function () {
    const self = this;

    /* MOTIF stage tab clicks */
    this._root.addEventListener('click', function (e) {
      const btn = e.target.closest('.dp-motif-tab, .dp-stage-tab');
      if (!btn || !btn.dataset.stage) return;
      self._activeStage = btn.dataset.stage;
      self._render();
    });

    /* dest_kind change: toggle path/gitur visibility */
    const destSel = this._root.querySelector('[name="dest_kind"]');
    if (destSel) {
      destSel.addEventListener('change', function () {
        const gRow = self._root.querySelector('#dp-dest-path-row');
        const gNote = self._root.querySelector('#dp-dest-gitur-note');
        const pubNote = self._root.querySelector('#dp-dest-publish-note');
        const giturDests = new Set(['github', 'gitlab']);
        const isG = giturDests.has(destSel.value);
        if (gRow) gRow.classList.toggle('dp-hidden', !isG);
        if (gNote) gNote.classList.toggle('dp-hidden', !isG);
        if (pubNote) pubNote.style.display = destSel.value === 'publish' ? '' : 'none';
      });
    }

    /* SAVE SETUP */
    const saveBtn = this._root.querySelector('#dp-save-btn');
    if (saveBtn) {
      saveBtn.addEventListener('click', function (e) {
        e.preventDefault();
        self._save();
      });
    }
  };

  ProfilesApp.prototype._collectForm = function () {
    const form = this._root.querySelector('#dp-form');
    if (!form) return null;
    const snap = this._snap || {};
    const profileId = snap.profile || this._activeProfile;
    const stageId = this._activeStage;

    const val = function (name) {
      const el = form.querySelector('[name="' + name + '"]');
      return el ? el.value : '';
    };

    /* collect step_setup for the active stage */
    const step = {};
    step[stageId] = {
      folders: val('folders'),
      files:   val('files'),
      prompt:  val('prompt'),
      roles:   val('roles'),
      bar:     val('bar') || undefined,
      n_free:  val('n_free') !== '' ? parseInt(val('n_free'), 10) : undefined,
    };

    /* collect stage notes */
    const stages = {};
    stages[stageId] = val('stage_note');

    return {
      profile:    profileId,
      define:     { text: val('define_text') },
      dest:       { kind: val('dest_kind'), path: val('dest_path') || '' },
      step_setup: step,
      stages:     stages,
    };
  };

  ProfilesApp.prototype._save = function () {
    const self = this;
    const body = this._collectForm();
    if (!body) return;
    self._saving = true;
    self._error = null;
    self._render();

    postProfile(self._base, body, self._token)
      .then(function (rec) {
        self._snap = rec;
        self._saving = false;
        self._lastSave = (rec.engine || {}).saved_at || new Date().toISOString();
        self._error = null;
        self._render();
      })
      .catch(function (e) {
        self._saving = false;
        self._error = e.message;
        self._render();
      });
  };

  /* ── public API ──────────────────────────────────────────────────── */
  global.DeckProfiles = {
    SKIN_NAMES:   SKIN_NAMES,
    PROFILE_ORDER: PROFILE_ORDER,
    skinUrl:      skinUrl,
    fetchProfile: fetchProfile,
    postProfile:  postProfile,

    /**
     * Mount the profiles panel into `rootEl`.
     *
     * @param {Element} rootEl   - container element
     * @param {string}  baseUrl  - e.g. 'http://127.0.0.1:8770' or '' for same-origin
     * @param {string}  token    - bearer token (may be empty on loopback)
     * @param {string}  [profile] - initial profile id (default 'website')
     */
    mount: function (rootEl, baseUrl, token, profile) {
      const app = new ProfilesApp(rootEl, baseUrl, token);
      if (profile && SKIN_NAMES[profile]) app._activeProfile = profile;
      app.init();
      return app;
    },
  };

}(typeof window !== 'undefined' ? window : this));
