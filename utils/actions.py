import requests

from django.contrib.contenttypes.models import ContentType

from user_activity.models import ActivityLog
import socket
import platform
import subprocess
import psutil


from django.utils import timezone


TODAY = timezone.now()


def get_device_model():
    system = platform.system()
    if system == "Windows":
        import wmi
        c = wmi.WMI()
        for system in c.Win32_ComputerSystem():
            return system.Model
    elif system == "Darwin":  # macOS
        result = subprocess.run(['system_profiler', 'SPHardwareDataType'], stdout=subprocess.PIPE)
        output = result.stdout.decode()
        for line in output.split('\n'):
            if 'Model Name' in line:
                return line.split(': ')[1]
    elif system == "Linux":
        try:
            with open('/sys/devices/virtual/dmi/id/product_name', 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            return "Unknown Model"
    else:
        return "Unsupported OS"


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    return (
        x_forwarded_for.split(",")[0]
        if x_forwarded_for
        else request.META.get("REMOTE_ADDR")
    )
    
def get_network_info():
    net_if_addrs = psutil.net_if_addrs()
    network_info = {}
    for interface_name, interface_addresses in net_if_addrs.items():
        for address in interface_addresses:
            if str(address.family) == 'AddressFamily.AF_INET':
                network_info[interface_name] = {
                    'IP Address': address.address,
                    'Netmask': address.netmask,
                    'Broadcast IP': address.broadcast
                }
    return network_info

def activity_log(qs, request,serializer,  *args, **kwargs):
    # Save Logger for Tracking 
    request_method = request.method
    request_url = request.build_absolute_uri()
    request_data = request.data 
    response_data = serializer.data
    try:
        response_user = request.user
    except:
        response_user = None

    try:
        send_action(qs,actor=response_user, action_type = request_method, action_status = 'SUCCESS',  request_url=request_url,request_data=request_data, response_data=response_data)
    except:
        pass
    return True
    
    
def send_action(qs,actor, action_type, action_status,  request_url,request_data, response_data, *args, **kwargs):
    
    if qs:
        content_type = ContentType.objects.get_for_model(qs.model if hasattr(qs, 'model') else qs)

        public_ip = None
        response = requests.get('https://api.ipify.org?format=json')
        if response.status_code == 200:
            data = response.json()
            # public_ip = data['ip']
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 1))
            public_ip = s.getsockname()[0]
            print(f"IP Address = {public_ip}")
            
            
            
        today = TODAY
        
        today_str = today.strftime("%d %B, %Y at %I:%M %p")
        
        hostname = socket.gethostname()
        fqdn = socket.getfqdn()
        os_info = platform.system() + " " + platform.release()
        device_model = get_device_model()

        remarks = (f"Action Taken From <b>'{hostname}'</b>, Fully Qualified Device Name, "
                f"<b>'{fqdn}'</b> and OS Info, <b>'{os_info}'</b> and Device Name <b>'{device_model}'</b>")

        message = f"{actor} is logged in with IP: {public_ip} at {today_str}, and also {remarks} and {get_network_info()}"


        ActivityLog.objects.create(
            actor=actor,
            action_type=action_type,
            remarks=message,
            request_url=request_url,
            action_status=action_status,
            ip_address=public_ip,
            request_data=request_data,
            response_data=response_data,
            content_type=content_type
        )

    return True
