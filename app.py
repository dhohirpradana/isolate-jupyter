import os
import requests
from flask import Flask, abort, request
from dotenv import load_dotenv
from register import handler as register_handler

load_dotenv()

app = Flask(__name__)

required_env_vars = ["PB_URL", "PB_ADMIN_LOGIN_URL", "PB_ADMIN_MAIL", "PB_USER_URL",
                     "PB_ADMIN_PASSWORD", "HDFS_URL", "SECRET", "ALLOWED_IPS", "ALLOWED_DOMAINS_URL"]


def validate_envs():
    for env_var in required_env_vars:
        if env_var not in os.environ:
            raise EnvironmentError(
                f"Required environment variable {env_var} is not set.")


# allowed_ips = os.environ.get('ALLOWED_IPS', '').split(',')
# allowed_domains = os.environ.get('ALLOWED_DOMAINS', '').split(',')
# ALLOWS_URL = os.environ.get('ALLOWS_URL')


# def check_access():
#     response = requests.get(ALLOWS_URL)

#     if response.status_code == 200:
#         data = response.json()
#         allowed_domains = data.get("allowed_domains", [])
#         return jsonify({"allowed_domains": allowed_domains})
#     else:
#         return jsonify({"error": "Failed to fetch allowed domains"}), 500

# client_ip = request.remote_addr
# client_host = request.host

# if client_ip not in allowed_ips and client_host not in allowed_domains:
#     abort(403)


@app.route('/jupyter', methods=['POST', 'DELETE'])
def replace_yaml():
    #    check_access()
    validate_envs()
    return register_handler()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7788)
