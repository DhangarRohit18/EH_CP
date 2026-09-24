/**
 * WebGuard Safe Content Extractor
 * 
 * STRICT CYBERSECURITY PRIVACY COMPLIANCE:
 * This script extracts ONLY publicly visible storefront catalog metadata.
 * It NEVER reads, accesses, or transmits:
 * - Passwords or password input fields
 * - Credit/debit card numbers or PANs
 * - CVV/CVC codes
 * - One-time passwords (OTP)
 * - User cookies or session authentication tokens
 * - Private user messages or profile credentials
 */

import { AnalysisPayload } from '../types';

export class WebGuardExtractor {
  public static extractPageData(): AnalysisPayload {
    const url = window.location.href;
    const domain = window.location.hostname;
    const pageTitle = document.title || '';
    const isHttps = window.location.protocol === 'https:';

    // 1. Safe Product Title Extraction
    const productName = this.extractProductName(pageTitle);

    // 2. Safe Price Extraction
    const { price, originalPrice, currency } = this.extractPricing();

    // 3. Safe Public Reviews Extraction
    const { reviews, rating, reviewCount } = this.extractReviews();

    // 4. Safe Return/Refund Policy Extraction
    const refundPolicyText = this.extractPolicyText();

    // 5. Payment Methods Indicators (Badges & text, NOT form values!)
    const paymentMethods = this.extractPaymentIndicators();

    // 6. Public Merchant Contact Info
    const { contactEmail, contactPhone, companyAddress } = this.extractMerchantContact();

    // 7. Structural Indicators (Hidden forms, off-screen redirects)
    const { hasHiddenForms, hasSuspiciousRedirects, behaviourSignals } = this.detectStructuralSignals();

    // 8. Checkout page determination
    const isCheckoutPage = this.isCheckoutOrPaymentUrl();

    return {
      url,
      domain,
      pageTitle,
      productName,
      price,
      originalPrice,
      currency,
      reviews,
      rating,
      reviewCount,
      refundPolicyText,
      paymentMethods,
      contactEmail,
      contactPhone,
      companyAddress,
      isHttps,
      hasHiddenForms,
      hasSuspiciousRedirects,
      behaviourSignals,
      isCheckoutPage
    };
  }

  private static extractProductName(pageTitle: string): string {
    // Check schema.org JSON-LD or meta tags
    const ogTitle = document.querySelector('meta[property="og:title"]')?.getAttribute('content');
    if (ogTitle) return ogTitle.trim();

    // Check h1 product title elements
    const h1Candidates = [
      document.querySelector('h1.product-title'),
      document.querySelector('h1[itemprop="name"]'),
      document.querySelector('.product-name h1'),
      document.querySelector('h1')
    ];

    for (const el of h1Candidates) {
      if (el && el.textContent) {
        const text = el.textContent.trim();
        if (text.length > 2 && text.length < 150) return text;
      }
    }

    return pageTitle.split(/[-|–]/)[0]?.trim() || 'Online Store Product';
  }

  private static extractPricing(): { price: number; originalPrice?: number; currency: string } {
    let price = 0;
    let originalPrice: number | undefined;
    let currency = '₹';

    // Check Schema.org metadata
    const schemaPriceEl = document.querySelector('[itemprop="price"]');
    if (schemaPriceEl) {
      const val = parseFloat(schemaPriceEl.getAttribute('content') || schemaPriceEl.textContent || '0');
      if (val > 0) price = val;
    }

    const schemaCurrEl = document.querySelector('[itemprop="priceCurrency"]');
    if (schemaCurrEl) {
      const c = schemaCurrEl.getAttribute('content');
      if (c) currency = c === 'INR' ? '₹' : c;
    }

    // Inspect visible price selectors
    const priceSelectors = [
      '.price', '.product-price', '.sale-price', '.current-price',
      '[data-price]', '#priceblock_ourprice', '.a-price-whole'
    ];

    for (const sel of priceSelectors) {
      const el = document.querySelector(sel);
      if (el && el.textContent) {
        const parsed = this.parsePriceText(el.textContent);
        if (parsed.price > 0 && price === 0) {
          price = parsed.price;
          if (parsed.currency) currency = parsed.currency;
        }
      }
    }

    // Look for strikethrough / original MRP
    const originalSelectors = [
      '.original-price', '.regular-price', '.was-price', '.mrp', 'del', 's'
    ];

    for (const sel of originalSelectors) {
      const el = document.querySelector(sel);
      if (el && el.textContent) {
        const parsed = this.parsePriceText(el.textContent);
        if (parsed.price > price) {
          originalPrice = parsed.price;
          break;
        }
      }
    }

    return { price, originalPrice, currency };
  }

  private static parsePriceText(text: string): { price: number; currency: string } {
    let clean = text.replace(/,/g, '');
    let currency = '₹';
    if (clean.includes('$')) currency = '$';
    else if (clean.includes('€')) currency = '€';
    else if (clean.includes('£')) currency = '£';
    else if (clean.includes('₹') || clean.includes('Rs') || clean.includes('INR')) currency = '₹';

    const match = clean.match(/[\d,]+(\.\d{1,2})?/);
    const price = match ? parseFloat(match[0]) : 0;
    return { price, currency };
  }

  private static extractReviews(): { reviews: Array<{ text: string; rating?: number; author?: string }>; rating: number; reviewCount: number } {
    const reviews: Array<{ text: string; rating?: number; author?: string }> = [];
    let rating = 4.5;
    let reviewCount = 0;

    // Review elements
    const reviewElements = document.querySelectorAll('.review, .review-item, [itemprop="review"], .customer-review');
    reviewElements.forEach((el, index) => {
      if (index < 10) {
        const bodyEl = el.querySelector('.review-text, [itemprop="reviewBody"], .comment, p');
        const text = (bodyEl || el).textContent?.trim() || '';
        if (text.length > 10) {
          reviews.push({ text: text.substring(0, 300) });
        }
      }
    });

    // Rating aggregate
    const aggRatingEl = document.querySelector('[itemprop="ratingValue"], .average-rating, .rating-score');
    if (aggRatingEl) {
      const val = parseFloat(aggRatingEl.getAttribute('content') || aggRatingEl.textContent || '0');
      if (val > 0) rating = val;
    }

    const reviewCountEl = document.querySelector('[itemprop="reviewCount"], .total-reviews, .review-count');
    if (reviewCountEl) {
      const val = parseInt((reviewCountEl.textContent || '').replace(/[^\d]/g, ''), 10);
      if (val > 0) reviewCount = val;
    }

    return { reviews, rating, reviewCount };
  }

  private static extractPolicyText(): string {
    const policyKeywords = ['refund', 'return', 'cancellation', 'exchange', 'warranty'];
    const candidates = Array.from(document.querySelectorAll('a, p, div, span, footer'));

    for (const el of candidates) {
      const text = el.textContent || '';
      for (const kw of policyKeywords) {
        if (text.toLowerCase().includes(kw) && text.length > 40 && text.length < 800) {
          return text.trim();
        }
      }
    }
    return '';
  }

  private static extractPaymentIndicators(): string[] {
    const methods: string[] = [];
    const pageText = document.body.innerText.toLowerCase();

    if (pageText.includes('cash on delivery') || pageText.includes('cod available')) {
      methods.push('Cash on Delivery');
    }
    if (pageText.includes('prepaid only') || pageText.includes('no cod') || pageText.includes('advance payment only')) {
      methods.push('Prepaid Only');
    }
    if (pageText.includes('upi') || pageText.includes('gpay') || pageText.includes('phonepe') || pageText.includes('paytm')) {
      methods.push('UPI Payment');
    }
    if (pageText.includes('razorpay') || pageText.includes('stripe') || pageText.includes('paypal')) {
      methods.push('Secure Gateway Verified');
    }
    if (pageText.includes('direct bank transfer') || pageText.includes('neft') || pageText.includes('western union')) {
      methods.push('Direct Bank Transfer');
    }

    return methods;
  }

  private static extractMerchantContact(): { contactEmail?: string; contactPhone?: string; companyAddress?: string } {
    const pageText = document.body.innerText;
    
    // Email regex
    const emailMatch = pageText.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/);
    const contactEmail = emailMatch ? emailMatch[0] : undefined;

    // Phone regex
    const phoneMatch = pageText.match(/(\+91[\s-]?)?[6789]\d{9}|1800[-\s]?\d{3}[-\s]?\d{4}/);
    const contactPhone = phoneMatch ? phoneMatch[0] : undefined;

    return { contactEmail, contactPhone };
  }

  private static detectStructuralSignals(): { hasHiddenForms: boolean; hasSuspiciousRedirects: boolean; behaviourSignals: string[] } {
    const behaviourSignals: string[] = [];
    let hasHiddenForms = false;
    let hasSuspiciousRedirects = false;

    // Detect hidden off-screen forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
      const style = window.getComputedStyle(form);
      if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
        hasHiddenForms = true;
      }
    });

    // Detect fake urgency countdown timer elements
    const timers = document.querySelectorAll('[class*="countdown"], [id*="timer"], [class*="urgency"]');
    if (timers.length > 0) {
      behaviourSignals.push('Aggressive countdown urgency trigger detected in DOM');
    }

    return { hasHiddenForms, hasSuspiciousRedirects, behaviourSignals };
  }

  public static isCheckoutOrPaymentUrl(): boolean {
    const path = window.location.pathname.toLowerCase();
    const hash = window.location.hash.toLowerCase();
    const query = window.location.search.toLowerCase();
    const full = path + hash + query;

    return (
      full.includes('checkout') ||
      full.includes('payment') ||
      full.includes('billing') ||
      full.includes('order-pay') ||
      full.includes('/cart/pay')
    );
  }
}
