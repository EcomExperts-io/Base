/**
 * Progress Bar Utility
 * 
 * Simple utility for updating progress bars based on Swiper slider state.
 */

export function updateProgressBar(swiper, progressFillElement) {
  if (!swiper || !progressFillElement) return;

  const totalSlides = swiper.slides.length;
  if (totalSlides === 0) return;
  
  const slidesPerView = swiper.params.slidesPerView || 1;
  const currentIndex = swiper.activeIndex;
  // Calculate the last visible slide index
  const lastVisibleIndex = currentIndex + slidesPerView - 1;
  const maxIndex = totalSlides - 1;
  
  // If we've reached the end (last visible slide is the last slide), show 100%
  if (lastVisibleIndex >= maxIndex) {
    progressFillElement.style.width = '100%';
  } else {
    const progress = ((lastVisibleIndex + 1) / totalSlides) * 100;
    console.log(progress);
    progressFillElement.style.width = `${progress}%`;
  }
}
