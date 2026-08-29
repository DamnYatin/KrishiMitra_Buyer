/**
 * File: buyer.js
 * Purpose: Logic for Buyer Marketplace screen (Screen 4).
 * Features:
 *   - Auto-fetches live active deals from GET /api/deals
 *   - Filters by crop and location, sorts by newest or price
 *   - Auto-polling every 15s with timer feedback
 *   - Inquiry Modal flow calling POST /api/deals/<id>/inquire to unlock farmer contact
 *   - In-session contact retention and tel: link generation
 */

let activeDeals = [];
let unlockedContacts = {}; // { dealId: { farmer_name, farmer_phone } }
let autoRefreshTimer = null;
let countdownSec = 15;

// ==========================================
// 1. Fetch Crops for Dropdown Filter
// ==========================================
async function loadCropFilter() {
  try {
    const res = await fetch("/api/crops");
    const data = await res.json();
    if (data.status === "success" && data.crops) {
      const select = document.getElementById("buyerCropFilter");
      if (!select) return;
      data.crops.forEach(c => {
        select.innerHTML += `<option value="${c.name}">${c.name}</option>`;
      });
    }
  } catch (e) {
    console.warn("Could not load crops for filter:", e);
  }
}

// ==========================================
// 2. Fetch Buyer Deals Feed
// ==========================================
async function fetchBuyerDeals() {
  const cropFilter = document.getElementById("buyerCropFilter") ? document.getElementById("buyerCropFilter").value : "";
  const locationFilter = document.getElementById("buyerLocationFilter") ? document.getElementById("buyerLocationFilter").value.trim() : "";
  const sortBy = document.getElementById("buyerSortFilter") ? document.getElementById("buyerSortFilter").value : "newest";

  const params = new URLSearchParams();
  if (cropFilter) params.append("crop", cropFilter);
  if (locationFilter) params.append("location", locationFilter);
  if (sortBy) params.append("sort", sortBy);

  try {
    const res = await fetch(`/api/deals?${params.toString()}`);
    const data = await res.json();

    if (data.status === "success") {
      activeDeals = data.deals || [];
      renderDealsFeed(activeDeals);
      const countElem = document.getElementById("dealCountDisplay");
      if (countElem) countElem.textContent = activeDeals.length;
    }
  } catch (err) {
    console.error("Buyer feed fetch error:", err);
    showToast("⚠️ Could not refresh marketplace feed.");
  }
}

// ==========================================
// 3. Render Deals Feed Cards
// ==========================================
function renderDealsFeed(deals) {
  const container = document.getElementById("buyerFeedContainer");
  if (!container) return;

  if (deals.length === 0) {
    container.innerHTML = `
      <div class="card" style="grid-column: 1 / -1; text-align: center; padding: 2.5rem 1rem;">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔍</div>
        <h3 style="color: var(--primary-dark); font-size: 1.15rem; font-weight: 700;">No Active Deals Found</h3>
        <p style="color: var(--text-muted); font-size: 0.88rem; max-width: 400px; margin: 0.5rem auto 1rem;">
          No farmer listings match your filter criteria. Try adjusting your crop or location filters.
        </p>
      </div>
    `;
    return;
  }

  container.innerHTML = "";

  deals.forEach(deal => {
    const card = document.createElement("div");
    card.className = "buyer-deal-card";

    const isUnlocked = !!unlockedContacts[deal.id];
    const contactInfo = unlockedContacts[deal.id];

    card.innerHTML = `
      <div>
        <!-- Top Metadata Row -->
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
          <span style="background: var(--primary-bg); color: var(--primary-dark); font-weight: 700; font-size: 0.78rem; padding: 0.25rem 0.65rem; border-radius: var(--radius-full);">
            🌱 ${deal.crop_name}
          </span>
          <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">
            🕒 ${deal.posted_ago}
          </span>
        </div>

        <!-- Asking Price & Deal Value -->
        <div style="margin-bottom: 0.75rem;">
          <div style="font-size: 1.45rem; font-weight: 800; color: var(--primary-dark); line-height: 1.2;">
            ₹${deal.price_per_quintal.toLocaleString()} <span style="font-size: 0.85rem; font-weight: 600; color: var(--text-muted);">/ quintal</span>
          </div>
          <div style="font-size: 0.82rem; color: var(--text-muted);">
            Est. Total Lot Value: <strong style="color: var(--text-main);">₹${deal.total_deal_value.toLocaleString()}</strong>
          </div>
        </div>

        <!-- Details Grid -->
        <div style="background: var(--bg-page); padding: 0.65rem; border-radius: var(--radius-sm); font-size: 0.82rem; margin-bottom: 0.85rem;">
          <div style="margin-bottom: 3px;">📍 Location: <strong>${deal.location_name}</strong></div>
          <div style="margin-bottom: 3px;">⚖️ Quantity: <strong>${deal.quantity_quintal} Quintals</strong></div>
          <div>👤 Farmer: <strong>${deal.farmer_name}</strong></div>
        </div>

        <!-- Inquiries Counter -->
        <div style="font-size: 0.78rem; font-weight: 600; color: #0284c7; margin-bottom: 0.85rem;">
          💬 ${deal.inquiry_count} Active Buyer Inquiries
        </div>
      </div>

      <!-- Action Section -->
      <div id="action-deal-${deal.id}">
        ${isUnlocked ? `
          <div style="background: #dcfce7; border: 1px solid #86efac; border-radius: var(--radius-sm); padding: 0.65rem; text-align: center;">
            <div style="font-size: 0.75rem; font-weight: 700; color: #166534; margin-bottom: 3px;">✅ CONTACT UNLOCKED</div>
            <a href="tel:${contactInfo.farmer_phone}" class="btn btn-primary" style="min-height: 36px; padding: 4px 10px; font-size: 0.85rem; width: 100%; display: flex; align-items: center; justify-content: center; gap: 4px;">
              📞 Call ${contactInfo.farmer_name}: ${contactInfo.farmer_phone}
            </a>
          </div>
        ` : `
          <button class="btn btn-primary" style="font-size: 0.88rem; width: 100%;" onclick="openInquiryModal(${deal.id})">
            🤝 I'm Interested
          </button>
        `}
      </div>
    `;

    container.appendChild(card);
  });
}

// ==========================================
// 4. Inquiry Modal & Contact Unlock
// ==========================================
window.openInquiryModal = function(dealId) {
  const deal = activeDeals.find(d => d.id === dealId);
  if (!deal) return;

  document.getElementById("inquiryDealId").value = dealId;
  const summaryElem = document.getElementById("modalDealSummary");
  summaryElem.innerHTML = `
    <div><strong>Crop:</strong> ${deal.crop_name}</div>
    <div><strong>Asking Price:</strong> ₹${deal.price_per_quintal.toLocaleString()} / qtl</div>
    <div><strong>Quantity:</strong> ${deal.quantity_quintal} Quintals (Total: ₹${deal.total_deal_value.toLocaleString()})</div>
    <div><strong>Location:</strong> ${deal.location_name} | Farmer: ${deal.farmer_name}</div>
  `;

  document.getElementById("inquiryModal").style.display = "flex";
};

function closeModal() {
  document.getElementById("inquiryModal").style.display = "none";
}

async function handleInquirySubmit(e) {
  e.preventDefault();
  const dealId = parseInt(document.getElementById("inquiryDealId").value);
  const buyerName = document.getElementById("buyerNameInput").value.trim();
  const buyerPhone = document.getElementById("buyerPhoneInput").value.trim();
  const btn = document.getElementById("confirmInquiryBtn");

  if (!dealId || !buyerName || !buyerPhone) {
    showToast("⚠️ Please enter your name and phone number.");
    return;
  }

  btn.disabled = true;
  btn.textContent = "Unlocking...";

  try {
    const res = await fetch(`/api/deals/${dealId}/inquire`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ buyer_name: buyerName, buyer_phone: buyerPhone })
    });

    const data = await res.json();
    if (data.status === "success") {
      unlockedContacts[dealId] = {
        farmer_name: data.farmer_name,
        farmer_phone: data.farmer_phone
      };
      showToast("🎉 Farmer contact unlocked! You may now call directly.");
      closeModal();
      renderDealsFeed(activeDeals);
    } else {
      showToast("⚠️ " + (data.message || "Could not register inquiry."));
    }
  } catch (err) {
    console.error("Inquiry registration failed:", err);
    showToast("⚠️ Network error while registering inquiry.");
  } finally {
    btn.disabled = false;
    btn.textContent = "🔓 Unlock Farmer Contact";
  }
}

// Toast helper
function showToast(msg) {
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

// ==========================================
// 5. Auto-Polling Timer
// ==========================================
function startAutoPolling() {
  countdownSec = 15;
  const statusElem = document.getElementById("autoRefreshStatus");

  if (autoRefreshTimer) clearInterval(autoRefreshTimer);

  autoRefreshTimer = setInterval(() => {
    countdownSec--;
    if (statusElem) {
      statusElem.textContent = `🔄 Auto-refreshing in ${countdownSec}s`;
    }
    if (countdownSec <= 0) {
      countdownSec = 15;
      fetchBuyerDeals();
    }
  }, 1000);
}

// ==========================================
// 6. Initialization
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  loadCropFilter();
  fetchBuyerDeals();
  startAutoPolling();

  // Filter Listeners
  const cropFilter = document.getElementById("buyerCropFilter");
  if (cropFilter) cropFilter.addEventListener("change", () => fetchBuyerDeals());

  const sortFilter = document.getElementById("buyerSortFilter");
  if (sortFilter) sortFilter.addEventListener("change", () => fetchBuyerDeals());

  const locationFilter = document.getElementById("buyerLocationFilter");
  if (locationFilter) {
    let timeout = null;
    locationFilter.addEventListener("input", () => {
      clearTimeout(timeout);
      timeout = setTimeout(fetchBuyerDeals, 350);
    });
  }

  const refreshBtn = document.getElementById("buyerRefreshBtn");
  if (refreshBtn) refreshBtn.addEventListener("click", () => {
    fetchBuyerDeals();
    countdownSec = 15;
    showToast("⚡ Deals feed refreshed");
  });

  // Modal Listeners
  const closeModalBtn = document.getElementById("closeModalBtn");
  if (closeModalBtn) closeModalBtn.addEventListener("click", closeModal);

  const inquiryForm = document.getElementById("inquiryForm");
  if (inquiryForm) inquiryForm.addEventListener("submit", handleInquirySubmit);
});
