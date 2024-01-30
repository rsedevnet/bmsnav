const fs = require('fs');
const path = require('node:path');
const archiver = require('archiver');
const pack = require('../package.json');

const zipPath = path.join('release', `BMSNavServer-${pack.version}.zip`);
const distPath = path.join('release', 'bmsnavserver.dist');
const licPath = path.join(distPath, 'LICENSE.txt');
const cfgPath = path.join(distPath, 'config.default.json');

if (!fs.existsSync(distPath)) {
  console.error('Error locatating dist dir: ' + distPath);
  process.exit(1);
}

try {
  fs.copyFileSync('LICENSE.txt', licPath);
  fs.copyFileSync('config.default.json', cfgPath);
} catch (err) {
  console.error('Error copying license and/or config file: ' + err);
  process.exit(1);
}

const zipFile = fs.createWriteStream(zipPath);
const archive = archiver('zip', { zlib: { level: 9 }});

zipFile.on('close', () => {
  console.log('Wrote zip file to: ' + zipPath);
  console.log(archive.pointer() + ' total bytes.');
})

try {
  archive.pipe(zipFile);
  archive.directory(distPath, false);
  archive.finalize();
} catch (err) {
  console.error('Error during compression: ' + err);
  process.exit(1);
}
