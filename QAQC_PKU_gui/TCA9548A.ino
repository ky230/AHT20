#include <Wire.h>
#include "TCA9548A.h"
#include <AHT20.h>

// 创建 TCA9548A 实例
TCA9548A I2CMux(0x70);

// 创建 AHT20 实例数组
AHT20 aht20s[8];

void setup() {
  Serial.begin(115200);   // 设置串口波特率
  Wire.begin();          // 启动 I2C 通信
  I2CMux.begin(Wire);   // 初始化 TCA9548A 复用器

  // 关闭所有LED灯
  disableAllLEDs();

  // 初始化所有 AHT20 传感器
  for (uint8_t i = 0; i < 8; i++) {
    initializeAHT20(aht20s[i], i);
  }
}

void loop() {
  static unsigned long previousMillis = 0;
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= 500) { // 每秒读取一次
    previousMillis = currentMillis;

    // 打印所有连接的 AHT20 传感器数据
    printSensorData();
  }
}

// 初始化 AHT20 传感器
void initializeAHT20(AHT20 &sensor, uint8_t channel) {
  I2CMux.openChannel(channel);  // 打开指定的通道
  delay(50);                    // 等待传感器稳定

  if (sensor.begin()) {
    Serial.print("AHT20 on channel ");
    Serial.print(channel);
    Serial.println(" initialized.");
  } else {
    Serial.print("AHT20 on channel ");
    Serial.print(channel);
    Serial.println(" not detected.");
  }

  I2CMux.closeChannel(channel);  // 关闭通道
}

// 打印所有连接的 AHT20 传感器数据
void printSensorData() {
  String output = "";

  bool hasData = false;

  for (uint8_t i = 0; i < 8; i++) {
    I2CMux.openChannel(i);  // 打开通道
    delay(50);              // 等待传感器稳定

    float temperature = -999.0;
    float humidity = -999.0;

    if (aht20s[i].begin()) {  // 确保传感器已初始化
      if (aht20s[i].available()) {
        aht20s[i].readData();  // 请求数据更新
        temperature = aht20s[i].getTemperature();
        humidity = aht20s[i].getHumidity();

        // 只在有数据的情况下构建输出字符串
        output += "AHT20_" + String(i) + ": Temperature: " + String(temperature, 2) + " °C, Humidity: " + String(humidity, 2) + " %   ";
        hasData = true;
      }
    }

    I2CMux.closeChannel(i);  // 关闭通道
  }

  // 只打印数据，如果有数据存在
  if (hasData) {
    Serial.println(output);
  }
}

// 关闭所有LED灯
void disableAllLEDs() {
  // 设置所有数字引脚为输出模式，并将其电平设为低
  for (int i = 0; i < 13; i++) {
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
  }
}




