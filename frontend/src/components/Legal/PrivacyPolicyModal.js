import React from 'react';

const PrivacyPolicyModal = ({ onClose, zIndex = 50 }) => {
    return (
        <div className={`fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-[${zIndex}]`}>
            <div className="bg-white rounded-xl max-w-2xl w-full max-h-[80vh] flex flex-col shadow-2xl">
                {/* Header */}
                <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                    <h2 className="text-2xl font-bold text-gray-800">🛡️ Pyramyd Privacy Policy</h2>
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
                        <h3 className="text-lg font-bold text-gray-900 mb-2">1. Data Collection and the Purpose of Processing</h3>
                        <p>
                            Pyramyd is committed to protecting the privacy and security of all our Partners. We collect personal and corporate information strictly to facilitate secure social agri-commerce and to comply with the Nigeria Data Protection Act (NDPA) 2023. This data includes your name, contact details, and what we refer to as "Trust Documents," such as National Identity Numbers (NIN), Corporate Affairs Commission (CAC) registration papers, and proof of address. The primary purpose of collecting this information is to verify the identity of our Partners, prevent fraudulent listings, and maintain a safe marketplace for the movement of agricultural goods. By providing this information, you consent to its use for identity verification and administrative purposes necessary to fulfill our service obligations to you.
                        </p>
                    </section>

                    <section>
                        <h3 className="text-lg font-bold text-gray-900 mb-2">2. Use of Sensitive Trust Documents</h3>
                        <p>
                            We recognize the sensitive nature of documents like the NIN and CAC status reports. These are stored using industry-standard encryption and are accessed only by authorized personnel for the purpose of account validation. We may utilize third-party verification services to confirm the authenticity of these documents via the NIMC or CAC portals. We do not sell, rent, or trade your sensitive identification documents to third parties for marketing purposes. These documents are retained only for as long as your account remains active or as required by statutory Nigerian laws regarding financial records and anti-money laundering regulations.
                        </p>
                    </section>

                    <section>
                        <h3 className="text-lg font-bold text-gray-900 mb-2">3. Third-Party Sharing and Logistics Coordination</h3>
                        <p>
                            To facilitate the delivery of agricultural produce, Pyramyd must share specific data with our designated Logistics Partners. This includes the pickup and delivery addresses, contact phone numbers, and the names of the parties involved in the transaction. This sharing is limited to the minimum information necessary to ensure the successful transit of goods. Whether your order is processed through PyExpress for rapid delivery or via a Farm Deal, our logistics partners are contractually bound to use your data solely for fulfillment purposes and to maintain the confidentiality of your information in accordance with our security standards.
                        </p>
                    </section>

                    <section>
                        <h3 className="text-lg font-bold text-gray-900 mb-2">4. Data Security and Partner Rights</h3>
                        <p>
                            We implement robust technical and organizational measures to safeguard your data against unauthorized access, loss, or alteration. As a Partner on Pyramyd, you retain several rights over your personal information under the NDPA 2023, including the right to access the data we hold about you, the right to request the rectification of inaccurate information, and the right to request the deletion of your data when it is no longer required for its original purpose. You may exercise these rights at any time by contacting our support team or updating your profile settings. We also utilize cookies and similar tracking technologies to improve platform performance and personalize your experience, which you can manage through your browser settings.
                        </p>
                    </section>

                    <section>
                        <h3 className="text-lg font-bold text-gray-900 mb-2">5. Social Interaction and Public Data</h3>
                        <p>
                            Please be aware that Pyramyd is a social commerce platform. Information you choose to post in public areas, such as the Community Page or your public Partner Profile (e.g., your business name, public reviews, and general farm location), may be visible to other users. We encourage you to be mindful of the information you share socially. While we provide tools to facilitate communication between Buyers and Sellers, we are not responsible for the privacy practices of other users. We maintain uneditable chat logs for dispute resolution purposes, ensuring that all interactions related to a transaction are recorded for your protection.
                        </p>
                    </section>

                </div>

                {/* Footer */}
                <div className="p-4 border-t border-gray-100 bg-gray-50 rounded-b-xl flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-6 py-2 bg-emerald-900 text-white rounded-lg hover:bg-emerald-800 transition-colors font-medium shadow-sm"
                    >
                        I Understand
                    </button>
                </div>
            </div>
        </div>
    );
};

export default PrivacyPolicyModal;
