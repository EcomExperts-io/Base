
document.addEventListener('DOMContentLoaded', function () {
  var thumbsSwiper = new Swiper('.thumbs-gallery', {
    spaceBetween: 8,
    slidesPerView: 5,
    freeMode: true,
    watchSlidesProgress: true,
    breakpoints: {
      600: { slidesPerView: 6 },
      900: { slidesPerView: 7 }
    }
  });
  var mainSwiper = new Swiper('.main-gallery', {
    spaceBetween: 10,
    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev',
    },
    pagination: {
      el: '.swiper-pagination',
      clickable: true,
    },
    thumbs: {
      swiper: thumbsSwiper,
    },
  });
});
