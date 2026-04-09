/* ========== home.js — Homepage Scripts ========== */

$(document).ready(function () {

  /* ---- Product card: quick add to cart (placeholder) ---- */
  $(document).on('click', '.card-product-grid .btn-cart', function (e) {
    e.preventDefault();
    var count = parseInt($('.badge.notify').text() || '0', 10);
    $('.badge.notify').text(count + 1);

    /* Visual feedback */
    var $btn = $(this);
    $btn.text('Added!').addClass('btn-success').removeClass('btn-primary');
    setTimeout(function () {
      $btn.text('Add to cart').addClass('btn-primary').removeClass('btn-success');
    }, 1200);
  });

  /* ---- Banner: simple fade-in ---- */
  $('.intro-banner-wrap img').css('opacity', 0).animate({ opacity: 1 }, 600);

  /* ---- Product cards: staggered fade-in ---- */
  $('.card-product-grid').each(function (i) {
    var $card = $(this);
    $card.css('opacity', 0);
    setTimeout(function () {
      $card.animate({ opacity: 1 }, 300);
    }, i * 60);
  });

});
