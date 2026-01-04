import { useState, useEffect } from "react";
import DeviceCard from "./DeviceCard";
import DevicePage from "./DevicePage";

export default function LandingPage(){

    const [devices, setDevices] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [selectedDevice, setSelectedDevice] = useState(null)

    useEffect(()=>{
        const fetchDevices = async () => {
        try{
            const response = await fetch('http://localhost:5000/api/discover', {method: 'POST'})
            if (!response.ok) { throw new Error('Failed to fetch devices') }

            const data = await response.json()
            setDevices(data)
        }
        catch (err){
            setError(err.message)
        }
        finally{
            setLoading(false)
        }
        }

        fetchDevices()
    }, [])

    const handleConfigureDevice = (device) => {
        setSelectedDevice(device)
    }

    const handleCloseModal = () => {
        setSelectedDevice(null)
    }

    if (loading) return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
            <div className="text-gray-600">Loading devices...</div>
        </div>
    )

    if (error) return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
            <div className="text-red-600">Error: {error}</div>
        </div>
    )

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-7xl mx-auto">
                <h1 className="text-3xl font-bold text-gray-900 mb-6">
                    Network Devices
                </h1>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {devices.devices.map((device) => (
                        <DeviceCard
                            key={device.hostname}
                            device={device}
                            onConfigure={handleConfigureDevice}
                        />
                    ))}
                </div>
            </div>

            {/* Device Configuration Modal */}
            {selectedDevice && (
                <DevicePage
                    device={selectedDevice}
                    onClose={handleCloseModal}
                />
            )}
        </div>
    )
}