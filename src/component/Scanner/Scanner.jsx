import axios from "axios";
import React, { useState } from "react";
import QrScanner from "react-qr-scanner";
import styles from "../Scanner/Scanner.module.scss";

export default function Scaner() {
    const [scannedId, setScannedId] = useState("");
    const [message, setMessage] = useState("");
    const [isScanning, setIsScanning] = useState(false);

    const handleScan = async (data) => {
        if (data) {
            setScannedId(data.text);
            setIsScanning(false); // Stop scanning after a successful scan
            try {
                const response = await axios.post("http://127.0.0.1:5000/update_status", {
                    id: data.text,
                });
                setMessage(response.data.message);
            } catch (error) {
                console.error("Error updating status:", error);
                setMessage("An error occurred. Please try again.");
            }
        }
    };

    const handleError = (err) => {
        console.error("QR Scanner Error:", err);
        setMessage("Error accessing the camera. Please check permissions.");
    };

    const toggleScanner = () => {
        setIsScanning(!isScanning);
        if (!isScanning) {
            setScannedId("");
            setMessage("");
        }
    };

    return (
        <div className={styles["scaner-container"]}>
            <div className={styles.container}>
                <h1>QR Code Scanner</h1>
                <button onClick={toggleScanner} className={styles.toggleButton}>
                    {isScanning ? "Stop Scanning" : "Start Scanning"}
                </button>
                {isScanning && (
                    <div className={styles.scannerContainer}>
                        <QrScanner
                            delay={300}
                            className={styles.scanner}
                            onError={handleError}
                            onScan={handleScan}
                        />
                    </div>
                )}
                <p>Scanned QR ID: {scannedId || "No QR code scanned yet."}</p>
                {message && <p className={styles.message}>{message}</p>}
            </div>
        </div>
    );
}