import React, { useState, useRef } from 'react';
import { Camera, Upload, Check, FileText } from 'lucide-react';
import TermsOfUseModal from '../Legal/TermsOfUseModal';
import PrivacyPolicyModal from '../Legal/PrivacyPolicyModal';

const VerificationStep = ({ formData, updateFormData, onRegister, onBack, role, requiredDocs, docLabels }) => {
    const [uploading, setUploading] = useState({}); // { docKey: boolean }
    const [previewUrls, setPreviewUrls] = useState({}); // { docKey: url } (blob urls)
    const [fileTypes, setFileTypes] = useState({}); // { docKey: 'image' | 'pdf' }
    const [activeCamera, setActiveCamera] = useState(null); // docKey of active camera
    const [cameraError, setCameraError] = useState({}); // { docKey: boolean }
    const [showTerms, setShowTerms] = useState(false);
    const [showPrivacy, setShowPrivacy] = useState(false);

    const fileInputRef = useRef({});
    const videoRef = useRef(null);
    const streamRef = useRef(null);

    // Stop camera stream
    const stopCamera = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
        setActiveCamera(null);
    };

    // Start live camera
    const startCamera = async (key) => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: "user", width: { ideal: 640 }, height: { ideal: 640 } }
            });
            streamRef.current = stream;
            setActiveCamera(key);
            setCameraError(prev => ({ ...prev, [key]: false }));
        } catch (err) {
            console.error("Camera access denied:", err);
            setCameraError(prev => ({ ...prev, [key]: true }));
            alert("Could not access camera. Please allow camera permissions or use upload fallback.");
        }
    };

    // Attach stream to video element when active
    React.useEffect(() => {
        if (activeCamera && videoRef.current && streamRef.current) {
            videoRef.current.srcObject = streamRef.current;
        }
        return () => {
            // Cleanup on unmount only if we are destroying the component
            // We handle explicit stop in stopCamera
        };
    }, [activeCamera]);

    // Handle photo capture
    const takePhoto = (key) => {
        if (!videoRef.current) return;

        const canvas = document.createElement('canvas');
        canvas.width = videoRef.current.videoWidth;
        canvas.height = videoRef.current.videoHeight;
        const ctx = canvas.getContext('2d');

        ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

        canvas.toBlob(blob => {
            if (!blob) return;

            // Create a file from blob
            const file = new File([blob], "selfie.jpg", { type: "image/jpeg" });

            // Generate preview
            const objectUrl = URL.createObjectURL(blob);
            setPreviewUrls(prev => ({ ...prev, [key]: objectUrl }));
            setFileTypes(prev => ({ ...prev, [key]: 'image' }));

            // Stop camera
            stopCamera();

            // Trigger upload logic
            handleFileUpload(file, key);
        }, 'image/jpeg', 0.8);
    };

    const handleFileUpload = async (file, docKey) => {
        setUploading(prev => ({ ...prev, [docKey]: true }));
        try {
            // 1. Get Presigned URL
            const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/upload/sign-public`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    folder: 'user-registration',
                    filename: file.name,
                    contentType: file.type
                })
            });

            if (!res.ok) throw new Error('Upload init failed');
            const data = await res.json();

            // 2. Upload to R2
            const uploadRes = await fetch(data.uploadUrl, {
                method: 'PUT',
                body: file,
                headers: { 'Content-Type': file.type }
            });

            if (!uploadRes.ok) throw new Error('Upload to storage failed');

            // 3. Update Form
            const finalUrl = data.publicUrl || data.key;
            const currentDocs = formData.documents || {};
            updateFormData({
                documents: { ...currentDocs, [docKey]: finalUrl },
                profile_picture: docKey === 'headshot' ? finalUrl : formData.profile_picture
            });

        } catch (err) {
            console.error("Upload error:", err);
            alert("Upload failed. Please try again.");
        } finally {
            setUploading(prev => ({ ...prev, [docKey]: false }));
        }
    };

    const handleFileSelect = (e, docKey) => {
        const file = e.target.files[0];
        if (!file) return;

        const isPdf = file.type === 'application/pdf';
        setFileTypes(prev => ({ ...prev, [docKey]: isPdf ? 'pdf' : 'image' }));

        const objectUrl = URL.createObjectURL(file);
        setPreviewUrls(prev => ({ ...prev, [docKey]: objectUrl }));
        handleFileUpload(file, docKey);
    };

    const isComplete = requiredDocs.every(key => formData.documents && formData.documents[key]);

    // Cleanup on unmount
    React.useEffect(() => {
        return () => stopCamera();
    }, []);

    // Helper to Determine Preview Type for Existing Data
    const getPreviewType = (key) => {
        // 1. Check local state (fresh upload)
        if (fileTypes[key]) return fileTypes[key];

        // 2. Check existing URL extension
        const url = formData.documents?.[key] || '';
        if (url.toLowerCase().endsWith('.pdf')) return 'pdf';

        return 'image'; // Default to image
    };

    return (
        <div className="space-y-6">
            <h3 className="text-lg font-bold text-center">Identity Verification</h3>
            <p className="text-sm text-gray-500 text-center">
                Please provide the required documents (JPG, PNG, PDF accepted).
            </p>

            <div className="space-y-4">
                {requiredDocs.map(key => {
                    const isHeadshot = key === 'headshot';
                    const hasPreview = previewUrls[key] || formData.documents?.[key];
                    const isActive = activeCamera === key;
                    const previewType = getPreviewType(key);

                    return (
                        <div key={key} className="border rounded-lg p-4 bg-gray-50">
                            <div className="flex justify-between items-center mb-2">
                                <label className="font-medium text-gray-700">
                                    {docLabels[key] || key} {isHeadshot && <span className="text-red-500 text-xs">(Camera Only)</span>}
                                </label>
                                {formData.documents?.[key] && <Check className="text-emerald-500" size={20} />}
                            </div>

                            {/* Camera Area */}
                            {isActive ? (
                                <div className="relative h-64 w-full bg-black rounded-lg overflow-hidden mb-2">
                                    <video
                                        ref={videoRef}
                                        autoPlay
                                        playsInline
                                        className="w-full h-full object-cover transform scale-x-[-1]" // Mirror effect
                                    />
                                    <div className="absolute bottom-4 left-0 right-0 flex justify-center space-x-4">
                                        <button
                                            onClick={() => takePhoto(key)}
                                            className="bg-white rounded-full p-3 shadow-lg hover:bg-gray-100"
                                        >
                                            <div className="w-8 h-8 rounded-full border-2 border-black"></div>
                                        </button>
                                        <button
                                            onClick={stopCamera}
                                            className="bg-gray-800 text-white px-4 py-2 rounded-full text-sm opacity-80"
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                </div>
                            ) : hasPreview ? (
                                <div className="relative h-48 w-full bg-gray-200 rounded-lg overflow-hidden mb-2 group flex items-center justify-center">
                                    {previewType === 'pdf' ? (
                                        <div className="flex flex-col items-center text-gray-600">
                                            <FileText size={48} className="mb-2 text-red-500" />
                                            <span className="text-sm font-medium">PDF Document Uploaded</span>
                                            <span className="text-xs text-gray-400 mt-1">Preview not available</span>
                                        </div>
                                    ) : (
                                        <img
                                            src={previewUrls[key] || formData.documents?.[key]}
                                            alt="Preview"
                                            className="w-full h-full object-cover"
                                        />
                                    )}

                                    {/* Overlay to Retake */}
                                    <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all flex items-center justify-center">
                                        <button
                                            onClick={() => isHeadshot ? startCamera(key) : fileInputRef.current[key].click()}
                                            className="opacity-0 group-hover:opacity-100 bg-white text-gray-900 px-4 py-2 rounded-lg font-medium transform translate-y-2 group-hover:translate-y-0 transition-all"
                                        >
                                            Retake {isHeadshot ? 'Photo' : 'Upload'}
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                <div onClick={() => {
                                    if (isHeadshot && !cameraError[key]) startCamera(key);
                                    else fileInputRef.current[key].click();
                                }}
                                    className="h-32 w-full border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center text-gray-400 cursor-pointer hover:bg-gray-100"
                                >
                                    {isHeadshot ? <Camera size={32} /> : <Upload size={32} />}
                                    <span className="text-sm mt-2 font-medium">
                                        {isHeadshot ? 'Open Camera' : 'Click to Upload'}
                                    </span>
                                    {!isHeadshot && (
                                        <span className="text-xs text-gray-400 mt-1">JPG, PNG, PDF</span>
                                    )}
                                    {isHeadshot && (
                                        <span className="text-xs text-gray-400 mt-1">Selfie Required</span>
                                    )}
                                </div>
                            )}

                            {/* Hidden Input for Fallback/Standard Upload */}
                            <input
                                ref={el => fileInputRef.current[key] = el}
                                type="file"
                                accept="image/png, image/jpeg, application/pdf"
                                className="hidden"
                                onChange={(e) => handleFileSelect(e, key)}
                            />

                            {/* Upload Status */}
                            {uploading[key] && (
                                <div className="mt-2 text-center text-sm text-blue-600 animate-pulse">
                                    Uploading secure document...
                                </div>
                            )}

                            {/* Fallback Link for Camera */}
                            {isHeadshot && !isActive && !hasPreview && (
                                <div className="text-center mt-2">
                                    <button
                                        type="button"
                                        onClick={() => fileInputRef.current[key].click()}
                                        className="text-xs text-gray-400 underline hover:text-gray-600"
                                    >
                                        Camera not working? Upload instead
                                    </button>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Terms and Conditions Checkbox */}
            <div className="mt-6 bg-gray-50 border border-gray-200 rounded-lg p-4">
                <label className="flex items-start space-x-3 cursor-pointer">
                    <input
                        type="checkbox"
                        checked={formData.agreedToTerms || false}
                        onChange={(e) => updateFormData({ agreedToTerms: e.target.checked })}
                        className="mt-1 h-4 w-4 text-emerald-600 border-gray-300 rounded focus:ring-emerald-500"
                    />
                    <div className="text-xs text-gray-600 leading-relaxed">
                        <span className="font-medium text-gray-800">
                            I have read and agree to the <button type="button" onClick={() => setShowTerms(true)} className="text-emerald-600 hover:text-emerald-700 underline">Pyramyd Terms of Use</button> and <button type="button" onClick={() => setShowPrivacy(true)} className="text-emerald-600 hover:text-emerald-700 underline">Privacy Policy</button>. By clicking submit, I authorize the verification of my identity and agree to the <button type="button" onClick={() => setShowTerms(true)} className="text-emerald-600 hover:text-emerald-700 underline">delivery validation guidelines</button>.
                        </span>
                    </div>
                </label>
            </div>

            <div className="flex justify-between mt-6">
                {onBack && (
                    <button onClick={onBack} className="text-gray-500 hover:text-gray-700 px-4 py-3">
                        Back
                    </button>
                )}
                <button
                    onClick={() => onRegister(formData)}
                    disabled={!isComplete || !formData.agreedToTerms}
                    className={`bg-emerald-600 text-white py-3 px-4 rounded-lg hover:bg-emerald-700 transition-colors font-medium flex-1 ml-4 disabled:bg-gray-300 disabled:cursor-not-allowed ${!onBack ? 'w-full' : ''}`}
                >
                    Complete Registration
                </button>
                {showTerms && <TermsOfUseModal onClose={() => setShowTerms(false)} zIndex={60} />}
                {showPrivacy && <PrivacyPolicyModal onClose={() => setShowPrivacy(false)} zIndex={60} />}
            </div>
            );
};

            export default VerificationStep;
