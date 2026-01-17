import React, { useState, useEffect } from 'react';

const AgentDeliveryDashboard = ({ user, token }) => {
    const [deliveries, setDeliveries] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('pending'); // pending, history

    useEffect(() => {
        fetchDeliveries();
    }, []);

    const fetchDeliveries = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/agent/deliveries`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setDeliveries(data.orders || []);
            }
        } catch (error) {
            console.error("Failed to fetch deliveries", error);
        } finally {
            setLoading(false);
        }
    };

    const updateStatus = async (orderId, newStatus, notes) => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/delivery/status`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    order_id: orderId,
                    status: newStatus,
                    notes: notes
                })
            });

            if (response.ok) {
                alert('Status updated!');
                fetchDeliveries();
            } else {
                alert('Failed to update status');
            }
        } catch (error) {
            console.error(error);
            alert('Error updating status');
        }
    };

    const filteredDeliveries = deliveries.filter(order => {
        if (activeTab === 'pending') {
            return !['delivered', 'cancelled'].includes(order.delivery_status);
        }
        return ['delivered', 'cancelled'].includes(order.delivery_status);
    });

    if (loading) return <div className="p-8 text-center">Loading deliveries...</div>;

    return (
        <div className="max-w-6xl mx-auto p-4 md:p-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-800">📦 Delivery Management</h1>
                <div className="bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full text-sm font-medium">
                    Agent: {user.username}
                </div>
            </div>

            {/* Tabs */}
            <div className="flex border-b mb-6">
                <button
                    className={`px-6 py-3 font-medium transition ${activeTab === 'pending' ? 'border-b-2 border-emerald-600 text-emerald-700' : 'text-gray-500 hover:text-gray-700'}`}
                    onClick={() => setActiveTab('pending')}
                >
                    Active Deliveries ({deliveries.filter(d => !['delivered', 'cancelled'].includes(d.delivery_status)).length})
                </button>
                <button
                    className={`px-6 py-3 font-medium transition ${activeTab === 'history' ? 'border-b-2 border-emerald-600 text-emerald-700' : 'text-gray-500 hover:text-gray-700'}`}
                    onClick={() => setActiveTab('history')}
                >
                    History
                </button>
            </div>

            <div className="grid gap-4">
                {filteredDeliveries.length === 0 ? (
                    <div className="text-center py-12 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                        <p className="text-gray-500">No deliveries found in this category.</p>
                    </div>
                ) : (
                    filteredDeliveries.map(order => (
                        <DeliveryCard key={order.order_id} order={order} onUpdate={updateStatus} />
                    ))
                )}
            </div>
        </div>
    );
};

const DeliveryCard = ({ order, onUpdate }) => {
    const [notes, setNotes] = useState(order.delivery_notes || '');
    const [isEditing, setIsEditing] = useState(false);

    const handleStatusChange = (newStatus) => {
        if (window.confirm(`Update status to ${newStatus}?`)) {
            onUpdate(order.order_id, newStatus, notes);
            setIsEditing(false);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'pending': return 'bg-yellow-100 text-yellow-800';
            case 'ready_for_pickup': return 'bg-blue-100 text-blue-800';
            case 'out_for_delivery': return 'bg-purple-100 text-purple-800';
            case 'delivered': return 'bg-green-100 text-green-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    return (
        <div className="bg-white border rounded-lg shadow-sm p-4 md:p-6 transition hover:shadow-md">
            <div className="flex justify-between items-start mb-4">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono text-gray-500 text-sm">#{order.order_id}</span>
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${getStatusColor(order.delivery_status || 'pending')}`}>
                            {(order.delivery_status || 'pending').replace(/_/g, ' ').toUpperCase()}
                        </span>
                    </div>
                    <h3 className="font-bold text-lg text-gray-900">
                        {order.product_details.name} <span className="text-gray-500 font-normal">x{order.quantity}</span>
                    </h3>
                    <p className="text-sm text-gray-600">
                        Sold by: <span className="font-medium text-gray-900">{order.seller_username}</span>
                    </p>
                </div>
                <div className="text-right">
                    <div className="text-xs text-gray-500 mb-1">Date</div>
                    <div className="font-medium text-gray-700">{new Date(order.created_at).toLocaleDateString()}</div>
                </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-4">
                {/* Customer Details */}
                <div className="bg-gray-50 p-3 rounded text-sm">
                    <h4 className="font-bold text-gray-700 mb-2 border-b pb-1">Customer Details</h4>
                    <p><span className="text-gray-500">Name:</span> {order.buyer_username}</p>
                    <p><span className="text-gray-500">Method:</span> {order.delivery_method}</p>
                    {order.shipping_address && (
                        <p className="mt-1"><span className="text-gray-500 block">Address:</span> {order.shipping_address}</p>
                    )}
                    {order.dropoff_location_details && (
                        <p className="mt-1"><span className="text-gray-500 block">Drop-off:</span> {order.dropoff_location_details.name} ({order.dropoff_location_details.address})</p>
                    )}
                </div>

                {/* Actions */}
                <div className="flex flex-col justify-between">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Delivery Notes</label>
                        <textarea
                            className="w-full border rounded p-2 text-sm h-20 resize-none focus:ring-1 focus:ring-emerald-500 outline-none"
                            placeholder="Add notes about delivery..."
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                        />
                    </div>
                </div>
            </div>

            <div className="flex flex-wrap gap-2 pt-4 border-t">
                <button
                    onClick={() => handleStatusChange('ready_for_pickup')}
                    disabled={order.delivery_status === 'ready_for_pickup'}
                    className="px-3 py-1.5 bg-blue-50 text-blue-700 rounded hover:bg-blue-100 text-sm font-medium disabled:opacity-50"
                >
                    Ready for Pickup
                </button>
                <button
                    onClick={() => handleStatusChange('out_for_delivery')}
                    disabled={order.delivery_status === 'out_for_delivery'}
                    className="px-3 py-1.5 bg-purple-50 text-purple-700 rounded hover:bg-purple-100 text-sm font-medium disabled:opacity-50"
                >
                    Out for Delivery
                </button>
                <button
                    onClick={() => handleStatusChange('delivered')}
                    disabled={order.delivery_status === 'delivered'}
                    className="px-3 py-1.5 bg-green-50 text-green-700 rounded hover:bg-green-100 text-sm font-medium disabled:opacity-50"
                >
                    Mark Delivered
                </button>
                {isEditing && (
                    <button
                        onClick={() => handleStatusChange(order.delivery_status)}
                        className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 text-sm font-medium ml-auto"
                    >
                        Save Notes Only
                    </button>
                )}
            </div>
        </div>
    );
};

export default AgentDeliveryDashboard;
