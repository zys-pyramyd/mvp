import React from 'react';

/**
 * ProductStory - Traceability Timeline Component
 * 
 * Visually displays the provenance of a product, showing the journey from
 * farmer/producer to the platform. Highlights verification status at each step.
 */
const ProductStory = ({ product }) => {
  if (!product) return null;

  // Determine roles and names
  const isAgentListed = product.listed_by_agent || !!product.agent_name;
  const producerName = product.farm_name || product.business_name || (isAgentListed ? 'Registered Farmer' : product.seller_name) || 'Unknown Producer';
  
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mt-8 mb-12">
      <div className="p-6 md:p-8 bg-gradient-to-r from-emerald-50 to-green-50 border-b border-emerald-100">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-xl shadow-sm border border-emerald-200">
            🌱
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">Product Story & Traceability</h3>
            <p className="text-sm text-emerald-700 font-medium">Verified supply chain journey</p>
          </div>
        </div>
      </div>

      <div className="p-6 md:p-8">
        <div className="relative border-l-2 border-emerald-200 ml-4 md:ml-6 space-y-10">
          
          {/* Step 1: The Origin (Farmer/Producer) */}
          <div className="relative pl-8 md:pl-12">
            <div className="absolute -left-3 md:-left-[1.1rem] top-1 w-6 h-6 md:w-8 md:h-8 bg-emerald-500 rounded-full border-4 border-white shadow flex items-center justify-center">
              <span className="text-white text-xs md:text-sm">1</span>
            </div>
            <div>
              <span className="text-xs font-bold tracking-wider text-gray-500 uppercase">Origin</span>
              <h4 className="text-lg font-bold text-gray-900 mt-1 flex items-center gap-2">
                Produced by {producerName}
                {(!isAgentListed && product.seller_is_verified) && (
                  <span className="bg-emerald-100 text-emerald-700 text-xs px-2 py-0.5 rounded-full flex items-center gap-1 font-medium border border-emerald-200">
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Verified Producer
                  </span>
                )}
              </h4>
              <p className="text-sm text-gray-600 mt-2 bg-gray-50 p-3 rounded-lg border border-gray-100">
                Grown and harvested in <span className="font-semibold text-gray-800">{product.location || 'Nigeria'}</span>. 
                Our platform ensures direct sourcing from the producer to maintain freshness and fair pricing.
              </p>
            </div>
          </div>

          {/* Step 2: Agent verification (if applicable) */}
          {isAgentListed && (
            <div className="relative pl-8 md:pl-12">
              <div className="absolute -left-3 md:-left-[1.1rem] top-1 w-6 h-6 md:w-8 md:h-8 bg-blue-500 rounded-full border-4 border-white shadow flex items-center justify-center">
                <span className="text-white text-xs md:text-sm">2</span>
              </div>
              <div>
                <span className="text-xs font-bold tracking-wider text-gray-500 uppercase">Quality Assurance</span>
                <h4 className="text-lg font-bold text-gray-900 mt-1 flex items-center gap-2">
                  Verified by Agent {product.agent_name}
                  <span className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full flex items-center gap-1 font-medium border border-blue-200">
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                    Certified Agent
                  </span>
                </h4>
                <p className="text-sm text-gray-600 mt-2 bg-gray-50 p-3 rounded-lg border border-gray-100">
                  This product was physically inspected and listed by our certified field agent. 
                  Agents ensure quality standards are met before products reach the PyramydHub marketplace.
                </p>
              </div>
            </div>
          )}

          {/* Step 3: Platform Guarantee */}
          <div className="relative pl-8 md:pl-12">
            <div className="absolute -left-3 md:-left-[1.1rem] top-1 w-6 h-6 md:w-8 md:h-8 bg-purple-500 rounded-full border-4 border-white shadow flex items-center justify-center">
              <span className="text-white text-xs md:text-sm">{isAgentListed ? '3' : '2'}</span>
            </div>
            <div>
              <span className="text-xs font-bold tracking-wider text-gray-500 uppercase">Marketplace</span>
              <h4 className="text-lg font-bold text-gray-900 mt-1 flex items-center gap-2">
                PyramydHub Guarantee
                <span className="bg-purple-100 text-purple-700 text-xs px-2 py-0.5 rounded-full flex items-center gap-1 font-medium border border-purple-200">
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  Escrow Protected
                </span>
              </h4>
              <p className="text-sm text-gray-600 mt-2 bg-gray-50 p-3 rounded-lg border border-gray-100">
                Your payment is held securely in escrow until you receive and confirm the order. 
                We guarantee the traceability and authenticity of this product.
              </p>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default ProductStory;
