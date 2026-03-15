import React from 'react';

const TermsOfUseModal = ({ onClose, zIndex = 50 }) => {
    return (
        <div className={`fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-[${zIndex}]`}>
            <div className="bg-white rounded-xl max-w-2xl w-full max-h-[80vh] flex flex-col shadow-2xl">
                {/* Header */}
                <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                    <h2 className="text-2xl font-bold text-gray-800">📜 Pyramyd Terms of Use</h2>
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
                        <h3 className="text-lg font-bold text-gray-900 mb-2">1. Acceptance of Terms and Platform Role</h3>
                        <p>
                            This document constitutes a legally binding agreement between you ("the Partner," "User," or "Agent") and Pyramyd ("the Platform"). By accessing or using our social agri-commerce services, you acknowledge that Pyramyd operates strictly as a digital intermediary and marketplace facilitator. We provide the technology to connect Farmers, Agents, and Businesses, but we are not a party to the actual contract of sale. The legal responsibility for the fulfillment of orders, product quality, and accuracy of descriptions rests solely with the Seller, while the obligation for payment and verification rests with the Buyer.
                        </p>
                    </section>

                    <section>
                        <h3 className="text-lg font-bold text-gray-900 mb-2">2. Account Registration and Partner Verification</h3>
                        <p>
                            To maintain a high-trust environment, all accounts (excluding basic personal buyer accounts) are classified as "Partners." By registering, you agree to undergo our mandatory Know Your Customer (KYC) process. This includes the submission of valid identification such as a National Identity Number (NIN), Corporate Affairs Commission (CAC) documents for businesses, and proof of address. You warrant that all uploaded documents are authentic and current. Pyramyd reserves the right to verify these details via third-party databases, including NIMC and the CAC portal. Providing fraudulent information is a material breach of these terms and may result in immediate account termination and reporting to relevant legal authorities.
                        </p>
                    </section>

                    <section>
                        <h3 className="text-lg font-bold text-gray-900 mb-2">3. PyExpress and Delivery Timelines</h3>
                        <p>
                            Pyramyd offers distinct service levels categorized by delivery speed and product source. Purchases made through PyExpress are guaranteed for rapid fulfillment, with delivery expected between 4 to 24 hours from the time of order confirmation. Conversely, products sourced via Farm Deals or the Community Page, which often involve rural aggregation and specialized logistics, carry a delivery window of 3 to 14 days. Partners acknowledge that these timelines are estimates based on standard operating conditions and may be affected by extreme weather, transit security, or agricultural variables beyond the Platform's control.
                        </p>
                    </section>

                    <section>
                        <h3 className="text-lg font-bold text-gray-900 mb-2">4. Quality Assurance and Seller Obligations</h3>
                        <p>
                            All Sellers and Agents acting on behalf of farmers are bound by the Pyramyd Quality Standard. Sellers must provide truthful, non-stock photography and accurate descriptions of produce, including harvest dates and variety grades. Because we deal in perishable agricultural goods, the Validation Handshake is mandatory. Upon delivery, the Seller must provide a unique system-generated code to the Buyer. The input of this code by the Buyer constitutes legal confirmation that the goods have been received in acceptable condition. Any claims regarding spoilage or sub-standard quality must be submitted with photographic evidence through the in-app dispute tool within two (2) hours of delivery.
                        </p>
                    </section>

                    <section>
                        <h3 className="text-lg font-bold text-gray-900 mb-2">5. Manual Payment and Financial Conduct</h3>
                        <p>
                            At this stage of operation, Pyramyd facilitates market matching while payments are settled manually between Partners (e.g., via direct bank transfer). Users agree that Pyramyd is not a payment processor and is not liable for failed transfers, bank errors, or fraudulent payment alerts. Partners are strongly advised to verify payments only upon physical inspection of goods. Attempting to bypass the platform to establish long-term off-platform trading for the purpose of avoiding future commissions or platform fees is strictly prohibited and constitutes a breach of the partnership agreement.
                        </p>
                    </section>

                    <section>
                        <h3 className="text-lg font-bold text-gray-900 mb-2">6. Social Conduct and Data Privacy</h3>
                        <p>
                            As a social commerce platform, Pyramyd thrives on community interaction. Users agree to communicate respectfully within the in-app chat and refrain from posting misleading agricultural advice or prohibited substances. In compliance with the Nigeria Data Protection Act (NDPA) 2023, your data is handled with the highest level of security. We collect and process your information strictly for the purposes of identity verification, logistics coordination, and platform security. By using the service, you consent to the sharing of necessary contact and location data with designated logistics partners to facilitate the delivery of your orders.
                        </p>
                    </section>

                    <div className="bg-emerald-50 p-4 rounded-lg border border-emerald-100 mt-8">
                        <p className="text-sm text-emerald-800 text-center font-medium">
                            By continuing to use Pyramyd, you acknowledge that you have read, understood, and agreed to these terms.
                        </p>
                    </div>
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-gray-100 bg-gray-50 rounded-b-xl flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-6 py-2 bg-emerald-900 text-white rounded-lg hover:bg-emerald-800 transition-colors font-medium shadow-sm"
                    >
                        I Accept
                    </button>
                </div>
            </div>
        </div>
    );
};

export default TermsOfUseModal;
