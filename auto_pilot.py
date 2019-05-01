import os
import signal
import subprocess

# Making sure to use virtual environment libraries
activate_this = "/home/lawz/Desktop/projects/lostandfound/env/bin/activate_this.py"
exec(open(activate_this).read(), dict(__file__=activate_this))

# Change directory to where your Flask's app.py is present
os.chdir("/home/lawz/Desktop/projects/lostandfound")
tf_ic_server = ""
flask_server = ""

try:
    print('Type Ctrl-C to quit')
    tf_ic_server = subprocess.Popen(["tensorflow_model_server "
                                     "--model_base_path=/home/lawz/Desktop/projects/lostandfound/lostandfound/image-classifier "
                                     "--rest_api_port=9001 --model_name=ItemImageClassifier"],
                                    stdout=subprocess.DEVNULL,
                                    shell=True,
                                    preexec_fn=os.setsid)
    print("Started TensorFlow Serving ImageClassifier server!")

    flask_server = subprocess.Popen(["export FLASK_ENV=development && python3 run.py"],
                                    stdout=subprocess.DEVNULL,
                                    shell=True,
                                    preexec_fn=os.setsid)
    print("Started Flask server!")
except KeyboardInterrupt:
    print('Shutting down all servers...')
    os.killpg(os.getpgid(tf_ic_server.pid), signal.SIGTERM)
    os.killpg(os.getpgid(flask_server.pid), signal.SIGTERM)
    print('Servers successfully shutdown!')