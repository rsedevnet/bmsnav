# BMSNav

BMSNav is a companion app for the [Falcon BMS](https://www.falcon-bms.com/) flight simulator that displays pilot kneeboards and various navigation aids on a mobile device.

In order to use BMSNav, you must run the accompanying server (BMSNavServer) on the same machine as BMS itself, and your mobile device must be able to access the server.

The server monitors the kneeboard files for the selected theater and automatically [re]generates the images any time a change is made in [Weapon Delivery Planner](https://www.weapondeliveryplanner.nl/). As such, there's no need to copy/paste files or manually convert to images and transfer them to your mobile device. Simply run the server, select a theater, and you're good to go!

[Installation](#installation)  
[Usage](#usage)  
[Donations](#donations)  
[Development](#development)  
[Contact](#contact)  
[License](#license) 

<a name="installation"></a>
## Installation

TODO

<a name="usage"></a>
## Usage

TODO

<a name="donations"></a>
## Donations

If you find this app useful, please consider donating. Any amount is greatly appreciated and helps to pay for things like app store/developer accounts. Thank you!

PayPal: [seidemiller@gmail.com](https://paypal.me/seidemiller)
Venmo: [@seidemiller](https://venmo.com/?txn=pay&audience=private&recipients=@seidemiller)

<a name="development"></a>
## Development

The source code for the mobile app (iOS and Android) is kept in a private repository.

The source code for the _server_ is kept here in this repository. It's a Python app and packaged as a Windows executable.

#### Requirements

* Windows 10/11 (have not tested with earlier versions)
* Falcon BMS (obviously)
* Node (preferably LTS)
* Python3
* PyQt5
* pillow

You can install Node and Python in whichever manner you choose. To install the required Python libraries...

```
pip install PyQt5
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
