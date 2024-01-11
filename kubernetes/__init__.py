import subprocess

def get_unused_port():
    try:
        result = subprocess.run(['bash', 'unused_port.sh'], capture_output=True, text=True, check=True)
        output_variable = result.stdout.strip()
        return output_variable

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Output: {e.output}")
        return None
    
def check_service(service):
    try:
        result = subprocess.run(['bash', 'check_service.sh', service], capture_output=True, text=True, check=True)
        output_variable = result.stdout.strip()
        return output_variable

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Output: {e.output}")
        return None