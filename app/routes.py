from flask import request, jsonify, Blueprint
from datetime import datetime, timezone
from .controller import sdn_controller

controller = sdn_controller(inventory_path='inventory/devices.yaml')
api_bp = Blueprint('api', __name__, url_prefix="/api")

@api_bp.route("/discover", methods=['POST'])
def discover_devices():
    """Discover and connect to all devices in inventory"""
    try:
        # Call controller to discover all devices
        discovery_results = controller.discover_devices()

        # Transform response to match API specification
        devices_list = []
        for hostname, result in discovery_results.items():
            device_info = controller.devices[hostname]

            device_entry = {
                'hostname': hostname,
                'ip': device_info['ip'],
                'port': device_info['port'],
                'vendor': device_info['vendor'],
                'status': 'connected' if result['success'] else 'unreachable'
            }

            if result['success']:
                device_entry['capabilities'] = len(result['capabilities'])
            else:
                # Extract error message from the controller response
                error_msg = result['message'].replace('Discovery failed: ', '')
                device_entry['error'] = error_msg

            devices_list.append(device_entry)

        # Build response
        response = {
            'status': 'success',
            'discovered': len(discovery_results),
            'devices': devices_list,
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Discovery failed: {str(e)}'
        }), 500

@api_bp.route("/<device_id>/status", methods=['GET'])
def get_device_status(device_id):
    """Get detailed status for a specific device"""
    try:
        # Call controller to get device status
        status_data = controller.get_device_status(device_id)

        # Wrap in success response
        response = {
            'status': 'success',
            **status_data
        }

        return jsonify(response), 200

    except KeyError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 404

    except ConnectionError as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to connect to device: {str(e)}'
        }), 503

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Internal error: {str(e)}'
        }), 500

@api_bp.route('/<device_id>/interface', methods=['POST'])
def configure_interface(device_id):
    """Configure an interface on a specific device"""
    try:
        # Parse request body
        data = request.get_json()

        if not data:
            raise ValueError('Request body is required')

        # Validate required fields
        required_fields = ['interface_name', 'ip_address', 'subnet_mask']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            raise ValueError(f'Missing required fields: {", ".join(missing_fields)}')

        # Call controller to configure interface
        result = controller.configure_interface(
            device_id,
            data['interface_name'],
            data['ip_address'],
            data['subnet_mask']
        )

        # Return success response
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

    except KeyError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 404

    except ConnectionError as e:
        return jsonify({
            'status': 'error',
            'message': f'Connection failed: {str(e)}'
        }), 503

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Configuration failed: {str(e)}'
        }), 500

