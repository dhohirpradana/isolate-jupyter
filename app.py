from flask import Flask
from register import handler as register_handler
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

required_env_vars = ["PB_URL", "PB_ADMIN_LOGIN_URL", "PB_ADMIN_MAIL", "PB_USER_URL", "PB_ADMIN_PASSWORD", "HDFS_URL"]

def validate_envs():
    for env_var in required_env_vars:
        if env_var not in os.environ:
            raise EnvironmentError(
                f"Required environment variable {env_var} is not set.")

@app.route('/jupyter/<username>', methods=['POST', 'DELETE'])
def replace_yaml(username):
    validate_envs()
    return register_handler(username)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7788)
