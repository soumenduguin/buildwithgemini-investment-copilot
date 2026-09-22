/* Investment Copilot — AI Portfolio Simulator
 * Dynamic Header, Dialogue Layout & Indicator Badges Engine
 */

(function () {
  'use strict';

  const APP_TITLE = 'Investment Copilot';
  const APP_SUBTITLE = 'AI Portfolio Simulator';
  const APP_DESCRIPTION = 'Explore fictional investment scenarios using synthetic data and AI-powered analysis.';
  const DISCLAIMER_TEXT = 'Educational simulation using synthetic data. Not financial advice and not a prediction of future returns.';
  const PAGE_TITLE = 'Investment Copilot — AI Portfolio Simulator';

  function applyTitle() {
    if (document.title !== PAGE_TITLE) {
      document.title = PAGE_TITLE;
    }
  }

  function injectHeader() {
    if (document.getElementById('copilot-header-bar')) return;

    const header = document.createElement('div');
    header.id = 'copilot-header-bar';
    header.innerHTML = `
      <div class="copilot-header-top">
        <div class="copilot-brand-container">
          <span class="copilot-logo-badge">IC</span>
          <h1 class="copilot-app-title">${APP_TITLE}</h1>
          <span class="copilot-app-subtitle">${APP_SUBTITLE}</span>
        </div>
      </div>
      <p class="copilot-app-description">${APP_DESCRIPTION}</p>
    `;

    document.body.insertBefore(header, document.body.firstChild);
  }

  function injectDisclaimer() {
    if (document.getElementById('copilot-disclaimer-banner')) return;

    const banner = document.createElement('div');
    banner.id = 'copilot-disclaimer-banner';
    banner.innerHTML = `⚠️ <span>${DISCLAIMER_TEXT}</span>`;

    document.body.appendChild(banner);
  }

  // Requirement 8: Attach visual indicators to assistant bubbles
  function attachAnalysisBadges() {
    const bubbles = document.querySelectorAll('.content-bubble, app-agent-message, .agent-message');
    bubbles.forEach(bubble => {
      if (bubble.querySelector('.copilot-indicator-badge')) return;

      const text = bubble.textContent.toLowerCase();
      let badgeHTML = '';

      if (text.includes('what-if') || text.includes('scenario') || text.includes('baseline vs') || text.includes('comparison')) {
        badgeHTML = `<div class="copilot-indicator-badge badge-scenario">🔄 Scenario Analysis</div>`;
      } else if (text.includes('portfolio') || text.includes('allocation') || text.includes('equities') || text.includes('asset class')) {
        badgeHTML = `<div class="copilot-indicator-badge badge-portfolio">🎯 Portfolio Analysis</div>`;
      } else if (text.includes('profile') || text.includes('monthly income') || text.includes('expenses') || text.includes('savings')) {
        badgeHTML = `<div class="copilot-indicator-badge badge-financial">📊 Financial Analysis</div>`;
      } else if (text.includes('market') || text.includes('simulation') || text.includes('returns') || text.includes('historical')) {
        badgeHTML = `<div class="copilot-indicator-badge badge-market">📈 Market Simulation</div>`;
      } else if (text.includes('compound') || text.includes('cagr') || text.includes('growth') || text.includes('projection')) {
        badgeHTML = `<div class="copilot-indicator-badge badge-quant">🔢 Quantitative Analysis</div>`;
      }

      if (badgeHTML) {
        const badgeContainer = document.createElement('div');
        badgeContainer.innerHTML = badgeHTML;
        bubble.insertBefore(badgeContainer.firstChild, bubble.firstChild);
      }
    });
  }

  function initRebrand() {
    applyTitle();
    injectHeader();
    injectDisclaimer();
    attachAnalysisBadges();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initRebrand);
  } else {
    initRebrand();
  }

  setInterval(initRebrand, 1000);
})();
