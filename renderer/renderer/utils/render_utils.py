import docker
import os
import shutil
from typing import List
from dotenv import load_dotenv
import oci
import time

load_dotenv()


def render_in_docker(filename: str):
    client = docker.from_env()
    docker_container_name = os.environ["DOCKER_CONTAINER_NAME"]
    container = client.containers.get(docker_container_name)
    exec_result = container.exec_run(
        f"manim -qm {filename} GenerateVideo", stdout=True, stderr=True
    )
    output = exec_result.output.decode("utf-8")
    print(output)
    return output


def create_file(filename: str, code: List[str]):
    if not os.path.exists("manim_code"):
        os.makedirs("manim_code")
    if os.path.exists(f"manim_code/{filename}.py"):
        os.remove(f"manim_code/{filename}.py")
    with open(f"manim_code/{filename}.py", "a") as f:
        for line in code:
            f.write(line + "\n")
    return f"{filename}.py"


def upload_video_to_bucket(filename: str):
    file_id = filename.split(".")[0]
    oci_config = oci.config.from_file()
    object_storage_client = oci.object_storage.ObjectStorageClient(oci_config)
    namespace = object_storage_client.get_namespace().data
    compartment_id = os.environ["OCI_COMPARTMENT_ID"]
    bucket_name = os.environ["OCI_BUCKET_NAME"]
    object_name = file_id + ".mp4" 
    oci_region = os.environ["OCI_REGION"]
    with open(f"manim_code/media/videos/{file_id}/720p30/GenerateVideo.mp4", "rb") as file:  
        object_storage_client.put_object(
                namespace_name=namespace,
                bucket_name=bucket_name,
                object_name=object_name,
                put_object_body=file
            )
    return f"https://objectstorage.{oci_region}.oraclecloud.com/n/{namespace}/b/{bucket_name}/o/{object_name}"

def is_older_than_five_minutes(path):
        return (time.time() - os.path.getmtime(path)) > 60 

def cleanup(filename: str):

    script_path = f"manim_code/{filename}.py"
    if os.path.exists(script_path):
        os.remove(script_path)
    
    video_dir = f"manim_code/media/videos/{filename}"
    if os.path.exists(video_dir):
        shutil.rmtree(video_dir)
    
    images_dir = f"manim_code/media/images/{filename}"
    if os.path.exists(images_dir):
        shutil.rmtree(images_dir)  
    
    text_dir = "manim_code/media/texts"
    tex_dir = "manim_code/media/Tex"
    if os.path.exists(text_dir):
        for name in os.listdir(text_dir):
            file_path = os.path.join(text_dir, name)
            if os.path.isfile(file_path):  
                if is_older_than_five_minutes(file_path):
                    os.remove(file_path)
    
    if os.path.exists(tex_dir):
        for name in os.listdir(tex_dir):
            file_path = os.path.join(tex_dir, name)
            if os.path.isfile(file_path):
                if is_older_than_five_minutes(file_path):
                    os.remove(file_path)

