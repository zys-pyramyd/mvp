import React, { useState, useEffect } from 'react';

/**
 * Reusable structured address block.
 *
 * Props:
 *   values      — { street, city, state, country }
 *   onChange    — called with updated { street?, city?, state?, country? }
 *   label       — section heading, e.g. "Residential Address" (default)
 *   accentColor — Tailwind ring/focus colour key, e.g. "emerald" | "purple" | "blue"
 *   required    — whether fields are required (default true)
 */

const NIGERIAN_STATES = [
    "Abia","Adamawa","Akwa Ibom","Anambra","Bauchi","Bayelsa","Benue","Borno",
    "Cross River","Delta","Ebonyi","Edo","Ekiti","Enugu","FCT - Abuja","Gombe",
    "Imo","Jigawa","Kaduna","Kano","Katsina","Kebbi","Kogi","Kwara","Lagos",
    "Nasarawa","Niger","Ogun","Ondo","Osun","Oyo","Plateau","Rivers","Sokoto",
    "Taraba","Yobe","Zamfara"
];

// A small list of countries — Nigeria first since that's the primary market.
// Expand as needed; keeping it manageable avoids the 250-country dropdown problem.
const COUNTRIES = [
    "Nigeria",
    "Ghana","Kenya","South Africa","Cameroon","Senegal","Cote d'Ivoire",
    "Tanzania","Uganda","Ethiopia","Egypt","Morocco","Algeria","Tunisia",
    "United Kingdom","United States","Canada","Germany","France",
    "Netherlands","UAE","Saudi Arabia","China","India","Other",
];

const AddressFields = ({
    values = {},
    onChange,
    label = "Address",
    accentColor = "emerald",
    required = true,
}) => {
    const ring = `focus:ring-2 focus:ring-${accentColor}-500 focus:border-${accentColor}-500`;
    const base = `w-full px-3 py-2 border border-gray-300 rounded-lg ${ring}`;

    const isNigeria = !values.country || values.country === 'Nigeria';

    return (
        <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-700">{label}</h4>

            {/* Street */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Street Address {required && <span className="text-red-500">*</span>}
                </label>
                <input
                    type="text"
                    value={values.street || ''}
                    onChange={e => onChange({ street: e.target.value })}
                    placeholder="e.g. 12, Awolowo Way"
                    className={base}
                    required={required}
                />
            </div>

            {/* City + State/Province */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        City / Town {required && <span className="text-red-500">*</span>}
                    </label>
                    <input
                        type="text"
                        value={values.city || ''}
                        onChange={e => onChange({ city: e.target.value })}
                        placeholder="e.g. Ikeja"
                        className={base}
                        required={required}
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        {isNigeria ? 'State' : 'State / Province'} {required && <span className="text-red-500">*</span>}
                    </label>
                    {isNigeria ? (
                        <select
                            value={values.state || ''}
                            onChange={e => onChange({ state: e.target.value })}
                            className={base}
                            required={required}
                        >
                            <option value="">Select State</option>
                            {NIGERIAN_STATES.map(s => (
                                <option key={s} value={s}>{s}</option>
                            ))}
                        </select>
                    ) : (
                        <input
                            type="text"
                            value={values.state || ''}
                            onChange={e => onChange({ state: e.target.value })}
                            placeholder="State / Province / Region"
                            className={base}
                            required={required}
                        />
                    )}
                </div>
            </div>

            {/* Country */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Country {required && <span className="text-red-500">*</span>}
                </label>
                <select
                    value={values.country || 'Nigeria'}
                    onChange={e => onChange({ country: e.target.value, state: '' })}
                    className={base}
                    required={required}
                >
                    {COUNTRIES.map(c => (
                        <option key={c} value={c}>{c}</option>
                    ))}
                </select>
            </div>
        </div>
    );
};

export default AddressFields;
