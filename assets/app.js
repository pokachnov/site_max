// MAX × МИЭМ — статический сайт: поиск, фильтр, частицы, курсор, reveal, 3D-tilt
(function () {
  'use strict';
  var prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var isTouch = window.matchMedia('(pointer: coarse)').matches;

  // ====== частицы ======
  if (!prefersReduced) initParticles();
  function initParticles() {
    var canvas = document.getElementById('particles');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    function resize() {
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      canvas.style.width = window.innerWidth + 'px';
      canvas.style.height = window.innerHeight + 'px';
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(dpr, dpr);
    }
    resize();
    var count = window.innerWidth < 768 ? 28 : 50;
    var particles = [];
    for (var i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        r: Math.random() * 1.5 + 0.5,
        hue: Math.random() > 0.5 ? 215 : 265
      });
    }
    var mouse = { x: -1000, y: -1000 };
    window.addEventListener('mousemove', function (e) { mouse.x = e.clientX; mouse.y = e.clientY; });
    window.addEventListener('resize', resize);
    function draw() {
      ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
      for (var i = 0; i < particles.length; i++) {
        var p = particles[i];
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0) p.x = window.innerWidth;
        if (p.x > window.innerWidth) p.x = 0;
        if (p.y < 0) p.y = window.innerHeight;
        if (p.y > window.innerHeight) p.y = 0;
        var dx = p.x - mouse.x, dy = p.y - mouse.y;
        var d = Math.sqrt(dx * dx + dy * dy);
        if (d < 140) { p.x += dx / d * 0.8; p.y += dy / d * 0.8; }
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = 'hsla(' + p.hue + ', 80%, 65%, 0.6)';
        ctx.fill();
        for (var j = i + 1; j < particles.length; j++) {
          var q = particles[j];
          var lx = p.x - q.x, ly = p.y - q.y;
          var ld = Math.sqrt(lx * lx + ly * ly);
          if (ld < 120) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(q.x, q.y);
            ctx.strokeStyle = 'hsla(' + p.hue + ', 80%, 60%, ' + (0.15 * (1 - ld / 120)) + ')';
            ctx.lineWidth = 0.6;
            ctx.stroke();
          }
        }
      }
      requestAnimationFrame(draw);
    }
    draw();
  }

  // ====== кастомный курсор ======
  if (!isTouch) initCursor();
  function initCursor() {
    var dot = document.getElementById('cDot');
    var ring = document.getElementById('cRing');
    if (!dot || !ring) return;
    var rx = window.innerWidth / 2, ry = window.innerHeight / 2;
    document.addEventListener('mousemove', function (e) {
      dot.style.transform = 'translate(' + (e.clientX - 3.5) + 'px,' + (e.clientY - 3.5) + 'px)';
    });
    (function loop() {
      var mx = 0, my = 0;
      document.addEventListener('mousemove', function (e) { mx = e.clientX; my = e.clientY; }, { passive: true });
      rx += (mx - rx) * 0.18;
      ry += (my - ry) * 0.18;
      ring.style.transform = 'translate(' + (rx - 19) + 'px,' + (ry - 19) + 'px)';
      // hack: read latest mouse
      rx += 0; ry += 0;
      requestAnimationFrame(loop);
    })();
    var hoverSel = 'a, button, .tile, .filter, .rel, .btn, .chip';
    document.addEventListener('mouseover', function (e) {
      if (e.target.closest && e.target.closest(hoverSel)) ring.classList.add('hover');
    });
    document.addEventListener('mouseout', function (e) {
      if (e.target.closest && e.target.closest(hoverSel)) ring.classList.remove('hover');
    });
  }

  // ====== прогресс-бар скролла + параллакс ======
  if (!prefersReduced) {
    var progress = document.getElementById('progress');
    var ticking = false;
    window.addEventListener('scroll', function () {
      if (!ticking) {
        requestAnimationFrame(function () {
          var h = document.documentElement.scrollHeight - window.innerHeight;
          var p = h > 0 ? window.scrollY / h : 0;
          if (progress) progress.style.transform = 'scaleX(' + p + ')';
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });
  }

  // ====== reveal анимация ======
  var els = document.querySelectorAll('.reveal');
  if (els.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -8% 0px' });
    els.forEach(function (el) { io.observe(el); });
  }

  // ====== счётчики ======
  document.querySelectorAll('[data-count]').forEach(function (el) {
    var target = parseFloat(el.getAttribute('data-count'));
    var decimals = target % 1 !== 0 ? 1 : 0;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          var start = null;
          function step(ts) {
            if (!start) start = ts;
            var t = Math.min((ts - start) / 1800, 1);
            var eased = 1 - Math.pow(1 - t, 3);
            el.textContent = (target * eased).toFixed(decimals);
            if (t < 1) requestAnimationFrame(step);
            else el.textContent = target.toFixed(decimals);
          }
          requestAnimationFrame(step);
          io.unobserve(el);
        }
      });
    }, { threshold: 0.5 });
    io.observe(el);
  });

  // ====== fit bars ======
  document.querySelectorAll('.fit-bar span[data-width]').forEach(function (el) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { el.style.width = el.getAttribute('data-width') + '%'; io.unobserve(el); }
      });
    }, { threshold: 0.4 });
    io.observe(el);
  });

  // ====== 3D-tilt ======
  if (!isTouch && !prefersReduced) initTilt();
  function initTilt() {
    document.querySelectorAll('.tile').forEach(function (tile) {
      var active = false;
      tile.addEventListener('mouseenter', function () { active = true; });
      tile.addEventListener('mousemove', function (e) {
        if (!active) return;
        var rect = tile.getBoundingClientRect();
        var x = e.clientX - rect.left;
        var y = e.clientY - rect.top;
        var cx = rect.width / 2, cy = rect.height / 2;
        tile.style.transform = 'perspective(800px) rotateX(' + ((y - cy) / cy * -6) + 'deg) rotateY(' + ((x - cx) / cx * 8) + 'deg) translateY(-4px)';
      });
      tile.addEventListener('mouseleave', function () { active = false; tile.style.transform = ''; });
    });
  }

  // ====== поиск + фильтр (только на хабе) ======
  var q = document.getElementById('q');
  var tiles = Array.prototype.slice.call(document.querySelectorAll('.tile'));
  var filters = Array.prototype.slice.call(document.querySelectorAll('.filter'));
  var empty = document.getElementById('empty');
  if (q && tiles.length) {
    var cat = 'all';
    function apply() {
      var needle = (q.value || '').trim().toLowerCase();
      var shown = 0;
      tiles.forEach(function (t) {
        var okCat = cat === 'all' || t.getAttribute('data-cat') === cat;
        var okText = !needle || (t.getAttribute('data-text') || '').indexOf(needle) !== -1;
        t.hidden = !(okCat && okText);
        if (!t.hidden) shown++;
      });
      if (empty) empty.hidden = shown !== 0;
    }
    q.addEventListener('input', apply);
    filters.forEach(function (b) {
      b.addEventListener('click', function () {
        filters.forEach(function (x) { x.classList.remove('on'); });
        b.classList.add('on');
        cat = b.getAttribute('data-filter');
        apply();
      });
    });
  }
})();