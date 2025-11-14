(function(){
  // Safely parse JSON if string, otherwise return object/null
  function safeParse(data){
    if (typeof data === 'string') {
      try { return JSON.parse(data); } catch(e) { return null; }
    }
    return (typeof data === 'object' && data !== null) ? data : null;
  }

  // Normalize common field name variations
  function extractString(obj, keys) {
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i];
      if (obj[k]) return String(obj[k]);
    }
    return '';
  }

  // Update UI; if elements not present yet, queue update until DOMContentLoaded
  var pendingUpdate = null;
  function applyUpdate(payload, fhirJsonText) {
    var welcomeEl = document.getElementById('welcome');
    var detailsEl = document.getElementById('details');
    var fhirEl = document.getElementById('fhirData');

    function doUpdate() {
      var first = extractString(payload, ['userFirstName']);
      var last = extractString(payload, ['userLastName']);
      if (welcomeEl) {
        welcomeEl.textContent = 'Welcome, ' + ((first || last) ? (first + (last ? ' ' + last : '')) : 'User');
      }
      if (detailsEl) detailsEl.textContent = JSON.stringify(payload, null, 2);
      if (fhirEl) fhirEl.textContent = fhirJsonText || 'No FHIR response or error.';
    }

    if (!welcomeEl || !detailsEl || !fhirEl) {
      pendingUpdate = {payload: payload, fhirText: fhirJsonText};
      document.addEventListener('DOMContentLoaded', function onReady(){
        document.removeEventListener('DOMContentLoaded', onReady);
        if (pendingUpdate) {
          welcomeEl = document.getElementById('welcome');
          detailsEl = document.getElementById('details');
          fhirEl = document.getElementById('fhirData');
          doUpdate();
          pendingUpdate = null;
        }
      });
    } else {
      doUpdate();
    }
  }

  // Perform async FHIR request to gateway using sdJwt (Bearer)
  async function fetchFhirForPatient(payload) {
    var gateway = extractString(payload, ['gatewayUrl','gatewayURL','gateway','gatewayurl']);
    var fhirPatient = extractString(payload, ['fhirPatient','fhirpatient','patientId','patient']);
    var sdJwt = extractString(payload, ['sdJwt','sdjwt','sd_jwt','token','authorization']);

    if (!gateway || !fhirPatient) {
      return { error: 'Missing gateway or fhirPatient in payload.' };
    }

    // Construct URL (ensure no double slash)
    var base = gateway.replace(/\/+$/,'');
    // Using a common FHIR Patient endpoint; adjust if your gateway expects different path
    var endpoint = base + '/Patient/' + encodeURIComponent(fhirPatient);

    try {
      var headers = {};
      if (sdJwt) headers['Authorization'] = 'Bearer ' + sdJwt;
      var resp = await fetch(endpoint, { method: 'GET', headers: headers, credentials: 'omit' });
      var text = await resp.text();
      try {
        var json = JSON.parse(text);
        return { status: resp.status, json: json };
      } catch (e) {
        return { status: resp.status, text: text, parseError: 'Response not valid JSON' };
      }
    } catch (err) {
      return { error: String(err) };
    }
  }

  window.addEventListener('message', function(event){
    // Optionally restrict allowed origins:
    // var allowed = ['https://your-parent.example'];
    // if (allowed.indexOf(event.origin) === -1) return;

    var payload = safeParse(event.data);
    if (!payload) {
      console.warn('Received non-JSON or invalid message:', event.data);
      return;
    }

    // Immediately show received payload; we'll update FHIR section after query
    applyUpdate(payload, 'Querying FHIR data...');

    // Fire-and-forget async FHIR fetch and then update UI with result
    fetchFhirForPatient(payload).then(function(result){
      var resultText;
      if (result === null) {
        resultText = 'No result';
      } else if (result.error) {
        resultText = 'Error: ' + result.error;
      } else if (result.json !== undefined) {
        resultText = JSON.stringify(result.json, null, 2);
      } else if (result.text !== undefined) {
        resultText = 'HTTP ' + result.status + ' - ' + result.text;
      } else {
        resultText = JSON.stringify(result, null, 2);
      }
      applyUpdate(payload, resultText);
    });

    // Send a simple acknowledgement back to the parent (if possible)
    try {
      var ack = { status: 'received', timestamp: new Date().toISOString(), fhirPatient: !!payload.fhirPatient };
      if (event.source && event.source.postMessage) {
        event.source.postMessage(JSON.stringify(ack), event.origin || '*');
      }
    } catch (e) {
      console.warn('Could not postMessage ack to parent:', e);
    }
  }, false);
})();
