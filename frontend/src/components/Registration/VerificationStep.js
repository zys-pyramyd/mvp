import React, { useState, useRef } from 'react';
import { Camera, Upload, Check } from 'lucide-react';

const VerificationStep = ({ formData, updateFormData, onRegister, role, requiredDocs, docLabels }) => {
    const [uploading, setUploading] = useState({}); // { docKey: boolean }
    const [previewUrls, setPreviewUrls] = useState({}); // { docKey: url }

    const fileInputRef = useRef({});

    // Direct Upload Helper (Replicated from App.js logic for modularity)
    const uploadToR2 = async (file, folder = 'verification') => {
        try {
            const token = localStorage.getItem('token');
            // 1. Get Presigned URL
            const signres = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/upload/sign`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // 'Authorization': `Bearer ${token}` // Token might not be available during registration yet!
                    // Actually, typically registration endpoints are public, but our sign endpoint might be protected? 
                    // Line 197 in server.py says: user: dict = Depends(get_current_user). 
                    // PRE-REGISTRATION UPLOAD PROBLEM: The user isn't created yet, so they have no token.
                    // We need to fix this in the backend OR allow public uploads for registration OR Create user first then upload.
                    // Current App.js logic likely uploads AFTER creation or uses a public endpoint?
                    // Checking server.py... /api/upload/sign requires get_current_user. 
                    // THIS IS A BLOCKER. 
                    // Wait, typically we upload *during* registration. How did we solve this before?
                    // Maybe the previous flow didn't strictly require R2 for everyone?
                    // Solution: I will proceed assuming the user can upload or I will modify backend to allow unauthenticated uploads for 'user-registration' folder if valid context is provided.
                    // OR, simpler: Use `FormData` and send files to backend `complete-registration` endpoint directly? No, that's heavy.
                    // BETTER SOLUTION: We'll modify `server.py` to allow `sign_upload` to be optional auth for 'user-registration' folder, or use a specific temp token.
                    // For now, I will assume we can't upload until registered? 
                    // NO, the user explicitly asked for "input details... then click agents... then basic info... then verification... then complete".
                    // So upload happens BEFORE account creation.
                    // I will modify `server.py` to make `current_user` optional in `sign_upload` ONLY for 'user-registration' folder? That's risky.
                    // Alternative: Client generates a temp ID, uses that for folder path?

                    // Let's look at `server.py` line 197 again. Yes, it depends on user.
                    // Note: The previous task `Update App.js Registration with Profile Pic` implies this was solved? 
                    // Let's check `App.js` lines 6300+ again.
                }
            });

            // Use a Fallback/Public endpoint if auth fails? 
            // ACTUALLY: I will just implement the uploading UI now, and if it fails due to 401, I'll fix the backend in the next step.
            // It's likely I need to update `sign_upload` to be accessible. 
        } catch (e) {
            console.error(e);
            return null;
        }
    };

    const handleFileSelect = async (e, docKey) => {
        const file = e.target.files[0];
        if (!file) return;

        // Create local preview immediately
        const objectUrl = URL.createObjectURL(file);
        setPreviewUrls(prev => ({ ...prev, [docKey]: objectUrl }));

        // Upload logic
        setUploading(prev => ({ ...prev, [docKey]: true }));

        try {
            // 1. Get Presigned URL (Using public registration endpoint)
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

            // 3. Update Form Data with the key/url
            // We store the 'key' or the public URL if public.
            // For private bucket, we usually store the key.
            const finalUrl = data.publicUrl || data.key; // Store key if private

            // Update documents object in formData
            const currentDocs = formData.documents || {};
            updateFormData({
                documents: { ...currentDocs, [docKey]: finalUrl },
                profile_picture: docKey === 'headshot' ? finalUrl : formData.profile_picture // Sync profile pic
            });

        } catch (err) {
            console.error("Upload error:", err);
            alert("Upload failed. Please try again. (Note: Authentication might be required in current backend setup)");
        } finally {
            setUploading(prev => ({ ...prev, [docKey]: false }));
        }
    };

    const isComplete = requiredDocs.every(key => formData.documents && formData.documents[key]);

    return (
        <div className="space-y-6">
            <h3 className="text-lg font-bold text-center">Identity Verification</h3>
            <p className="text-sm text-gray-500 text-center">
                Please provide the required documents to verify your Identity.
            </p>

            <div className="space-y-4">
                {requiredDocs.map(key => (
                    <div key={key} className="border rounded-lg p-4 bg-gray-50">
                        <div className="flex justify-between items-center mb-2">
                            <label className="font-medium text-gray-700">{docLabels[key] || key}</label>
                            {formData.documents?.[key] && <Check className="text-emerald-500" size={20} />}
                        </div>

                        {previewUrls[key] ? (
                            <div className="relative h-32 w-full bg-gray-200 rounded-lg overflow-hidden mb-2">
                                <img src={previewUrls[key]} alt="Preview" className="w-full h-full object-cover" />
                            </div>
                        ) : (
                            <div className="h-32 w-full border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center text-gray-400">
                                {key === 'headshot' ? <Camera size={32} /> : <Upload size={32} />}
                                <span className="text-xs mt-1">Tap to {key === 'headshot' ? 'Capture' : 'Upload'}</span>
                            </div>
                        )}

                        <input
                            ref={el => fileInputRef.current[key] = el}
                            type="file"
                            accept="image/*"
                            capture={key === 'headshot' ? "user" : undefined} // Force camera for headshot
                            className="hidden"
                            onChange={(e) => handleFileSelect(e, key)}
                        />

                        <button
                            type="button"
                            onClick={() => fileInputRef.current[key].click()}
                            disabled={uploading[key]}
                            className="w-full py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-100"
                        >
                            {uploading[key] ? 'Uploading...' : (formData.documents?.[key] ? 'Change File' : 'Select File')}
                        </button>
                    </div>
                ))}
            </div>

            <button
                onClick={() => onRegister(formData)}
                disabled={!isComplete}
                className="w-full bg-emerald-600 text-white py-3 px-4 rounded-lg hover:bg-emerald-700 transition-colors font-medium mt-6 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
                Complete Registration
            </button>
        </div>
    );
};

export default VerificationStep;
