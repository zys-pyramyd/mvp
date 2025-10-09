import React, { useState } from 'react';
import { DemoModeManager } from './DemoMode';

const DemoKYCSubmission = ({ onComplete, onCancel }) => {
  const [step, setStep] = useState(1);
  const [uploading, setUploading] = useState(false);
  const [formData, setFormData] = useState({
    business_name: 'Demo Agricultural Solutions',
    registration_number: 'RC-DEMO-001',
    tin_number: 'TIN-DEMO-001',
    business_address: 'No. 15 Agric Road, Ikeja, Lagos State, Nigeria',
    contact_person: 'Demo Agent',
    contact_phone: '+234 800 000 0001',
    business_type: 'Agricultural Trading',
    documents: {
      certificate_of_incorporation: null,
      tin_certificate: null,
      business_license: null,
      utility_bill: null
    }
  });

  const [documentStatus, setDocumentStatus] = useState({
    certificate_of_incorporation: 'pending',
    tin_certificate: 'pending', 
    business_license: 'pending',
    utility_bill: 'pending'
  });

  const documentTypes = [
    {
      key: 'certificate_of_incorporation',
      label: 'Certificate of Incorporation',
      description: 'Official business registration document',
      icon: '📜'
    },
    {
      key: 'tin_certificate', 
      label: 'TIN Certificate',
      description: 'Tax Identification Number certificate',
      icon: '🧾'
    },
    {
      key: 'business_license',
      label: 'Business License',
      description: 'Valid business operating license',
      icon: '📋'
    },
    {
      key: 'utility_bill',
      label: 'Utility Bill',
      description: 'Recent utility bill for address verification',
      icon: '⚡'
    }
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleFileUpload = async (documentType) => {
    setUploading(true);
    setDocumentStatus(prev => ({
      ...prev,
      [documentType]: 'uploading'
    }));

    // Simulate file upload delay
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Mock successful upload
    const mockFile = {
      name: `demo_${documentType}.pdf`,
      size: 1024 * 500, // 500KB
      type: 'application/pdf',
      url: `https://demo.pyramyd.com/documents/demo_${documentType}.pdf`,
      uploadDate: new Date().toISOString()
    };

    setFormData(prev => ({
      ...prev,
      documents: {
        ...prev.documents,
        [documentType]: mockFile
      }
    }));

    setDocumentStatus(prev => ({
      ...prev,
      [documentType]: 'uploaded'
    }));

    setUploading(false);
  };

  const handleSubmitKYC = async () => {
    setUploading(true);
    
    // Simulate KYC processing
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Mock instant approval for demo
    const kycResult = {
      status: 'approved',
      submitted_at: new Date().toISOString(),
      approved_at: new Date().toISOString(),
      can_trade: true,
      requires_kyc: false,
      business_verified: true,
      documents_verified: true,
      approval_message: 'Congratulations! Your KYC has been approved instantly for demo purposes.'
    };

    // Update demo KYC status
    localStorage.setItem('pyramyd_demo_kyc_status', JSON.stringify(kycResult));
    
    setUploading(false);
    setStep(4); // Go to success step
  };

  const renderBusinessInfoStep = () => (
    <div className="space-y-4">
      <div className="text-center mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Business Information</h3>
        <p className="text-sm text-gray-600">Enter your business details for KYC verification</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Business Name</label>
          <input
            type="text"
            value={formData.business_name}
            onChange={(e) => handleInputChange('business_name', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
            placeholder="Enter business name"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Registration Number</label>
          <input
            type="text"
            value={formData.registration_number}
            onChange={(e) => handleInputChange('registration_number', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
            placeholder="RC number"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">TIN Number</label>
          <input
            type="text"
            value={formData.tin_number}
            onChange={(e) => handleInputChange('tin_number', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
            placeholder="Tax identification number"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Business Type</label>
          <input
            type="text"
            value={formData.business_type}
            onChange={(e) => handleInputChange('business_type', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
            placeholder="e.g., Agricultural Trading"
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">Business Address</label>
          <textarea
            value={formData.business_address}
            onChange={(e) => handleInputChange('business_address', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
            rows="2"
            placeholder="Complete business address"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Contact Person</label>
          <input
            type="text"
            value={formData.contact_person}
            onChange={(e) => handleInputChange('contact_person', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
            placeholder="Contact person name"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Contact Phone</label>
          <input
            type="tel"
            value={formData.contact_phone}
            onChange={(e) => handleInputChange('contact_phone', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
            placeholder="+234 XXX XXX XXXX"
          />
        </div>
      </div>

      <div className="flex justify-between pt-4">
        <button
          onClick={onCancel}
          className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          onClick={() => setStep(2)}
          className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
        >
          Next: Upload Documents
        </button>
      </div>
    </div>
  );

  const renderDocumentUploadStep = () => (
    <div className="space-y-4">
      <div className="text-center mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Document Upload</h3>
        <p className="text-sm text-gray-600">Upload required business documents for verification</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {documentTypes.map((doc) => (
          <div key={doc.key} className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <span className="text-2xl">{doc.icon}</span>
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{doc.label}</h4>
                <p className="text-xs text-gray-600 mb-2">{doc.description}</p>
                
                {documentStatus[doc.key] === 'pending' && (
                  <button
                    onClick={() => handleFileUpload(doc.key)}
                    disabled={uploading}
                    className="text-sm bg-emerald-600 text-white px-3 py-1 rounded hover:bg-emerald-700 disabled:opacity-50"
                  >
                    Upload Document
                  </button>
                )}
                
                {documentStatus[doc.key] === 'uploading' && (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-sm text-emerald-600">Uploading...</span>
                  </div>
                )}
                
                {documentStatus[doc.key] === 'uploaded' && (
                  <div className="flex items-center space-x-2">
                    <span className="text-green-600">✓</span>
                    <span className="text-sm text-green-600">Uploaded successfully</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="flex justify-between pt-4">
        <button
          onClick={() => setStep(1)}
          className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Back
        </button>
        <button
          onClick={() => setStep(3)}
          disabled={Object.values(documentStatus).some(status => status !== 'uploaded')}
          className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Review & Submit
        </button>
      </div>
    </div>
  );

  const renderReviewStep = () => (
    <div className="space-y-4">
      <div className="text-center mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Review & Submit</h3>
        <p className="text-sm text-gray-600">Please review your information before submission</p>
      </div>

      <div className="bg-gray-50 rounded-lg p-4 space-y-3">
        <h4 className="font-medium text-gray-900">Business Information</h4>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div><strong>Business Name:</strong> {formData.business_name}</div>
          <div><strong>Registration:</strong> {formData.registration_number}</div>
          <div><strong>TIN Number:</strong> {formData.tin_number}</div>
          <div><strong>Business Type:</strong> {formData.business_type}</div>
          <div className="col-span-2"><strong>Address:</strong> {formData.business_address}</div>
        </div>
      </div>

      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-2">Uploaded Documents</h4>
        <div className="space-y-1">
          {documentTypes.map((doc) => (
            <div key={doc.key} className="flex items-center space-x-2 text-sm">
              <span className="text-green-600">✓</span>
              <span>{doc.label}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
        <div className="flex items-start space-x-2">
          <span className="text-yellow-600">⚡</span>
          <div className="text-sm">
            <strong className="text-yellow-800">Demo Mode:</strong>
            <p className="text-yellow-700">This is a demo submission. KYC will be approved instantly for testing purposes.</p>
          </div>
        </div>
      </div>

      <div className="flex justify-between pt-4">
        <button
          onClick={() => setStep(2)}
          className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Back
        </button>
        <button
          onClick={handleSubmitKYC}
          disabled={uploading}
          className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 flex items-center space-x-2"
        >
          {uploading && <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>}
          <span>{uploading ? 'Processing...' : 'Submit KYC'}</span>
        </button>
      </div>
    </div>
  );

  const renderSuccessStep = () => (
    <div className="text-center space-y-4">
      <div className="text-6xl">🎉</div>
      <h3 className="text-xl font-semibold text-green-600">KYC Approved!</h3>
      <p className="text-gray-600">Your business verification has been completed successfully.</p>
      
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="text-sm text-green-800">
          <strong>Demo Approval:</strong> Your KYC has been instantly approved for demonstration purposes.
          You can now access all agent features including farmer registration and product management.
        </div>
      </div>

      <div className="space-y-2 text-sm text-gray-600">
        <div>✅ Business information verified</div>
        <div>✅ Documents approved</div>
        <div>✅ Trading permissions activated</div>
        <div>✅ Agent dashboard unlocked</div>
      </div>

      <button
        onClick={onComplete}
        className="px-8 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-medium"
      >
        Continue to Agent Dashboard
      </button>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-2">
              <span className="text-emerald-600 text-xl">🔒</span>
              <h2 className="text-xl font-semibold">Demo KYC Submission</h2>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-xs bg-orange-100 text-orange-600 px-2 py-1 rounded-full font-medium">
                DEMO MODE
              </span>
              <button
                onClick={onCancel}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
          </div>

          {/* Progress Indicator */}
          <div className="flex items-center space-x-2 mb-6">
            {[1, 2, 3, 4].map((num) => (
              <div key={num} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step >= num ? 'bg-emerald-600 text-white' : 'bg-gray-200 text-gray-600'
                }`}>
                  {step > num ? '✓' : num}
                </div>
                {num < 4 && (
                  <div className={`w-8 h-0.5 ${step > num ? 'bg-emerald-600' : 'bg-gray-200'}`} />
                )}
              </div>
            ))}
          </div>

          {/* Step Content */}
          {step === 1 && renderBusinessInfoStep()}
          {step === 2 && renderDocumentUploadStep()}
          {step === 3 && renderReviewStep()}
          {step === 4 && renderSuccessStep()}
        </div>
      </div>
    </div>
  );
};

export default DemoKYCSubmission;