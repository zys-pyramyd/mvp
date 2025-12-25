import React from 'react';
import { Facebook, Twitter, Instagram, Linkedin, Mail, Phone, MapPin } from 'lucide-react';

const Footer = ({ onOpenTerms, onOpenPrivacy, onOpenAbout }) => {
    return (
        <footer className="bg-emerald-900 text-white pt-12 pb-6">
            <div className="container mx-auto px-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
                    {/* Brand Section */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-2">
                            {/* Logo Placeholder */}
                            <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center text-emerald-900 font-bold text-xl">P</div>
                            <span className="text-2xl font-bold">Pyramyd</span>
                        </div>
                        <p className="text-emerald-100 text-sm leading-relaxed">
                            Connecting rural farmers to urban markets. Experience fresh produce, fair prices, and fast delivery.
                        </p>
                        <div className="flex gap-4">
                            <a href="#" className="w-8 h-8 rounded-full bg-emerald-800 flex items-center justify-center hover:bg-emerald-700 transition">
                                <Facebook size={16} />
                            </a>
                            <a href="#" className="w-8 h-8 rounded-full bg-emerald-800 flex items-center justify-center hover:bg-emerald-700 transition">
                                <Twitter size={16} />
                            </a>
                            <a href="#" className="w-8 h-8 rounded-full bg-emerald-800 flex items-center justify-center hover:bg-emerald-700 transition">
                                <Instagram size={16} />
                            </a>
                            <a href="#" className="w-8 h-8 rounded-full bg-emerald-800 flex items-center justify-center hover:bg-emerald-700 transition">
                                <Linkedin size={16} />
                            </a>
                        </div>
                    </div>

                    {/* Quick Links */}
                    <div>
                        <h3 className="text-lg font-bold mb-4">Quick Links</h3>
                        <ul className="space-y-2 text-emerald-100 text-sm">
                            <li><button onClick={onOpenAbout} className="hover:text-white hover:underline text-left">About Us</button></li>
                            <li><button onClick={onOpenTerms} className="hover:text-white hover:underline text-left">Terms of Use</button></li>
                            <li><button onClick={onOpenPrivacy} className="hover:text-white hover:underline text-left">Privacy Policy</button></li>
                            <li><a href="#" className="hover:text-white hover:underline">Help Center</a></li>
                        </ul>
                    </div>

                    {/* Services */}
                    <div>
                        <h3 className="text-lg font-bold mb-4">Services</h3>
                        <ul className="space-y-2 text-emerald-100 text-sm">
                            <li>PyExpress Delivery</li>
                            <li>Farm Deals</li>
                            <li>Agent Network</li>
                            <li>Logistics Partners</li>
                            <li>Community Marketplace</li>
                        </ul>
                    </div>

                    {/* Contact */}
                    <div>
                        <h3 className="text-lg font-bold mb-4">Contact Us</h3>
                        <ul className="space-y-3 text-emerald-100 text-sm">
                            <li className="flex items-start gap-3">
                                <MapPin size={18} className="shrink-0 mt-0.5" />
                                <span>123 Agri-Tech Hub, Victoria Island, Lagos, Nigeria</span>
                            </li>
                            <li className="flex items-center gap-3">
                                <Phone size={18} className="shrink-0" />
                                <span>+234 800 PYRAMYD</span>
                            </li>
                            <li className="flex items-center gap-3">
                                <Mail size={18} className="shrink-0" />
                                <span>support@pyramyd.com</span>
                            </li>
                        </ul>
                    </div>
                </div>

                {/* Bottom Bar */}
                <div className="border-t border-emerald-800 pt-6 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-emerald-300">
                    <div>
                        &copy; {new Date().getFullYear()} Pyramyd. All rights reserved.
                    </div>
                    <div className="flex gap-6">
                        <button onClick={onOpenTerms} className="hover:text-white">Terms</button>
                        <button onClick={onOpenPrivacy} className="hover:text-white">Privacy</button>
                        <button onClick={onOpenAbout} className="hover:text-white">About</button>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
