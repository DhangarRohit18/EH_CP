/**
 * WebGuard Real-Time Behaviour Monitor
 * Monitors SPA navigation, DOM mutations, and checkout transitions.
 */

export type NavigationCallback = (isCheckout: boolean, url: string) => void;

export class BehaviourMonitor {
  private lastUrl: string = window.location.href;
  private observer: MutationObserver | null = null;
  private debounceTimer: number | null = null;
  private onNavigate: NavigationCallback;

  constructor(onNavigate: NavigationCallback) {
    this.onNavigate = onNavigate;
    this.initUrlListener();
    this.initDomObserver();
  }

  private initUrlListener(): void {
    // Intercept History API pushes for SPAs (React, Next.js, Vue)
    const originalPushState = window.history.pushState;
    const originalReplaceState = window.history.replaceState;

    window.history.pushState = (...args) => {
      originalPushState.apply(window.history, args);
      this.checkUrlChange();
    };

    window.history.replaceState = (...args) => {
      originalReplaceState.apply(window.history, args);
      this.checkUrlChange();
    };

    window.addEventListener('popstate', () => this.checkUrlChange());
    window.addEventListener('hashchange', () => this.checkUrlChange());
  }

  private checkUrlChange(): void {
    const currentUrl = window.location.href;
    if (currentUrl !== this.lastUrl) {
      this.lastUrl = currentUrl;
      const isCheckout = this.isCheckoutUrl(currentUrl);
      this.onNavigate(isCheckout, currentUrl);
    }
  }

  private initDomObserver(): void {
    // Debounced observer to detect dynamically mounted checkout buttons or payment iframes
    this.observer = new MutationObserver(() => {
      if (this.debounceTimer) window.clearTimeout(this.debounceTimer);
      this.debounceTimer = window.setTimeout(() => {
        const isCheckout = this.isCheckoutUrl(window.location.href);
        const hasPaymentInputs = document.querySelector('button[id*="checkout"], button[class*="pay"], .payment-section') !== null;
        if (isCheckout || hasPaymentInputs) {
          this.onNavigate(true, window.location.href);
        }
      }, 800);
    });

    this.observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  public isCheckoutUrl(url: string): boolean {
    const lower = url.toLowerCase();
    return (
      lower.includes('checkout') ||
      lower.includes('payment') ||
      lower.includes('billing') ||
      lower.includes('order-pay')
    );
  }

  public destroy(): void {
    if (this.observer) this.observer.disconnect();
    if (this.debounceTimer) window.clearTimeout(this.debounceTimer);
  }
}
