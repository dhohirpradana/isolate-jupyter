import json
import os
import subprocess
import time
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from kubernetes import check_service, get_unused_port
from hdfs import mkdir, rmdir, check_connection as hdfs_check_connection
from pb_user import user_create, user_remove, check_connection as pb_check_connection, user_check

load_dotenv()

secret_env = os.environ.get('SECRET')


def delete_dpy(output_filename):
    subprocess.run(["kubectl", "delete", "-f",
                    output_filename], check=True, text=True)


def delete_jupyter_user(username):
    url = f'http://10.1.111.7:30004/hub/api/users/{username}'
    try:
        response = requests.delete(url)
        response.raise_for_status()
        data = response.json()

        print(data)
        print('Jupyter User Deleted')
        return True
    except requests.exceptions.HTTPError as errh:
        print(f'HTTP Error: {errh}')
        return False


def handler():
    secret = request.args.get('secret')
    if secret == secret_env:
        pass
    else:
        return jsonify({'error': 'Invalid key!'}), 403

    input_filename = 'input.yaml'
    try_count = 10

    # DELETE USER
    if request.method == 'DELETE':

        try:
            username = request.args.get('username')
            company = request.args.get('company')
            output_filename = f'output-{username}.yaml'

            if username:
                pass
            else:
                return jsonify({'error': 'Parameter "username" not provided'}), 400

            if company:
                pass
            else:
                return jsonify({'error': 'Parameter "company" not provided'}), 400

            rmdir(f'/usersapujagad/{company}/{username}')
            delete_jupyter_user(username)
            user_remove(username)
            subprocess.run(["kubectl", "-n", "sapujagad2", "delete",
                           "statefulset", f"jupyter-{username}"], check=True, text=True)
            subprocess.run(["kubectl", "-n", "sapujagad2", "delete", "service",
                           f"jupyter-{username}-nodeport"], check=True, text=True)
            return jsonify({"message": f"User {username} deleted successfully!"}), 200
        except:
            return jsonify({"message": f"User {username} deleted successfully!"}), 200

    required_fields = ['username', 'email', 'password',
                       'firstName', 'lastName', 'createdBy', 'company']
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body can not be empty."}), 400

    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"message": f"{field} is required."}), 400

    username = data['username']
    company = data['company']
    password = data['password']
    email = data['email']
    first_name = data['firstName']
    last_name = data['lastName']
    created_by = data['createdBy']

    output_filename = f'output-{username}.yaml'

    pb_conn = pb_check_connection()
    hdfs_conn = hdfs_check_connection()

    if not pb_conn:
        return jsonify({"message": "Connection error to PB."}), 500

    if not hdfs_conn:
        return jsonify({"message": "Connection error to HDFS."}), 500

    service_name = username
    user_not_exists = user_check(email, service_name)

    if not user_not_exists:
        return jsonify({"message": f"User with email {email} or username {service_name} already exists."}), 409

    try:
        check_svc = check_service(f"jupyter-{service_name}")
        if check_svc == '1':
            return jsonify({'error': f'Service {service_name} already exists!'}), 409

        unused_port_result = get_unused_port()
        print("Unused Port:", unused_port_result)

        if unused_port_result is None:
            return jsonify({'error': 'No unused port available!'}), 404

        try:
            service_port = 'SERVICE_PORT'

            with open(input_filename, 'r') as file:
                input_content = file.read()

            modified_content = input_content.replace('SERVICE_NAME', service_name).replace(
                service_port, f'{unused_port_result}')

            with open(output_filename, 'w') as file:
                file.write(modified_content)

            with open(output_filename, 'r') as file:
                yaml_data = file.read()

            try:
                subprocess.run(["kubectl", "apply", "-f",
                               output_filename], check=True, text=True)

                print("Sleep 10")
                time.sleep(10)
                print("Sleep finish")

                # create user in jupyterhub
                def create_jupyter_user():
                    try:
                        subprocess.run(
                            f"curl --location --request POST 'http://10.1.111.7:{unused_port_result}/hub/api/users/{service_name}' --header 'Authorization: Bearer test-token-123'", shell=True, check=True, text=True)
                        print("Jupyter User Created")

                        try_count_admin = 10

                        # # set user as admin
                        def set_user_as_admin():
                            data_dict = {"name": service_name, "admin": True}

                            curl_update_command = [
                                'curl',
                                '--location',
                                '--request',
                                'PATCH',
                                f'http://10.1.111.7:{unused_port_result}/hub/api/users/{service_name}',
                                '--header',
                                'Authorization: Bearer test-token-123',
                                '--header',
                                'Content-Type: application/json',
                                '--data',
                                json.dumps(data_dict)
                            ]

                            try_count_start_server = 10

                            try:
                                subprocess.run(curl_update_command, check=True)

                                # start server
                                def start_server():
                                    curl_command = [
                                        'curl',
                                        '--location',
                                        '--request',
                                        'POST',
                                        f'http://10.1.111.7:{unused_port_result}/hub/api/users/{service_name}/server',
                                        '--header',
                                        'Authorization: Bearer test-token-123'
                                    ]

                                    try:
                                        subprocess.run(
                                            curl_command, check=True)
                                    except subprocess.CalledProcessError as e:
                                        print(f"Error: {e}")
                                        if try_count_start_server > 0:
                                            print("Retrying...")
                                            time.sleep(2)
                                            start_server()
                                        else:
                                            print(
                                                "Max retry reached. Exiting...")
                                            delete_jupyter_user(service_name)
                                            delete_dpy(output_filename)
                                            return jsonify({"error": f"Register not succesfully. {e}"}), 500

                                start_server()

                            except subprocess.CalledProcessError as e:
                                print(f"Error: {e}")
                                if try_count_admin > 0:
                                    print("Retrying...")
                                    time.sleep(2)
                                    set_user_as_admin()
                                else:
                                    print("Max retry reached. Exiting...")
                                    delete_jupyter_user(service_name)
                                    delete_dpy(output_filename)
                                    return jsonify({"error": f"Register not succesfully. {e}"}), 500

                            set_user_as_admin()

                    except subprocess.CalledProcessError as e:
                        print(f"Error: {e}")
                        if try_count > 0:
                            print("Retrying...")
                            time.sleep(2)
                            create_jupyter_user()
                        else:
                            print("Max retry reached. Exiting...")
                            delete_jupyter_user(service_name)
                            delete_dpy(output_filename)
                            return jsonify({"error": f"Register not succesfully. {e}"}), 500

                create_jupyter_user()

                # HDFS
                hdfs_mkdir = mkdir(
                    f'/usersapujagad/{company}/{service_name}', service_name)

                if hdfs_mkdir[0] is False:
                    delete_jupyter_user(service_name)
                    delete_dpy(output_filename)
                    return jsonify({"error": f"Register not succesfully. {hdfs_mkdir[1]}"}), 500

                # POCKETBASE
                create_user = user_create(
                    unused_port_result, username, password, email, first_name, last_name, created_by, company)
                if create_user[0] is False:
                    rmdir(f'/usersapujagad/{company}/{service_name}')
                    delete_jupyter_user(service_name)
                    delete_dpy(output_filename)
                    return jsonify({"error": f"Register not succesfully. {create_user[1]}"}), 500

                return jsonify({"message": f"Register user {service_name} successfully!", "port": unused_port_result}), 200

            except subprocess.CalledProcessError as e:
                return jsonify({"error": f"An error occurred: {e}"}), 500

        except FileNotFoundError:
            return jsonify({"error": "File not found."}), 404

        except IOError as ioe:
            return jsonify({"error": f"Error reading/writing to file: {ioe}"}), 500

        except Exception as e:
            return jsonify({"error": f"An error occurred: {e}"}), 500

    except Exception as e:
        print(f"Error: {e}")
