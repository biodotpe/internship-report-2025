import os
import json
import time
import threading
from flask import Flask, jsonify, send_file, request, make_response, Response
from flask_cors import CORS
import eventlet
from camera_pi import Camera
import picommon
import atexit
import RPi.GPIO as GPIO
import glob
from datetime import datetime
from threading import Event

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Create a dummy exit event
exit_event = Event()

# Initialize SPI for sensors and actuators
picommon.spi_init(0, 2, 30000)

# Global camera instance
camera = None

# Initialize camera with proper settings
def init_camera():
    global camera
    if camera is None:
        # Create dummy socketio for the camera
        class DummySocketIO:
            def __init__(self):
                self.handlers = {}

            def emit(self, *args, **kwargs):
                print(f"SocketIO emit: {args} {kwargs}")

            def on(self, event, handler=None):
                print(f"SocketIO registering handler for: {event}")
                if handler is not None:
                    print(f"Registering handler: {handler.__name__ if hasattr(handler, '__name__') else 'lambda'}")
                    self.handlers[event] = handler
                else:
                    print("No handler provided, returning decorator")

                def decorator(f):
                    print(f"Registering decorated handler: {f.__name__ if hasattr(f, '__name__') else 'lambda'}")
                    self.handlers[event] = f
                    return f

                return decorator        
    
            def trigger(self, event, *args, **kwargs):
                if event in self.handlers:
                    return self.handlers[event](*args, **kwargs)

        dummy_socketio = DummySocketIO()
        
        # Initialize camera with proper exit event and socketio
        camera = Camera(exit_event, dummy_socketio)
        
        # Initialize with default settings
        camera.cam_data['camera'] = 'pi'  # Set to 'pi' to enable camera
        camera.on_cam({'cmd': 'select', 'parameters': {'camera': 'pi'}})
        
        # Initial strobe update
        camera.update_strobe_data()
        
        print("Camera and strobe initialized")
    return camera

# Global camera settings
current_settings = {
    'width': 1024,
    'height': 768,
    'fps': 49,
    'exposure_mode': 'auto',  # 'auto' or 'manual'
    'exposure_time_us': None  # Only used in manual mode
}

# Update camera settings
def update_camera_settings(width=None, height=None, fps=None, exposure_mode=None, exposure_time_us=None):
    global current_settings
    
    # Update settings with provided values or use current values
    if width is not None:
        current_settings['width'] = width
    if height is not None:
        current_settings['height'] = height
    if fps is not None:
        current_settings['fps'] = fps
    if exposure_mode is not None:
        current_settings['exposure_mode'] = exposure_mode
    if exposure_time_us is not None:
        current_settings['exposure_time_us'] = exposure_time_us

    print(f"Applying camera settings - Width: {current_settings['width']}, Height: {current_settings['height']}, "
          f"FPS: {current_settings['fps']}, Exposure Mode: {current_settings['exposure_mode']}, "
          f"Exposure: {current_settings.get('exposure_time_us', 'auto')}µs")
    
    # Prepare camera settings
    cam_settings = {
        'cmd': 'init',
        'width': current_settings['width'],
        'height': current_settings['height'],
        'fps': current_settings['fps'],
        'exposure_mode': current_settings['exposure_mode']
    }
    
    # Only set exposure time if in manual mode and a value is provided
    if current_settings['exposure_mode'] == 'manual' and current_settings.get('exposure_time_us'):
        cam_settings['exposure_time_us'] = current_settings['exposure_time_us']
    
    # Apply settings
    camera.on_cam(cam_settings)
    
    return current_settings

# API Endpoints
@app.route('/api/camera/init', methods=['POST'])
def camera_init():
    try:
        init_camera()
        return jsonify({'status': 'success', 'message': 'Camera initialized'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/camera/settings', methods=['GET'])
def get_camera_settings():
    """Get current camera settings including resolution, FPS, and exposure time"""
    try:
        settings = update_camera_settings()  # This will initialize or update settings
        return jsonify({
            'status': 'success',
            'settings': {
                'width': settings['width'],
                'height': settings['height'],
                'fps': settings['fps'],
                'exposure_mode': settings['exposure_mode'],
                'exposure_time_us': settings.get('exposure_time_us')
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/camera/settings', methods=['POST'])
def update_camera_settings_endpoint():
    """Update camera settings (resolution, FPS, exposure mode, and/or exposure time)"""
    try:
        data = request.get_json()
        
        # Get new settings
        width = data.get('width')
        height = data.get('height')
        fps = data.get('fps')
        exposure_mode = data.get('exposure_mode')
        exposure_time_us = data.get('exposure_time_us')
        
        # Validate inputs
        if any(x is not None and (not isinstance(x, int) or x <= 0) for x in [width, height, fps, exposure_time_us] if x is not None):
            return jsonify({'status': 'error', 'message': 'Width, height, FPS, and exposure time must be positive integers'}), 400
        
        if exposure_mode is not None and exposure_mode not in ['auto', 'manual']:
            return jsonify({'status': 'error', 'message': 'Exposure mode must be either "auto" or "manual"'}), 400
        
        # This will update settings and apply them to the camera
        settings = update_camera_settings(
            width=width,
            height=height,
            fps=fps,
            exposure_mode=exposure_mode,
            exposure_time_us=exposure_time_us
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Camera settings updated',
            'settings': {
                'width': settings['width'],
                'height': settings['height'],
                'fps': settings['fps'],
                'exposure_mode': settings['exposure_mode'],
                'exposure_time_us': settings.get('exposure_time_us')
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/camera/capture', methods=['GET'])
def capture_image():
    try:
        init_camera()
        
        # Define the correct snapshots directory
        snapshots_dir = os.path.expanduser('/home/pi/webapp/snapshots')
        os.makedirs(snapshots_dir, exist_ok=True)
        
        # Capture a new frame
        frame = camera.get_frame()
        if frame is None:
            raise Exception("Failed to capture frame")
            
        # Generate filename with timestamp
        filename = f'snapshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
        filepath = os.path.join(snapshots_dir, filename)
        
        # Save the image to the snapshots directory
        with open(filepath, 'wb') as f:
            f.write(frame)
        
        # For all requests, return the image directly
        response = make_response(frame)
        response.headers.set('Content-Type', 'image/jpeg')
        response.headers.set('Content-Disposition', 'attachment', filename=filename)
        return response
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/camera/stream')
def stream_frames():
    def generate():
        try:
            # Initialize camera for streaming
            init_camera()
            
            while True:
                # Capture frame to memory
                frame = camera.get_frame()
                if frame is None:
                    print("Failed to get frame")
                    continue
                    
                # Yield the frame in the HTTP response
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                
                # Control frame rate
                time.sleep(1/current_settings['fps'])  # Use the actual FPS setting
        except Exception as e:
            print(f"Stream error: {e}")
        finally:
            # Clean up camera resources when stream ends
            cleanup()
    
    return Response(
        generate(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/api/camera/exposure', methods=['GET'])
def get_exposure_time():
    """Get the current camera exposure time in microseconds"""
    try:
        if camera is None:
            init_camera()
        
        # Update the strobe data to get the latest exposure time
        camera.update_strobe_data()
        
        # Get the exposure time from the camera
        exposure_us = camera.camera.shutter_speed
        #exposure_us = camera.strobe_data.get('cam_shutter_speed_us', 0)
        
        return jsonify({
            'status': 'success',
            'exposure_time_us': exposure_us
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/strobe/settings', methods=['GET', 'POST'])
def handle_strobe_settings():
    """Get or update strobe settings"""
    try:
        if camera is None:
            init_camera()
            
        if request.method == 'GET':
            # Get current strobe settings
            camera.update_strobe_data()  # Ensure we have the latest data
            return jsonify({
                'status': 'success',
                'settings': {
                    'enabled': camera.strobe_data['enable'],
                    'hold': camera.strobe_data['hold'],
                    'period_ns': camera.strobe_data['period_ns'],
                    'wait_ns': camera.strobe_data.get('wait_ns', 0),
                    'framerate': camera.strobe_data.get('framerate', 0)
                }
            })
        else:  # POST
            data = request.get_json()
            
            # Update settings if provided
            if 'enable' in data:
                camera.on_strobe({
                    'cmd': 'enable',
                    'parameters': {'on': 1 if data['enable'] else 0}
                })
                
            if 'hold' in data:
                camera.on_strobe({
                    'cmd': 'hold',
                    'parameters': {'on': 1 if data['hold'] else 0}
                })
                
            if 'period_ns' in data or 'wait_ns' in data:
                camera.on_strobe({
                    'cmd': 'timing',
                    'parameters': {
                        'period_ns': int(data.get('period_ns', camera.strobe_data['period_ns'])),
                        'wait_ns': int(data.get('wait_ns', camera.strobe_data.get('wait_ns', 0)))
                    }
                })
            
            # Get updated settings
            camera.update_strobe_data()
            return jsonify({
                'status': 'success',
                'message': 'Strobe settings updated',
                'settings': {
                    'enabled': camera.strobe_data['enable'],
                    'hold': camera.strobe_data['hold'],
                    'period_ns': camera.strobe_data['period_ns'],
                    'wait_ns': camera.strobe_data.get('wait_ns', 0),
                    'framerate': camera.strobe_data.get('framerate', 0)
                }
            })
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Cleanup function
def cleanup():
    global camera
    try:
        if camera is not None:
            # Stop any ongoing recordings
            if hasattr(camera, 'recording') and camera.recording:
                camera.stop_recording()
                
            # Close camera resources
            if hasattr(camera, 'camera') and camera.camera is not None:
                camera.camera.close()
                
            # Clean up strobe
            if hasattr(camera, 'strobe_cam') and camera.strobe_cam is not None:
                camera.strobe_cam.close()
                
            camera = None
            
    except Exception as e:
        print(f"Error during cleanup: {e}")
    finally:
        # Close SPI
        picommon.spi_close()
        exit_event.set()

# Register cleanup to run on exit
atexit.register(cleanup)

# Start the server
if __name__ == '__main__':
    try:
        # Initialize camera and flow controller on startup
        init_camera()
        
        # Start the Flask server with debug=False to prevent auto-reloader issues
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cleanup()