(function () {
  var $ = function (id) { return document.getElementById(id); };
  var fmt = function (n) { return Number(n).toLocaleString("en-US"); };

  async function api(path, body) {
    var r = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || {})
    });
    return r.json();
  }

  var tabs = document.querySelectorAll(".tab");
  tabs.forEach(function (t) {
    t.onclick = function () {
      tabs.forEach(function (x) { x.classList.remove("active"); });
      document.querySelectorAll(".panel").forEach(function (p) { p.classList.remove("show"); });
      t.classList.add("active");
      $(t.dataset.p).classList.add("show");
    };
  });

  function setStatus(t, busy) {
    $("engineStatus").textContent = t;
    $("dot").classList.toggle("busy", !!busy);
  }

  function pushLog(el, txt, cls) {
    var d = document.createElement("div");
    d.className = "ln" + (cls ? " " + cls : "");
    d.textContent = txt;
    el.appendChild(d);
    while (el.children.length > 9) el.removeChild(el.firstChild);
  }

  var otpBusy = false;
  $("otpStart").onclick = async function () {
    if (otpBusy) return;
    otpBusy = true;
    var rate = parseInt($("otpRate").value, 10);
    var res = await api("/api/otp", { target: $("otpTarget").value, rate: rate });
    var lg = $("otpLog");
    lg.innerHTML = "";
    pushLog(lg, "> target resolved: " + res.target);
    pushLog(lg, "> space = 1,000,000 codes, rate = " + fmt(rate) + "/s");
    pushLog(lg, "> sweeping from 000000 ...");
    setStatus("sweeping otp space", true);
    $("otpStart").disabled = true;
    $("otpRateDisp").textContent = fmt(rate) + "/s";
    var target = res.index, tries = 0;
    var step = Math.max(1, Math.round(target / 70));
    var t0 = Date.now();
    var iv = setInterval(function () {
      tries = Math.min(tries + step, target);
      var cov = tries / 1000000;
      $("otpBar").style.width = (cov * 100).toFixed(2) + "%";
      $("otpTried").textContent = fmt(tries);
      $("otpCover").textContent = (cov * 100).toFixed(2) + "%";
      $("otpEta").textContent = ((1000000 - tries) / rate).toFixed(2) + "s";
      if (tries >= target) {
        clearInterval(iv); otpBusy = false;
        $("otpStart").disabled = false;
        setStatus("otp cracked", false);
        pushLog(lg, "> " + res.code + " accepted  <-- LIVE CODE", "ok");
        pushLog(lg, "> code = " + res.code + "  (" + fmt(target) + " attempts, " +
          ((Date.now() - t0) / 1000).toFixed(1) + "s)", "hit");
      }
    }, 60);
  };

  function makeCracker(cfg) {
    $(cfg.mode).onchange = function () {
      $(cfg.bruteRow).style.display = this.value === "brute" ? "flex" : "none";
    };
    var busy = false;
    $(cfg.start).onclick = async function () {
      if (busy) return;
      busy = true;
      var res = await api("/api/crack", {
        target: $(cfg.user).value, salt: cfg.salt,
        mode: $(cfg.mode).value, length: parseInt($(cfg.len).value, 10)
      });
      $(cfg.space).textContent = fmt(res.total);
      $(cfg.result).style.display = "none";
      var lg = $(cfg.log);
      lg.innerHTML = "";
      pushLog(lg, "> resolving " + res.target + " ...");
      pushLog(lg, "> account exists, handshake ok");
      pushLog(lg, "> search space: " + fmt(res.total) + " candidates");
      pushLog(lg, "> launching attack ...");
      setStatus("cracking " + res.target, true);
      $(cfg.start).disabled = true;
      var shownRate = Math.max(60, Math.round(res.total / 10));
      $(cfg.rate).textContent = fmt(shownRate) + "/s";
      var target = res.attempts, tries = 0;
      var step = Math.max(1, Math.round(target / 70));
      var iv = setInterval(function () {
        tries = Math.min(tries + step, target);
        $(cfg.bar).style.width = ((tries / res.total) * 100).toFixed(3) + "%";
        $(cfg.tried).textContent = fmt(tries);
        $(cfg.eta).textContent = ((res.total - tries) / shownRate).toFixed(1) + "s";
        $(cfg.current).textContent = "trying: " + cfg.cand(tries, res);
        if (tries % (step * 3) < step) pushLog(lg, "> " + cfg.cand(tries, res) + "  ... rejected");
        if (tries >= target) {
          clearInterval(iv); busy = false;
          $(cfg.start).disabled = false;
          setStatus("access granted", false);
          $(cfg.current).textContent = "trying: " + res.password;
          pushLog(lg, "> " + res.password + " accepted  <-- MATCH", "ok");
          $(cfg.resUser).textContent = res.target;
          $(cfg.resPass).textContent = res.password;
          $(cfg.resTries).textContent = fmt(res.attempts);
          $(cfg.res2fa).textContent = res.twofa ? "triggered \u2014 run the otp sweep" : "not enabled";
          $(cfg.result).style.display = "block";
        }
      }, 60);
    };
  }

  var CHARSET = "abcdefghijklmnopqrstuvwxyz0123456789";
  function idxToPass(i, len) {
    var s = "";
    for (var k = 0; k < len; k++) { s = CHARSET[i % CHARSET.length] + s; i = Math.floor(i / CHARSET.length); }
    return s;
  }
  var candFn = function (n, res) { return res.mode === "brute" ? idxToPass(n, res.length) : "(dict)"; };

  makeCracker({ user:"igUser", mode:"igMode", len:"igLen", bruteRow:"igBruteRow", start:"igStart",
    tried:"igTried", space:"igSpace", rate:"igRate", eta:"igEta", bar:"igBar", current:"igCurrent",
    log:"igLog", result:"igResult", resUser:"igResUser", resPass:"igResPass", resTries:"igResTries",
    res2fa:"igRes2fa", salt:"ig", cand:candFn });

  makeCracker({ user:"gmUser", mode:"gmMode", len:"gmLen", bruteRow:"gmBruteRow", start:"gmStart",
    tried:"gmTried", space:"gmSpace", rate:"gmRate", eta:"gmEta", bar:"gmBar", current:"gmCurrent",
    log:"gmLog", result:"gmResult", resUser:"gmResUser", resPass:"gmResPass", resTries:"gmResTries",
    res2fa:"gmRes2fa", salt:"gm", cand:candFn });

  $("lkGen").onclick = async function () {
    var res = await api("/api/link", {
      label: $("lkName").value, service: $("lkSvc").value, redirect: $("lkRedirect").value
    });
    $("lkUrl").textContent = res.url;
    $("lkOpen").href = res.url;
    $("lkOut").style.display = "block";
    setStatus("link armed", false);
  };

  $("lkCopy").onclick = function () {
    var t = $("lkUrl").textContent;
    if (navigator.clipboard) {
      navigator.clipboard.writeText(t).then(function () {
        $("lkCopy").textContent = "copied";
        setTimeout(function () { $("lkCopy").textContent = "copy"; }, 1200);
      });
    }
  };

  function renderCaptures(rows) {
    var box = $("capList");
    if (!rows.length) { box.innerHTML = '<div class="muted" style="font-size:12px">nothing captured yet</div>'; return; }
    box.innerHTML = rows.map(function (r) {
      var when = new Date(r.created * 1000).toLocaleString();
      return '<div class="cap"><div class="cap-hd"><span>' + r.kind + '</span>' +
        '<span class="mono">' + when + ' · ' + r.ip + '</span></div>' +
        '<pre>' + JSON.stringify(JSON.parse(r.payload), null, 1) + '</pre></div>';
    }).join("");
  }
  async function loadCaptures() {
    var r = await fetch("/api/captures");
    renderCaptures(await r.json());
  }
  $("capRefresh").onclick = loadCaptures;
  $("lkPoll").onclick = loadCaptures;
  loadCaptures();
})();
