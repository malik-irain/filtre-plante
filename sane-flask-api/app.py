from flask import Flask, request, Response
import datetime
import subprocess
import uwsgi

app = Flask(__name__)


def extension_to_mimetype(ext):
	if ext == "tiff":
		return "image/tiff"
	elif ext == "png":
		return "image/png"
	elif ext == "jpeg":
		return "image/jpeg"
	elif ext == "pnm":
		return "image/x-portable-anymap"
	else:
		return "application/octet-stream"


@app.route('/find')
def find():
	args = request.args
	serial_id = args.get('serial-id', type=str)
	usb_bus_serial_process = subprocess.Popen(['/bin/bash', '-c', 'for dev in /dev/bus/usb/00*/*; do echo $(basename $(dirname ${dev})):$(basename ${dev}) $(udevadm info --name=${dev}  | grep ID_SERIAL_SHORT | awk -F "=" "{ print $2 }"); done;'], stdout=subprocess.PIPE)
	usb_bus_serial_process.wait()	
	usb_bus_serial_list = usb_bus_serial_process.stdout.read().decode('utf-8').splitlines()
	if usb_bus_serial_list and serial_id:
		for usb_bus_device in usb_bus_serial_list:
			if serial_id in usb_bus_device:
				usb_device = usb_bus_device.split(' ')[0]
				return usb_device, 200
	return '', 404


'''
	Provides a `/list` access point.
	Execute `scanimage --list-devices` and parse the result into a list (where each scanner is an element).
'''
@app.route('/list')
def list_devices():
	scan_process = subprocess.Popen(['scanimage', '--list-devices'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
	scan_process.wait()
	scanners_list = list(map(lambda x : x.split("`")[1].split('\'')[0], scan_process.stdout.read().decode('utf-8').split('\n')[:-1]))

	return scanners_list


'''
	Provides a `/scan` access point that should be parametized with: 
		- scanner:    the scanner device name to scan with.
		- name:       the scanner user friendly name to scan with.
		- format:     the output image format (pnm, tiff, png or jpeg).
		- resolution: the scan resolution in dpi (200, 300, 600, 1200 or 2400).
		- mode:       the color mode of the scan (Color, Grayscale or Monochrome).
		- tlx:        the x-axis starting point of the scan in mm (between 0 and 215.9).
		- tlx:        the y-axis starting point of the scan in mm (between 0 and 297.18).
		- width:      the x-axis ending point of the scan in mm (between 0 and 215.9).
		- height:     the y-axis ending point of the scan in mm (between 0 and 297.18).

	Executes `scanimage --device={device} --format={format} --resolution={resolution} --mode={mode} -l {tlx} -t {tly} -x {width} -y {height}`
	and returns either the scan output (HTTP Error Code 200) or the stderr output (HTTP Error Code 400)
'''
@app.route('/scan')
def scan():
	# Getting all the differents args
	args = request.args
	scanner = args.get("scanner", type=str)
	name = args.get("name", type=str)

	_format = args.get("format", type=str)
	if _format not in ["pnm", "tiff", "png", "jpeg"]:
		_format = "jpeg"

	resolution = args.get("resolution", type=int)
	if resolution not in [200, 300, 600, 1200, 2400]:
		resolution = 1200

	mode = args.get("mode", type=str)
	if mode not in ["Color", "Grayscale", "Monochrome"]:
		mode = "Color"

	tlx = args.get("tlx", default=0, type=int)
	tlx = max(0, min(215.9, tlx))

	tly = args.get("tly", default=0, type=int)
	tly = max(0, min(297.18, tly))

	width = args.get("width", default=215.9, type=float)
	width = max(0, min(215.9, width))

	height = args.get("height", default=297.18, type=float)
	height = max(0, min(297.18, height))

	# Only one scan at a time (big scans may take up a lot of memory)
	uwsgi.lock()

	scan_cmd = ['scanimage', f'--device={scanner}', f'--format={_format}', f'--resolution={resolution}', f'--mode={mode}', f'-l {tlx}', f'-t {tly}', f'-x {width}', f'-y {height}']
	print('Executing: ' + ' '.join(scan_cmd))
	scan_process = subprocess.Popen(scan_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
	output = scan_process.stdout.read()
	scan_process.wait()

	uwsgi.unlock()

	# If the scan succeded the function returns the scan output with HTTP Error Code 200
	# Else the stderr output is returned with HTTP Error Code 400
	print(f'Return Code is: {scan_process.returncode}')
	if scan_process.returncode == 0:
		now = datetime.datetime.today().strftime('%Y_%m_%d-%H:%M:%S')
		filename = f'{now}_{name}_{mode}_{resolution}dpi_{width - tlx}x{height - tlx}.{_format}'.replace(' ', '_').replace(':', '_').replace('/', '_')
		content_type = extension_to_mimetype(_format)
		response = Response(response=output, status=200, content_type=content_type,
			headers={
				"Content-disposition": f"attachment; filename={filename}",
				"scanner": scanner,
				"name": name,
				"format": _format,
				"resolution": resolution,
				"mode": mode,
				"tlx": tlx,
				"tly": tly,
				"width": width,
				"height": height
			})
	else:
		err = scan_process.stderr.read()
		print(err)
		response = Reponse(response=err, status=400, content_type="text/plain")
	return response
