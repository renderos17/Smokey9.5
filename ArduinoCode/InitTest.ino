#include <SPI.h>
#include <Adafruit_DotStar.h>
#include <Adafruit_GFX.h>    // Core graphics library
#include <Adafruit_ST7735.h> // Hardware-specific library
#include <SPI.h>
#include <Servo.h>

#define NUMPIXELS1 12
#define NUMPIXELS2 12

#define DATAPIN1   7
#define CLOCKPIN1  6
#define DATAPIN2   5
#define CLOCKPIN2  4

Adafruit_DotStar botStripLeft = Adafruit_DotStar(NUMPIXELS1, DATAPIN1, CLOCKPIN1, DOTSTAR_BGR);
Adafruit_DotStar botStripRight = Adafruit_DotStar(NUMPIXELS2, DATAPIN2, CLOCKPIN2, DOTSTAR_BGR);

#define TFT_CS     45
#define TFT_RST    51
#define TFT_DC     53
#define TFT_SCLK   49
#define TFT_MOSI   47

Adafruit_ST7735 tft = Adafruit_ST7735(TFT_CS, TFT_DC, TFT_MOSI, TFT_SCLK, TFT_RST);


Servo gripper;

int pos = 0;

int in1Pin = 22;
int enablePin1 = 2;
int in2Pin = 24;
int in3Pin = 26;
int enablePin2 = 3;
int in4Pin = 28;

byte val;
bool isNotMoving = true;
bool isGrip = true;

void setup() {
  botStripLeft.begin();
  botStripLeft.show(); 
  botStripRight.begin();
  botStripRight.show(); 
  
  Serial.begin(9600);
  
  pinMode(in1Pin, OUTPUT);
  pinMode(in2Pin, OUTPUT);
  pinMode(enablePin1, OUTPUT);
  pinMode(in3Pin, OUTPUT);
  pinMode(in4Pin, OUTPUT);
  pinMode(enablePin2, OUTPUT);

  tft.initR(INITR_BLACKTAB);
  testdrawcircles(10, ST7735_WHITE);

  gripper.attach(12);
}

int      head  = 0, tail = -10; // Index of first 'on' and 'off' pixels
uint32_t color = 0xFF0000;

void loop() {
  if (Serial.available()) {
    val = Serial.read();
    Serial.println(int(val));
    motorMove(int(val));
  }
 else {
  if (isNotMoving)
    rainbow();
  else
    motorMove(int(val));
  }
}
void motorMove(int x) {
  if (x == 89 || x == 90) //Stop
  {
    setMotor1(0, true);
    setMotor2(0, true);
    doubleBotColor(botStripLeft.Color(255, 0, 0));
    isNotMoving = true;
  }

  if (x == 66) //Move front
  {
    setMotor1(255, true);
    setMotor2(255, true);
    doubleBotColor(botStripLeft.Color(0, 0, 255));
    isNotMoving = false;
  }

  if (x == 78) //Move back
  {
    setMotor1(255, false);
    setMotor2(255, false);
    doubleBotColor(botStripLeft.Color(0, 255, 0));
    isNotMoving = false;
  }

  if (x == 77) //left
  {
    setMotor1(255, false);
    setMotor2(255, true);
    isNotMoving = false;
  }

  if (x == 87) //right
  {
    setMotor1(255, true);
    setMotor2(255, false);
    isNotMoving = false;
  }

  if (x == 82) //grip ena
  {
    if (isGrip) {
      gripper.write(180);
      isGrip = false;
    }
    else {
      gripper.write(0);
      isGrip = true;
    }
  }
}

void setMotor1(int speed, boolean reverse)
{
  analogWrite(enablePin1, speed);
  digitalWrite(in1Pin, !reverse);
  digitalWrite(in2Pin, reverse);
}

void setMotor2(int speed, boolean reverse)
{
  analogWrite(enablePin2, speed);
  digitalWrite(in3Pin, !reverse);
  digitalWrite(in4Pin, reverse);
}

void doubleBotColor(uint32_t c) { //C is color
  for (uint16_t i = 0; i < botStripLeft.numPixels(); i++) {
    botStripLeft.setPixelColor(i, c);
    botStripRight.setPixelColor(i, c);
    botStripLeft.show();
    botStripRight.show();
  }
}

void doubleBotSepColor(uint32_t c1, uint32_t c2) {
  for (uint16_t i = 0; i < botStripLeft.numPixels(); i++) {
    botStripLeft.setPixelColor(i, c1);
    botStripRight.setPixelColor(i, c2);
    botStripLeft.show();
    botStripRight.show();
  }
}

void rainbow(){
  for (int x = 0;  x < 255; x++) {
      doubleBotColor(Wheel(x));
      delay(5);
          if (Serial.available() > 0)
            break;
  }
}

uint32_t Wheel(byte WheelPos) {
  WheelPos = 255 - WheelPos;
  if (WheelPos < 85) {
    return botStripLeft.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  }
  if (WheelPos < 170) {
    WheelPos -= 85;
    return botStripLeft.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
  WheelPos -= 170;
  return botStripLeft.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
}

void testdrawcircles(uint8_t radius, uint16_t color) {
  for (int16_t x=0; x < tft.width()+radius; x+=radius*2) {
    for (int16_t y=0; y < tft.height()+radius; y+=radius*2) {
      tft.drawCircle(x, y, radius, color);
    }
  }
}

/*          
    for (int x = 0; x <= 255; x++) {
        setMotor1(x,false);
        setMotor2(x,false);
        Serial.println(x);
        delay(100);
      }
      
    for (int x = 255; x >= 0; x--) {
        setMotor1(x,false);
        setMotor2(x,false);
        Serial.println(x);
        delay(100);
      }

  botStrip.setPixelColor(head, color);
  botStrip.setPixelColor(tail, 0);
  botStrip.show();
  delay(20);

  if(++head >= NUMPIXELS1) {
    head = 0;
    if((color >>= 8) == 0)
      color = 0xFF0000;
  }
  if(++tail >= NUMPIXELS1) tail = 0;
 */
