import React, { useState, useEffect } from 'react';

const ChatModal = ({ isOpen, onClose, user, API_BASE_URL, initialContext }) => {
    // --- Messaging System Logic ---
    const [conversations, setConversations] = useState([]);
    const [activeConversation, setActiveConversation] = useState(null); // { user: {...}, ... }
    const [chatMessages, setChatMessages] = useState([]);
    const [messageInput, setMessageInput] = useState('');
    const [attachmentFile, setAttachmentFile] = useState(null);
    const [usernameSearch, setUsernameSearch] = useState('');
    const [foundUsers, setFoundUsers] = useState([]);

    // Poll for conversations (unread counts)
    useEffect(() => {
        if (user && isOpen) {
            fetchConversations();
            const interval = setInterval(fetchConversations, 10000); // Poll every 10s
            return () => clearInterval(interval);
        }
    }, [user, isOpen]);

    // Handle Initial Context (Deep Linking)
    useEffect(() => {
        if (isOpen && initialContext) {
            const { recipient, message } = initialContext;

            if (message) setMessageInput(message);

            if (recipient) {
                // 1. Check if conversation already exists
                const existing = conversations.find(c => c.user.username === recipient);
                if (existing) {
                    setActiveConversation(existing);
                } else {
                    // 2. If not, we need to fetch the user profile to start a new one
                    // We'll use the search endpoint for now as it's available
                    const findUser = async () => {
                        try {
                            const token = localStorage.getItem('token');
                            const res = await fetch(`${API_BASE_URL}/api/users/search?q=${recipient}`, {
                                headers: { 'Authorization': `Bearer ${token}` }
                            });
                            if (res.ok) {
                                const data = await res.json();
                                const targetUser = data.users.find(u => u.username === recipient);
                                if (targetUser) {
                                    startConversation(targetUser);
                                }
                            }
                        } catch (err) { console.error("Error finding user for context", err); }
                    };
                    findUser();
                }
            }
        }
    }, [isOpen, initialContext, conversations.length]); // Depend on conversations.length to retry if they load later

    // Poll for messages when chat is open
    useEffect(() => {
        if (activeConversation && isOpen) {
            fetchChatHistory(activeConversation.user.username);
            const interval = setInterval(() => fetchChatHistory(activeConversation.user.username), 5000);
            return () => clearInterval(interval);
        }
    }, [activeConversation, isOpen]);

    const fetchConversations = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_BASE_URL}/api/conversations`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setConversations(data.conversations);
            }
        } catch (err) { console.error("Error fetching conversations", err); }
    };

    const fetchChatHistory = async (otherUsername) => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_BASE_URL}/api/messages/${otherUsername}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setChatMessages(data.messages);

                // If unread messages exist, mark as read
                // (In a real app, do this only when window is focused)
                markAsRead(otherUsername);
            }
        } catch (err) { console.error("Error fetching chat history", err); }
    };

    const markAsRead = async (senderUsername) => {
        try {
            const token = localStorage.getItem('token');
            await fetch(`${API_BASE_URL}/api/messages/read/${senderUsername}`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            // Refresh conversations to update badge
            fetchConversations();
        } catch (err) { console.error("Error marking read", err); }
    };

    const searchUsers = async (q) => {
        if (!q.trim()) { setFoundUsers([]); return; }
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_BASE_URL}/api/users/search?q=${q}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setFoundUsers(data.users);
            }
        } catch (err) { console.error("Search error", err); }
    };

    const handleSendMessage = async () => {
        if ((!messageInput.trim() && !attachmentFile) || !activeConversation) return;

        try {
            const token = localStorage.getItem('token');
            let attachmentKeys = [];

            // 1. Upload Attachment if exists (Secure Message Bucket)
            if (attachmentFile) {
                const signRes = await fetch(`${API_BASE_URL}/api/upload/sign`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        folder: 'messages', // Private bucket
                        filename: attachmentFile.name,
                        contentType: attachmentFile.type
                    })
                });

                if (signRes.ok) {
                    const signData = await signRes.json();
                    await fetch(signData.uploadUrl, {
                        method: 'PUT',
                        headers: { 'Content-Type': attachmentFile.type },
                        body: attachmentFile
                    });
                    attachmentKeys.push(signData.key);

                    // Save metadata
                    await fetch(`${API_BASE_URL}/api/user/documents`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            type: 'message_attachment',
                            key: signData.key,
                            bucket: signData.bucket,
                            filename: attachmentFile.name
                        })
                    });
                }
            }

            // 2. Send Message
            const res = await fetch(`${API_BASE_URL}/api/messages`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    recipient_username: activeConversation.user.username,
                    content: messageInput,
                    attachments: attachmentKeys
                })
            });

            if (res.ok) {
                setMessageInput('');
                setAttachmentFile(null);
                fetchChatHistory(activeConversation.user.username); // Refresh immediately
                fetchConversations(); // Update "Last Message" in sidebar
            }

        } catch (err) {
            console.error("Error sending message", err);
            alert("Failed to send message");
        }
    };

    const startConversation = (targetUser) => {
        // Check if conversation already exists
        const existing = conversations.find(c => c.user.username === targetUser.username);
        if (existing) {
            setActiveConversation(existing);
        } else {
            // Create temporary conversation object
            setActiveConversation({
                user: targetUser,
                last_message: {},
                unread_count: 0
            });
        }
        setFoundUsers([]); // Close search results
        setUsernameSearch('');
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-[60] flex items-center justify-center p-4">
            <div className="bg-white rounded-lg w-full max-w-5xl h-[85vh] flex overflow-hidden shadow-2xl">

                {/* Sidebar (Conversations) */}
                <div className="w-1/3 border-r border-gray-200 bg-gray-50 flex flex-col">
                    <div className="p-4 border-b border-gray-200 bg-white">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="font-bold text-lg text-gray-800">Messages</h3>
                            <button onClick={onClose} className="md:hidden text-gray-500">×</button>
                        </div>
                        {/* User Search Input */}
                        <div className="relative">
                            <input
                                type="text"
                                placeholder="Search users..."
                                value={usernameSearch}
                                onChange={(e) => {
                                    setUsernameSearch(e.target.value);
                                    searchUsers(e.target.value);
                                }}
                                className="w-full px-4 py-2 border border-gray-300 rounded-full focus:ring-2 focus:ring-emerald-500 text-sm"
                            />
                            {foundUsers.length > 0 && (
                                <div className="absolute top-12 left-0 right-0 bg-white shadow-lg rounded-lg border border-gray-200 z-10 max-h-60 overflow-y-auto">
                                    {foundUsers.map(u => (
                                        <button
                                            key={u.username}
                                            onClick={() => startConversation(u)}
                                            className="w-full text-left px-4 py-3 hover:bg-emerald-50 flex items-center gap-3 border-b border-gray-100 last:border-0"
                                        >
                                            <img src={u.profile_picture} alt="" className="w-8 h-8 rounded-full bg-gray-200 object-cover" />
                                            <div>
                                                <div className="font-medium text-gray-900">{u.display_name}</div>
                                                <div className="text-xs text-gray-500">@{u.username}</div>
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto">
                        {conversations.length === 0 ? (
                            <div className="p-8 text-center text-gray-500 text-sm">No conversations yet</div>
                        ) : (
                            conversations.map(conv => (
                                <button
                                    key={conv.user.username}
                                    onClick={() => {
                                        setActiveConversation(conv);
                                        if (conv.unread_count > 0) markAsRead(conv.user.username);
                                    }}
                                    className={`w-full text-left px-4 py-4 flex items-center gap-3 border-b border-gray-100 hover:bg-white transition-colors ${activeConversation?.user?.username === conv.user.username ? 'bg-white border-l-4 border-l-emerald-500 shadow-sm' : ''
                                        }`}
                                >
                                    <img src={conv.user.profile_picture} alt="" className="w-10 h-10 rounded-full bg-gray-200 object-cover" />
                                    <div className="flex-1 min-w-0">
                                        <div className="flex justify-between items-baseline mb-1">
                                            <div className="font-semibold text-gray-900 truncate">{conv.user.first_name} {conv.user.last_name}</div>
                                            <div className="text-xs text-gray-400">{new Date(conv.last_message.created_at).toLocaleDateString()}</div>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <div className="text-sm text-gray-500 truncate max-w-[140px]">
                                                {conv.last_message.is_own ? 'You: ' : ''}{conv.last_message.content || '📎 Attachment'}
                                            </div>
                                            {conv.unread_count > 0 && (
                                                <span className="bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full min-w-[20px] text-center">
                                                    {conv.unread_count}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </button>
                            ))
                        )}
                    </div>
                </div>

                {/* Chat Window */}
                <div className="flex-1 flex flex-col bg-white">
                    {activeConversation ? (
                        <>
                            {/* Header */}
                            <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-white">
                                <div className="flex items-center gap-3">
                                    <img src={activeConversation.user.profile_picture} alt="" className="w-10 h-10 rounded-full bg-gray-200 object-cover" />
                                    <div>
                                        <h3 className="font-bold text-gray-900">{activeConversation.user.first_name} {activeConversation.user.last_name}</h3>
                                        <div className="text-xs text-emerald-600">@{activeConversation.user.username}</div>
                                    </div>
                                </div>
                                <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">×</button>
                            </div>

                            {/* Messages Area */}
                            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                                {chatMessages.map((msg, idx) => {
                                    const isOwn = msg.sender_id === user.id;
                                    return (
                                        <div key={msg.id || idx} className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}>
                                            <div className={`max-w-[70%] rounded-2xl p-4 ${isOwn ? 'bg-emerald-600 text-white rounded-br-none' : 'bg-white text-gray-800 shadow-sm rounded-bl-none border border-gray-100'
                                                }`}>
                                                {msg.attachments && msg.attachments.length > 0 && (
                                                    <div className="mb-2 space-y-2">
                                                        {msg.attachment_urls && msg.attachment_urls.map((url, i) => (
                                                            url ? (
                                                                <a key={i} href={url} target="_blank" rel="noopener noreferrer" className="block">
                                                                    <img src={url} alt="Attachment" className="max-w-full h-auto rounded-lg border border-white/20" />
                                                                </a>
                                                            ) : <div key={i} className="text-xs italic opacity-70">Attachment unavailable</div>
                                                        ))}
                                                    </div>
                                                )}
                                                {msg.content && <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>}
                                                <div className={`text-[10px] mt-1 flex items-center justify-end gap-1 ${isOwn ? 'text-emerald-100' : 'text-gray-400'}`}>
                                                    {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                    {isOwn && (
                                                        <span>{msg.is_read ? ' • Seen' : ' • Sent'}</span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>

                            {/* Input Area */}
                            <div className="p-4 border-t border-gray-200 bg-white">
                                {attachmentFile && (
                                    <div className="flex items-center gap-2 mb-2 p-2 bg-emerald-50 rounded-lg text-xs text-emerald-700 w-fit">
                                        <span>📎 {attachmentFile.name} ({(attachmentFile.size / 1024).toFixed(1)} KB)</span>
                                        <button onClick={() => setAttachmentFile(null)} className="hover:text-red-500">×</button>
                                    </div>
                                )}
                                <div className="flex items-end gap-3">
                                    <label className="cursor-pointer text-gray-400 hover:text-emerald-600 p-2">
                                        <input
                                            type="file"
                                            className="hidden"
                                            onChange={(e) => e.target.files[0] && setAttachmentFile(e.target.files[0])}
                                        />
                                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" /></svg>
                                    </label>
                                    <textarea
                                        className="flex-1 bg-gray-100 border-0 rounded-2xl px-4 py-3 focus:ring-2 focus:ring-emerald-500 resize-none max-h-32 text-sm"
                                        placeholder="Type a message..."
                                        rows="1"
                                        value={messageInput}
                                        onChange={(e) => setMessageInput(e.target.value)}
                                        onKeyDown={(e) => {
                                            if (e.key === 'Enter' && !e.shiftKey) {
                                                e.preventDefault();
                                                handleSendMessage();
                                            }
                                        }}
                                    />
                                    <button
                                        onClick={handleSendMessage}
                                        disabled={!messageInput.trim() && !attachmentFile}
                                        className="bg-emerald-600 text-white p-3 rounded-full hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                    >
                                        <svg className="w-5 h-5 translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
                                    </button>
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="flex-1 flex flex-col items-center justify-center text-gray-400 bg-gray-50">
                            <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mb-4">
                                <span className="text-3xl">💬</span>
                            </div>
                            <p className="text-lg font-medium">Select a conversation</p>
                            <p className="text-sm">or search for a user to start chatting</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ChatModal;
