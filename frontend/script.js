/* ============================================
   PropPredict AI — Frontend Logic
   Vanilla JS · No Frameworks
   ============================================ */

(function () {
  'use strict';

  // ─── State ─────────────────────────────────────
  const state = {
    selectedCity: '',
    propertyType: 'Flat',
    bedrooms: 2,
    bathrooms: 1,
    furnishing: 'Semi-Furnished',
    parking: true,
    chatHistory: [],
  };

  // ─── DOM References ────────────────────────────
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  const navbar = $('#navbar');
  const navLinks = $('#navLinks');
  const navHamburger = $('#navHamburger');

  const cityCards = $$('.city-card');
  const citySelect = $('#citySelect');
  const localitySelect = $('#localitySelect');

  const propertyTypeGroup = $('#propertyTypeGroup');
  const bedroomsGroup = $('#bedroomsGroup');
  const bathroomsGroup = $('#bathroomsGroup');
  const floorGroup = $('#floorGroup');
  const furnishingGroup = $('#furnishingGroup');

  const sizeSlider = $('#sizeSlider');
  const sizeValue = $('#sizeValue');
  const ageSlider = $('#ageSlider');
  const ageValue = $('#ageValue');
  const floorInput = $('#floorInput');

  const parkingToggle = $('#parkingToggle');
  const parkingLabel = $('#parkingLabel');

  const predictForm = $('#predictForm');
  const predictBtn = $('#predictBtn');
  const resultsContainer = $('#resultsContainer');
  const priceResult = $('#priceResult');
  const rentResult = $('#rentResult');
  const resultMeta = $('#resultMeta');

  const chatMessages = $('#chatMessages');
  const chatInput = $('#chatInput');
  const chatSend = $('#chatSend');
  const typingIndicator = $('#typingIndicator');
  const suggestionChips = $('#suggestionChips');
  const toastContainer = $('#toastContainer');

  // ─── Toast Notifications ──────────────────────
  function showToast(message, type = 'info') {
    const icons = { error: '✕', success: '✓', warning: '⚠', info: 'ℹ' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${icons[type] || 'ℹ'}</span> ${message}`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('fade-out');
      toast.addEventListener('animationend', () => toast.remove());
    }, 4000);
  }

  // ─── API Helper ───────────────────────────────
  async function apiFetch(url, options = {}) {
    try {
      const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
      });
      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        throw new Error(errBody.error || `Request failed (${res.status})`);
      }
      return await res.json();
    } catch (err) {
      if (err.name === 'TypeError') {
        throw new Error('Cannot reach the server. Is the backend running?');
      }
      throw err;
    }
  }

  // ─── Navigation ───────────────────────────────
  // Scroll shadow
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 20);
  });

  // Active link tracking
  const sections = $$('section[id], .hero[id]');
  const navAnchors = $$('.nav-links a');

  function updateActiveLink() {
    let current = '';
    sections.forEach((sec) => {
      const top = sec.offsetTop - 100;
      if (window.scrollY >= top) current = sec.id;
    });
    navAnchors.forEach((a) => {
      a.classList.toggle('active', a.getAttribute('href') === `#${current}`);
    });
  }
  window.addEventListener('scroll', updateActiveLink);

  // Hamburger
  navHamburger.addEventListener('click', () => {
    navLinks.classList.toggle('open');
  });
  navAnchors.forEach((a) => {
    a.addEventListener('click', () => navLinks.classList.remove('open'));
  });

  // ─── Scroll Reveal (Intersection Observer) ────
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    },
    { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
  );
  $$('.reveal').forEach((el) => revealObserver.observe(el));

  // ─── Feature Bars Animation ───────────────────
  const barObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const fills = entry.target.querySelectorAll('.feature-bar-fill');
          fills.forEach((fill) => {
            fill.style.width = fill.dataset.width + '%';
          });
        }
      });
    },
    { threshold: 0.3 }
  );
  const featureBarList = $('#featureBarList');
  if (featureBarList) barObserver.observe(featureBarList);

  // ─── City Card Selection ──────────────────────
  cityCards.forEach((card) => {
    card.addEventListener('click', () => {
      cityCards.forEach((c) => c.classList.remove('selected'));
      card.classList.add('selected');
      const city = card.dataset.city;
      state.selectedCity = city;
      citySelect.value = city;
      loadLocalities(city);

      // Smooth scroll to predictor
      document.getElementById('predict').scrollIntoView({ behavior: 'smooth' });
    });
  });

  // ─── City Dropdown Change ─────────────────────
  citySelect.addEventListener('change', () => {
    const city = citySelect.value;
    state.selectedCity = city;
    // Sync card selection
    cityCards.forEach((c) =>
      c.classList.toggle('selected', c.dataset.city === city)
    );
    loadLocalities(city);
  });

  // ─── Load Localities ──────────────────────────
  async function loadLocalities(city) {
    localitySelect.disabled = true;
    localitySelect.innerHTML = '<option value="" disabled selected>Loading…</option>';

    try {
      const data = await apiFetch(`/api/localities/${encodeURIComponent(city)}`);
      const localities = data.localities || [];

      localitySelect.innerHTML = '<option value="" disabled selected>Select locality</option>';
      localities.forEach((loc) => {
        const opt = document.createElement('option');
        opt.value = loc;
        opt.textContent = loc;
        localitySelect.appendChild(opt);
      });
      localitySelect.disabled = false;
    } catch (err) {
      showToast(err.message, 'error');
      localitySelect.innerHTML = '<option value="" disabled selected>Failed to load</option>';
    }
  }

  // ─── Property Type Toggle ─────────────────────
  propertyTypeGroup.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn-option');
    if (!btn) return;
    propertyTypeGroup.querySelectorAll('.btn-option').forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    state.propertyType = btn.dataset.value;
    toggleLandFields();
  });

  function toggleLandFields() {
    const isLand = state.propertyType === 'Land';
    [bedroomsGroup, bathroomsGroup, floorGroup, furnishingGroup].forEach((g) => {
      if (g) {
        g.style.display = isLand ? 'none' : '';
        g.style.opacity = isLand ? '0' : '1';
      }
    });
  }

  // ─── Number Button Groups ────────────────────
  function setupNumButtons(containerId, stateKey) {
    const container = $(`#${containerId}`);
    if (!container) return;
    container.addEventListener('click', (e) => {
      const btn = e.target.closest('.num-btn');
      if (!btn) return;
      container.querySelectorAll('.num-btn').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      state[stateKey] = parseInt(btn.dataset.value, 10);
    });
  }
  setupNumButtons('bedroomsButtons', 'bedrooms');
  setupNumButtons('bathroomsButtons', 'bathrooms');

  // ─── Furnishing Toggle ────────────────────────
  const furnishingButtons = $('#furnishingButtons');
  if (furnishingButtons) {
    furnishingButtons.addEventListener('click', (e) => {
      const btn = e.target.closest('.btn-option');
      if (!btn) return;
      furnishingButtons.querySelectorAll('.btn-option').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      state.furnishing = btn.dataset.value;
    });
  }

  // ─── Range Sliders ────────────────────────────
  sizeSlider.addEventListener('input', () => {
    sizeValue.textContent = parseInt(sizeSlider.value, 10).toLocaleString();
  });
  ageSlider.addEventListener('input', () => {
    ageValue.textContent = ageSlider.value;
  });

  // ─── Parking Toggle ───────────────────────────
  parkingToggle.addEventListener('click', () => {
    state.parking = !state.parking;
    parkingToggle.classList.toggle('active', state.parking);
    parkingLabel.textContent = state.parking ? 'Yes' : 'No';
  });

  // ─── Animated Counter ─────────────────────────
  function animateCounter(element, target, duration = 1200, prefix = '', suffix = '') {
    const startTime = performance.now();
    const startVal = 0;

    // Determine decimal places from target
    const decimals = (target.toString().split('.')[1] || '').length;

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const currentVal = startVal + (target - startVal) * eased;

      if (decimals > 0) {
        element.textContent = prefix + currentVal.toFixed(decimals) + suffix;
      } else {
        element.textContent = prefix + Math.round(currentVal).toLocaleString('en-IN') + suffix;
      }

      if (progress < 1) {
        requestAnimationFrame(update);
      }
    }
    requestAnimationFrame(update);
  }

  // ─── Form Submit → Predict ────────────────────
  predictForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Validation
    if (!citySelect.value) {
      showToast('Please select a city', 'warning');
      citySelect.focus();
      return;
    }
    if (!localitySelect.value) {
      showToast('Please select a locality', 'warning');
      localitySelect.focus();
      return;
    }

    const body = {
      city: citySelect.value,
      locality: localitySelect.value,
      property_type: state.propertyType,
      size_sqft: parseInt(sizeSlider.value, 10),
      bedrooms: state.propertyType === 'Land' ? 0 : state.bedrooms,
      bathrooms: state.propertyType === 'Land' ? 0 : state.bathrooms,
      floor: state.propertyType === 'Land' ? 0 : parseInt(floorInput.value, 10) || 0,
      age_years: parseInt(ageSlider.value, 10),
      furnishing: state.propertyType === 'Land' ? 'Unfurnished' : state.furnishing,
      parking: state.parking,
    };

    // Loading state
    predictBtn.classList.add('loading');
    predictBtn.disabled = true;
    resultsContainer.classList.remove('show');

    try {
      const data = await apiFetch('/api/predict', {
        method: 'POST',
        body: JSON.stringify(body),
      });

      // Show results
      resultsContainer.classList.add('show');
      animateCounter(priceResult, data.price_lakhs, 1400);
      animateCounter(rentResult, Math.round(data.rent_monthly), 1400);

      const modelInfo = data.model_info || {};
      resultMeta.textContent = `Model: ${modelInfo.name || 'Ridge Regression'} | R² Score: ${(modelInfo.r2_score || 0).toFixed(3)}`;

      showToast('Prediction generated successfully!', 'success');

      // Scroll to results
      setTimeout(() => {
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }, 200);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      predictBtn.classList.remove('loading');
      predictBtn.disabled = false;
    }
  });

  // ─── RAG Chat ─────────────────────────────────

  function formatTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function addChatMessage(content, sender, sources = []) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${sender}`;

    let sourcesHTML = '';
    if (sources && sources.length > 0) {
      const sourceItems = sources
        .map(
          (s) =>
            `<div class="source-item">
              <span class="source-file">📄 ${s.file || 'source'}</span>
              <span class="source-score">${s.score ? (s.score * 100).toFixed(0) + '% match' : ''}</span>
              <div style="margin-top:4px; font-size:0.76rem; color:var(--text-muted);">${truncate(s.text || '', 120)}</div>
            </div>`
        )
        .join('');

      sourcesHTML = `
        <div class="message-sources">
          <button class="sources-toggle" onclick="this.classList.toggle('open'); this.nextElementSibling.classList.toggle('show');">
            📎 ${sources.length} source${sources.length > 1 ? 's' : ''} <span class="chevron">▼</span>
          </button>
          <div class="sources-list">${sourceItems}</div>
        </div>`;
    }

    msgDiv.innerHTML = `
      <div class="message-bubble">${escapeHTML(content)}</div>
      ${sourcesHTML}
      <div class="message-time">${formatTime()}</div>
    `;

    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function truncate(str, len) {
    return str.length > len ? str.substring(0, len) + '…' : str;
  }

  async function sendChatMessage(question) {
    if (!question.trim()) return;

    addChatMessage(question, 'user');
    chatInput.value = '';
    chatSend.disabled = true;

    // Hide suggestion chips after first message
    if (suggestionChips) suggestionChips.style.display = 'none';

    // Show typing indicator
    typingIndicator.classList.add('show');
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
      const data = await apiFetch('/api/ask', {
        method: 'POST',
        body: JSON.stringify({ question }),
      });

      typingIndicator.classList.remove('show');
      addChatMessage(data.answer || 'No response received.', 'ai', data.sources || []);
    } catch (err) {
      typingIndicator.classList.remove('show');
      addChatMessage(`Sorry, I encountered an error: ${err.message}`, 'ai');
      showToast(err.message, 'error');
    } finally {
      chatSend.disabled = false;
      chatInput.focus();
    }
  }

  chatSend.addEventListener('click', () => sendChatMessage(chatInput.value));
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage(chatInput.value);
    }
  });

  // Suggestion chips
  if (suggestionChips) {
    suggestionChips.addEventListener('click', (e) => {
      const chip = e.target.closest('.suggestion-chip');
      if (chip) sendChatMessage(chip.dataset.question);
    });
  }

  // ─── Load Model Info from API ─────────────────
  async function loadModelInfo() {
    try {
      const data = await apiFetch('/api/model-info');

      // Update feature importance bars
      if (data.feature_importance) {
        const list = $('#featureBarList');
        if (list) {
          const entries = Object.entries(data.feature_importance)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 6);

          const maxVal = entries[0]?.[1] || 1;

          list.innerHTML = entries
            .map(
              ([name, value]) => `
              <div class="feature-bar-item">
                <div class="feature-bar-label">
                  <span class="feature-bar-name">${escapeHTML(name)}</span>
                  <span class="feature-bar-value">${(value * 100 / maxVal).toFixed(0)}%</span>
                </div>
                <div class="feature-bar-track">
                  <div class="feature-bar-fill" data-width="${(value * 100 / maxVal).toFixed(0)}"></div>
                </div>
              </div>`
            )
            .join('');

          // Re-observe for animation
          barObserver.observe(list);
        }
      }

      // Update model comparison table
      if (data.price_model || data.rent_model) {
        const tbody = document.querySelector('#modelTable tbody');
        if (tbody) {
          tbody.innerHTML = '';

          const models = [];
          if (data.price_model) {
            models.push({ ...data.price_model, label: `${data.price_model.name || 'Model'} (Price)` });
          }
          if (data.rent_model) {
            models.push({ ...data.rent_model, label: `${data.rent_model.name || 'Model'} (Rent)` });
          }

          models.forEach((m) => {
            const r2Class = m.r2 >= 0.85 ? 'metric-good' : 'metric-ok';
            const row = document.createElement('tr');
            row.innerHTML = `
              <td class="model-name">${escapeHTML(m.label)}</td>
              <td class="${r2Class}">${m.r2 != null ? m.r2.toFixed(3) : '—'}</td>
              <td>${m.mae != null ? m.mae.toFixed(2) : '—'}</td>
              <td>${m.rmse != null ? m.rmse.toFixed(2) : '—'}</td>
            `;
            tbody.appendChild(row);
          });
        }
      }
    } catch (err) {
      // Silently fail — use default placeholder data
      console.log('Model info not available, using defaults.');
    }
  }

  // ─── Initialize ───────────────────────────────
  function init() {
    toggleLandFields();
    sizeValue.textContent = parseInt(sizeSlider.value, 10).toLocaleString();
    ageValue.textContent = ageSlider.value;
    loadModelInfo();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
