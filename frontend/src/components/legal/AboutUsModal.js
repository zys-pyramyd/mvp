import React from 'react';

const AboutUsModal = ({ onClose, zIndex = 50 }) => {
    return (
        <div className={`fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-[${zIndex}]`}>
            <div className="bg-white rounded-xl max-w-2xl w-full max-h-[80vh] flex flex-col shadow-2xl">
                {/* Header */}
                <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                    <h2 className="text-2xl font-bold text-gray-800">🌟 About Pyramyd</h2>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                    >
                        ✕
                    </button>
                </div>

                {/* Scrollable Content */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6 text-gray-600 leading-relaxed text-sm md:text-base">

                    <section>
                        <h3 className="text-lg font-bold text-gray-900 mb-2">About Pyramyd</h3>
                        <p>
                            Pyramyd is a premier social agri-commerce platform designed to bridge the gap between rural production and urban demand. We empower Farmers, Agents, and Businesses by providing a high-trust digital marketplace where community interaction meets seamless trade. Our mission is to build a more efficient, transparent, and connected agricultural supply chain across Nigeria.
                        </p>
                        <p className="mt-4">
                            At Pyramyd, we understand that agriculture is the backbone of the economy, yet it faces significant hurdles in logistics and market access. We solve this by offering specialized services tailored to different needs: <span className="font-medium text-emerald-700">PyExpress</span> for rapid 4 to 24-hour delivery, and <span className="font-medium text-emerald-700">Farm Deals</span> for bulk, farm-gate sourcing delivered within 3 to 14 days. By integrating social communication with commercial tools, we allow partners to interact directly, ensuring that every transaction is rooted in community and verified quality.
                        </p>
                    </section>

                    <section>
                        <h3 className="text-lg font-bold text-gray-900 mb-2">Our Vision</h3>
                        <p>
                            We envision a future where every farmer has a direct line to the market and every business can source fresh produce with total confidence. Through our robust Partner Verification (KYC) and unique Delivery Validation Handshake, we are eliminating the uncertainties of traditional trade. Whether you are a smallholder farmer looking to reach new buyers or a large-scale business managing complex inventory, Pyramyd is your partner in growth.
                        </p>
                    </section>

                </div>

                {/* Footer */}
                <div className="p-4 border-t border-gray-100 bg-gray-50 rounded-b-xl flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-6 py-2 bg-emerald-900 text-white rounded-lg hover:bg-emerald-800 transition-colors font-medium shadow-sm"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AboutUsModal;
