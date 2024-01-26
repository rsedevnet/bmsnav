# <img src="https://rsedevnet.github.io/bmsnav/images/icon.png" height="128" width="128"/>

BMSNav is a companion app for the [Falcon BMS](https://www.falcon-bms.com/) flight simulator that displays kneeboards, briefings, and various navigation aids on a mobile device. It was built primarily to act as a sort of physical kneeboard, obviating the need to activate the pilot model and to flip through the in-game kneeboards. I use it myself on every mission that I fly. That was the impetus, in fact. It's something that I _wanted_, but which didn't exist.

Note that in order to use BMSNav, you must run the accompanying server (BMSNavServer) on the same machine as BMS itself. The server monitors the kneeboard files for the selected theater and automatically [re]generates the images any time a change is made in [Weapon Delivery Planner](https://www.weapondeliveryplanner.nl/). It also monitors the briefings directory and grabs the latest HTML file whenever a change is made (when the user "prints" the briefing in BMS). As such, there's no need to copy/paste files or manually convert images and transfer them to your mobile device. Simply run the server, select a theater, and you're good to go!

[Installation](#installation)  
[Usage](#usage)  
[Donations](#donations)  
[Development](#development)  
[Contact](#contact)  
[License](#license) 

<a name="installation"></a>
## Installation

#### BMSNav

The BMSNav mobile app will soon be availble for both iOS and Android devices via the Apple Store and the Google Play Console. Details to come...

#### BMSNavServer

The latest server release can be downloaded here. Simply unzip the file and place the directory anywhere you like (again, on the same machine as your Falcon BMS installation). It's that simple.

<a name="usage"></a>
## Usage

TODO

<a name="donations"></a>
## Donations

If you find this app useful, please consider donating. Any amount is greatly appreciated and helps to pay for things like app store/developer accounts. Thank you very much!

PayPal: [seidemiller@gmail.com](https://paypal.me/seidemiller)  
Venmo: [@seidemiller](https://venmo.com/?txn=pay&audience=private&recipients=@seidemiller)

<a name="development"></a>
## Development

The source code for the mobile app (iOS and Android) is kept in a private repository.

The source code for the _server_ is kept here in this repository. It's a Python app and packaged as a Windows executable. Several of the ideas are borrowed from the [kneeboard-extractor](https://github.com/root0fall/kneeboard-extractor) project by root0fall.

#### Requirements

* Windows 10/11 (have not tested with earlier versions)
* Falcon BMS (obviously)
* Node (preferably LTS)
* Python3
* Git
* PyQt5
* PyInstaller
* pillow

You can install Node, Python and Git by whichever method you choose. To install the required Python libraries...

```
pip install PyQt5
pip install PyInstaller
pip install pillow
```

#### Retrieving Dependencies

You only need to run this once, or after running `npm run clean`.

```
npm install
```

#### Running the Server

```
npm run start
```

Just as the packaged executable, it will attempt to locate the Falcon BMS home directory and use that as the root for locating the kneeboard files for the selected theater. 

#### Packaging the Executable

```
npm run package
```

<a name="contact"></a>
## Contact

Email: seidemiller@gmail.com  
Falcon Lounge: Terminus

<a name="license"></a>
## MIT License

Copyright (c) 2024 Sean Eidemiller

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be  included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
