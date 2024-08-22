#include <Wire.h>
#include <AHT20.h>

AHT20 aht20;

void setup() {
  Serial.begin(115200);
  Wire.begin(); // Join I2C bus

  // Initialize the AHT20 sensor
  if (aht20.begin() == false) {
    Serial.println("AHT20 not detected. Please check wiring. Freezing.");
    while (1);
  }
}

void loop() {
  static unsigned long previousMillis = 0;
  unsigned long currentMillis = millis();

  // If a new measurement is available
  if (aht20.available() == true) {
    // Get the new temperature and humidity value
    float temperature = aht20.getTemperature();
    float humidity = aht20.getHumidity();

    // Send the results over Serial every second
    if (currentMillis - previousMillis >= 1000) { // 每秒
      previousMillis = currentMillis;

      // Print the results to Serial Monitor
      Serial.print(temperature, 2);
      Serial.print(" ");
      Serial.println(humidity, 2);
    }
  }

  // The AHT20 can respond with a reading every ~50ms. However, increased read time can cause the IC to heat around 1.0C above ambient.
  // The datasheet recommends reading every 2 seconds.
  //delay(1000);
}


// #include <Wire.h>
// #include <Adafruit_AHTX0.h>
// #include <SoftWire.h>

// // 创建两个AHT20对象
// Adafruit_AHTX0 aht20_1;
// Adafruit_AHTX0 aht20_2;

// // 创建软件I2C对象
// SoftWire myWire(2, 3); // SDA = D2, SCL = D3

// void setup()
// {
//   Serial.begin(115200);
//   Wire.begin(); // 初始化硬件I2C

//   // 初始化第一块AHT20传感器
//   if (!aht20_1.begin()) {
//     Serial.println("AHT20 #1 not detected. Please check wiring. Freezing.");
//     while (1);
//   }

//   // 使用软件I2C初始化第二块AHT20传感器
//   myWire.begin();
//   if (!aht20_2.begin(&myWire)) {
//     Serial.println("AHT20 #2 not detected. Please check wiring. Freezing.");
//     while (1);
//   }
// }

// void loop()
// {
//   static unsigned long previousMillis = 0;
//   unsigned long currentMillis = millis();

//   if (currentMillis - previousMillis >= 1000) {
//     previousMillis = currentMillis;

//     // 从第一块AHT20读取数据
//     sensors_event_t humidity, temp;
//     aht20_1.getEvent(&humidity, &temp);
//     Serial.print("Sensor 1: ");
//     Serial.print("Temperature: ");
//     Serial.print(temp.temperature);
//     Serial.print(" °C, Humidity: ");
//     Serial.print(humidity.relative_humidity);
//     Serial.println(" %");

//     // 从第二块AHT20读取数据
//     aht20_2.getEvent(&humidity, &temp);
//     Serial.print("Sensor 2: ");
//     Serial.print("Temperature: ");
//     Serial.print(temp.temperature);
//     Serial.print(" °C, Humidity: ");
//     Serial.print(humidity.relative_humidity);
//     Serial.println(" %");
//   }

//   delay(1000); // 每秒读取一次数据
// }
