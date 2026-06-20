import React, { useState, useEffect, useCallback } from 'react';

/**
 * SmartProductSearch — Location-Aware Two-Section Product Display
 *
 * Section 1: "Searches Near You" — products in user's detected city/state
 * Section 2: "Searches Outside Your Location" — national fallback when local < threshold
 *
 * Features:
 * - Browser Geolocation API with reverse geocoding (Geoapify)
 * - State dropdown fallback if GPS denied
 * - Visual distinction between local and national results
 * - Animated section headers with result counts
 */

const NIGERIAN_STATES = [
  'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa', 'Benue',
  'Borno', 'Cross River', 'Delta', 'Ebonyi', 'Edo', 'Ekiti', 'Enugu',
  'FCT - Abuja', 'Gombe', 'Imo', 'Jigawa', 'Kaduna', 'Kano', 'Katsina',
  'Kebbi', 'Kogi', 'Kwara', 'Lagos', 'Nasarawa', 'Niger', 'Ogun', 'Ondo',
  'Osun', 'Oyo', 'Plateau', 'Rivers', 'Sokoto', 'Taraba', 'Yobe', 'Zamfara'
];

const API_BASE = process.env.REACT_APP_BACKEND_URL;
const GEOAPIFY_KEY = process.env.REACT_APP_GEOAPIFY_KEY || '';

// How many local results before we consider "enough" — below this, show national expansion
const LOCAL_THRESHOLD = 4;

// ─────────────────────────────────────────────
// Helper: reverse geocode lat/lng → state + city
// ─────────────────────────────────────────────
async function reverseGeocode(lat, lng) {
  try {
    if (!GEOAPIFY_KEY) return null;
    const res = await fetch(
      `https://api.geoapify.com/v1/geocode/reverse?lat=${lat}&lon=${lng}&apiKey=${GEOAPIFY_KEY}`
    );
    if (!res.ok) return null;
    const data = await res.json();
    const props = data?.features?.[0]?.properties;
    if (!props) return null;
    return {
      city: props.city || props.town || props.village || props.county || '',
      state: props.state || '',
      country: props.country || 'Nigeria',
    };
  } catch {
    return null;
  }
}

// ─────────────────────────────────────────────
// Helper: fetch products with optional state/city filter
// ─────────────────────────────────────────────
async function fetchProductsFromAPI({ state, city, searchTerm, category, platform, global_search = false }) {
  try {
    const params = new URLSearchParams();
    if (platform) params.append('platform', platform);
    if (category) params.append('category', category);
    if (searchTerm) params.append('search_term', searchTerm);
    if (state) params.append('location', state);
    if (city) params.append('city', city);
    if (global_search) params.append('global_search', 'true');
    params.append('limit', '20');

    const res = await fetch(`${API_BASE}/api/products?${params.toString()}`);
    if (!res.ok) return [];
    const data = await res.json();
    return Array.isArray(data) ? data : (data.products || []);
  } catch {
    return [];
  }
}

// ─────────────────────────────────────────────
// Sub-component: Product Card (mini, inline)
// ─────────────────────────────────────────────
const SmartProductCard = ({ product, onSelect, badge }) => {
  const img = product.images?.[0] || product.image_url || product.thumbnail;
  const price = product.price_per_unit || product.price || 0;
  const sellerVerified = product.seller_is_verified;

  return (
    <div
      onClick={() => onSelect && onSelect(product)}
      className="smart-product-card group cursor-pointer bg-white rounded-2xl overflow-hidden border border-gray-100 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-300"
      style={{ position: 'relative' }}
    >
      {/* Badge */}
      {badge && (
        <div
          className={`absolute top-3 left-3 z-10 px-2 py-0.5 rounded-full text-xs font-bold flex items-center gap-1 ${
            badge === 'near'
              ? 'bg-emerald-500 text-white'
              : 'bg-blue-500 text-white'
          }`}
        >
          {badge === 'near' ? '📍 Near You' : '🌍 Nationwide'}
        </div>
      )}

      {/* Verified */}
      {sellerVerified && (
        <div className="absolute top-3 right-3 z-10 bg-white/90 backdrop-blur-sm rounded-full p-1">
          <span title="Verified Seller" className="text-emerald-600 text-xs">✅</span>
        </div>
      )}

      {/* Image */}
      <div className="w-full h-44 bg-gradient-to-br from-emerald-50 to-green-100 overflow-hidden">
        {img ? (
          <img
            src={img}
            alt={product.title}
            loading="lazy"
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            onError={e => { e.target.style.display = 'none'; }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-5xl">🌾</div>
        )}
      </div>

      {/* Info */}
      <div className="p-3">
        <p className="text-xs text-gray-400 capitalize mb-0.5 truncate">{product.category || 'General'}</p>
        <h4 className="font-semibold text-gray-800 text-sm leading-snug line-clamp-2 mb-1">
          {product.title}
        </h4>
        <div className="flex items-center justify-between mt-2">
          <span className="text-emerald-700 font-bold text-sm">
            ₦{price.toLocaleString()}
            <span className="text-gray-400 font-normal text-xs">/{product.unit || 'unit'}</span>
          </span>
          {product.city || product.location ? (
            <span className="text-xs text-gray-400 truncate max-w-[80px]">
              📍 {product.city || product.location}
            </span>
          ) : null}
        </div>
      </div>
    </div>
  );
};

// ─────────────────────────────────────────────
// Sub-component: Section Header
// ─────────────────────────────────────────────
const SectionHeader = ({ icon, title, subtitle, count, accentColor = 'emerald', isExpanded }) => (
  <div className={`flex items-center gap-3 mb-5 pb-3 border-b-2 ${accentColor === 'emerald' ? 'border-emerald-200' : 'border-blue-200'}`}>
    <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-xl font-bold shadow-sm ${
      accentColor === 'emerald'
        ? 'bg-gradient-to-br from-emerald-500 to-green-600 text-white'
        : 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white'
    }`}>
      {icon}
    </div>
    <div className="flex-1">
      <h3 className="font-bold text-gray-900 text-base leading-tight">{title}</h3>
      {subtitle && <p className="text-xs text-gray-500 mt-0.5">{subtitle}</p>}
    </div>
    {count !== undefined && (
      <span className={`px-3 py-1 rounded-full text-xs font-bold ${
        accentColor === 'emerald'
          ? 'bg-emerald-100 text-emerald-700'
          : 'bg-blue-100 text-blue-700'
      }`}>
        {count} {count === 1 ? 'result' : 'results'}
      </span>
    )}
  </div>
);

// ─────────────────────────────────────────────
// Location Bar Sub-component
// ─────────────────────────────────────────────
const LocationBar = ({ detectedLocation, selectedState, onStateChange, onDetectLocation, isDetecting, locationError }) => {
  const displayLocation = detectedLocation?.city
    ? `${detectedLocation.city}, ${detectedLocation.state}`
    : selectedState || null;

  return (
    <div className="flex flex-wrap items-center gap-3 mb-6 p-4 bg-gradient-to-r from-emerald-50 to-green-50 rounded-2xl border border-emerald-100">
      {/* Location indicator */}
      <div className="flex items-center gap-2 flex-1 min-w-0">
        <div className="w-8 h-8 bg-emerald-600 rounded-full flex items-center justify-center flex-shrink-0">
          <span className="text-white text-xs">📍</span>
        </div>
        <div className="min-w-0">
          {displayLocation ? (
            <>
              <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Your Location</p>
              <p className="font-bold text-gray-800 text-sm truncate">{displayLocation}</p>
            </>
          ) : (
            <p className="text-sm text-gray-500">Location not set — showing all results</p>
          )}
        </div>
      </div>

      {/* State dropdown */}
      <select
        value={selectedState}
        onChange={e => onStateChange(e.target.value)}
        className="text-sm border border-emerald-200 rounded-xl px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-400 text-gray-700 min-w-[160px]"
      >
        <option value="">📋 Select a State</option>
        {NIGERIAN_STATES.map(s => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>

      {/* Detect button */}
      <button
        onClick={onDetectLocation}
        disabled={isDetecting}
        className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold rounded-xl transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed shadow-sm hover:shadow-md"
      >
        {isDetecting ? (
          <>
            <span className="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full"></span>
            Detecting...
          </>
        ) : (
          <>
            <span>🎯</span> Detect My Location
          </>
        )}
      </button>

      {locationError && (
        <p className="text-xs text-red-500 w-full mt-1 flex items-center gap-1">
          <span>⚠️</span> {locationError}
        </p>
      )}
    </div>
  );
};

// ─────────────────────────────────────────────
// MAIN COMPONENT
// ─────────────────────────────────────────────
const SmartProductSearch = ({
  searchTerm = '',
  category = '',
  platform = 'home',
  onProductSelect,
  // Optional: pass in existing products from parent to avoid double-fetching
  existingProducts = null,
}) => {
  const [detectedLocation, setDetectedLocation] = useState(null); // { city, state }
  const [selectedState, setSelectedState] = useState('');
  const [isDetecting, setIsDetecting] = useState(false);
  const [locationError, setLocationError] = useState('');

  const [localProducts, setLocalProducts] = useState([]);
  const [nationalProducts, setNationalProducts] = useState([]);
  const [loadingLocal, setLoadingLocal] = useState(false);
  const [loadingNational, setLoadingNational] = useState(false);
  const [showNational, setShowNational] = useState(false);

  // Derive the active location from detector or dropdown
  const activeState = detectedLocation?.state || selectedState || '';
  const activeCity = detectedLocation?.city || '';

  // ── Detect location via browser GPS ──
  const handleDetectLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setLocationError('Your browser does not support location detection.');
      return;
    }
    setIsDetecting(true);
    setLocationError('');
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude, longitude } = pos.coords;
        const geo = await reverseGeocode(latitude, longitude);
        if (geo) {
          setDetectedLocation(geo);
          setSelectedState(geo.state || '');
        } else {
          setLocationError('Could not determine your address. Please select a state manually.');
        }
        setIsDetecting(false);
      },
      (err) => {
        setIsDetecting(false);
        if (err.code === 1) {
          setLocationError('Location access denied. Please select your state using the dropdown.');
        } else {
          setLocationError('Could not get your location. Please select your state manually.');
        }
      },
      { timeout: 8000, maximumAge: 300000 }
    );
  }, []);

  // ── Fetch products when location or search changes ──
  useEffect(() => {
    const load = async () => {
      // If parent passed products in, split them without fetching
      if (existingProducts !== null) {
        splitProducts(existingProducts);
        return;
      }

      if (activeState || searchTerm || category) {
        setLoadingLocal(true);
        const local = await fetchProductsFromAPI({
          state: activeState,
          city: activeCity,
          searchTerm,
          category,
          platform,
        });
        setLocalProducts(local);
        setLoadingLocal(false);

        const needsExpansion = local.length < LOCAL_THRESHOLD;
        setShowNational(needsExpansion || !activeState);

        if (needsExpansion || !activeState) {
          setLoadingNational(true);
          const national = await fetchProductsFromAPI({
            searchTerm,
            category,
            platform,
            global_search: true,
          });
          // Exclude any products already in local results
          const localIds = new Set(local.map(p => p.id || p._id));
          setNationalProducts(national.filter(p => !localIds.has(p.id || p._id)));
          setLoadingNational(false);
        } else {
          setNationalProducts([]);
        }
      } else {
        // No location + no search: fetch all (national mode only)
        setShowNational(true);
        setLocalProducts([]);
        setLoadingNational(true);
        const all = await fetchProductsFromAPI({ platform, searchTerm, category, global_search: true });
        setNationalProducts(all);
        setLoadingNational(false);
      }
    };

    load();
  }, [activeState, activeCity, searchTerm, category, platform, existingProducts]);

  // Split pre-fetched products into local vs national
  const splitProducts = useCallback((prods) => {
    if (!activeState) {
      setLocalProducts([]);
      setNationalProducts(prods);
      setShowNational(true);
      return;
    }
    const local = prods.filter(p =>
      (p.state && p.state.toLowerCase().includes(activeState.toLowerCase())) ||
      (p.location && p.location.toLowerCase().includes(activeState.toLowerCase()))
    );
    const national = prods.filter(p => !local.includes(p));
    setLocalProducts(local);
    setNationalProducts(national);
    setShowNational(local.length < LOCAL_THRESHOLD || !activeState);
  }, [activeState]);

  const totalResults = localProducts.length + (showNational ? nationalProducts.length : 0);
  const hasAnything = localProducts.length > 0 || nationalProducts.length > 0;
  const isLoading = loadingLocal || loadingNational;

  return (
    <div className="smart-product-search-container w-full">
      {/* Location Bar */}
      <LocationBar
        detectedLocation={detectedLocation}
        selectedState={selectedState}
        onStateChange={(val) => {
          setSelectedState(val);
          setDetectedLocation(null);
        }}
        onDetectLocation={handleDetectLocation}
        isDetecting={isDetecting}
        locationError={locationError}
      />

      {/* Loading skeleton */}
      {isLoading && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 mb-8">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="bg-white rounded-2xl overflow-hidden border border-gray-100 shadow-sm animate-pulse">
              <div className="h-44 bg-gray-200"></div>
              <div className="p-3 space-y-2">
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                <div className="h-4 bg-gray-200 rounded w-full"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* No results state */}
      {!isLoading && !hasAnything && (
        <div className="text-center py-20">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-xl font-bold text-gray-700 mb-2">No products found</h3>
          <p className="text-gray-500 text-sm max-w-xs mx-auto">
            {searchTerm
              ? `No results for "${searchTerm}". Try a different search term or broaden your location.`
              : 'Be the first to list a product in this category!'}
          </p>
        </div>
      )}

      {/* ── SECTION 1: Near You ── */}
      {!isLoading && localProducts.length > 0 && (
        <section className="mb-10">
          <SectionHeader
            icon="📍"
            title="Searches Near You"
            subtitle={
              activeCity
                ? `Products available in ${activeCity}${activeState ? `, ${activeState}` : ''}`
                : `Products available in ${activeState}`
            }
            count={localProducts.length}
            accentColor="emerald"
          />
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {localProducts.map(product => (
              <SmartProductCard
                key={product.id || product._id}
                product={product}
                onSelect={onProductSelect}
                badge="near"
              />
            ))}
          </div>
        </section>
      )}

      {/* ── SECTION 1 (no location): All Products header ── */}
      {!isLoading && !activeState && nationalProducts.length > 0 && (
        <section className="mb-10">
          <SectionHeader
            icon="🛒"
            title="All Available Products"
            subtitle="Set your location above to see products near you first"
            count={nationalProducts.length}
            accentColor="emerald"
          />
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {nationalProducts.map(product => (
              <SmartProductCard
                key={product.id || product._id}
                product={product}
                onSelect={onProductSelect}
              />
            ))}
          </div>
        </section>
      )}

      {/* ── SECTION 2: Outside Your Location ── */}
      {!isLoading && activeState && showNational && nationalProducts.length > 0 && (
        <section>
          {/* Divider with explanation */}
          <div className="relative my-8 flex items-center gap-4">
            <div className="flex-1 border-t-2 border-dashed border-gray-200"></div>
            <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 border border-blue-100 rounded-full text-xs text-blue-600 font-semibold whitespace-nowrap">
              <span>🌍</span>
              {localProducts.length < LOCAL_THRESHOLD
                ? `Only ${localProducts.length} result${localProducts.length !== 1 ? 's' : ''} near you — expanding nationwide`
                : 'More results from other locations'}
            </div>
            <div className="flex-1 border-t-2 border-dashed border-gray-200"></div>
          </div>

          <SectionHeader
            icon="🌍"
            title="Searches Outside Your Location"
            subtitle={`Sellers in other states that can potentially ship to ${activeState}`}
            count={nationalProducts.length}
            accentColor="blue"
          />
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {nationalProducts.map(product => (
              <SmartProductCard
                key={product.id || product._id}
                product={product}
                onSelect={onProductSelect}
                badge="national"
              />
            ))}
          </div>
        </section>
      )}
    </div>
  );
};

export default SmartProductSearch;
