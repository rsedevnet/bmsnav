const fs = require('fs');
const path = require('node:path');
const archiver = require('archiver');

let zipFile;

const zipPath = path.join('dist', 'BMSNavServer-1.0.0.zip');
const exePath = path.join('dist', 'BMSNavServer.exe');
const icoPath = path.join('dist', 'icon.ico');
const licPath = path.join('dist', 'LICENSE.txt');
const configPath = 'config.default.json';

try {
  if (!fs.existsSync(exePath)) throw new Error(exePath + ' does not exist');
  zipFile = fs.createWriteStream(zipPath);
} catch (err) {
  console.error('Unable to create zip file: ' + err);
  process.exit(1);
}

try {
  fs.copyFileSync(path.join('resources', 'icon.ico'), icoPath);
  fs.copyFileSync('LICENSE.txt', licPath);
} catch (err) {
  console.error('Unable to copy icon and/or license file: ' + err);
  process.exit(1);
}

const archive = archiver('zip', { zlib: { level: 9 }});

zipFile.on('close', () => {
  console.log('Wrote zip file to: ' + zipPath);
  console.log(archive.pointer() + ' total bytes.');
})

try {
  archive.pipe(zipFile);
  archive.append(fs.createReadStream(exePath), { name: 'BMSNavServer.exe' });
  archive.append(fs.createReadStream(configPath), { name: 'config.default.json' });
  archive.append(fs.createReadStream(configPath), { name: 'config.json' });
  archive.append(fs.createReadStream(icoPath), { name: 'icon.ico' });
  archive.append(fs.createReadStream(licPath), { name: 'LICENSE.txt' });
  archive.finalize();
} catch (err) {
  console.error('Error during compression: ' + err);
  process.exit(1);
}
