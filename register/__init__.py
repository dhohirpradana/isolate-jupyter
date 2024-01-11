from flask import Flask, request, jsonify
from kubernetes import check_service, get_unused_port
from hdfs import mkdir, rmdir, check_connection as hdfs_check_connection
from pb_user import user_create, user_remove, check_connection as pb_check_connection, user_check

def handler(username):
    input_filename = 'input.yaml'
    output_filename = 'output.yaml'
    
    required_fields = ['email', 'password', 'firstName', 'lastName']
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "Request body can not be empty."}), 400
    
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"message": f"{field} is required."}), 400
    
    password = data['password']
    email = data['email']
    first_name = data['firstName']
    last_name = data['lastName']
    
    pb_conn = pb_check_connection()
    hdfs_conn = hdfs_check_connection()
    
    if not pb_conn:
        return jsonify({"message": "Connection error to PB."}), 500
    
    if not hdfs_conn:
        return jsonify({"message": "Connection error to HDFS."}), 500
    
    # DELETE USER
    if request.method == 'DELETE':
        rmdir(f'/usersapujagad/{service_name}')
        user_remove(service_name)
        subprocess.run(["kubectl", "delete", "-f", output_filename], check=True, text=True)
        return jsonify({"message": f"User {service_name} deleted successfully!"}), 200
    
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
            
            modified_content = input_content.replace('SERVICE_NAME', service_name).replace(service_port, f'{unused_port_result}')

            with open(output_filename, 'w') as file:
                file.write(modified_content)

            with open(output_filename, 'r') as file:
                yaml_data = file.read()
                
            import subprocess

            try:
                subprocess.run(["kubectl", "apply", "-f", output_filename], check=True, text=True)
                
                # HDFS
                hdfs_mkdir = mkdir(f'/usersapujagad/{service_name}')
                
                if hdfs_mkdir[0] == False:
                    subprocess.run(["kubectl", "delete", "-f", output_filename], check=True, text=True)
                    return jsonify({"error": f"Register not succesfully. {hdfs_mkdir[1]}"}), 500
                
                # POCKETBASE
                create_user = user_create(unused_port_result, username, password, email, first_name, last_name)
                if create_user(0) == False:
                    rmdir(f'/usersapujagad/{service_name}')
                    subprocess.run(["kubectl", "delete", "-f", output_filename], check=True, text=True)
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