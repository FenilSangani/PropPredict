/* ============================================
   PropPredict AI — Frontend Logic
   Vanilla JS · No Frameworks
   ============================================ */

(function () {
  'use strict';

  // --- State ---
  const state = {
    selectedCity: '',
    propertyType: 'Flat',
    bedrooms: 2,
    totalFloors: 2,
    furnishing: 'Semi-Furnished',
    parking: true,
    chatHistory: [],
  };

  // --- DOM References ---
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
  const floorGroup = $('#floorGroup');
  const totalFloorsGroup = $('#totalFloorsGroup');
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

  // Age and Parking group wrappers (for hiding in Land mode)
  const ageGroup = $('#ageGroup') || (ageSlider ? ageSlider.closest('.form-group') : null);
  const parkingGroup = $('#parkingGroup') || (parkingToggle ? parkingToggle.closest('.form-group') : null);

  // --- Toast Notifications ---
  function showToast(message, type) {
    type = type || 'info';
    var icons = { error: 'X', success: 'OK', warning: '!', info: 'i' };
    var toast = document.createElement('div');
    toast.className = 'toast ' + type;
    toast.innerHTML = '<span>' + (icons[type] || 'i') + '</span> ' + message;
    toastContainer.appendChild(toast);

    setTimeout(function () {
      toast.classList.add('fade-out');
      toast.addEventListener('animationend', function () { toast.remove(); });
    }, 4000);
  }

  // --- API Helper ---
  async function apiFetch(url, options) {
    options = options || {};
    try {
      var res = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
      });
      if (!res.ok) {
        var errBody = await res.json().catch(function () { return {}; });
        throw new Error(errBody.error || 'Request failed (' + res.status + ')');
      }
      return await res.json();
    } catch (err) {
      if (err.name === 'TypeError') {
        throw new Error('Cannot reach the server. Is the backend running?');
      }
      throw err;
    }
  }

  // --- Navigation ---
  // Scroll shadow
  window.addEventListener('scroll', function () {
    navbar.classList.toggle('scrolled', window.scrollY > 20);
  });

  // Active link tracking
  var sections = $$('section[id], .hero[id]');
  var navAnchors = $$('.nav-links a');

  function updateActiveLink() {
    var current = '';
    sections.forEach(function (sec) {
      var top = sec.offsetTop - 100;
      if (window.scrollY >= top) current = sec.id;
    });
    navAnchors.forEach(function (a) {
      a.classList.toggle('active', a.getAttribute('href') === '#' + current);
    });
  }
  window.addEventListener('scroll', updateActiveLink);

  // Hamburger
  navHamburger.addEventListener('click', function () {
    navLinks.classList.toggle('open');
  });
  navAnchors.forEach(function (a) {
    a.addEventListener('click', function () { navLinks.classList.remove('open'); });
  });

  // --- Scroll Reveal (Intersection Observer) ---
  var revealObserver = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    },
    { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
  );
  $$('.reveal').forEach(function (el) { revealObserver.observe(el); });

  // --- Feature Bars Animation ---
  var barObserver = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var fills = entry.target.querySelectorAll('.feature-bar-fill');
          fills.forEach(function (fill) {
            fill.style.width = fill.dataset.width + '%';
          });
        }
      });
    },
    { threshold: 0.3 }
  );
  var featureBarList = $('#featureBarList');
  if (featureBarList) barObserver.observe(featureBarList);

  // --- City Card Selection ---
  cityCards.forEach(function (card) {
    card.addEventListener('click', function () {
      cityCards.forEach(function (c) { c.classList.remove('selected'); });
      card.classList.add('selected');
      var city = card.dataset.city;
      state.selectedCity = city;
      citySelect.value = city;
      loadLocalities(city);

      // Smooth scroll to predictor
      document.getElementById('predict').scrollIntoView({ behavior: 'smooth' });
    });
  });

  // --- City Dropdown Change ---
  citySelect.addEventListener('change', function () {
    var city = citySelect.value;
    state.selectedCity = city;
    // Sync card selection
    cityCards.forEach(function (c) {
      c.classList.toggle('selected', c.dataset.city === city);
    });
    loadLocalities(city);
  });

  // --- Load Localities ---
  async function loadLocalities(city) {
    localitySelect.disabled = true;
    localitySelect.innerHTML = '<option value="" disabled selected>Loading...</option>';

    try {
      var data = await apiFetch('/api/localities/' + encodeURIComponent(city));
      var localities = data.localities || [];

      localitySelect.innerHTML = '<option value="" disabled selected>Select locality</option>';
      localities.forEach(function (loc) {
        var opt = document.createElement('option');
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

  // --- Property Type Toggle ---
  propertyTypeGroup.addEventListener('click', function (e) {
    var btn = e.target.closest('.btn-option');
    if (!btn) return;
    propertyTypeGroup.querySelectorAll('.btn-option').forEach(function (b) { b.classList.remove('active'); });
    btn.classList.add('active');
    state.propertyType = btn.dataset.value;
    togglePropertyFields();
  });

  function togglePropertyFields() {
    var type = state.propertyType;

    if (type === 'Flat') {
      // Flat: show bedrooms, floor number, furnishing, age, parking. Hide totalFloors.
      if (bedroomsGroup) bedroomsGroup.style.display = '';
      if (floorGroup) floorGroup.style.display = '';
      if (totalFloorsGroup) totalFloorsGroup.style.display = 'none';
      if (furnishingGroup) furnishingGroup.style.display = '';
      if (ageGroup) ageGroup.style.display = '';
      if (parkingGroup) parkingGroup.style.display = '';
    } else if (type === 'House') {
      // House: hide bedrooms, floor number. Show totalFloors, furnishing, age, parking.
      if (bedroomsGroup) bedroomsGroup.style.display = 'none';
      if (floorGroup) floorGroup.style.display = 'none';
      if (totalFloorsGroup) totalFloorsGroup.style.display = '';
      if (furnishingGroup) furnishingGroup.style.display = '';
      if (ageGroup) ageGroup.style.display = '';
      if (parkingGroup) parkingGroup.style.display = '';
    } else if (type === 'Land') {
      // Land: hide bedrooms, floor, totalFloors, furnishing, age, parking.
      if (bedroomsGroup) bedroomsGroup.style.display = 'none';
      if (floorGroup) floorGroup.style.display = 'none';
      if (totalFloorsGroup) totalFloorsGroup.style.display = 'none';
      if (furnishingGroup) furnishingGroup.style.display = 'none';
      if (ageGroup) ageGroup.style.display = 'none';
      if (parkingGroup) parkingGroup.style.display = 'none';
    }
  }

  // --- Number Button Groups ---
  function setupNumButtons(containerId, stateKey) {
    var container = $('#' + containerId);
    if (!container) return;
    container.addEventListener('click', function (e) {
      var btn = e.target.closest('.num-btn');
      if (!btn) return;
      container.querySelectorAll('.num-btn').forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      state[stateKey] = parseInt(btn.dataset.value, 10);
    });
  }
  setupNumButtons('bedroomsButtons', 'bedrooms');
  setupNumButtons('totalFloorsButtons', 'totalFloors');

  // --- Furnishing Toggle ---
  var furnishingButtons = $('#furnishingButtons');
  if (furnishingButtons) {
    furnishingButtons.addEventListener('click', function (e) {
      var btn = e.target.closest('.btn-option');
      if (!btn) return;
      furnishingButtons.querySelectorAll('.btn-option').forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      state.furnishing = btn.dataset.value;
    });
  }

  // --- Range Sliders ---
  sizeSlider.addEventListener('input', function () {
    sizeValue.textContent = parseInt(sizeSlider.value, 10).toLocaleString();
  });
  ageSlider.addEventListener('input', function () {
    ageValue.textContent = ageSlider.value;
  });

  // --- Parking Toggle ---
  parkingToggle.addEventListener('click', function () {
    state.parking = !state.parking;
    parkingToggle.classList.toggle('active', state.parking);
    parkingLabel.textContent = state.parking ? 'Yes' : 'No';
  });

  // --- Animated Counter ---
  function animateCounter(element, target, duration, prefix, suffix) {
    duration = duration || 1200;
    prefix = prefix || '';
    suffix = suffix || '';
    var startTime = performance.now();
    var startVal = 0;

    // Determine decimal places from target
    var decimals = (target.toString().split('.')[1] || '').length;

    function update(currentTime) {
      var elapsed = currentTime - startTime;
      var progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      var eased = 1 - Math.pow(1 - progress, 3);
      var currentVal = startVal + (target - startVal) * eased;

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

  // --- Form Submit -> Predict ---
  predictForm.addEventListener('submit', async function (e) {
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

    var body;
    var type = state.propertyType;

    if (type === 'Flat') {
      body = {
        city: citySelect.value,
        locality: localitySelect.value,
        property_type: 'Flat',
        size_sqft: parseInt(sizeSlider.value, 10),
        bedrooms: state.bedrooms,
        floor: parseInt(floorInput.value, 10) || 0,
        age_years: parseInt(ageSlider.value, 10),
        furnishing: state.furnishing,
        parking: state.parking,
      };
    } else if (type === 'House') {
      body = {
        city: citySelect.value,
        locality: localitySelect.value,
        property_type: 'House',
        size_sqft: parseInt(sizeSlider.value, 10),
        bedrooms: 0,
        floor: state.totalFloors,
        age_years: parseInt(ageSlider.value, 10),
        furnishing: state.furnishing,
        parking: state.parking,
      };
    } else {
      // Land
      body = {
        city: citySelect.value,
        locality: localitySelect.value,
        property_type: 'Land',
        size_sqft: parseInt(sizeSlider.value, 10),
        bedrooms: 0,
        floor: 0,
        age_years: 0,
        furnishing: 'Unfurnished',
        parking: false,
      };
    }

    // Loading state
    predictBtn.classList.add('loading');
    predictBtn.disabled = true;
    resultsContainer.classList.remove('show');

    try {
      var data = await apiFetch('/api/predict', {
        method: 'POST',
        body: JSON.stringify(body),
      });

      // Show results
      resultsContainer.classList.add('show');
      
      var priceVal = data.price_lakhs;
      var unitSpan = document.querySelector('.result-card.price .result-unit');
      if (priceVal >= 100) {
        priceVal = Math.round((priceVal / 100) * 100) / 100;
        if (unitSpan) unitSpan.textContent = 'Crore';
        animateCounter(priceResult, priceVal, 1400);
      } else {
        if (unitSpan) unitSpan.textContent = 'Lakhs';
        animateCounter(priceResult, priceVal, 1400);
      }
      
      animateCounter(rentResult, Math.round(data.rent_monthly), 1400);

      var modelInfo = data.model_info || {};
      resultMeta.textContent = 'Model: ' + (modelInfo.name || 'Ridge Regression') + ' | R2 Score: ' + (modelInfo.r2_score || 0).toFixed(3);

      showToast('Prediction generated successfully!', 'success');

      // Scroll to results
      setTimeout(function () {
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }, 200);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      predictBtn.classList.remove('loading');
      predictBtn.disabled = false;
    }
  });

  // --- RAG Chat ---

  function formatTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function addChatMessage(content, sender, sources) {
    sources = sources || [];
    var msgDiv = document.createElement('div');
    msgDiv.className = 'chat-message ' + sender;

    var sourcesHTML = '';
    if (sources && sources.length > 0) {
      var sourceItems = sources
        .map(function (s) {
          return '<div class="source-item">' +
            '<span class="source-file">[doc] ' + (s.file || 'source') + '</span>' +
            '<span class="source-score">' + (s.score ? (s.score * 100).toFixed(0) + '% match' : '') + '</span>' +
            '<div style="margin-top:4px; font-size:0.76rem; color:var(--text-muted);">' + truncate(s.text || '', 120) + '</div>' +
            '</div>';
        })
        .join('');

      sourcesHTML =
        '<div class="message-sources">' +
        '<button class="sources-toggle" onclick="this.classList.toggle(\'open\'); this.nextElementSibling.classList.toggle(\'show\');">' +
        '[+] ' + sources.length + ' source' + (sources.length > 1 ? 's' : '') + ' <span class="chevron">v</span>' +
        '</button>' +
        '<div class="sources-list">' + sourceItems + '</div>' +
        '</div>';
    }

    msgDiv.innerHTML =
      '<div class="message-bubble">' + escapeHTML(content) + '</div>' +
      sourcesHTML +
      '<div class="message-time">' + formatTime() + '</div>';

    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function escapeHTML(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function truncate(str, len) {
    return str.length > len ? str.substring(0, len) + '...' : str;
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
      var data = await apiFetch('/api/ask', {
        method: 'POST',
        body: JSON.stringify({ question: question }),
      });

      typingIndicator.classList.remove('show');
      addChatMessage(data.answer || 'No response received.', 'ai', data.sources || []);
    } catch (err) {
      typingIndicator.classList.remove('show');
      addChatMessage('Sorry, I encountered an error: ' + err.message, 'ai');
      showToast(err.message, 'error');
    } finally {
      chatSend.disabled = false;
      chatInput.focus();
    }
  }

  chatSend.addEventListener('click', function () { sendChatMessage(chatInput.value); });
  chatInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage(chatInput.value);
    }
  });

  // Suggestion chips
  if (suggestionChips) {
    suggestionChips.addEventListener('click', function (e) {
      var chip = e.target.closest('.suggestion-chip');
      if (chip) sendChatMessage(chip.dataset.question);
    });
  }

  // --- Load Model Info from API ---
  async function loadModelInfo() {
    try {
      var data = await apiFetch('/api/model-info');

      // Update feature importance bars
      if (data.feature_importance) {
        var list = $('#featureBarList');
        if (list) {
          var entries = Object.entries(data.feature_importance)
            .sort(function (a, b) { return b[1] - a[1]; })
            .slice(0, 6);

          var maxVal = (entries[0] && entries[0][1]) || 1;

          list.innerHTML = entries
            .map(function (entry) {
              var name = entry[0];
              var value = entry[1];
              return '<div class="feature-bar-item">' +
                '<div class="feature-bar-label">' +
                '<span class="feature-bar-name">' + escapeHTML(name) + '</span>' +
                '<span class="feature-bar-value">' + (value * 100).toFixed(0) + '%</span>' +
                '</div>' +
                '<div class="feature-bar-track">' +
                '<div class="feature-bar-fill" data-width="' + (value * 100).toFixed(0) + '"></div>' +
                '</div>' +
                '</div>';
            })
            .join('');

          // Re-observe for animation
          barObserver.observe(list);
        }
      }

      // Update model comparison table
      if (data.price_model || data.rent_model) {
        var tbody = document.querySelector('#modelTable tbody');
        if (tbody) {
          tbody.innerHTML = '';

          var models = [];
          if (data.price_model) {
            models.push({ r2: data.price_model.r2, mae: data.price_model.mae, rmse: data.price_model.rmse, label: (data.price_model.name || 'Model') + ' (Price)' });
          }
          if (data.rent_model) {
            models.push({ r2: data.rent_model.r2, mae: data.rent_model.mae, rmse: data.rent_model.rmse, label: (data.rent_model.name || 'Model') + ' (Rent)' });
          }

          models.forEach(function (m) {
            var r2Class = m.r2 >= 0.85 ? 'metric-good' : 'metric-ok';
            var row = document.createElement('tr');
            row.innerHTML =
              '<td class="model-name">' + escapeHTML(m.label) + '</td>' +
              '<td class="' + r2Class + '">' + (m.r2 != null ? m.r2.toFixed(3) : '--') + '</td>' +
              '<td>' + (m.mae != null ? m.mae.toFixed(2) : '--') + '</td>' +
              '<td>' + (m.rmse != null ? m.rmse.toFixed(2) : '--') + '</td>';
            tbody.appendChild(row);
          });
        }
      }
    } catch (err) {
      // Silently fail -- use default placeholder data
      console.log('Model info not available, using defaults.');
    }
  }

  // --- Initialize ---
  function init() {
    togglePropertyFields();
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
