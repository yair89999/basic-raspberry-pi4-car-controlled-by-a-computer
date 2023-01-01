# basic-raspberry-pi4-car-controlled-by-a-computer
This is a raspberry pi 4 car using the Adafruit DC & Stepper Motor HAT

It can move forward/backward, turn, get the distance from objects and see what the car sees all by another program on your pc.

the raspberry pi is the server side of the project and your computer which controls the car is the client side, all by the socket module in python and a TCP protocol

<p>the <a href="https://thepihut.com/products/adafruit-dc-stepper-motor-hat-for-raspberry-pi-mini-kit">Adafruit DC & Stepper Motor HAT</a></p>
<p><img src="https://cdn-shop.adafruit.com/970x728/2348-01.jpg" width="300px"></p>
<b>This is an continued project</b>
and at the end will have:
<ul>
  <h5>on the screen you control the pi from</h5>
  <li>A camera on the car that will send the image to your computer and show it as the background of the movement screen(using a usb camera and openCV)</li>
  <li>The distance the car is from an object(using an ultrasonic distance sensor), will show __.__ if it doesnt get the distance</li>
 </ul>

<ul>
  <h5>versions(each version has the features of the one before):</h5>
  <li>v1:16/12/2022:can only move the car, not see or get the distance</li>
  <li>v2:__/__/____:can see the distance of the car from the object that is in front of it(can be wall,chair...)</li>
  <li>v3:__/__/____:can see the camera in the background of the mvoement screen</li>
</ul>
