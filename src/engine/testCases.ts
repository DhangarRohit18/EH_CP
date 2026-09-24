import { DemoTestCase } from '../types';

export const DEMO_TEST_CASES: DemoTestCase[] = [
  {
    id: 'test-case-2-official',
    name: 'Suspicious Discount Store (Official Demo)',
    tagline: 'flashdeal-electronics.local - 79% price drop on iPhone 16 Pro',
    expectedRisk: 'CRITICAL',
    expectedScore: 86,
    description: 'Exact scenario from cybersecurity evaluation: Domain age 8 days, reference price ₹1,19,999 listed at ₹24,999, repetitive synthetic reviews, incomplete refund policy, and prepaid-only payment.',
    data: {
      url: 'https://flashdeal-electronics.local/products/iphone-16-pro-256gb',
      domain: 'flashdeal-electronics.local',
      pageTitle: 'iPhone 16 Pro (256GB, Natural Titanium) - Flash Deal 79% Off',
      productName: 'iPhone 16 Pro 256GB (Natural Titanium)',
      price: 24999,
      originalPrice: 119999,
      referenceMarketPrice: 119999,
      currency: '₹',
      domainAgeDays: 8,
      isHttps: true,
      rating: 4.9,
      reviewCount: 142,
      reviews: [
        {
          author: 'Vikram S.',
          text: 'Great product arrived in 2 days. Very happy with purchase! 100% genuine.',
          rating: 5,
          date: 'Yesterday'
        },
        {
          author: 'Ramesh K.',
          text: 'Great product arrived in 2 days. Very happy with purchase! 100% genuine.',
          rating: 5,
          date: 'Yesterday'
        },
        {
          author: 'Sunita P.',
          text: 'Great product arrived in 2 days. Very happy with purchase! Must buy.',
          rating: 5,
          date: '2 days ago'
        },
        {
          author: 'Anil M.',
          text: 'Great product arrived in 2 days. Very happy with purchase! 100% genuine.',
          rating: 5,
          date: '3 days ago'
        }
      ],
      refundPolicyText: 'Returns may be accepted at store sole discretion if contacted within 24 hours. Customer responsible for 35% restocking fee and return transit. Clearance items final.',
      paymentMethods: ['Prepaid Only (UPI / NetBanking)', 'Personal UPI QR (paytm-merchant9812@paytm)', 'No Cash on Delivery'],
      contactEmail: 'flashdealssupport99@gmail.com',
      contactPhone: '+91 98765 00000',
      companyAddress: 'Plot 41, Industrial Zone (Unverified)',
      hasSuspiciousRedirects: true,
      hasHiddenForms: true,
      behaviourSignals: ['Forced 05:00 countdown timer urging immediate checkout', 'External redirection to checkout-pay-gateway.icu'],
      isCheckoutPage: false
    }
  },
  {
    id: 'test-case-1-trusted',
    name: 'Trusted Official Store',
    tagline: 'croma-electronics.com - Established Authorized Retailer',
    expectedRisk: 'LOW',
    expectedScore: 12,
    description: 'Long-standing domain (8+ years), standard authorized retail pricing, organic review sentiment distribution, clear 14-day refund policy, certified Razorpay/Visa/COD gateway.',
    data: {
      url: 'https://croma-electronics.com/apple-iphone-16-pro-128gb',
      domain: 'croma-electronics.com',
      pageTitle: 'Buy Apple iPhone 16 Pro 128GB - Official Croma Store',
      productName: 'Apple iPhone 16 Pro (128GB, Desert Titanium)',
      price: 114999,
      originalPrice: 119999,
      referenceMarketPrice: 119999,
      currency: '₹',
      domainAgeDays: 3100,
      isHttps: true,
      rating: 4.4,
      reviewCount: 842,
      reviews: [
        {
          author: 'Arjun Mehta',
          text: 'Battery life is superb, cameras are noticeable upgrade from iPhone 13. Delivered in standard sealed box.',
          rating: 5,
          date: '1 week ago'
        },
        {
          author: 'Deepika Rao',
          text: 'Good build quality but delivery took 4 days instead of promised 2 days. Packaging was intact.',
          rating: 4,
          date: '2 weeks ago'
        },
        {
          author: 'Kunal Shah',
          text: 'Titanium finish feels lighter in hand. Authorized Apple warranty active on setup.',
          rating: 5,
          date: '3 weeks ago'
        }
      ],
      refundPolicyText: 'We offer an easy 14-day replacement or full refund policy on all eligible electronic purchases. Items must be returned in original packaging with serial number intact. Reverse pickup is free.',
      paymentMethods: ['Credit/Debit Cards (Visa/Mastercard)', 'UPI (Verified Merchant)', 'NetBanking', 'Cash on Delivery (COD)', 'EMI Options'],
      contactEmail: 'support@croma-electronics.com',
      contactPhone: '1800-258-3636',
      companyAddress: 'Infinity Tower, Sector 21, Gurgaon, Haryana, India',
      hasSuspiciousRedirects: false,
      hasHiddenForms: false,
      behaviourSignals: [],
      isCheckoutPage: false
    }
  },
  {
    id: 'test-case-3-fake-reviews',
    name: 'New Domain + Fake Reviews',
    tagline: 'luxurystore-vip-deals.shop - Ultra-luxury goods at 98% discount',
    expectedRisk: 'CRITICAL',
    expectedScore: 94,
    description: 'Domain registered 3 days ago on disposable .shop TLD. Luxury watch valued at ₹8,50,000 offered for ₹12,500. Highly repetitive synthesized bot reviews.',
    data: {
      url: 'https://luxurystore-vip-deals.shop/rolex-submariner-date',
      domain: 'luxurystore-vip-deals.shop',
      pageTitle: 'Rolex Submariner Date Steel - VIP Flash Clearance 98% Off',
      productName: 'Rolex Submariner Date 41mm Oystersteel',
      price: 12500,
      originalPrice: 850000,
      referenceMarketPrice: 850000,
      currency: '₹',
      domainAgeDays: 3,
      isHttps: true,
      rating: 5.0,
      reviewCount: 310,
      reviews: [
        {
          author: 'John D.',
          text: 'Best watch ever received in 2 days. 100% original authentic verified Rolex.',
          rating: 5,
          date: 'Today'
        },
        {
          author: 'Mark T.',
          text: 'Best watch ever received in 2 days. 100% original authentic verified Rolex.',
          rating: 5,
          date: 'Today'
        },
        {
          author: 'David L.',
          text: 'Best watch ever received in 2 days. 100% original authentic verified Rolex.',
          rating: 5,
          date: 'Yesterday'
        }
      ],
      refundPolicyText: 'Due to extreme liquidation discounts, all sales are strictly final and non-refundable. No returns accepted under any circumstances.',
      paymentMethods: ['Crypto (USDT / BTC)', 'Direct Wire Transfer', 'Prepaid Gift Cards'],
      contactEmail: 'luxuryviphelp@yahoo.com',
      contactPhone: '',
      companyAddress: '',
      hasSuspiciousRedirects: true,
      hasHiddenForms: true,
      behaviourSignals: ['Fake recent-purchase notifications popping up every 3 seconds', 'Obfuscated JavaScript obfuscator detected'],
      isCheckoutPage: false
    }
  },
  {
    id: 'test-case-4-prepaid-only',
    name: 'Prepaid-Only Trap Store',
    tagline: 'quickcart-direct-sales.top - Unregulated UPI payment demand',
    expectedRisk: 'HIGH',
    expectedScore: 76,
    description: 'Forces buyers to scan personal QR code or transfer directly via personal UPI VPA without escrow or merchant protections. Refund policy is vague and lacks return window.',
    data: {
      url: 'https://quickcart-direct-sales.top/dyson-airwrap-multistyler',
      domain: 'quickcart-direct-sales.top',
      pageTitle: 'Dyson Airwrap Multi-Styler Complete - Direct Factory Price',
      productName: 'Dyson Airwrap Multi-Styler Complete Long',
      price: 14999,
      originalPrice: 45900,
      referenceMarketPrice: 45900,
      currency: '₹',
      domainAgeDays: 22,
      isHttps: true,
      rating: 3.2,
      reviewCount: 18,
      reviews: [
        {
          author: 'Pooja V.',
          text: 'Item received had damaged box. Took 2 weeks to respond.',
          rating: 3,
          date: '5 days ago'
        },
        {
          author: 'Sneha M.',
          text: 'They demanded UPI payment before dispatch. Product is okay.',
          rating: 3,
          date: '8 days ago'
        }
      ],
      refundPolicyText: 'Refunds processed only if product is damaged on arrival. Customer must provide unboxing video within 2 hours of courier delivery.',
      paymentMethods: ['Personal UPI (direct transfer to upi-merchant92@okhdfcbank)', 'Prepaid Only', 'No Cards Accepted'],
      contactEmail: 'quickcartoperations@gmail.com',
      contactPhone: '+91 88888 12345',
      companyAddress: 'Warehouse 9, Bypass Road, Surat',
      hasSuspiciousRedirects: false,
      hasHiddenForms: false,
      behaviourSignals: ['Pre-payment demand prior to order receipt generation'],
      isCheckoutPage: false
    }
  },
  {
    id: 'test-case-5-brand-impersonation',
    name: 'Brand Impersonation & Typosquatting',
    tagline: 'amaz0n-prime-security-checkout.co - Mimics Amazon Prime',
    expectedRisk: 'HIGH',
    expectedScore: 84,
    description: 'Typosquatting domain using numeral "0" instead of "o", mimicking Amazon brand logo and styles, generic contact email, and cross-site redirection on checkout.',
    data: {
      url: 'https://amaz0n-prime-security-checkout.co/deal/sony-wh1000xm5',
      domain: 'amaz0n-prime-security-checkout.co',
      pageTitle: 'Amazon Prime Exclusive: Sony WH-1000XM5 Wireless Headphones',
      productName: 'Sony WH-1000XM5 Noise Cancelling Headphones',
      price: 9999,
      originalPrice: 34990,
      referenceMarketPrice: 34990,
      currency: '₹',
      domainAgeDays: 11,
      isHttps: true,
      rating: 4.8,
      reviewCount: 520,
      reviews: [
        {
          author: 'Customer',
          text: 'Fast prime delivery, authentic Sony headphones.',
          rating: 5,
          date: 'Yesterday'
        }
      ],
      refundPolicyText: 'Amazon 30 days return guarantee (Copied generic text without valid fulfillment contract).',
      paymentMethods: ['Prepaid Credit/Debit', 'UPI Instant Pay'],
      contactEmail: 'prime-support-desk@hotmail.com',
      contactPhone: '',
      companyAddress: 'Amazon Fulfillment Center (Unverified imitation)',
      hasSuspiciousRedirects: true,
      hasHiddenForms: true,
      behaviourSignals: ['Domain typosquatting (amaz0n vs amazon)', 'Cross-domain iframe injection in DOM'],
      isCheckoutPage: true
    }
  }
];
