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

**Part 1**
**Basic Docker Concepts__image_000000_39e68af6226d7c9f358e7875c730cf800029a15e0a193e367c9cf7a0abe012ed_part1.png**
![Part 1](all_images/Basic Docker Concepts__image_000000_39e68af6226d7c9f358e7875c730cf800029a15e0a193e367c9cf7a0abe012ed_part1.png)
**Part 2**
**Basic Docker Concepts__image_000000_39e68af6226d7c9f358e7875c730cf800029a15e0a193e367c9cf7a0abe012ed_part2.png**
![Part 2](all_images/Basic Docker Concepts__image_000000_39e68af6226d7c9f358e7875c730cf800029a15e0a193e367c9cf7a0abe012ed_part2.png)

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

Docker will download the required image layers. Once the download is complete, the latest NGINX image will be available on your local machine.

**Expected Output**

You should see output similar to the following in the Puku CLI terminal:

**Basic Docker Concepts__image_000002_c40b3889b133ac72b0b44ed744890dcceefe1c0bbc070b02312622efbe61ce89.png**
![Image](all_images/Basic Docker Concepts__image_000002_c40b3889b133ac72b0b44ed744890dcceefe1c0bbc070b02312622efbe61ce89.png)

#### Verify the Download

To confirm that the image has been downloaded successfully, run:

docker images

**Basic Docker Concepts__image_000003_d3fc8307702e79a6b4cdc1b678530e15cf63a6a43cb7cca5084874114778b5b2.png**
![Image](all_images/Basic Docker Concepts__image_000003_d3fc8307702e79a6b4cdc1b678530e15cf63a6a43cb7cca5084874114778b5b2.png)

**Expected Output**

The command should list the nginx image with the latest tag.

**Basic Docker Concepts__image_000004_f79b74c4f53d0758a6232ef685c6d87d512cd25a9721e9864b096b5e07d1e03b.png**
![Image](all_images/Basic Docker Concepts__image_000004_f79b74c4f53d0758a6232ef685c6d87d512cd25a9721e9864b096b5e07d1e03b.png)

This format is much cleaner because the screenshots you capture from **Puku CLI** will naturally match the text in your documentation.

Here's the Puku CLI version with only the necessary changes. The commands stay the same except for the project path.

### Step 2: Create a Directory for Web Content

Open the **Puku CLI integrated terminal** and create a directory to store your custom HTML content. This directory will later be mounted into the NGINX container.

**Basic Docker Concepts__image_000005_a6eec19b9f1450b21498f87672dffe4d945b9f9ffedc98fb62d17983ab347e1d.png**
![Image](all_images/Basic Docker Concepts__image_000005_a6eec19b9f1450b21498f87672dffe4d945b9f9ffedc98fb62d17983ab347e1d.png)

This directory will act as the source for the web content served by the NGINX container, allowing you to update files without modifying the container itself.

### Step 3: Create a Simple Web Page

Create a simple HTML page inside the html directory by running the following command:

**Basic Docker Concepts__image_000006_39c020f80ffd0ac5e551a3081535353b2a89df210d92c855a519a4ff67ff0751.png**
![Image](all_images/Basic Docker Concepts__image_000006_39c020f80ffd0ac5e551a3081535353b2a89df210d92c855a519a4ff67ff0751.png)

This page will be served by the NGINX web server once the container is running.

### Step 4: Run the NGINX Container

From the **Puku CLI integrated terminal** , run the following command:

**Basic Docker Concepts__image_000007_0df2f31113b163049852f4c1946f45849f4473033ef58ba5d07deb057ce494e2.png**
![Image](all_images/Basic Docker Concepts__image_000007_0df2f31113b163049852f4c1946f45849f4473033ef58ba5d07deb057ce494e2.png)

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

## 

## Step 5: Verify the Setup

### Check Running Containers

Run the following command to confirm that the NGINX container is running:

**Basic Docker Concepts__image_000009_a2367ebb15710c3761d2368ce26d19dad75a0acf4735ef52268efc555a9695a0.png**
![Image](all_images/Basic Docker Concepts__image_000009_a2367ebb15710c3761d2368ce26d19dad75a0acf4735ef52268efc555a9695a0.png)

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

**Canny with Sobel Filter**
**dip1__image_000001_6b2a2aecf78dafd441f3adf18a857fa49a80e7232d98a4f09bda07851334f781_part1.png**
![Canny with Sobel Filter](all_images/dip1__image_000001_6b2a2aecf78dafd441f3adf18a857fa49a80e7232d98a4f09bda07851334f781_part1.png)
**Canny with Prewitt Filter**
**dip1__image_000001_6b2a2aecf78dafd441f3adf18a857fa49a80e7232d98a4f09bda07851334f781_part2.png**
![Canny with Prewitt Filter](all_images/dip1__image_000001_6b2a2aecf78dafd441f3adf18a857fa49a80e7232d98a4f09bda07851334f781_part2.png)
**Canny with Roberts Cross Filter**
**dip1__image_000001_6b2a2aecf78dafd441f3adf18a857fa49a80e7232d98a4f09bda07851334f781_part3.png**
![Canny with Roberts Cross Filter](all_images/dip1__image_000001_6b2a2aecf78dafd441f3adf18a857fa49a80e7232d98a4f09bda07851334f781_part3.png)

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

```
FIXED_LOW_THRESHOLD = 30 FIXED_HIGH_THRESHOLD = 90 kernel_sizes = [3, 5, 7] edges_ksize_comparison = [] for ksize in kernel_sizes: edges = custom_canny(gray_image, BEST_FILTER, ksize, FIXED_SIGMA, FIXED_LOW_THRESHOLD, FI edges_ksize_comparison.append(edges) plt.figure(figsize=(18, 6)) for i, ksize in enumerate(kernel_sizes): plt.subplot(1, len(kernel_sizes), i + 1) plt.imshow(edges_ksize_comparison[i], cmap='gray') plt.title(f'Kernel Size: {ksize}x{ksize}') plt.axis('off') plt.suptitle('Canny Edge Detection: Gaussian Kernel Size Comparison (Sobel Filter)', fontsize plt.tight_layout(rect=[0, 0.03, 1, 0.95]) plt.show()
```

**Kernel Size: 3x3**
**dip1__image_000002_88f56ae1b1c542bdc2f7dfcfa596deedff49ecb868129a11429e95b78d4f7b82_part1.png**
![Kernel Size: 3x3](all_images/dip1__image_000002_88f56ae1b1c542bdc2f7dfcfa596deedff49ecb868129a11429e95b78d4f7b82_part1.png)
**Kernel Size: 5x5**
**dip1__image_000002_88f56ae1b1c542bdc2f7dfcfa596deedff49ecb868129a11429e95b78d4f7b82_part2.png**
![Kernel Size: 5x5](all_images/dip1__image_000002_88f56ae1b1c542bdc2f7dfcfa596deedff49ecb868129a11429e95b78d4f7b82_part2.png)
**Kernel Size: 7x7**
**dip1__image_000002_88f56ae1b1c542bdc2f7dfcfa596deedff49ecb868129a11429e95b78d4f7b82_part3.png**
![Kernel Size: 7x7](all_images/dip1__image_000002_88f56ae1b1c542bdc2f7dfcfa596deedff49ecb868129a11429e95b78d4f7b82_part3.png)

## Sigma Value Tuning 

The impact of the sigma value (standard deviation of the Gaussian blur) on edge detection is investigated. A kernel size of 5x5 (selected from previous experiments for its balanced performance) is used, with fixed thresholds. Sigma values of 0.5, 1.0, and 1.5 are evaluated.

```
BEST_KSIZE_FOR_SIGMA_TUNING = 5 sigma_values = [0.5, 1.0, 1.5] edges_sigma_comparison = [] for sigma in sigma_values: edges = custom_canny(gray_image, BEST_FILTER, BEST_KSIZE_FOR_SIGMA_TUNING, sigma, FIXED_L edges_sigma_comparison.append(edges) plt.figure(figsize=(18, 6)) for i, sigma in enumerate(sigma_values): plt.subplot(1, len(sigma_values), i + 1) plt.imshow(edges_sigma_comparison[i], cmap='gray') plt.title(f'Sigma: {sigma}') plt.axis('off') plt.suptitle('Canny Edge Detection: Sigma Value Comparison (Sobel Filter)', fontsize=16) plt.tight_layout(rect=[0, 0.03, 1, 0.95])
```

**Sigma: 0.5**
**dip1__image_000003_1b2f0ecbd658fe2501663cad87e9b1d7f5a468eff25ff8376c0c2ad447a07d1c_part1.png**
![Sigma: 0.5](all_images/dip1__image_000003_1b2f0ecbd658fe2501663cad87e9b1d7f5a468eff25ff8376c0c2ad447a07d1c_part1.png)
**Sigma: 1.0**
**dip1__image_000003_1b2f0ecbd658fe2501663cad87e9b1d7f5a468eff25ff8376c0c2ad447a07d1c_part2.png**
![Sigma: 1.0](all_images/dip1__image_000003_1b2f0ecbd658fe2501663cad87e9b1d7f5a468eff25ff8376c0c2ad447a07d1c_part2.png)
**Sigma: 1.5**
**dip1__image_000003_1b2f0ecbd658fe2501663cad87e9b1d7f5a468eff25ff8376c0c2ad447a07d1c_part3.png**
![Sigma: 1.5](all_images/dip1__image_000003_1b2f0ecbd658fe2501663cad87e9b1d7f5a468eff25ff8376c0c2ad447a07d1c_part3.png)

## Threshold Pair Tuning 

This section explores the effect of varying low\_threshold and high\_threshold values, which are critical for determining strong and weak edges. The previously identified optimal kernel\_size and sigma values are maintained. Threshold pairs (0.03, 0.09), (0.05, 0.11), and (0.08, 0.16) are tested. Note that the custom Canny functions expect thresholds in the 0-255 range, necessitating scaling of the provided 0-1 range values.

```
BEST_KSIZE_FOR_THRESHOLD_TUNING = 5 BEST_SIGMA_FOR_THRESHOLD_TUNING = 1.0 threshold_pairs = [(0.03, 0.09), (0.05, 0.11), (0.08, 0.16)] edges_threshold_comparison = [] scaled_threshold_pairs = [] for low_t, high_t in threshold_pairs: scaled_low = int(low_t * 255) scaled_high = int(high_t * 255) scaled_threshold_pairs.append((scaled_low, scaled_high)) print(f"Original relative threshold pairs: {threshold_pairs}") print(f"Scaled absolute threshold pairs (low, high): {scaled_threshold_pairs}") for low_t, high_t in scaled_threshold_pairs: edges = custom_canny(gray_image, BEST_FILTER, BEST_KSIZE_FOR_THRESHOLD_TUNING, BEST_SIGMA edges_threshold_comparison.append(edges) plt.figure(figsize=(18, 6)) for i, (low_t_orig, high_t_orig) in enumerate(threshold_pairs): plt.subplot(1, len(threshold_pairs), i + 1) plt.imshow(edges_threshold_comparison[i], cmap='gray') plt.title(f'Thresholds: ({low_t_orig:.2f}, {high_t_orig:.2f})') plt.axis('off') plt.suptitle('Canny Edge Detection: Threshold Comparison (Sobel Filter)', fontsize=16) plt.tight_layout(rect=[0, 0.03, 1, 0.95]) plt.show()
```

**Thresholds: (0.03, 0.09)**
**dip1__image_000004_2e625d801c33b7155ee659cab4e48241db57b559175f46f7d5808fadbe992aa6_part1.png**
![Thresholds: (0.03, 0.09)](all_images/dip1__image_000004_2e625d801c33b7155ee659cab4e48241db57b559175f46f7d5808fadbe992aa6_part1.png)
**Thresholds: (0.05, 0.11)**
**dip1__image_000004_2e625d801c33b7155ee659cab4e48241db57b559175f46f7d5808fadbe992aa6_part2.png**
![Thresholds: (0.05, 0.11)](all_images/dip1__image_000004_2e625d801c33b7155ee659cab4e48241db57b559175f46f7d5808fadbe992aa6_part2.png)
**Thresholds: (0.08, 0.16)**
**dip1__image_000004_2e625d801c33b7155ee659cab4e48241db57b559175f46f7d5808fadbe992aa6_part3.png**
![Thresholds: (0.08, 0.16)](all_images/dip1__image_000004_2e625d801c33b7155ee659cab4e48241db57b559175f46f7d5808fadbe992aa6_part3.png)

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


**english__image_000000_6f908a88098ac838841104999bfe1747649cfafbc0acb0ba2a19733bfed24e8f.png**
![Image](all_images/english__image_000000_6f908a88098ac838841104999bfe1747649cfafbc0acb0ba2a19733bfed24e8f.png)

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

**Part 1**
**english__image_000001_68fef000f0eae4b7c86f474a6502eb3342265cc0d9b23eaca65e9e4f4e155791_part1.png**
![Part 1](all_images/english__image_000001_68fef000f0eae4b7c86f474a6502eb3342265cc0d9b23eaca65e9e4f4e155791_part1.png)
**Part 2**
**english__image_000001_68fef000f0eae4b7c86f474a6502eb3342265cc0d9b23eaca65e9e4f4e155791_part2.png**
![Part 2](all_images/english__image_000001_68fef000f0eae4b7c86f474a6502eb3342265cc0d9b23eaca65e9e4f4e155791_part2.png)
**Part 3**
**english__image_000001_68fef000f0eae4b7c86f474a6502eb3342265cc0d9b23eaca65e9e4f4e155791_part3.png**
![Part 3](all_images/english__image_000001_68fef000f0eae4b7c86f474a6502eb3342265cc0d9b23eaca65e9e4f4e155791_part3.png)
**Part 4**
**english__image_000001_68fef000f0eae4b7c86f474a6502eb3342265cc0d9b23eaca65e9e4f4e155791_part4.png**
![Part 4](all_images/english__image_000001_68fef000f0eae4b7c86f474a6502eb3342265cc0d9b23eaca65e9e4f4e155791_part4.png)

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

**english__image_000003_8e61b127eb4349ce4577a91991ee7c74967af64a5934db860877661cdd30926f.png**
![Image](all_images/english__image_000003_8e61b127eb4349ce4577a91991ee7c74967af64a5934db860877661cdd30926f.png)

→x

## Legistic Rogression Application:

BA obblA!Nd

- Probabilitg of having heart attack, (2) to predict whether an email is spar ornof.
- ③ Probabilitg of faileree of a Parcticuilar Protect.
- Democrate or Republican Panty boned on tesidence, occupation, 'income ete.
- (8) In NLP it's osed to determine the sentiment of movie review, Marcketings ,(8) outcome of amatch

9上

**english__image_000004_1cd87fe306291e246cab5ff05926e61987675086e3119ba62e0cba9151e371b7.png**
![Image](all_images/english__image_000004_1cd87fe306291e246cab5ff05926e61987675086e3119ba62e0cba9151e371b7.png)

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
