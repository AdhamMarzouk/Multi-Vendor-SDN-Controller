export default function DeviceCard({ device, onConfigure }) {
  return (
    <article className="bg-white rounded-lg border border-gray-200 shadow-md hover:shadow-lg transition-shadow duration-200 p-4">
      {/* Header Section */}
      <div className="flex items-start justify-between mb-3">
        {/* Status & Hostname */}
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              device.status === 'connected' ? 'bg-green-500' : 'bg-red-500'
            }`}
            aria-label={`Status: ${device.status}`}
          />
          <h3 className="text-lg font-semibold text-gray-900">
            {device.hostname}
          </h3>
        </div>

        {/* Vendor Badge */}
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          {device.vendor}
        </span>
      </div>

      {/* Body Section */}
      <div className="space-y-2">
        {/* Connection Details */}
        <div className="flex items-center gap-1 text-sm">
          <span className="text-gray-600">IP:</span>
          <span className="text-gray-900 font-mono">{device.ip}:{device.port}</span>
        </div>

        {/* Capabilities or Error */}
        {device.status === 'connected' ? (
          <div className="flex items-center gap-1 text-sm">
            <span className="text-gray-600">Capabilities:</span>
            <span className="text-gray-900">{device.capabilities}</span>
          </div>
        ) : (
          <div className="text-sm text-red-600">
            {device.error || 'Device unreachable'}
          </div>
        )}
      </div>

      {/* Configure Button */}
      <div className="mt-4 pt-3 border-t border-gray-200">
        <button
          onClick={() => onConfigure(device)}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 hover:cursor-pointer font-medium text-sm transition-colors"
        >
          Configure
        </button>
      </div>
    </article>
  );
}