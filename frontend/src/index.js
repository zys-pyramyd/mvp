import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./index.css";
import App from "./App";
<<<<<<< HEAD
import * as serviceWorkerRegistration from './serviceWorkerRegistration';
import { AuthProvider } from "./context/AuthContext";
=======
import AdminLogin from "./AdminLogin";

import ErrorBoundary from "./components/ErrorBoundary";
>>>>>>> 3c08bac4cdd6f65fe0f1b7cf2bb12556ec177a49

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
<<<<<<< HEAD
    <AuthProvider>
      <App />
    </AuthProvider>
=======
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/pyadmin" element={<AdminLogin />} />
          <Route path="*" element={<App />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
>>>>>>> 3c08bac4cdd6f65fe0f1b7cf2bb12556ec177a49
  </React.StrictMode>,
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://cra.link/PWA
serviceWorkerRegistration.unregister();
