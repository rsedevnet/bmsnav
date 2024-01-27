# <img src="https://rsedevnet.github.io/bmsnav/images/icon.png" height="128" width="128"/>

BMSNav is a companion app for the [Falcon BMS](https://www.falcon-bms.com/) flight simulator that displays kneeboards, briefings, and various navigation aids on a mobile device. It was built primarily to act as a sort of physical kneeboard, obviating the need to activate the pilot model and to flip through the in-game kneeboards. I use it myself on every mission that I fly, and that was the impetus, in fact. It's something that I wanted, but which didn't exist.

Note that in order to use BMSNav, you must run the accompanying server (BMSNavServer) on the same machine as BMS itself. The server monitors the kneeboard files for the selected theater and automatically [re]generates the images any time a change is made in [Weapon Delivery Planner](https://www.weapondeliveryplanner.nl/). It also monitors the briefings directory and grabs the latest HTML file whenever a change is made (when the user "prints" the briefing in BMS). As such, there's no need to copy/paste files or manually convert images and transfer them to your mobile device. Simply run the server, select a theater, and you're good to go!

[NOTE FOR APP STORE REVIEWERS](#reviewers)  
[Installation](#installation)  
[Usage](#usage)  
[Donations](#donations)  
[Development](#development)  
[Contact](#contact)  
[License](#license)  
[FalconDED Font](#font)

<a name="reviewers"></a>
## Important Note for App Store Reviewers

As mentioned above, the functionality of the app depends on access to a server running on the same machine as the game (Falcon BMS). There is, however, a "Demo Mode" for reviewers or those simply wishing to get an idea of how the app works, without having to install the game or the server. To enable the demo mode, click the settings (gear) icon on the top right of the screen and select "Demo Mode" at the bottom of the list. Then click the back button or "Save" to apply.

Once in demo mode, the kneeboards and the briefing will be "static" and served from a host on the Internet. It should give you a good idea of what users will see when connected to an actual server.

<img src="http://rsedevnet.github.io/bmsnav/images/not-timed-out-helper.png" height="540" width="405"/>
<img src="http://rsedevnet.github.io/bmsnav/images/settings-demo-helper.png" height="540" width="405"/>

<a name="installation"></a>
## Installation

#### BMSNav

The BMSNav mobile app will soon be availble for both iOS and Android devices via the Apple Store and the Google Play Console. Details to come...

#### BMSNavServer

The latest server release can be downloaded here. Simply unzip the file and place the directory anywhere you like (again, on the same machine as your Falcon BMS installation). It's that simple.

<a name="usage"></a>
## Usage

#### BMSNav

There are four main screens in BMSNav: Left Board, Briefing, Notepad, and Right Board, all of which are fairly self-explanatory.

The Left and Right Board screens display the left and right kneeboards, respectively (up to 16 pages each). Swipe left or right to navigate between pages, and pinch if you need to zoom-in. The number of pages displayed for each board is independently configurable via the settings panel (gear icon on the top right). This is helpful, for example, if you only have, six kneeboards on the left side and you don't wish to scroll through 10 blank pages.

BMSNav integrates seamlessly with Weapon Delivery Planner and anything else that generates kneeboards. When you update/save the kneeboards in WDP, BMSNavServer will automatically serve the new images. Note that you'll have to refresh the screen in the app to see the updated kneeboards (the refresh icon on the top right, next to the gear icon).

<img src="http://rsedevnet.github.io/bmsnav/images/datacard.jpg" height="540" width="405"/>

The Briefing screen displays an HTML version of the mission briefing. Like the kneeboards, when you update the briefing by clicking "Print" in the 2D mission screen (on the briefing panel), the server will automatically serve the new HTML file. And again, you'll need to refresh the screen in the app in order to see the updated briefing. You will also need to enabled the "Briefing Output to File" and "HTML Briefings" options in the BMS configuration tool.

<img src="http://rsedevnet.github.io/bmsnav/images/briefing.png" height="540" width="405"/>

Finally, the Notepad screen is for taking notes, either during the mission or beforehand. Flight lead mentions something important during the briefing that isn't on the kneeboards? Write it down on the notepad. JTAC coordinates for a target strike? Write it down on... you get the idea.

Note that the functionality differs somewhat between iOS and Android; the former being the more "full-featured" experience.

With regard to input, you _can_ use your finger, but you'll be much happier with a stylus. And rest assured that you don't need to spend >$100 for an Apple stylus. I use one of these with my iPad ($30 on Amazon; link below). It works great!

[https://www.amazon.com/dp/B08Z7LGR1L](https://www.amazon.com/dp/B08Z7LGR1L)

It doesn't work on my Android tablet, however. I'm no expert when it comes to Android devices, so I'll leave you to figure out on your own what sort of stylus you need for that. Sorry. :\

<img src="http://rsedevnet.github.io/bmsnav/images/notepad.png" height="540" width="405"/>

#### BMSNavServer

To start the server, click on the ```BMSNavServer.exe``` file in the directory that was unzipped per the instructions in the [Installation](#installation) section above. This should open a new window. The server will attempt to generate the kneeboards for the selected theater (default is Korea) and the most recently saved briefing (irrespective of theater). The kneeboards and the briefing will then be made available via HTTP on the default port of 2676, unless overridden in the config file (```config.json```). Additionally, the server will monitor both the briefings directory and the kneeboards for the selected theater. If any changes are made, whether by BMS or Weapon Delivery Planner, the kneeboards and/or briefing will be regenerated and re-served automatically. You do _not_ need to restart the server when, for example, the kneeboards are saved in WDP.

If for some reason you need to run the server on a port other that 2676, simply open the ```config.json``` file in the same directory as the executable and set the port as desired. For example...

```
{
  "selectedTheater": "Korea",
  "port": 8000
}
```

Note that you may need to _add_ the "port" property if it doesn't exist.

Restart the server for any config changes to take effect.

Once the server is up and running, you'll need to configure the relevant settings in the mobile app. Click on the gear icon on the top right of the screen and enter the IP and port of the server. The IP will obviously be the address of the machine on which the server is running. Of course you'll need to make sure that your mobile device is able to route to the server.

<img src="http://rsedevnet.github.io/bmsnav/images/settings.jpg" height="540" width="405"/>

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

<a name="font"></a>
## FalconDED Font

The FalconDED font used in the logo was created by ura_ba and licensed under Creative Commons Attribution Non-commercial Share Alike.

Home: [https://fontstruct.com/fontstructions/show/1014500](https://fontstruct.com/fontstructions/show/1014500)  
License: [http://creativecommons.org/licenses/by-nc-sa/3.0](http://creativecommons.org/licenses/by-nc-sa/3.0)
