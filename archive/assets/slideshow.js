// Stand-in for Cargo's slideshow script: one image at a time, arrows, autoplay.
document.querySelectorAll('.image-gallery[image-gallery="slideshow"]').forEach(function (g) {
  var list = g.querySelector('.slick-list'), track = g.querySelector('.slick-track');
  if (!list || !track) return;
  track.querySelectorAll('.slick-cloned').forEach(function (c) { c.remove(); });
  var slides = Array.prototype.slice.call(track.children), n = slides.length, i = 0;
  var h = parseFloat(list.style.height) || 400;
  list.style.cssText = 'width:100%;overflow:hidden;position:relative;height:auto';
  track.style.cssText = 'display:flex;width:100%;transition:transform .5s ease;transform:none';
  slides.forEach(function (s) {
    s.style.cssText = 'flex:0 0 100%;width:100%;display:flex;align-items:center;justify-content:center;float:none';
    var img = s.querySelector('img');
    if (img) { img.style.cssText = 'max-width:100%;max-height:' + h + 'px;width:auto;height:auto;display:block;margin:0 auto'; }
  });
  function go(k) { i = (k + n) % n; track.style.transform = 'translateX(' + (-100 * i) + '%)'; }
  var arrows = g.querySelectorAll('.slick-arrow');
  arrows.forEach(function (a) {
    a.style.height = '100%'; a.style.width = '15%'; a.classList.remove('hidden');
    a.addEventListener('click', function () { go(i + (a.classList.contains('slick-next') ? 1 : -1)); });
  });
  var paused = false;
  g.addEventListener('mouseenter', function () { paused = true; });
  g.addEventListener('mouseleave', function () { paused = false; });
  if (n > 1 && !matchMedia('(prefers-reduced-motion: reduce)').matches)
    setInterval(function () { if (!paused) go(i + 1); }, 2500);
});
