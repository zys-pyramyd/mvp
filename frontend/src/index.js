import React, { lazy, Suspense } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./index.css";
import App from "./App";
import ProductPage from "./components/product/ProductPage";
import * as serviceWorkerRegistration from './serviceWorkerRegistration';
import { AuthProvider } from "./context/AuthContext";
import AdminLogin from "./AdminLogin";
import ErrorBoundary from "./components/ErrorBoundary";
import CreateAdmin from "./components/admin/CreateAdmin";

// Lazy-load AdminDashboard — it's ~68 KB and only needed by admins
const AdminDashboard = lazy(() => import('./components/admin/AdminDashboard'));

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/pyadmin" element={<AdminLogin />} />
            <Route path="/admin-dashboard" element={
              <Suspense fallback={<div className="flex items-center justify-center h-screen bg-gray-100"><div className="text-gray-500 text-lg">Loading Admin Panel...</div></div>}>
                <AdminDashboard />
              </Suspense>
            } />
            <Route path="/product/:id" element={<ProductPage />} />
            <Route path="/setup/create-admin" element={<CreateAdmin />} />
            <Route path="*" element={<App />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  </React.StrictMode>,
);

// Service Worker enabled — caches static assets for faster repeat visits (PWA)
serviceWorkerRegistration.register();
