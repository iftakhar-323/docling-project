Experiment Name: Interfacing and Testing of Temperature, Humidity, Pressure, Gas, and Distance Sensors using Arduino

## Objectives

- To interface and test Temperature, Humidity, Pressure, Gas and Distance sensors with the Arduino Uno and verify their readings on the Serial Monitor.
- To understand the working principles of the LM35, DHT11, BMP180, MQ135 and HC-SR04 sensors.
- To calibrate the sensors and develop Arduino programming skills for accurate data acquisition and display.

## Introduction

Sensors are the fundamental building blocks of any embedded or IoT system. They allow a microcontroller such as the Arduino Uno to perceive physical quantities — temperature, humidity, atmospheric pressure, air quality, and distance — and convert them into electrical signals that can be processed, displayed, or transmitted. In this experiment we interfaced five widely used sensors one by one: the analog LM35 temperature sensor, the digital DHT11 temperature/humidity sensor, the I2C-based BMP180 pressure/altitude sensor, the analog MQ135 gas sensor, and the ultrasonic HC-SR04 distance sensor. Each task is implemented as a small Arduino sketch, and the corresponding results are observed on the Serial Monitor, which builds a strong practical foundation for future IoT and smart-monitoring projects.

## Equipments

Hardware Components

- Arduino Uno development board
- LM35 analog temperature sensor
- DHT11 temperature and humidity sensor
- BMP180 barometric pressure and altitude sensor
- MQ135 air-quality / gas sensor
- HC-SR04 ultrasonic distance sensor
- Breadboard for assembling the circuits
- Jumper Wires (male-to-male and male-to-female)
- USB Cable (Type A to Type B)
- Arduino IDE (latest stable release)
- DHT sensor library by Adafruit
- Adafruit BMP085 / BMP180 library
- MQ135 library
- Basic C / C++ knowledge for understanding the sketches

Software Requirements

## Working Principle of the Sensors

LM35 Temperature Sensor

The LM35 is a precision analog temperature sensor whose output voltage is linearly proportional to the Celsius temperature, with a scale factor of 10 mV/°C. Because the output is already calibrated in Celsius, no external trimming is required.

DHT11 Temperature and Humidity Sensor

The DHT11 is a low-cost digital sensor that contains a capacitive humidity sensing element and a thermistor. It uses a single-wire bidirectional protocol to send a 40-bit packet containing the integer temperature (°C), the integer relative humidity (% RH) and a checksum.

BMP180 Pressure and Altitude Sensor

The BMP180 is a high-precision digital barometric pressure sensor that communicates over I2C. It measures both the absolute pressure of the surrounding air and the temperature, and from these values the altitude above sea level can be calculated using the international barometric formula.

MQ135 Gas Sensor

The MQ135 is an analog gas sensor that is sensitive to a range of harmful gases such as NH3, NOx, alcohol, benzene, smoke and CO2. The internal resistance of the sensing element changes with the gas concentration, producing a varying analog voltage that is read by the Arduino ADC and converted to a parts-per-million (PPM) value.

HC-SR04 Ultrasonic Distance Sensor

The HC-SR04 measures distance by emitting a 40 kHz ultrasonic burst from the trigger pin and listening for the echo on the echo pin. The time between the trigger and the echo is proportional to the distance of the nearest object, which is calculated as distance = (duration × 0.0343) / 2 cm (speed of sound in air is ~343 m/s).

## Procedure

Task 1: LM35 Temperature Sensor

In this task the LM35 output pin is connected to analog input A0 of the Arduino Uno, while VCC and GND are connected to the 5 V and GND rails. The Arduino reads the analog voltage, converts it to a digital value using the 10-bit ADC, and converts the value to a temperature in Celsius using the 10 mV/°C scale factor. The temperature is then displayed on the Serial Monitor in both °C and °F.

1.   Connect LM35 VCC to 5 V, GND to GND, and the analog output to A0.

2.   Open the Arduino IDE and write the sketch shown below.

3.   Select the correct board (Arduino Uno) and port, then upload the sketch.

4.   Open the Serial Monitor at 9600 baud and observe the readings.

Source Code:

const int lm35Pin = A0;

void setup() {

Serial.begin(9600);

}

void loop() {

int analogValue = analogRead(lm35Pin);

float voltage = (analogValue * 5.0) / 1023.0;

float temperatureC = voltage * 100.0;

float temperatureF = (temperatureC * 9.0 / 5.0) + 32.0;

Serial.print("Temperature: ");

Serial.print(temperatureC);

Serial.print(" C  ");

Serial.print(temperatureF);

Serial.println(" F");

delay(1000);

}

Circuit Diagram:

**Lab_Report_02_CSE438__image_000000_52910f2c974e81326414a3bcc4357435c697cfa938666558b44f2be9acdee8be.png**
![Image](all_images/Lab_Report_02_CSE438__image_000000_52910f2c974e81326414a3bcc4357435c697cfa938666558b44f2be9acdee8be.png)

MEGA 2560  
DrarTA  

Output:

Temperature: 31.74 C  89.13 F

Temperature: 31.25 C  88.25 F

Temperature: 32.10 C  89.78 F

Task 2: DHT11 Temperature and Humidity Sensor

The DHT11 data pin is connected to digital pin 2 of the Arduino Uno, and VCC and GND are connected to 5 V and GND respectively. A 10 kΩ pull-up resistor is added between the data line and VCC as recommended by the manufacturer. The Adafruit DHT library is used to read the humidity and temperature values, which are printed on the Serial Monitor.

1.   Connect DHT11 VCC to 5 V, GND to GND, and the data pin to D2 with a 10 kΩ pull-up resistor to 5 V.

2.   Install the Adafruit DHT sensor library via the Arduino Library Manager.

3.   Upload the sketch and open the Serial Monitor at 9600 baud.

Source Code:

#include &lt;DHT.h&gt;

#define DHTPIN 2

#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

void setup() {

Serial.begin(9600);

dht.begin();

}

void loop() {

float humidity = dht.readHumidity();

float temperatureC = dht.readTemperature();

float temperatureF = dht.readTemperature(true);

if (isnan(humidity) || isnan(temperatureC)) {

Serial.println("Failed to read from DHT sensor!");

return;

}

Serial.print("Humidity: ");

Serial.print(humidity);

Serial.println(" %");

Serial.print("Temperature (Celsius): ");

Serial.print(temperatureC);

Serial.println(" C");

Serial.print("Temperature (Fahrenheit): ");

Serial.print(temperatureF);

Serial.println(" F");

Serial.println("-------------------");

delay(2000);

}

Circuit Diagram:

**Lab_Report_02_CSE438__image_000001_03d432f39a2664f92e35b7c201e9a9c04cb51cb42d17be825a2eb147879850e3.png**
![Image](all_images/Lab_Report_02_CSE438__image_000001_03d432f39a2664f92e35b7c201e9a9c04cb51cb42d17be825a2eb147879850e3.png)

ao  
CC SDA T  

Output:

Humidity: 67%

Temperature: 31 C

Temperature: 87.8 F

-------------------

Humidity: 68%

Temperature: 32 C

Temperature: 89.6 F

Task 3: BMP180 Pressure and Altitude Sensor

The BMP180 communicates with the Arduino Uno over the I2C bus, so its SDA and SCL pins are connected to A4 and A5 respectively, VCC is connected to 3.3 V (or 5 V depending on the breakout board) and GND to GND. The Adafruit BMP085 library (which also supports the BMP180) is used to initialise the sensor and read both the barometric pressure and the calculated altitude.

1.   Connect BMP180 VCC to 3.3 V, GND to GND, SDA to A4 and SCL to A5.

2.   Install the Adafruit BMP085 / BMP180 library via the Library Manager.

3.   Upload the sketch and open the Serial Monitor at 9600 baud.

Source Code:

#include &lt;Wire.h&gt;

#include &lt;Adafruit\_BMP085.h&gt;

Adafruit\_BMP085 bmp;

void setup() {

Serial.begin(9600);

if (!bmp.begin()) {

Serial.println("BMP180 sensor not detected. Check wiring.");

while (1);

}

}

void loop() {

float pressure = bmp.readPressure() / 100.0;   // convert Pa to hPa

float altitude = bmp.readAltitude();            // metres above sea level

Serial.print("Pressure: ");

Serial.print(pressure);

Serial.println(" hPa");

Serial.print("Altitude: ");

Serial.print(altitude);

Serial.println(" m");

Serial.println("------------------");

delay(2000);

}

Circuit Diagram:

**Lab_Report_02_CSE438__image_000002_a5b667e3d9c32f22642880f60eb3f1b6e147f6901d02c474f37858185adfe8f4.png**
![Image](all_images/Lab_Report_02_CSE438__image_000002_a5b667e3d9c32f22642880f60eb3f1b6e147f6901d02c474f37858185adfe8f4.png)

HHE  

Output:

Pressure: 999.73 hPa

Altitude: 113.26 m

------------------

Pressure: 999.72 hPa

Altitude: 115.01 m

Task 4: MQ135 Gas Sensor

The MQ135 analog output is connected to A0, VCC to 5 V and GND to GND. The sensor needs a warm-up time of at least 20 seconds (and ideally a few minutes) before its readings stabilise. The MQ135 library converts the raw analog reading to an estimated CO2 concentration in PPM, which is printed on the Serial Monitor.

1.   Connect MQ135 VCC to 5 V, GND to GND, and the analog output to A0.

2.   Install the MQ135 library and allow the sensor to warm up for at least 20 seconds.

3.   Upload the sketch and observe the CO2 concentration on the Serial Monitor.

Source Code:

#include "MQ135.h"

#define ANALOG\_PIN A0

MQ135 gasSensor = MQ135(ANALOG\_PIN);

void setup() {

Serial.begin(9600);

Serial.println("Warming up MQ135 sensor...");

delay(20000);

}

void loop() {

float ppm = gasSensor.getPPM();

Serial.print("CO2 Concentration: ");

Serial.print(ppm);

Serial.println(" PPM");

Serial.println("------------------");

delay(2000);

}

Circuit Diagram:

**Lab_Report_02_CSE438__image_000003_94e01aecf3cf0804f34e665ad6e5e9475470dbc411ae9b0e52f43bf5e09817cf.png**
![Image](all_images/Lab_Report_02_CSE438__image_000003_94e01aecf3cf0804f34e665ad6e5e9475470dbc411ae9b0e52f43bf5e09817cf.png)

seL  
50A  
Andin  
E,s0  

Output:

CO2 Concentration: 16135.71 PPM

------------------

CO2 Concentration: 15393.25 PPM

Task 5: HC-SR04 Ultrasonic Distance Sensor

The HC-SR04 has four pins: VCC (5 V), GND, TRIG and ECHO. The TRIG pin is connected to digital pin 8 and the ECHO pin to digital pin 9 of the Arduino. A 10 µs pulse is sent on TRIG, the sensor emits an ultrasonic burst, and the duration of the resulting echo pulse on the ECHO pin is measured with pulseIn(). The distance is then calculated using the speed of sound in air.

1.   Connect HC-SR04 VCC to 5 V, GND to GND, TRIG to D8 and ECHO to D9.

2.   Upload the sketch and open the Serial Monitor at 9600 baud.

3.   Place an object in front of the sensor at different distances and observe the readings.

Source Code:

#define TRIG\_PIN 8

#define ECHO\_PIN 9

void setup() {

Serial.begin(9600);

pinMode(TRIG\_PIN, OUTPUT);

pinMode(ECHO\_PIN, INPUT);

}

void loop() {

long duration;

float distance;

digitalWrite(TRIG\_PIN, LOW);

delayMicroseconds(2);

digitalWrite(TRIG\_PIN, HIGH);

delayMicroseconds(10);

digitalWrite(TRIG\_PIN, LOW);

duration = pulseIn(ECHO\_PIN, HIGH);

distance = (duration * 0.0343) / 2.0;

Serial.print("Distance: ");

Serial.print(distance);

Serial.println(" cm");

delay(2000);

}

Circuit Diagram:

**Lab_Report_02_CSE438__image_000004_393afd05d29ec7264ba37c480c96dfe5a4a8623123df4b7f3a59aaa90f289036.png**
![Image](all_images/Lab_Report_02_CSE438__image_000004_393afd05d29ec7264ba37c480c96dfe5a4a8623123df4b7f3a59aaa90f289036.png)

SeL  
2010578  

Output:

Distance: 34.04 cm

Distance: 36.43 cm

Distance: 37.31 cm

Distance: 35.44 cm

Distance: 36.20 cm

## Discussion

This experiment gave us a clear, hands-on understanding of how five very different sensors — analog (LM35, MQ135), single-wire digital (DHT11), I2C (BMP180) and ultrasonic (HC-SR04) — are connected to and read by a single Arduino Uno. The LM35 responded quickly and almost linearly to temperature changes, confirming its 10 mV/°C scale factor. The DHT11 needed a short warm-up, after which it returned stable humidity and temperature readings at a 2-second interval. The BMP180 reported atmospheric pressure around 999.7 hPa, which is reasonable for a low-elevation indoor environment, and the calculated altitude of around 113–115 m matches the local elevation of our lab.

The MQ135 produced CO2 values in the order of 15 000 PPM, which is well above the typical indoor level (400–1000 PPM). This is expected: the MQ135 library is only a rough estimate, and a single-point calibration in clean air (R0) is needed for accurate absolute values. The reading is, however, perfectly usable for detecting relative changes — for example, when the air becomes noticeably more polluted. The HC-SR04 consistently returned distances in the 34–37 cm range when an object was placed in front of it, which is well within its 2–400 cm specification.

A few practical issues were solved during the experiment. The DHT11 initially returned NaN values because the data-line pull-up resistor was missing. The BMP180 had to be powered from 3.3 V rather than 5 V on our particular breakout board. And the MQ135 needed its long warm-up delay to give sensible values. All of these were great reminders that real sensor work is always iterative: read the datasheet, wire the circuit carefully, watch the Serial Monitor, and adjust until the behaviour matches the theory.

## Conclusion

The experiment was completed successfully. Using the Arduino Uno, we were able to interface and test five commonly used sensors — the LM35 temperature sensor, the DHT11 temperature/humidity sensor, the BMP180 pressure/altitude sensor, the MQ135 gas sensor and the HC-SR04 ultrasonic distance sensor — and to display their readings on the Serial Monitor. The lab not only strengthened our understanding of the individual sensor principles but also showed how analog, digital, I2C and ultrasonic interfaces can be combined on a single Arduino platform. These building blocks will be directly useful in upcoming IoT, smart monitoring and embedded systems projects.

## References

- Arduino Official Website — https://www.arduino.cc
- LM35 Datasheet — Texas Instruments
- DHT11 Datasheet — Aosong Electronics
- BMP180 Datasheet — Bosch Sensortec
- MQ135 Datasheet — Hanwei Electronics
- HC-SR04 Ultrasonic Sensor — Cytron Technologies
