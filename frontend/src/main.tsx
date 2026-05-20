import React from "react";
import ReactDOM from "react-dom/client";
import { MapDashboard } from "./components/MapDashboard";
import "./styles/app.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <MapDashboard />
  </React.StrictMode>,
);
