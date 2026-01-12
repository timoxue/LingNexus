/**
 * Lazy Load Directive
 * Delays loading of images/content until they enter the viewport
 */
import type { Directive } from 'vue'

interface LazyLoadElement extends HTMLElement {
  _lazyLoadObserver?: IntersectionObserver
  _lazyLoadSrc?: string
}

const lazyLoadDirective: Directive<LazyLoadElement, string> = {
  mounted(el, binding) {
    // Store original source
    el._lazyLoadSrc = binding.value

    // Create placeholder or show loading state
    if (el.tagName === 'IMG') {
      el.style.opacity = '0'
      el.style.transition = 'opacity 0.3s ease-in-out'
      // Add loading placeholder
      el.dataset.src = binding.value
    }

    // Create Intersection Observer
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            loadElement(el)
            observer.unobserve(el)
          }
        })
      },
      {
        rootMargin: '50px', // Start loading 50px before element enters viewport
        threshold: 0.01
      }
    )

    el._lazyLoadObserver = observer
    observer.observe(el)
  },

  updated(el, binding) {
    // Update source if changed
    if (binding.value !== binding.oldValue) {
      el._lazyLoadSrc = binding.value

      // If already loaded, update immediately
      if (el._lazyLoadObserver) {
        loadElement(el)
      }
    }
  },

  unmounted(el) {
    // Cleanup observer
    if (el._lazyLoadObserver) {
      el._lazyLoadObserver.disconnect()
      delete el._lazyLoadObserver
    }
  }
}

function loadElement(el: LazyLoadElement) {
  const src = el._lazyLoadSrc
  if (!src) return

  if (el.tagName === 'IMG') {
    // Load image
    const img = new Image()

    img.onload = () => {
      el.setAttribute('src', src)
      el.style.opacity = '1'
    }

    img.onerror = () => {
      // Show error placeholder
      el.setAttribute('alt', 'Failed to load')
      el.style.opacity = '1'
    }

    img.src = src
  } else if (el.tagName === 'IFRAME') {
    // Load iframe
    el.setAttribute('src', src)
  } else {
    // For other elements, set background image
    el.style.backgroundImage = `url(${src})`
    el.style.opacity = '1'
  }
}

/**
 * Lazy load component for more complex scenarios
 */
export function setupLazyLoad(app: any) {
  app.directive('lazy', lazyLoadDirective)
}

export default lazyLoadDirective
