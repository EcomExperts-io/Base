# Theme Utilities

`assets/theme.js` exports utility functions shared across the application. This module provides common helper functions used by other components in the theme.

**Source:** [`assets/theme.js`](../../assets/theme.js)

## Overview

The `theme.js` module:
- Provides reusable utility functions
- Exports functions for use in other modules
- Currently includes a debounce function for performance optimization

## Exported Functions

### debounce(fn, wait)

Delays the execution of a function until after a specified wait time has passed since the last time it was invoked. Useful for limiting the rate at which functions execute, particularly for event handlers like input events.

**Parameters:**
- `fn` (Function): The function to debounce
- `wait` (number): The number of milliseconds to delay

**Returns:**
- `Function`: The debounced function

**Usage:**

```javascript
import { debounce } from './theme.js';

// Create a debounced function
const debouncedSearch = debounce((searchTerm) => {
  console.log('Searching for:', searchTerm);
}, 300);

// Call it multiple times - only executes after 300ms of inactivity
debouncedSearch('a');
debouncedSearch('ab');
debouncedSearch('abc'); // Only this call executes after 300ms
```

## Implementation

```javascript
export function debounce(fn, wait) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn.apply(this, args), wait);
  };
}
```

**How it works:**
1. Returns a new function that wraps the original
2. Each call clears the previous timeout
3. Sets a new timeout to execute the function after the wait period
4. Only executes if no new calls are made within the wait period

## Usage Examples

### Input Search Debouncing

```javascript
import { debounce } from './theme.js';

const searchInput = document.querySelector('#search');
searchInput.addEventListener('input', debounce((e) => {
  performSearch(e.target.value);
}, 500));
```

### Window Resize Handler

```javascript
import { debounce } from './theme.js';

window.addEventListener('resize', debounce(() => {
  updateLayout();
}, 250));
```

### Scroll Event Optimization

```javascript
import { debounce } from './theme.js';

window.addEventListener('scroll', debounce(() => {
  checkScrollPosition();
}, 100));
```

## Integration

The `debounce` function is used by the `PredictiveSearch` component:

```javascript
import { debounce } from './theme.js';

// In PredictiveSearch constructor
this.input.addEventListener('input', debounce((e) => this.onChange(e), 700));
```

## Implementation Notes

- The debounce function uses `setTimeout` and `clearTimeout` for timing
- The function preserves `this` context using `fn.apply(this, args)`
- Arguments are passed through using rest parameters (`...args`)
- Each call cancels the previous timeout, ensuring only the last call executes
- The function is pure and has no side effects
- Can be used with any function that needs rate limiting
- Commonly used for: search inputs, resize handlers, scroll events, API calls

