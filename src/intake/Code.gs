/**
 * Africa Reframed – intake.
 *
 * Receives the forms of africareframed.com (Request access, and the partner message form on the Partner portal),
 * writes one row per message to the spreadsheet "Partner database" (Drive, 06 Partners), saves an attached file
 * to the folder "Partner database – files received", tells us by email and confirms to the sender.
 *
 * The master copy of this file is src/intake/Code.gs in the repository africareframed/africareframed-site.
 * It runs as a Google Apps Script web app in the account td@africareframed.com (Execute as: Me; Who has access:
 * Anyone). After a change here: paste it into the script, then Deploy > Manage deployments > edit > New version,
 * so the address of the web app stays the same. How it all hangs together: src/intake/README.md.
 */

const CONFIG = {
  // The two addresses on the Drive are not kept in this public file. They stand in the first line of the copy in
  // the script project, above this text:  const IDS = { SHEET_ID: '…', FOLDER_ID: '…' };
  get SHEET_ID() { return IDS.SHEET_ID; },
  get FOLDER_ID() { return IDS.FOLDER_ID; },
  NOTIFY: 'partnerships@africareframed.com',
  REPLY_TO: 'partnerships@africareframed.com',
  SENDER_NAME: 'Africa Reframed',
  SITE_KEY: 'ar-intake-2026',          // not a secret: it only tells our own forms from stray posts
  MAX_FILE_MB: 10,
  FILE_TYPES: ['pdf', 'png', 'jpg', 'jpeg', 'webp', 'gif', 'docx', 'pptx', 'xlsx', 'txt'],
  MAX_PER_MINUTE: 20,
  TZ: 'Europe/Copenhagen'
};

const TABS = {
  Requests: ['ID', 'Received', 'Status', 'Organisation', 'Type of organisation', 'Country', 'Name', 'Role', 'Email',
             'A colleague at a partner', 'Focus of the work', 'How the images will be used', 'Imagery looked for',
             'Consent', 'Known partner', 'Source', 'Flag', 'Notes'],
  Messages: ['ID', 'Received', 'Status', 'Kind', 'Organisation', 'Name', 'Email', 'Message', 'Link', 'Photo IDs',
             'File', 'Known partner', 'Source', 'Flag', 'Notes'],
  Partners: ['Organisation', 'Email or domain', 'Type of organisation', 'Country', 'Partner since', 'Notes'],
  Log: ['When', 'Level', 'What']
};

const KINDS = {
  made: 'Show us what you made',
  missing: 'Tell us what is missing',
  feedback: 'Feedback',
  bigger: 'Build with us',
  question: 'A question'
};

/** Run once from the editor: makes the tabs and their headings, and the weekly summary. Safe to run again. */
function setup() {
  const ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);
  Object.keys(TABS).forEach(function (name) {
    let sh = ss.getSheetByName(name);
    if (!sh) sh = ss.insertSheet(name);
    if (sh.getLastRow() === 0) {
      sh.getRange(1, 1, 1, TABS[name].length).setValues([TABS[name]]).setFontWeight('bold');
      sh.setFrozenRows(1);
    }
  });
  const first = ss.getSheetByName('Sheet1') || ss.getSheetByName('Ark1');
  if (first && first.getLastRow() === 0 && ss.getSheets().length > 1) ss.deleteSheet(first);
  DriveApp.getFolderById(CONFIG.FOLDER_ID).getName();   // asks for the Drive permission at the same time
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'weeklySummary') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('weeklySummary').timeBased().onWeekDay(ScriptApp.WeekDay.MONDAY).atHour(8).inTimezone(CONFIG.TZ).create();
  log_('info', 'setup run');
  return 'ok';
}

/** A plain check that the web app answers. */
function doGet() {
  return json_({ ok: true, service: 'Africa Reframed intake' });
}

function doPost(e) {
  try {
    const d = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    if (d.key !== CONFIG.SITE_KEY) return json_({ ok: false, error: 'not from our form' });
    if (clean_(d.website)) return json_({ ok: true, id: '' });            // the trap field: a robot filled it in
    if (tooMany_()) { log_('warn', 'too many posts in a minute'); return json_({ ok: false, error: 'busy' }); }

    const form = d.form === 'request' ? 'request' : 'message';
    const email = clean_(d.email).toLowerCase();
    const organisation = clean_(d.organisation);
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return json_({ ok: false, error: 'email' });
    if (!organisation) return json_({ ok: false, error: 'organisation' });

    const flags = [];
    if (d.test) flags.push('test');
    if (Number(d.elapsed) > 0 && Number(d.elapsed) < 3000) flags.push('sent in under 3 seconds');

    const ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);
    const known = knownPartner_(ss, email);
    const when = Utilities.formatDate(new Date(), CONFIG.TZ, 'yyyy-MM-dd HH:mm');
    const source = clean_(d.source) || clean_(d.page);

    let file = null;
    if (d.file && d.file.data) {
      file = saveFile_(d.file);
      if (file.error) return json_({ ok: false, error: file.error });
    }

    const lock = LockService.getScriptLock();
    lock.waitLock(20000);
    let id, row, sheetName;
    try {
      if (form === 'request') {
        sheetName = 'Requests';
        id = nextId_(ss, sheetName, 'R');
        row = [id, when, 'new', organisation, clean_(d.org_type), clean_(d.country), clean_(d.name), clean_(d.role), email,
               d.colleague ? 'yes' : '', clean_(d.focus), clean_(d.use), clean_(d.looking_for),
               d.consent ? 'yes' : 'no', known, source, flags.join('; '), ''];
      } else {
        sheetName = 'Messages';
        id = nextId_(ss, sheetName, 'M');
        const kind = KINDS[d.kind] || KINDS.question;
        if (!clean_(d.text) && !clean_(d.link) && !file) return json_({ ok: false, error: 'empty' });
        row = [id, when, 'new', kind, organisation, clean_(d.name), email, clean_(d.text), clean_(d.link),
               clean_(d.photo_ids), file ? file.url : '', known, source, flags.join('; '), ''];
      }
      ss.getSheetByName(sheetName).appendRow(row.map(safe_));
    } finally {
      lock.releaseLock();
    }
    if (file) { try { DriveApp.getFileById(file.id).setName(id + ' – ' + file.name); } catch (err) { log_('warn', 'rename: ' + err); } }

    try { notify_(sheetName, id, row, ss, email, flags); } catch (err) { log_('error', 'notify ' + id + ': ' + err); }
    try { confirm_(form, id, d, email); } catch (err) { log_('error', 'confirm ' + id + ': ' + err); }
    return json_({ ok: true, id: id });
  } catch (err) {
    log_('error', String(err && err.stack || err));
    return json_({ ok: false, error: 'server' });
  }
}

/** Monday morning: what came in during the week, and proof that the system is alive. */
function weeklySummary() {
  const ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);
  const since = new Date(Date.now() - 7 * 24 * 3600 * 1000);
  const lines = [];
  ['Requests', 'Messages'].forEach(function (name) {
    const sh = ss.getSheetByName(name);
    const rows = sh.getLastRow() > 1 ? sh.getRange(2, 1, sh.getLastRow() - 1, 3).getValues() : [];
    const recent = rows.filter(function (r) { return new Date(String(r[1]).replace(' ', 'T')) >= since; }).length;
    const open = rows.filter(function (r) { return String(r[2]).toLowerCase() === 'new'; }).length;
    lines.push(name + ': ' + recent + ' in the last seven days, ' + open + ' still marked new.');
  });
  const logSh = ss.getSheetByName('Log');
  const logs = logSh.getLastRow() > 1 ? logSh.getRange(2, 1, logSh.getLastRow() - 1, 3).getValues() : [];
  const errors = logs.filter(function (r) { return r[1] === 'error' && new Date(String(r[0]).replace(' ', 'T')) >= since; }).length;
  lines.push('Errors logged: ' + errors + '.');
  MailApp.sendEmail({
    to: CONFIG.NOTIFY,
    name: CONFIG.SENDER_NAME + ' intake',
    subject: '[Intake] The week: ' + lines[0].split(',')[0] + '; ' + lines[1].split(',')[0],
    body: lines.join('\n') + '\n\nThe spreadsheet: ' + ss.getUrl() + '\n\nThis summary is sent every Monday by the intake script. If it stops coming, the script has stopped.'
  });
}

// ---------------------------------------------------------------------------------------------------------------

function notify_(sheetName, id, row, ss, email, flags) {
  const head = TABS[sheetName];
  const body = head.map(function (h, i) { return row[i] !== '' && h !== 'Notes' ? h + ': ' + row[i] : null; })
    .filter(Boolean).join('\n');
  const what = sheetName === 'Requests' ? (row[9] ? 'Access for a colleague' : 'Request access') : row[3];
  MailApp.sendEmail({
    to: CONFIG.NOTIFY,
    replyTo: email,
    name: CONFIG.SENDER_NAME + ' intake',
    subject: '[Intake] ' + id + ' · ' + what + ' · ' + row[sheetName === 'Requests' ? 3 : 4] + (flags.length ? ' · ' + flags.join(', ') : ''),
    body: body + '\n\nThe spreadsheet: ' + ss.getUrl() + '\nAnswering this email answers the sender.'
  });
}

/**
 * The confirmation to the sender. It names what she sent, in the words of the card she pressed (How we speak –
 * working notes, Trial 2, version A; Thomas, 16 November 2026, 14:29). The words are drafts.
 */
const SENT = {
  made: 'What you made',
  missing: 'Your note on what is missing',
  feedback: 'Your feedback',
  bigger: 'What you have in mind'
};

function confirm_(form, id, d, email) {
  const name = clean_(d.name).split(' ')[0];
  const hello = name ? 'Dear ' + name + ',\n\n' : '';
  let subject, text;
  if (form === 'request') {
    subject = 'Africa Reframed: we have your request (' + id + ')';
    text = 'Thank you. Your request is with us. We read every request ourselves, and you have our answer within a working day.';
  } else {
    subject = 'Africa Reframed: we have your message (' + id + ')';
    text = 'Thank you. ' + (SENT[d.kind] || 'Your message') + ' is with us.';
  }
  MailApp.sendEmail({
    to: email,
    replyTo: CONFIG.REPLY_TO,
    name: CONFIG.SENDER_NAME,
    subject: subject,
    body: hello + text + '\n\nTo add something, answer this email. If it was not you who wrote, tell us the same way.\n\nAfrica Reframed\nReference: ' + id
  });
}

function saveFile_(f) {
  const name = String(f.name || 'file').replace(/[\\/:*?"<>|\u0000-\u001f]/g, ' ').trim().slice(0, 120) || 'file';
  const ext = (name.split('.').pop() || '').toLowerCase();
  if (CONFIG.FILE_TYPES.indexOf(ext) === -1) return { error: 'file type' };
  const bytes = Utilities.base64Decode(String(f.data));
  if (bytes.length > CONFIG.MAX_FILE_MB * 1024 * 1024) return { error: 'file size' };
  const blob = Utilities.newBlob(bytes, String(f.type || 'application/octet-stream'), name);
  const file = DriveApp.getFolderById(CONFIG.FOLDER_ID).createFile(blob);
  return { id: file.getId(), url: file.getUrl(), name: name };
}

function knownPartner_(ss, email) {
  const sh = ss.getSheetByName('Partners');
  if (!sh || sh.getLastRow() < 2) return 'no';
  const domain = email.split('@')[1];
  const col = sh.getRange(2, 2, sh.getLastRow() - 1, 1).getValues();
  for (let i = 0; i < col.length; i++) {
    const v = String(col[i][0]).trim().toLowerCase().replace(/^@/, '');
    if (v && (v === email || v === domain)) return 'yes';
  }
  return 'no';
}

function nextId_(ss, sheetName, prefix) {
  const sh = ss.getSheetByName(sheetName);
  let n = 0;
  if (sh.getLastRow() > 1) {
    const last = String(sh.getRange(sh.getLastRow(), 1).getValue());
    n = parseInt(last.replace(/\D/g, ''), 10) || (sh.getLastRow() - 1);
  }
  return prefix + '-' + ('0000' + (n + 1)).slice(-4);
}

function tooMany_() {
  const cache = CacheService.getScriptCache();
  const key = 'n' + Math.floor(Date.now() / 60000);
  const n = (parseInt(cache.get(key), 10) || 0) + 1;
  cache.put(key, String(n), 120);
  return n > CONFIG.MAX_PER_MINUTE;
}

function clean_(v) {
  return String(v == null ? '' : v).replace(/\r/g, '').trim().slice(0, 5000);
}

/** A cell that begins like a formula is written as text. */
function safe_(v) {
  return typeof v === 'string' && /^[=+\-@]/.test(v) ? "'" + v : v;
}

function log_(level, what) {
  try {
    SpreadsheetApp.openById(CONFIG.SHEET_ID).getSheetByName('Log')
      .appendRow([Utilities.formatDate(new Date(), CONFIG.TZ, 'yyyy-MM-dd HH:mm'), level, String(what).slice(0, 2000)]);
  } catch (err) { /* the log must never stop a message */ }
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
