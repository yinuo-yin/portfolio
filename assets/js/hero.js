// Hero animation: a slowly rotating globe of dots with a few "hot" clusters
// and data arcs travelling between them. Drag to spin it. Plain canvas, no
// libraries. Respects prefers-reduced-motion and pauses when off screen.
(function () {
  const canvas = document.getElementById("globe");
  if (!canvas || !canvas.getContext) return;
  const ctx = canvas.getContext("2d");

  const ACCENT = [180, 73, 31];   // #b4491f
  const BLUE = [47, 111, 159];    // #2f6f9f
  const DOT = [201, 196, 189];    // #c9c4bd
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Points spread evenly over a sphere (Fibonacci lattice)
  const N = 1100;
  const pts = [];
  const golden = Math.PI * (3 - Math.sqrt(5));
  for (let i = 0; i < N; i++) {
    const y = 1 - (i / (N - 1)) * 2;
    const r = Math.sqrt(1 - y * y);
    const t = golden * i;
    pts.push([Math.cos(t) * r, y, Math.sin(t) * r]);
  }

  // A few cluster centres; each point gets a "heat" from the nearest one
  const seed = (s => () => (s = (s * 16807) % 2147483647) / 2147483647)(42);
  const centers = [];
  for (let k = 0; k < 7; k++) {
    // mid latitudes, spread around the globe so a few are always in view
    const u = (seed() - 0.5) * 1.1, th = (k / 7) * Math.PI * 2 + seed() * 0.5, rr = Math.sqrt(1 - u * u);
    centers.push({ v: [Math.cos(th) * rr, u, Math.sin(th) * rr], blue: k % 3 === 2 });
  }
  const heat = pts.map(p => {
    let best = 0, blue = false;
    for (const c of centers) {
      const d = p[0] * c.v[0] + p[1] * c.v[1] + p[2] * c.v[2]; // cosine
      const h = Math.max(0, (d - 0.88) / 0.12);
      if (h > best) { best = h; blue = c.blue; }
    }
    return { h: best, blue };
  });

  // Great-circle arcs between some cluster pairs
  const pairs = [[0, 1], [1, 3], [2, 4], [3, 5], [4, 6], [5, 0]];
  function slerp(a, b, t) {
    const dot = Math.min(1, Math.max(-1, a[0] * b[0] + a[1] * b[1] + a[2] * b[2]));
    const om = Math.acos(dot), so = Math.sin(om) || 1;
    const s1 = Math.sin((1 - t) * om) / so, s2 = Math.sin(t * om) / so;
    const lift = 1 + 0.07 * Math.sin(Math.PI * t); // arc rises off the surface
    return [(a[0] * s1 + b[0] * s2) * lift, (a[1] * s1 + b[1] * s2) * lift, (a[2] * s1 + b[2] * s2) * lift];
  }

  let W = 0, H = 0, R = 0, dpr = 1;
  function resize() {
    const box = canvas.getBoundingClientRect();
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = box.width; H = box.height;
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    R = Math.min(W, H) * 0.4;
  }

  let rotY = 2.4, rotX = -0.3, vel = 0.0022, dragging = false, lastX = 0, lastY = 0;
  function project(p) {
    const cy = Math.cos(rotY), sy = Math.sin(rotY), cx = Math.cos(rotX), sx = Math.sin(rotX);
    const x1 = p[0] * cy + p[2] * sy, z1 = -p[0] * sy + p[2] * cy;
    const y2 = p[1] * cx - z1 * sx, z2 = p[1] * sx + z1 * cx;
    return [W / 2 + x1 * R, H / 2 + y2 * R, z2];
  }
  const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;

  let t0 = performance.now();
  function draw(now) {
    const time = (now - t0) / 1000;
    ctx.clearRect(0, 0, W, H);

    // faint outline of the sphere
    ctx.beginPath(); ctx.arc(W / 2, H / 2, R, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(138,132,124,0.25)"; ctx.lineWidth = 1; ctx.stroke();

    for (let i = 0; i < N; i++) {
      const [x, y, z] = project(pts[i]);
      const front = z > 0;
      const depth = (z + 1) / 2;                 // 0 back .. 1 front
      const hh = heat[i].h;
      let col = DOT, a = front ? 0.35 + 0.45 * depth : 0.08, r = 1.1 + 1.2 * depth;
      if (hh > 0 && front) {
        col = heat[i].blue ? BLUE : ACCENT;
        const pulse = reduce ? 1 : 0.75 + 0.25 * Math.sin(time * 2 + i);
        a = (0.35 + 0.65 * hh) * pulse; r = 1.4 + 2.2 * hh * depth;
      }
      ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fillStyle = rgba(col, a); ctx.fill();
    }

    // arcs with a travelling highlight
    pairs.forEach(([i, j], k) => {
      const a = centers[i].v, b = centers[j].v, steps = 48;
      let prev = null;
      const head = reduce ? 0.5 : ((time * 0.25 + k * 0.2) % 1);
      for (let s = 0; s <= steps; s++) {
        const t = s / steps, q = project(slerp(a, b, t));
        if (prev && q[2] > -0.1 && prev[2] > -0.1) {
          const near = Math.max(0, 1 - Math.abs(t - head) * 6);
          ctx.beginPath(); ctx.moveTo(prev[0], prev[1]); ctx.lineTo(q[0], q[1]);
          ctx.strokeStyle = rgba(ACCENT, 0.18 + 0.7 * near);
          ctx.lineWidth = 1 + 1.5 * near; ctx.stroke();
        }
        prev = q;
      }
    });
  }

  let running = true, visible = true;
  function loop(now) {
    if (!dragging) rotY += vel;
    draw(now);
    if (running && visible && !reduce) requestAnimationFrame(loop);
  }

  canvas.addEventListener("pointerdown", e => { dragging = true; lastX = e.clientX; lastY = e.clientY; canvas.setPointerCapture(e.pointerId); });
  canvas.addEventListener("pointermove", e => {
    if (!dragging) return;
    rotY += (e.clientX - lastX) * 0.008;
    rotX = Math.max(-1.2, Math.min(1.2, rotX + (e.clientY - lastY) * 0.008));
    lastX = e.clientX; lastY = e.clientY;
    if (reduce) draw(performance.now());
  });
  canvas.addEventListener("pointerup", () => { dragging = false; });
  canvas.addEventListener("pointercancel", () => { dragging = false; });

  if ("IntersectionObserver" in window) {
    new IntersectionObserver(entries => {
      const was = visible; visible = entries[0].isIntersecting;
      if (visible && !was && !reduce) requestAnimationFrame(loop);
    }).observe(canvas);
  }
  window.addEventListener("resize", () => { resize(); draw(performance.now()); });

  resize();
  if (reduce) draw(performance.now()); else requestAnimationFrame(loop);
})();
