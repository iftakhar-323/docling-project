## Lab Details

## Running an NGINX Web Server in a Docker Container

### Overview of This Lab

In this lab, you will learn how to set up and run an NGINX web server inside a Docker container using **Puku CLI** . You will use the integrated terminal in Puku CLI to execute Docker commands, manage containers, and configure an NGINX web server.

By the end of this lab, you will understand how Docker simplifies application deployment by providing a lightweight, portable, and scalable environment for hosting web applications.

### What You'll Learn

- Use Docker commands in the **Puku CLI integrated terminal** to pull images, run containers, and manage container configurations.
- Deploy an NGINX web server inside a Docker container.
- Start, stop, restart, and remove Docker containers.
- View and analyze container logs for monitoring and troubleshooting.

Lab start

## Running an NGINX Web Server in a Docker Container

In today's DevOps and cloud-native world, the ability to quickly deploy services in isolated environments is essential. **Docker** makes this possible by providing lightweight, portable containers. In this lab, you will use **Puku CLI** and its integrated terminal to build, run, and manage an NGINX web server inside a Docker container.

**Basic Docker Concepts__image_000000_39e68af6226d7c9f358e7875c730cf800029a15e0a193e367c9cf7a0abe012ed.png**
![Image](all_images/Basic Docker Concepts__image_000000_39e68af6226d7c9f358e7875c730cf800029a15e0a193e367c9cf7a0abe012ed.png)

_Extracted text:_
```text
Pull Nginx Image
Run the Image
dockerhub
from DockerHub
Container
Nginx
Image
Verify the Container is running
using
"docker ps"
Project
-Volume Mount-
usr/share/
Workspace/html
nginx/html
```

This lab will guide you through the complete process of running an **NGINX web server inside a Docker container** using **Puku CLI** . You will learn how to pull the official NGINX Docker image, create a custom HTML page, configure a volume mount, run the container, and verify that the web server is running successfully.

### Lab Overview

In this lab, you will:

- Understand the basics of Docker and NGINX.
- Pull the official NGINX Docker image.
- Create and serve a custom HTML page from a Docker container.
- Map ports and mount volumes between your local project workspace and the Docker container.
- Manage the container lifecycle using the **Puku CLI integrated terminal** (start, stop, view logs, and remove containers).

## Concepts Explained

Before starting the lab, let's understand the key technologies used.

### What is Docker?

Docker is a containerization platform that packages applications and their dependencies into **containers** . These containers are lightweight, portable, and provide a consistent runtime environment across different systems.

### What is NGINX?

NGINX is a high-performance web server that serves web content efficiently. It can also function as a reverse proxy, load balancer, and HTTP cache, making it a popular choice for hosting modern web applications.

### Docker Image vs. Container

- **Image:** A read-only template that contains everything needed to run an application (for example, the official **NGINX** image).
- **Container:** A running instance of an image with its own isolated filesystem, processes, and networking.

## Hands-on: Running NGINX in Docker

In the following exercises, you will use the **Puku CLI integrated terminal** to pull the official NGINX Docker image, run it as a container, and manage it using Docker commands.

Yes, exactly. Since you're **actually running the commands in Puku CLI** , your documentation should say **Puku CLI** , not AWS Terminal. The commands remain the same.

Here's a professional version for your docs:

### Step 1: Pull the Official NGINX Docker Image

Open **Puku CLI** and launch the **integrated terminal** .

Run the following command to download the latest official NGINX image from Docker Hub:

docker pull nginx

**Basic Docker Concepts__image_000001_3d0f24c68bef2702dd4fdfe756e9ada4d7031e99ced5f0bc1c249906e5faf772.png**
![Image](all_images/Basic Docker Concepts__image_000001_3d0f24c68bef2702dd4fdfe756e9ada4d7031e99ced5f0bc1c249906e5faf772.png)

_Extracted text:_
```text
PROBLEMS
DEBUG CONSOLE
bash
OUTPUT
TERMINAL
X
iftakhar@iftakhar-PC:~/Poridhi$
docker pull nginx
```

Docker will download the required image layers. Once the download is complete, the latest NGINX image will be available on your local machine.

**Expected Output**

You should see output similar to the following in the Puku CLI terminal:

**Basic Docker Concepts__image_000002_c40b3889b133ac72b0b44ed744890dcceefe1c0bbc070b02312622efbe61ce89.png**
![Image](all_images/Basic Docker Concepts__image_000002_c40b3889b133ac72b0b44ed744890dcceefe1c0bbc070b02312622efbe61ce89.png)

_Extracted text:_
```text
iftakhar@iftakhar-PC:~/Poridhi$ docker pull nginx
Using default tag: latest
latest: Pulling from library/nginx
1645c1e06f46: Pull complete
1b30016634d5: Pull complete
e95a6c7ea7d4: Pull complete
acf093e7a04f: Pull complete
cd9307c9ecd8: Pull complete
fcb6fd84b2a0: Pull complete
df68ee7e7a00: Pull complete
1cf7d051b485:Download complete
e2c07e54e55a: Download complete
Digest: sha256:ec4ed8b5299e5e90694af7750eb6dffd2627317d30544d056b0371f8082f7bce
Status: Downloaded newer image for nginx:latest
docker.io/library/nginx:latest
iftakhar@iftakhar-PC:~/Poridhi$
```

#### Verify the Download

To confirm that the image has been downloaded successfully, run:

docker images

**Basic Docker Concepts__image_000003_d3fc8307702e79a6b4cdc1b678530e15cf63a6a43cb7cca5084874114778b5b2.png**
![Image](all_images/Basic Docker Concepts__image_000003_d3fc8307702e79a6b4cdc1b678530e15cf63a6a43cb7cca5084874114778b5b2.png)

_Extracted text:_
```text
o
docker
iftakhar@iftakhar-PC:~/Poridhi$
images
0
```

**Expected Output**

The command should list the nginx image with the latest tag.

**Basic Docker Concepts__image_000004_f79b74c4f53d0758a6232ef685c6d87d512cd25a9721e9864b096b5e07d1e03b.png**
![Image](all_images/Basic Docker Concepts__image_000004_f79b74c4f53d0758a6232ef685c6d87d512cd25a9721e9864b096b5e07d1e03b.png)

_Extracted text:_
```text
iftakhar@iftakhar-PC:~/Poridhi$ docker images
Info
In Use
IMAGE
ID
DISK USAGE
CONTENT SIZE
EXTRA
build-runner-project_api:latest
a9eeb7cd9d9f
439MB
106MB
build-runner-project_worker:latest
fa01c8c718c6
439MB
106MB
99af191ea365
build-runner/0c606283-15f6-4706-864a-3f433bala4d0:latest
177MB
43.2MB
93af4c330ff8
124MB
build-runner/0c92df8a-5b6e-4e3d-9236-90a668dc60a5:latest
451MB
93af4c330ff8
build-runner/14e4a58f-9210-4326-a9d3-27dc3b000354:latest
451MB
124MB
build-runner/309c6d47-5556-4373-a0c8-9d472910a8c7:latest
93af4c330ff8
451MB
124MB
build-runner/5fc26aa3-41ee-4c3f-923a-5efe3c1dc1b6:latest
93af4c330ff8
451MB
124MB
93af4c330ff8
build-runner/669b00b5-c03f-494a-8bd9-4b6d72e0217a:latest
451MB
124MB
93af4c330ff8
124MB
build-runner/7429b478-6a03-4dbe-8e92-3f3bcf0a8323:latest
451MB
build-runner/be4a3148-46b7-4f75-9150-c3900be78bee:latest
7688c88a8738
451MB
124MB
7688c88a8738
build-runner/c0a0458e-d782-4c59-a2be-49e7a76c2572:latest
451MB
124MB
e7eb96123c54
U
ghcr.io/iftakhar-323/demo-app:latest
177MB
43.2MB
191fb7f5390f
1.17GB
265MB
ghcr.io/mlflow/mlflow:v2.22.0
25.9kB
hello-world:latest
0e760fdfbc48
9.49kB
minio/minio:RELEASE.2025-09-07T16-13-09Z
14cea493d9a3
241MB
62.2MB
0b4c7bd72b0e
ml-fastapi-app:latest
820MB
175MB
285MB
ml-tracker-mlflow:latest
84dcd250ea95
1.24GB
ec4ed8b5299e
nginx:latest
241MB
66MB
230MB
968df39aedce
57.8MB
node:22-alpine
164MB
1b92e7a80c02
633MB
postgres:15
e013e867e712
420MB
117MB
U
postgres:16-alpine
a39549e211a1
179MB
45.4MB
python:3.12-slim
09160599abd2
155MB
38.2MB
redis:alpine
U
611MB
57adc8acda08
152MB
smart_park-backend:latest
311MB
smart park-frontend:latest
0c2ce49a7c50
1.22GB
f3d28607ddd7
160MB
45.3MB
ubuntu:latest
iftakhar@iftakhar-PC:~/Poridhi$
口
```

This format is much cleaner because the screenshots you capture from **Puku CLI** will naturally match the text in your documentation.

Here's the Puku CLI version with only the necessary changes. The commands stay the same except for the project path.

### Step 2: Create a Directory for Web Content

Open the **Puku CLI integrated terminal** and create a directory to store your custom HTML content. This directory will later be mounted into the NGINX container.

**Basic Docker Concepts__image_000005_a6eec19b9f1450b21498f87672dffe4d945b9f9ffedc98fb62d17983ab347e1d.png**
![Image](all_images/Basic Docker Concepts__image_000005_a6eec19b9f1450b21498f87672dffe4d945b9f9ffedc98fb62d17983ab347e1d.png)

_Extracted text:_
```text
iftakhar@iftakhar-PC:~/Poridhi$ mkdir -p r
nginx-lab/html
iftakhar@iftakhar-PC:~/Poridhi$
_
```

This directory will act as the source for the web content served by the NGINX container, allowing you to update files without modifying the container itself.

### Step 3: Create a Simple Web Page

Create a simple HTML page inside the html directory by running the following command:

**Basic Docker Concepts__image_000006_39c020f80ffd0ac5e551a3081535353b2a89df210d92c855a519a4ff67ff0751.png**
![Image](all_images/Basic Docker Concepts__image_000006_39c020f80ffd0ac5e551a3081535353b2a89df210d92c855a519a4ff67ff0751.png)

_Extracted text:_
```text
iftakhar@iftakhar-PC:~/Poridhi$
'<h1>Hello from NGINX running in Docker!</h1>'
nginx-lab/html/index.html
echo
```

This page will be served by the NGINX web server once the container is running.

### Step 4: Run the NGINX Container

From the **Puku CLI integrated terminal** , run the following command:

**Basic Docker Concepts__image_000007_0df2f31113b163049852f4c1946f45849f4473033ef58ba5d07deb057ce494e2.png**
![Image](all_images/Basic Docker Concepts__image_000007_0df2f31113b163049852f4c1946f45849f4473033ef58ba5d07deb057ce494e2.png)

_Extracted text:_
```text
iftakhar@iftakhar-PC:~/Poridhi$ docker run --name my-nginx
-v $(pwd)/nginx-lab/html:/usr/share/nginx/html:ro
-p 8000:80
-d nginx
```

**Note:** On Windows PowerShell, replace $(pwd) with ${PWD} if required.

#### Command Breakdown

- --name my-nginx – Assigns the name **my-nginx** to the container.
- -v $(pwd)/nginx-lab/html:/usr/share/nginx/html:ro – Mounts your local HTML directory into the container's web root in read-only mode.
- -p 8000:80 – Maps port **8000** on your machine to port **80** inside the container.
- -d nginx – Runs the NGINX container in detached mode.

**Expected Output**

If the command executes successfully, Docker will return a long container ID.

**Basic Docker Concepts__image_000008_f10c690de8c020aaf4dfa513c3bac71456f0180a41b0bd26b88556a47883a968.png**
![Image](all_images/Basic Docker Concepts__image_000008_f10c690de8c020aaf4dfa513c3bac71456f0180a41b0bd26b88556a47883a968.png)

_Extracted text:_
```text
iftakhar@iftakhar-PC:~/Poridhi$ docker run --name my-nginx
-v $(pwd)/nginx-lab/html:/usr/share/nginx/html:ro
-p 50000:80
-d nginx
8106ee13f2aab334720b134d3b913e9b0a42f712b13d8fcbeba0b3150a0066bb
iftakhar@iftakhar-PC:~/Poridhi$
```

## 

## Step 5: Verify the Setup

### Check Running Containers

Run the following command to confirm that the NGINX container is running:

**Basic Docker Concepts__image_000009_a2367ebb15710c3761d2368ce26d19dad75a0acf4735ef52268efc555a9695a0.png**
![Image](all_images/Basic Docker Concepts__image_000009_a2367ebb15710c3761d2368ce26d19dad75a0acf4735ef52268efc555a9695a0.png)

_Extracted text:_
```text
CaOOOOROCTCaORaaaaUOnCTaZTIzHRo
I6aCTCaCntCTaoZ+CCaRRZLCTaOOOTo
iftakhar@iftakhar-PC:~/Poridhi$ docker ps
CONTAINER ID
IMAGE
COMMAND
CREATED
STATUS
PORTS
NAMES
II
8106ee13f2aa
7
0.0.0.0:500
Up 7 minutes
"/docker-entrypoint.
nginx
minutes ago
00->80/tcp, [::]:50000->80/tcp
my-nginx
II
99ca1a076de7
ml-tracker-mlflow
"mlflow server --hos.
0.0.0.0:500
Up 2 days (unhealthy)
2 days ago
mltracker-mlflow
0->5000/tcp, [::]:5000->5000/tcp
II
46cd8ec48e3b
0.0.0.0:543
'docker-entrypoint.s.
2 days ago
postgres:16-alpine
Up 2 days (healthy)
2->5432/tcp,[::]:5432->5432/tcp
mltracker-postgres
minio/minio:RELEASE.2025-09-07T16-13-09Z
b3bc11e07f95
z"/usr/bin/docker-ent..."
0.0.0.0:900
2 days ago
Up 2 days (healthy)
0-9001->9000-9001/tcp, [::]:9000-9001->9000-9001/tcp
mltracker-minio
a5d37b839de4
0.0.0.0:808
ghcr.io/iftakhar-323/demo-app:latest
Up 7 days
9 days ago
'python /app.py
0->8080/tcp，[::]:8080->8080/tcp
demo-app
iftakhar@iftakhar-PC:~/Poridhi$■
```

Verify that:

- The container name is **my-nginx**
- The status is **Up**
- **Host port 5000 is mapped to container port 80**

### View the Web Page

Test the web server directly from the terminal:

curl http://localhost:50000

Expected output:

**Basic Docker Concepts__image_000010_d64048952936f48016d8e9ea0550e2e399a991fd8d490401f6d1e16968a88dff.png**
![Image](all_images/Basic Docker Concepts__image_000010_d64048952936f48016d8e9ea0550e2e399a991fd8d490401f6d1e16968a88dff.png)

_Extracted text:_
```text
localhost:50000
C
三口
Hello from NGINX
running in Docker!
```

If you're using **Puku CLI** , you can also open the forwarded port from the Ports panel or the generated preview URL to view the page in your browser.

You should see:

Hello from NGINX running in Docker!

## Managing the NGINX Container

### Stop the Container

docker stop my-nginx

### Start the Container Again

docker start my-nginx

### View Container Logs

Display the NGINX logs:

docker logs my-nginx

Example output:

**Basic Docker Concepts__image_000011_8e0750bc17bffa7d2e5f89de88015943c2d017cffd2672fb153d722895e911cd.png**
![Image](all_images/Basic Docker Concepts__image_000011_8e0750bc17bffa7d2e5f89de88015943c2d017cffd2672fb153d722895e911cd.png)

_Extracted text:_
```text
ddp -ouən
iftakhar@iftakhar-PC:~/Poridhi$ docker logs my-nginx
/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
/docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf
10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf
/docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
/docker-entrypoint.sh: Launching/docker-entrypoint.d/30-tune-worker-processes.sh
/docker-entrypoint.sh: Configuration complete; ready for start up
2026/06/25 08:47:19 [notice] 1#1: using the "epoll" event method
[notice] 1#1: nginx/1.31.2
2026/06/25 08:47:19
[notice]
2026/06/25 08:47:19
1 1#1: built by gcc 14.2.0 (Debian 14.2.0-19)
j 1#1: 0S: Linux 6.17.0-35-generic
2026/06/25 08:47:19
[notice]
2026/06/25 08:47:19
[notice]
1#1: getrlimit(RLIMIT_NOFILE):1024:524288
2026/06/25 08:47:19
[notice]
1#1: start worker processes
2026/06/25 08:47:19
[notice]
1#1: start worker process 29
08:47:19
1#1: start worker process 30
2026/06/25
[notice]
[notice]
2026/06/25 08:47:19
1#1: start worker process 31
2026/06/25 08:47:19
[notice]
1#1: start worker process 32
2026/06/25 08:47:19
[notice]
1#1: start worker process 33
2026/06/25 08:47:19
[notice]
1#1: start worker process 34
2026/06/25 08:47:19
[notice]
1#1: start worker process 35
2026/06/25 08:47:19
[notice]
1#1: start worker process 36
2026/06/25
08:47:19
[notice]
1#1: start worker
process 37
2026/06/25
08:47:19
[notice]
1#1: start worker process 38
2026/06/25 08:47:19
[notice]
1#1: start worker process 39
2026/06/25 08:47:19
1#1: start worker process 40
[notice]
2026/06/25 08:47:19
1#1: start worker process 41
[notice]
[notice]
1#1: start worker process 42
2026/06/25 08:47:19
2026/06/25 08:47:19
1#1: start worker process 43
[notice]
2026/06/25 08:47:19
1#1: start worker process 44
[notice]
"-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, li
172.17.0.1
[25/Jun/2026:09:01:27 +0000] "GET / HTTP/1.1" 200 45
ke Gecko) Chrome/148.0.0.0 Safari/537.36" "_"
2a :   t s  : t  (   :#  :: n
.0.1, server: localhost, request: "GET /favicon.ico HTTP/1.1", host: "localhost:50000", referrer: "http://localhost:50000/"
1  ) / 00:0//:  0 / / 1. [00+ L:::// - - 6
64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36" "_"
iftakhar@iftakhar-PC:~/Poridhi$■
```

Viewing logs is useful for debugging configuration issues and monitoring the container.

## Remove the Container

Once you're finished with the lab, stop and remove the container.

Stop the container:

docker stop my-nginx

Remove the container:

docker rm my-nginx

The NGINX image will remain on your system, allowing you to create new containers without downloading the image again.

## Conclusion

Congratulations! 🎉

You have successfully deployed an **NGINX web server inside a Docker container using Puku CLI** .

Throughout this lab, you learned how to:

- Pull a Docker image from Docker Hub.
- Run an NGINX container.
- Map host ports to container ports.
- Mount a local directory to serve a custom HTML page.
- Verify that the container is running.
- Access the web server using both curl and the Puku CLI browser preview.
- View container logs for troubleshooting.
- Stop, restart, and remove Docker containers.

This exercise demonstrates how Docker provides a portable and reproducible environment for running web applications. Using **Puku CLI** , you can develop, test, and manage containerized applications directly from your browser without installing Docker locally.
