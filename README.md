## Freenove 4WD Smart Car Kit for Raspberry Pi

> A 4WD smart car kit for Raspberry Pi.

<img src='Picture/icon.png' width='30%'/>

Please note that this is a fork of the original Freenove 4WD smart car project, and includes some additional capabilities like using state models for performing various auto-drive functionality, addition of headlight, taillights, two different robot arms (one in the back with 2 degrees of freedom, and one in the front with 4 degrees of freedom, using up all 8 servo channels on board). In addition, the UI-based server is replaced with a non-UI server side, and the robot can be controlled using any USB keyboard (you can use a mini-keyboard with a USB dongle). Keycodes from the keyboard may vary from one keyboard to another, so additional improvements may need to be made to this fork before it is fully portable. Use at your own risk.

I am using the following additional GPIO pins and servo channels. See <a href='Code/Server/server_noui.py'>Server code</a> and <a href='Code/Server/Robotarm.py'>Robotarm code</a> for additional details.

* Pin 16: Headlights
* Pin 20: Right turn signal
* Pin 21: Tail light (green)
* Pin 26: Left turn signal

The following servo channels are added:
* Channel '02': Tail arm (up/down)
* Channel '03': Tail claw (open/close)
* Channel '04': Main robotarm pan (left/right)
* Channel '05': Main robotarm top (up/down)
* Channel '06': Main robotarm reach (forward/backward)
* Channel '07': Main robotarm claw (open/close)

I may add a schematic and/or additional resources on the final build here or send on request.

### Download

* **Use command in console**

	Run following command to download all the files in this repository.

	`git clone https://github.com/Freenove/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi.git`

* **Manually download in browser**

	Click the green "Clone or download" button, then click "Download ZIP" button in the pop-up window.
	Do NOT click the "Open in Desktop" button, it will lead you to install Github software.

> If you meet any difficulties, please contact our support team for help.

### Support

Freenove provides free and quick customer support. Including but not limited to:

* Quality problems of products
* Using Problems of products
* Questions of learning and creation
* Opinions and suggestions
* Ideas and thoughts

Please send an email to:

[support@freenove.com](mailto:support@freenove.com)

We will reply to you within one working day.

### Purchase

Please visit the following page to purchase our products:

http://store.freenove.com

Business customers please contact us through the following email address:

[sale@freenove.com](mailto:sale@freenove.com)

### Copyright

All the files in this repository are released under [Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License](http://creativecommons.org/licenses/by-nc-sa/3.0/).

![markdown](https://i.creativecommons.org/l/by-nc-sa/3.0/88x31.png)

This means you can use them on your own derived works, in part or completely. But NOT for the purpose of commercial use.
You can find a copy of the license in this repository.

Freenove brand and logo are copyright of Freenove Creative Technology Co., Ltd. Can't be used without formal permission.


### About

Freenove is an open-source electronics platform.

Freenove is committed to helping customer quickly realize the creative idea and product prototypes, making it easy to get started for enthusiasts of programing and electronics and launching innovative open source products.

Our services include:

* Robot kits
* Learning kits for Arduino, Raspberry Pi and micro:bit
* Electronic components and modules, tools
* Product customization service

Our code and circuit are open source. You can obtain the details and the latest information through visiting the following web site:

http://www.freenove.com
