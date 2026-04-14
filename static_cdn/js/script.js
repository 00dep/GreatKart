/* ========== script.js — GreatKart Global Scripts ========== */

$(document).ready(function () {

  /* ---- Navbar: close on outside click (mobile) ---- */
  $(document).on('click', function (e) {
    if (!$(e.target).closest('.navbar').length) {
      $('.navbar-collapse').collapse('hide');
    }
  });

  /* ---- Cart badge: keep server-rendered count only ---- */
  /* Removed localStorage overrides so the navbar uses the backend cart_count value. */

  /* ---- Search: prevent empty submit ---- */
  $('form.search').on('submit', function (e) {
    var q = $(this).find('input[type="text"]').val().trim();
    if (!q) {
      e.preventDefault();
      $(this).find('input[type="text"]').focus();
    }
  });

  /* ---- Dropdown: keyboard close on Esc ---- */
  $(document).on('keydown', function (e) {
    if (e.key === 'Escape') {
      $('.dropdown-menu').removeClass('show');
      $('.dropdown-toggle').attr('aria-expanded', 'false');
    }
  });

});
