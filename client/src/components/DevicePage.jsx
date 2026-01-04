import { useState, useEffect, useRef } from "react";

// Helper Components
function Spinner({ size = "small" }) {
  const sizeClasses = {
    small: "w-4 h-4",
    medium: "w-6 h-6",
    large: "w-8 h-8"
  };

  return (
    <svg
      className={`animate-spin ${sizeClasses[size]} text-blue-600`}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}

function LoadingState() {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="text-center">
        <Spinner size="large" />
        <p className="text-gray-600 mt-4">Loading device information...</p>
      </div>
    </div>
  );
}

function ErrorState({ error }) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6">
      <div className="flex items-center gap-2 text-red-800 mb-2">
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
        </svg>
        <h3 className="font-semibold">Error Loading Device</h3>
      </div>
      <p className="text-red-700 text-sm">{error}</p>
    </div>
  );
}

function InfoField({ label, value, mono, span2 }) {
  return (
    <div className={span2 ? "md:col-span-2" : ""}>
      <span className="block text-sm text-gray-600">{label}</span>
      <span className={`block text-sm font-medium text-gray-900 mt-1 ${mono ? 'font-mono' : ''}`}>
        {value}
      </span>
    </div>
  );
}

function DeviceInfoSection({ deviceInfo }) {
  return (
    <div className="bg-gray-50 rounded-lg p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
        Device Information
        <span className={`w-2 h-2 rounded-full ${
          deviceInfo.connection_success ? 'bg-green-500' : 'bg-red-500'
        }`} />
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-3">
        <InfoField label="Hostname" value={deviceInfo.hostname} />
        <InfoField label="Status" value={deviceInfo.status} />
        <InfoField
          label="Vendor"
          value={
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {deviceInfo.device_info.vendor}
            </span>
          }
        />
        <InfoField
          label="Connection"
          value={deviceInfo.connection_success ? 'Successful' : 'Failed'}
        />
        <InfoField
          label="Description"
          value={deviceInfo.device_info.description}
          span2
        />
        <InfoField label="IP Address" value={deviceInfo.device_info.ip} mono />
        <InfoField label="Port" value={deviceInfo.device_info.port} />
        <InfoField label="Username" value={deviceInfo.device_info.username} mono />
        <InfoField label="Password" value={deviceInfo.device_info.password} mono />
      </div>
    </div>
  );
}

function InterfaceCard({ iface, onEdit }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex justify-between items-start mb-3">
        <div>
          <h4 className="font-semibold text-gray-900">{iface.name}</h4>
          <span className="text-sm text-gray-600">{iface.type}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
            iface.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
          }`}>
            {iface.enabled ? 'Enabled' : 'Disabled'}
          </span>
          <button
            onClick={onEdit}
            className="text-blue-600 hover:text-blue-800 hover:cursor-pointer text-sm font-medium transition-colors"
          >
            Edit
          </button>
        </div>
      </div>

      <div className="space-y-1 text-sm">
        <div>
          <span className="text-gray-600">IP Address: </span>
          <span className="font-mono text-gray-900">{iface.ip}</span>
        </div>
        <div>
          <span className="text-gray-600">Netmask: </span>
          <span className="font-mono text-gray-900">{iface.netmask}</span>
        </div>
      </div>
    </div>
  );
}

function InterfaceEditCard({ iface, errors, onChange, onSave, onCancel, isSaving }) {
  return (
    <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-4">
      <div className="mb-3">
        <h4 className="font-semibold text-gray-900">{iface.name}</h4>
        <span className="text-sm text-gray-600">{iface.type}</span>
      </div>

      <div className="space-y-3">
        {/* IP Address Field */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            IP Address
          </label>
          <input
            type="text"
            value={iface.ip}
            onChange={(e) => onChange('ip', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
            placeholder="192.168.1.1"
          />
          {errors.ip && <p className="text-red-600 text-xs mt-1">{errors.ip}</p>}
        </div>

        {/* Netmask Field */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Netmask
          </label>
          <input
            type="text"
            value={iface.netmask}
            onChange={(e) => onChange('netmask', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
            placeholder="255.255.255.0"
          />
          {errors.netmask && <p className="text-red-600 text-xs mt-1">{errors.netmask}</p>}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2 mt-4">
        <button
          onClick={onSave}
          disabled={isSaving}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 hover:cursor-pointer font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
        >
          {isSaving && <Spinner size="small" />}
          {isSaving ? 'Saving...' : 'Save Changes'}
        </button>
        <button
          onClick={onCancel}
          disabled={isSaving}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 hover:cursor-pointer font-medium text-sm disabled:opacity-50 transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}

// Validation Functions
const validateIP = (ip) => {
  const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/;
  if (!ip) return "IP address is required";
  if (!ipRegex.test(ip)) return "Invalid IP format (e.g., 192.168.1.1)";

  const parts = ip.split('.');
  for (let part of parts) {
    const num = parseInt(part);
    if (num < 0 || num > 255) return "IP octets must be between 0-255";
  }
  return null;
};

const validateNetmask = (netmask) => {
  const validMasks = [
    "255.0.0.0", "255.255.0.0", "255.255.255.0",
    "255.255.255.128", "255.255.255.192", "255.255.255.224",
    "255.255.255.240", "255.255.255.248", "255.255.255.252",
    "255.255.255.254"
  ];

  if (!netmask) return "Netmask is required";
  if (!validMasks.includes(netmask)) {
    return "Invalid netmask (e.g., 255.255.255.0)";
  }
  return null;
};

const validateInterface = (iface) => {
  const errors = {};

  const ipError = validateIP(iface.ip);
  const netmaskError = validateNetmask(iface.netmask);

  if (ipError) errors.ip = ipError;
  if (netmaskError) errors.netmask = netmaskError;

  return errors;
};

// Main Component
export default function DevicePage({ device, onClose }) {
  const [deviceInfo, setDeviceInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingInterfaceIndex, setEditingInterfaceIndex] = useState(null);
  const [editedInterface, setEditedInterface] = useState(null);
  const [validationErrors, setValidationErrors] = useState({});
  const [isSaving, setIsSaving] = useState(false);
  const modalRef = useRef(null);

  // ESC key handler
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  // Body scroll lock
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  // Fetch device info
  useEffect(() => {
    const fetchDeviceInfo = async () => {
      try {
        const response = await fetch(
          `http://localhost:5000/api/${device.hostname}/status`,
          { method: 'GET' }
        );
        if (!response.ok) throw new Error('Failed to fetch device info');
        const data = await response.json();
        setDeviceInfo(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchDeviceInfo();
  }, [device.hostname]);

  // Interface editing handlers
  const handleEditInterface = (index) => {
    setEditingInterfaceIndex(index);
    setEditedInterface({...deviceInfo.running_config.interfaces[index]});
    setValidationErrors({});
  };

  const handleCancelEdit = () => {
    setEditingInterfaceIndex(null);
    setEditedInterface(null);
    setValidationErrors({});
  };

  const handleFieldChange = (field, value) => {
    setEditedInterface(prev => ({ ...prev, [field]: value }));
    setValidationErrors(prev => ({ ...prev, [field]: null }));
  };

  const handleSaveInterface = async () => {
    // Validate
    const errors = validateInterface(editedInterface);

    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      return;
    }

    try {
      setIsSaving(true);

      const response = await fetch(
        `http://localhost:5000/api/${device.hostname}/interface`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            interface_name: editedInterface.name,
            ip_address: editedInterface.ip,
            subnet_mask: editedInterface.netmask,
          })
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to update interface');
      }

      // Update local state
      setDeviceInfo(prev => ({
        ...prev,
        running_config: {
          ...prev.running_config,
          interfaces: prev.running_config.interfaces.map((iface, idx) =>
            idx === editingInterfaceIndex ? editedInterface : iface
          )
        }
      }));

      // Exit edit mode
      setEditingInterfaceIndex(null);
      setEditedInterface(null);
      setValidationErrors({});

    } catch (err) {
      setError(err.message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-40"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal Container */}
      <div className="fixed inset-0 z-50 overflow-y-auto" onClick={onClose}>
        <div className="flex min-h-full items-center justify-center p-4">
          <div
            ref={modalRef}
            className="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
          >
            {/* Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center z-10">
              <h2 id="modal-title" className="text-2xl font-bold text-gray-900">
                {device.hostname} Configuration
              </h2>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
                aria-label="Close modal"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Content Area */}
            <div className="overflow-y-auto max-h-[calc(90vh-5rem)] px-6 py-6">
              {loading && <LoadingState />}
              {error && <ErrorState error={error} />}
              {deviceInfo && (
                <>
                  <DeviceInfoSection deviceInfo={deviceInfo} />

                  {/* Interfaces Section */}
                  <div>
                    <div className="mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">Network Interfaces</h3>
                      <p className="text-sm text-gray-600 mt-1">
                        Configure IP addressing and interface status
                      </p>
                    </div>

                    <div className="space-y-4">
                      {deviceInfo.running_config.interfaces.map((iface, index) => (
                        editingInterfaceIndex === index ? (
                          <InterfaceEditCard
                            key={iface.name}
                            iface={editedInterface}
                            errors={validationErrors}
                            onChange={handleFieldChange}
                            onSave={handleSaveInterface}
                            onCancel={handleCancelEdit}
                            isSaving={isSaving}
                          />
                        ) : (
                          <InterfaceCard
                            key={iface.name}
                            iface={iface}
                            onEdit={() => handleEditInterface(index)}
                          />
                        )
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
