# Combined Document

_Generated from 4 source file(s) in `input_docs`._


---

## Source 1: `Basic Docker Concepts.md`


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

PROBLEMS  
DEBUG CONSOLE  
bash  
OUTPUT  
TERMINAL  
X  
iftakhar@iftakhar-PC:~/Poridhi$  
docker pull nginx  

Docker will download the required image layers. Once the download is complete, the latest NGINX image will be available on your local machine.

**Expected Output**

You should see output similar to the following in the Puku CLI terminal:

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

#### Verify the Download

To confirm that the image has been downloaded successfully, run:

docker images

**Basic Docker Concepts__image_000003_d3fc8307702e79a6b4cdc1b678530e15cf63a6a43cb7cca5084874114778b5b2.png**
![Image](all_images/Basic Docker Concepts__image_000003_d3fc8307702e79a6b4cdc1b678530e15cf63a6a43cb7cca5084874114778b5b2.png)

o  
docker  
iftakhar@iftakhar-PC:~/Poridhi$  
images  
0  

**Expected Output**

The command should list the nginx image with the latest tag.

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

This format is much cleaner because the screenshots you capture from **Puku CLI** will naturally match the text in your documentation.

Here's the Puku CLI version with only the necessary changes. The commands stay the same except for the project path.

### Step 2: Create a Directory for Web Content

Open the **Puku CLI integrated terminal** and create a directory to store your custom HTML content. This directory will later be mounted into the NGINX container.

iftakhar@iftakhar-PC:~/Poridhi$ mkdir -p r  
nginx-lab/html  
iftakhar@iftakhar-PC:~/Poridhi$  
_  

This directory will act as the source for the web content served by the NGINX container, allowing you to update files without modifying the container itself.

### Step 3: Create a Simple Web Page

Create a simple HTML page inside the html directory by running the following command:

iftakhar@iftakhar-PC:~/Poridhi$  
'<h1>Hello from NGINX running in Docker!</h1>'  
nginx-lab/html/index.html  
echo  

This page will be served by the NGINX web server once the container is running.

### Step 4: Run the NGINX Container

From the **Puku CLI integrated terminal** , run the following command:

iftakhar@iftakhar-PC:~/Poridhi$ docker run --name my-nginx  
-v $(pwd)/nginx-lab/html:/usr/share/nginx/html:ro  
-p 8000:80  
-d nginx  

**Note:** On Windows PowerShell, replace $(pwd) with ${PWD} if required.

#### Command Breakdown

- --name my-nginx – Assigns the name **my-nginx** to the container.
- -v $(pwd)/nginx-lab/html:/usr/share/nginx/html:ro – Mounts your local HTML directory into the container's web root in read-only mode.
- -p 8000:80 – Maps port **8000** on your machine to port **80** inside the container.
- -d nginx – Runs the NGINX container in detached mode.

**Expected Output**

If the command executes successfully, Docker will return a long container ID.

iftakhar@iftakhar-PC:~/Poridhi$ docker run --name my-nginx  
-v $(pwd)/nginx-lab/html:/usr/share/nginx/html:ro  
-p 50000:80  
-d nginx  
8106ee13f2aab334720b134d3b913e9b0a42f712b13d8fcbeba0b3150a0066bb  
iftakhar@iftakhar-PC:~/Poridhi$  

## 

## Step 5: Verify the Setup

### Check Running Containers

Run the following command to confirm that the NGINX container is running:

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

localhost:50000  
C  
三口  
Hello from NGINX  
running in Docker!  

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


---

## Source 2: `Untitled presentation.md`


INTERNET OF THINGS (IOT):

CONNECTING THE PHYSICAL

AND DIGITAL WORLD

COURSE: ADVANCED NETWORKING

UNIVERSITY OF TECHNOLOGY

2024

PAGE 1

What is IoT?

Physical objects embedded with sensors, software &amp; connectivity to exchange data over the internet. Term coined by Kevin Ashton, MIT, 1999. 15.9B connected devices in 2023 → 29.4B by 2030.

Data

Exchange

Real-time data transmission

Smart

Objects

Everyday devices become intelligent

Physical-

Digital

Bridges two worlds seamlessly

PAGE 2

History &amp; Evolution of IoT

1969–1999: Origins

• 1969: ARPANET — first networked computers

• 1982: CMU Coke Machine — first internet-connected device

• 1991: World Wide Web goes public

• 1999: Kevin Ashton coins "Internet of Things" at MIT

2000–2016: Growth Era

• 2007: iPhone launches — smartphones accelerate IoT

• 2011: IPv6 enables trillions of device addresses

• 2014: Amazon Echo — voice-controlled IoT enters homes

• 2016: Mirai Botnet hijacks 600,000+ IoT devices

2017–2030: Intelligent IoT

• 2020: 5G + Edge Computing deployed globally

• 2023: 15.9 billion connected devices worldwide

• 2025: TinyML &amp; AIoT — self-learning smart devices

• 2030: Quantum IoT Security + 29.4B devices projected

01

02

03

PAGE 3

How IoT Works

SENSE

Sensors detect physical data — temperature, motion, light, humidity. Smart thermostat reads room temperature and environmental conditions in real time.

CONNECT &amp; PROCESS

Data transmitted via Wi-Fi, Zigbee, LoRaWAN, or 5G. Edge or cloud platform analyzes the incoming sensor data stream instantly.

ACT

Automated response triggered — thermostat adjusts heating, alert sent to app. System responds without human intervention, closing the IoT loop.

01

02

03

PAGE 4


---

## Source 3: `dip1.md`


## Comparative Analysis of Canny Edge Detection 

This assignment conducts a comparative analysis of the Canny edge detection algorithm. The primary objectives are to evaluate the performance of different gradient filters and to investigate the impact of hyperparameter tuning on the resultant edge maps.

```
import cv2 import numpy as np import matplotlib.pyplot as plt image_path = '/content/sample_data/dip.webp' original_image = cv2.imread(image_path) if original_image is None: print(f"Error: Image not found at {image_path}. Please verify the path.") else: gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY) plt.figure(figsize=(8, 6)) plt.imshow(gray_image, cmap='gray') plt.title('Original Grayscale Image') plt.axis('off') plt.show() print("Setup complete: Image loaded and converted to grayscale.")
```

## Original Grayscale Image

**dip1__image_000000_18bf7451bd2650cc0b63c7659d15ae4f1b381866c7f785ab98fcd22ee146f8bf.png**
![Image](all_images/dip1__image_000000_18bf7451bd2650cc0b63c7659d15ae4f1b381866c7f785ab98fcd22ee146f8bf.png)

5  

Setup complete: Image loaded and converted to grayscale.

- Custom Canny Edge Detector Implementation 

As cv2.Canny() internally utilizes only the Sobel filter, a custom implementation of the Canny algorithm is necessary to compare various gradient filters (Sobel, Prewitt, Roberts Cross). This involves manually implementing Gaussian blurring, gradient calculation, non-maximum suppression (NMS), and double-threshold hysteresis. This approach ensures a consistent and comparable pipeline across all evaluated filters.

```
def gaussian_blur(image, kernel_size, sigma): return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma) def calculate_gradients(image, filter_type='sobel'): if filter_type == 'sobel': Gx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3) Gy = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3) elif filter_type == 'prewitt': kernel_x = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32) kernel_y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32) Gx = cv2.filter2D(image, cv2.CV_64F, kernel_x) Gy = cv2.filter2D(image, cv2.CV_64F, kernel_y) elif filter_type == 'roberts': kernel_x = np.array([[1, 0], [0, -1]], dtype=np.float32) kernel_y = np.array([[0, 1], [-1, 0]], dtype=np.float32) Gx = cv2.filter2D(image, cv2.CV_64F, kernel_x) Gy = cv2.filter2D(image, cv2.CV_64F, kernel_y) else: raise ValueError("Invalid filter_type. Choose 'sobel', 'prewitt', or 'roberts'.") magnitude = np.sqrt(Gx**2 + Gy**2) magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U) direction = np.arctan2(Gy, Gx) return magnitude, direction def non_maximum_suppression(magnitude, direction): rows, cols = magnitude.shape output = np.zeros_like(magnitude, dtype=np.uint8) angle = direction * 180. / np.pi angle[angle < 0] += 180 for i in range(1, rows - 1): for j in range(1, cols - 1): q = 255 r = 255 if (0 <= angle[i, j] < 22.5) or (157.5 <= angle[i, j] <= 180): q = magnitude[i, j + 1] r = magnitude[i, j - 1] elif (22.5 <= angle[i, j] < 67.5): q = magnitude[i + 1, j - 1] r = magnitude[i - 1, j + 1] elif (67.5 <= angle[i, j] < 112.5): q = magnitude[i + 1, j] r = magnitude[i - 1, j] elif (112.5 <= angle[i, j] < 157.5): q = magnitude[i - 1, j - 1] r = magnitude[i + 1, j + 1] if (magnitude[i, j] >= q) and (magnitude[i, j] >= r): output[i, j] = magnitude[i, j] else: output[i, j] = 0 return output
```

```
def double_threshold_hysteresis(image, low_threshold, high_threshold): image = image.astype(np.float32) rows, cols = image.shape output = np.zeros_like(image, dtype=np.uint8) strong_i, strong_j = np.where(image >= high_threshold) weak_i, weak_j = np.where((image >= low_threshold) & (image < high_threshold)) output[strong_i, strong_j] = 255 output[weak_i, weak_j] = 75 for i in range(1, rows - 1): for j in range(1, cols - 1): if output[i, j] == 75: if ((output[i + 1, j - 1] == 255) or (output[i + 1, j] == 255) or (output[i + or (output[i, j - 1] == 255) or (output[i, j + 1] == 255) or (output[i - 1, j - 1] == 255) or (output[i - 1, j] == 255) or (output[ output[i, j] = 255 else: output[i, j] = 0 return output def custom_canny(image, filter_type, gaussian_ksize, sigma, low_threshold, high_threshold): blurred_image = gaussian_blur(image, gaussian_ksize, sigma) magnitude, direction = calculate_gradients(blurred_image, filter_type) nms_output = non_maximum_suppression(magnitude, direction) final_edges = double_threshold_hysteresis(nms_output, low_threshold, high_threshold) return final_edges print("Custom Canny components (Gaussian blur, gradient calculation, NMS, Hysteresis) defined Custom Canny components (Gaussian blur, gradient calculation, NMS, Hysteresis) defined.
```

## Task 1: Gradient Filter Comparison 

The Canny edge detection algorithm is applied using three distinct gradient filters: Sobel, Prewitt, and Roberts Cross. To ensure a fair comparison, Gaussian kernel size, sigma, and threshold values are maintained constant across all three filters.

```
GAUSSIAN_KSIZE = 5 SIGMA = 1.0 LOW_THRESHOLD = 30 HIGH_THRESHOLD = 90 sobel_edges = custom_canny(gray_image, 'sobel', GAUSSIAN_KSIZE, SIGMA, LOW_THRESHOLD, HIGH_TH prewitt_edges = custom_canny(gray_image, 'prewitt', GAUSSIAN_KSIZE, SIGMA, LOW_THRESHOLD, HIG roberts_edges = custom_canny(gray_image, 'roberts', GAUSSIAN_KSIZE, SIGMA, LOW_THRESHOLD, HIG plt.figure(figsize=(18, 6)) plt.subplot(1, 3, 1) plt.imshow(sobel_edges, cmap='gray') plt.title('Canny with Sobel Filter') plt.axis('off') plt.subplot(1, 3, 2) plt.imshow(prewitt_edges, cmap='gray') plt.title('Canny with Prewitt Filter')
```

plt.axis('off')  
plt.subplot(1, 3, 3)  
plt.imshow(roberts_edges, cmap='gray')  
plt.title('Canny with Roberts Cross Filter')  
plt.axis('off')  
plt.suptitle('Gradient Filter Comparison for Canny Edge Detection', fontsize=16)  
plt.tight_layout(rect=[0, 0.03, 1, 0.95])  
plt.show()  
Gradient Filter Comparison for Canny Edge Detection  
Canny with Prewitt Filter  
Canny with Roberts Cross Filter  
Canny with Sobel Filter  

## Comparison Summary of Gradient Filters:

- Sobel Filter: Produced strong, continuous edges, effectively outlining primary subjects with good noise handling. Its 3x3 kernel provides a balanced approach to noise suppression and detail retention.
- Prewitt Filter: Exhibited performance similar to Sobel, with comparable edge continuity, though edges appeared marginally less defined in certain areas.
- Roberts Cross Filter: Demonstrated high sensitivity due to its 2x2 kernel, detecting fine details but also exacerbating noise. This resulted in thinner, fragmented, and jagged edges, indicating high susceptibility to noise.

Conclusion: The Sobel filter provided the most effective and clean edge map for the given image, achieving an optimal balance between edge strength, continuity, and noise suppression. Therefore, the Sobel filter will be utilized for subsequent hyperparameter tuning in Task 2.

## Task 2: Hyperparameter Tuning (using Sobel Filter) 

Following the selection of the Sobel filter, this section focuses on tuning Canny's hyperparameters. This process aims to understand the influence of each parameter on the final edge map and to identify optimal settings for the image.

## Gaussian Kernel Size Tuning 

This experiment evaluates the effect of varying Gaussian blur kernel sizes on edge detection. Kernel sizes of 3x3, 5x5, and 7x7 are tested, while maintaining constant sigma and threshold values, to assess their impact on smoothing levels.

```
BEST_FILTER = 'sobel' FIXED_SIGMA = 1.0
```

**dip1__image_000002_88f56ae1b1c542bdc2f7dfcfa596deedff49ecb868129a11429e95b78d4f7b82.png**
![Image](all_images/dip1__image_000002_88f56ae1b1c542bdc2f7dfcfa596deedff49ecb868129a11429e95b78d4f7b82.png)

Canny Edge Detection: Gaussian Kernel Size Comparison (Sobel Filter)  
Kernel Size: 3x3  
Kernel Size: 5x5  
Kernel Size: 7x7  

## Sigma Value Tuning 

The impact of the sigma value (standard deviation of the Gaussian blur) on edge detection is investigated. A kernel size of 5x5 (selected from previous experiments for its balanced performance) is used, with fixed thresholds. Sigma values of 0.5, 1.0, and 1.5 are evaluated.

**dip1__image_000003_1b2f0ecbd658fe2501663cad87e9b1d7f5a468eff25ff8376c0c2ad447a07d1c.png**
![Image](all_images/dip1__image_000003_1b2f0ecbd658fe2501663cad87e9b1d7f5a468eff25ff8376c0c2ad447a07d1c.png)

plt.show()  
Canny Edge Detection: Sigma Value Comparison (Sobel Filter)  
Sigma: 0.5  
Sigma:1.5  
Sigma: 1.0  

## Threshold Pair Tuning 

This section explores the effect of varying low\_threshold and high\_threshold values, which are critical for determining strong and weak edges. The previously identified optimal kernel\_size and sigma values are maintained. Threshold pairs (0.03, 0.09), (0.05, 0.11), and (0.08, 0.16) are tested. Note that the custom Canny functions expect thresholds in the 0-255 range, necessitating scaling of the provided 0-1 range values.

**dip1__image_000004_2e625d801c33b7155ee659cab4e48241db57b559175f46f7d5808fadbe992aa6.png**
![Image](all_images/dip1__image_000004_2e625d801c33b7155ee659cab4e48241db57b559175f46f7d5808fadbe992aa6.png)

Original relative threshold pairs: [(0.03, 0.09), (0.05, 0.11), (0.08, 0.16)]  
Scaled absolute threshold pairs (low, high): [(7, 22), (12, 28), (20, 40)]  
Canny Edge Detection: Threshold Comparison (Sobel Filter)  
Thresholds: (0.03, 0.09)  
Thresholds: (0.05, 0.11)  
Thresholds: (0.08,0.16)  

## Final Optimized Edge Map 

Based on the comprehensive hyperparameter tuning, the optimal Canny parameters are applied to generate the final, most effective edge map for the given image.

```
OPTIMUM_KSIZE = 5 OPTIMUM_SIGMA = 1.0 OPTIMUM_LOW_THRESHOLD = int(0.05 * 255) OPTIMUM_HIGH_THRESHOLD = int(0.11 * 255) print("Selected Optimum Parameters:") print(f"  Gradient Filter: {BEST_FILTER.capitalize()}") print(f"  Gaussian Kernel Size: {OPTIMUM_KSIZE}x{OPTIMUM_KSIZE}") print(f"  Sigma Value: {OPTIMUM_SIGMA}") print(f"  Low Threshold: {OPTIMUM_LOW_THRESHOLD} (relative ~0.05)") print(f"  High Threshold: {OPTIMUM_HIGH_THRESHOLD} (relative ~0.11)") print("--------------------------------------------------") final_best_edges = custom_canny(gray_image, BEST_FILTER, OPTIMUM_KSIZE, OPTIMUM_SIGMA, OPTIMUM_ plt.figure(figsize=(8, 6)) plt.imshow(final_best_edges, cmap='gray') plt.title('Final Best Edge Map (Optimum Parameters)') plt.axis('off') plt.show()
```

Selected Optimum Parameters: Gradient Filter: Sobel Gaussian Kernel Size: 5x5 Sigma Value: 1.0 Low Threshold: 12 (relative ~0.05)

High Threshold: 28 (relative ~0.11)

--------------------------------------------------

Final Best Edge Map (Optimum Parameters)

**dip1__image_000005_6e5b120aad826372e366096ae820fe295881cdcbdc3edaaa6994a5b6a66fd306.png**
![Image](all_images/dip1__image_000005_6e5b120aad826372e366096ae820fe295881cdcbdc3edaaa6994a5b6a66fd306.png)


---

## Source 4: `english.md`


Set-04  

Regrossion:

Regresion aralysis is a foreom ofPredictive modeling techriue cohich investigalas the relationship botaron a dependent and independentvartiable.

-mainty used fore Prediting &amp;. forcaoting.

Regression

Linearc

maps a continjous f of 2

logistic

maps a continjous xto biniary (TruelPalse

Linear Rogression: 1 a Prcedictive modecing tecmique.

- attempts to model the relationstip betcveen. tewa varciables by titting a linear equation to the observed data.
- one varciable is called - Exploratory verciable
- Other Varciable is called - dependent varciasle
- the best fil- line coould be the line cohice hes the least differuence betweer the estimated ralne annd actal vare.

copaodop=  
sw  
Linearc Rigresiion  
→ ①Dependent.(we Predict thevalt  
Tao variable  
②Independent  
x= independert  
122d  
2  
i6=mxc=slope  
tibo  
C=intercept  
bmp  
2ev byilpib2asued  
Simple linearc Regression.'  
y=do+dixc  
boen wdi = Regressim co-efficent  
moltile linearc egression2dN independentvar.  
J= defendent Var.  
y=20+d1x22  
sust  
6.mp  
for preediction?  
How linear Regression Corks  
Lirar Rogrcenim Performs the tok to preedict a dependent  
Varciable()bared onagirer indeperdentvarciable:S0,  
2M3)  
Hhis regression fechnique finds out ar linear relatimship  
between Cintut) and outplty. ba  
Hypotheis functim for linear tegressi:i  
CV  
b~~  
690  
=xo+xx  
∑(x-x)(y-9)  
wis fik fead 20  
Niv22v  
∑(x-x)2  
Here; doE intercept INibi  
222  
=coefficientof  
trvot?  
once, we find the best do and i yalues, we yoiu  
get tee bost fit Line, sg wher we are finally using  
our model Predictim, it will Predict the Vaine  
of y for tne ingnt valne of x,  

sitls

TOV

for the best fit line wke need to update tue

valweofdo and d,to farabo sjbal

cost function (J): By achieving tue best fit rugressim line, the model aims to Predict y valves sveh that ther error differenc between predictied value and. true valut is minimurn, so we need to update tue vahe of doi dp to reach best value tuat minimize fcobmpb valwe and tove (Y) value,

cost function (J) of linear regressim and treevahely),

## Scoilsibunf one (Predyi) =f fueqiet qoteoqce n 1=1 edl·cmost aiom

the Root mean squered. Error (RMSE) beth Predicted Valye(y)

to update do and xi. valun in order to reduce cost functian and achieving tue best fit line the model uses aradient Pescerti. the idee is to start with randimnt koilknd di vaiwes reaching ininin t, d tit fod t o fibaa7 1ic H mifoibsi 1abom 1

|   x |   R | (x-x)   |    |       | (y-y)1(x-x(x-元)0-5)   | g       | (-y)        |
|-----|-----|---------|----|-------|-----------------------|---------|-------------|
|   1 |   2 | -2      | -2 | 4     | 4 2.8                 | 0.8     | (9-y)2 0.64 |
|   2 |   4 | -1      |  0 | 1     | 0                     | 0.C     | 0.36        |
|   3 |   5 | Q       |  1 | 0     | 3.4 4                 |         |             |
|   4 |   4 | 1       |  0 | 0 1 0 | 4,6                   | -1      | 1           |
|   5 |   5 | 2       |  1 | 4 2   | 5.2                   | 0.6 0,2 | 75.0 he,g   |

<!-- formula-not-decoded -->

Linear regression, &lt;0 =x0+x1x

<!-- formula-not-decoded -->

do can be calculated using thecordinate (x,7)= (3.4)

<!-- formula-not-decoded -->

∴ y = 2.2 + 0.6Xx, which is the regression line.

Now, error=

∑(g-y)

n-2

**english__image_000002_d9d0b8e98957249d3c8c4af2407bb20a61dd5687a737e50d404a6aef419a9075.png**
![Image](all_images/english__image_000002_d9d0b8e98957249d3c8c4af2407bb20a61dd5687a737e50d404a6aef419a9075.png)

5  
4  
2  
5  
2  

0.89

J8:0

- D Business ften uselineac regression to understima the relationship betwveen adverctising spending &amp; revenue. 0

22.0

po.o

- 2) Medical tieseatechere use lineate treg ten im to anderstarid therelatinship! betaween draug dosage &amp; blood prasurce of a Patienl=x 27211
2. 3 Agricultarel scientists use Linear reegrerin to meanurce the effect tof fertilizer s cwaterilon (已-巳)(x-0)子 Crcop yeilds, x= 2.0 01 (x-K)3
3. futurce montrs. (AC)(④)Foreccooting
4. Price on riumber of sales. Impact of produet 2.0+0x=P&lt; 6 SC=Ox

P8.0

~(P-e)3

fo      e Predictive analysis?

Logistic regressin is a method which falls unden supervised ML algorithm, It is used to predict the binary outcomes for a given set of independent variable, The dependent variable outeome is discreate.

109 of odds as Logistic regressimn uses

dependentveriasu

the

logisticeregressianieavation,.

3.0

<!-- formula-not-decoded -->

function on lirean ploweis t bulddo b gethted togistico relgression orst2 ei lioris arp gedtadw toibat of Sigmoid function; P n 1+e

where,

y

tb2o toibt (A)

os radtedes

0051d0999

ro t2ibif

at~10m

V

te09

213

2eiaraolob of bo20 2ti

Divonr

amaobvo(2).

t0

tosit0s2

x ()

dabamrp The output of tue logistic regressin is a Sigmoid curve. there are onry 2 Possizk value to make our predictimi fse

Probabilit  
1  
0<d  
outcome=(1)(trne)  
s-curue  
thresho'dvalue20.5  
0.5  
Probability <015  
5xs+  
outcome =0 (False)  
5  
3  
78  
4  

→x

## Legistic Rogression Application:

BA obblA!Nd

- Probabilitg of having heart attack, (2) to predict whether an email is spar ornof.
- ③ Probabilitg of faileree of a Parcticuilar Protect.
- Democrate or Republican Panty boned on tesidence, occupation, 'income ete.
- (8) In NLP it's osed to determine the sentiment of movie review, Marcketings ,(8) outcome of amatch

9上

(9)Handwrciting  
recognition - matched ore not matched.  
Linearc  
bLogistic  
(4) Models data using  
mumeric. value.  
values.  
® Linearc reelationship beth  
(2) Not reeqairced.  
dependent & independent  
varciable is reequirced,  
(3) The Probability is  
(③) the data is modelled usikg  
rcepreserted as a linearfunction  
a straight line.  
(D Independent varcables  
(A) Must be correlated  
Can be correlated with  
with eacrother.  
eacn other.  
Logistic regresslon ean:  
5) Lineare Feegressin equation  
5)  
P  
J=xotd1x  
in  
20+01℃  
-  
6  
1  
Q  
↑  
(3)  
1  
.3  
0.5  
2  
一  
0  
0  
2  
3  
8.Erronrminimizatian  
(8) Error miniznizatin  
techniane..  
fcchnique:  
logistic loss function.  
leont square metnod  

## Linear Regression!

## Advantage:

- Modeling speed is fast
- -reuns fort aith large amount of dataset.

## Disaduartage:

- Non-lineate data can't be ciell fited
- Can be overcfiHted.

## Legistic Ragression:

## Advantage:

- veryefficien L asttas resources.

doesr't reequitce features to be scaled.

- ensty to implement &amp; train J 十0 =

## Disadvantege:

- D (3) Can't solve non-linear pooblem
- — Aecurcaay not so high.
- camn predict only catagooical outeome.
- to overfitting srrarlns—

bubbom

## clamificatim

- D The output is a class on catagory.
- 2) Evaluating by mearsurirg aocuracy.
- (③) Algo: Decision-tree, kNN
- 4)The depen dent variable
- are Unordered.

## Igesion

- (4) -the output is nurerla value
- (2) fvalua-ted by leastsquare method.
3. 3 linear, Logistic regression.
- (4) dependent Vanicsu are ordeved,
