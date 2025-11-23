/**
 * Utility functions shared across the application
 */

/**
 * Debounce function that delays the execution of a function until after a specified wait time
 * @param {Function} fn - The function to debounce
 * @param {number} wait - The number of milliseconds to delay
 * @returns {Function} The debounced function
 */
export function debounce(fn, wait) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn.apply(this, args), wait);
  };
}
